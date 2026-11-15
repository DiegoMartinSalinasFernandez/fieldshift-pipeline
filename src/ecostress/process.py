"""Procesa la extracción de ECOSTRESS (data/raw/ecostress/ecostress_extraccion_<mes>.csv) a
data/processed/ecostress/ecostress_mensual.csv y regenera docs/datasets/ecostress.md.

Uso: python src/ecostress/process.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.config import estados_config  # noqa: E402
from src.zona_texto import lista_estados  # noqa: E402

RAW = REPO / "data/raw/ecostress"
OUT = REPO / "data/processed/ecostress"
CARD = REPO / "docs/datasets/ecostress.md"
MIN_PX = 10  # píxeles agrícolas válidos mínimos para que una pasada cuente en el condado
# meses bajados en r005-r006 con un bbox que dejaba afuera el oeste de Iowa (ver download.py); solo
# existen en la máquina de la primera tanda (IA, IL, IN)
MESES_BBOX_ESTE = (["2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10"]
                   if "IA" in estados_config() else [])

S = "NASA JPL ECOSTRESS colección 2 (LP DAAC), 70 m"
COLS = [
    ("lst_ecostress_c", "Temperatura de superficie (ECO_L2T_LSTE.002 capa LST) media del mes: promedio de las "
     "pasadas con datos, cada una la media de los píxeles agrícolas de buena calidad y sin nube de la ventana "
     "de 2,24 km del condado", "°C", S + ", ECO_L2T_LSTE.002", "X01"),
    ("et_ecostress_mm_dia", "Evapotranspiración diaria (ECO_L3T_JET.002 capa ETdaily) media del mes, mismas "
     "pasadas y píxeles que la LST", "mm/día", S + ", ECO_L3T_JET.002", "X02"),
    ("esi_ecostress", "Índice de estrés evaporativo (ECO_L4T_ESI.002 capa ESI, ET/PET) medio del mes, mismas "
     "pasadas y píxeles que la LST", "adim.", S + ", ECO_L4T_ESI.002", "X03"),
    ("n_pasadas_ecostress", "Pasadas diurnas del mes con al menos 10 píxeles agrícolas válidos de LST en la "
     "ventana del condado (0 si todas nubladas, sin dato o sin pasada sobre la ventana)", "pasadas", S, ""),
]


def cargar() -> pd.DataFrame:
    archivos = sorted(RAW.glob("ecostress_extraccion_*.csv"))
    if not archivos:
        return pd.DataFrame()
    df = pd.concat([pd.read_csv(p, dtype={"fips": str, "granulo": str, "fecha_hora_utc": str}) for p in archivos],
                   ignore_index=True)
    df["fips"] = df.fips.str.zfill(5)
    # una misma pasada puede caer en dos teselas MGRS que se solapan: queda la de más píxeles agrícolas
    df["pasada"] = df.granulo.str.rsplit("_", n=1).str[0] + "_" + df.fecha_hora_utc
    df = df.sort_values(["fips", "pasada", "n_px_agricolas", "tesela"], ascending=[True, True, False, True])
    df = df.drop_duplicates(["fips", "pasada"], keep="first")
    df["mes"] = df.fecha_hora_utc.str[:4] + "-" + df.fecha_hora_utc.str[4:6]
    return df


def mensual(df: pd.DataFrame) -> pd.DataFrame:
    ok = df[df.n_px_lst.fillna(0) >= MIN_PX].copy()
    ok["lst_c"] = ok.lst_k_media - 273.15
    for c, n in (("et_daily_media", "n_px_et"), ("esi_media", "n_px_esi")):
        ok.loc[ok[n].fillna(0) < MIN_PX, c] = float("nan")
    g = ok.groupby(["fips", "mes"])
    m = pd.DataFrame({
        "lst_ecostress_c": g.lst_c.mean(),
        "et_ecostress_mm_dia": g.et_daily_media.mean(),
        "esi_ecostress": g.esi_media.mean(),
        "n_pasadas_ecostress": g.size(),
    })
    # condado-mes con pasadas sobre el condado pero ninguna válida: n_pasadas = 0, el resto vacío
    # y todos los condados de condados.csv en cada mes bajado: sin ninguna pasada sobre su ventana, n_pasadas = 0
    cond = pd.read_csv(REPO / "data/reference/condados.csv", dtype={"fips": str}).fips.str.zfill(5)
    todos = pd.MultiIndex.from_product([sorted(cond), sorted(df.mes.unique())], names=["fips", "mes"])
    todos = pd.DataFrame(index=todos)
    m = todos.join(m).reset_index()
    # meses bajados con el bbox angosto de r005-r006 (sin el oeste de Iowa) y todavía sin su suplemento
    # _oeste: los condados que no aparecen en la extracción no se consultaron, así que quedan vacíos
    incompletos = {p.stem.split("_")[-1] for p in RAW.glob("ecostress_extraccion_????-??.csv")
                   if p.stem.split("_")[-1] in MESES_BBOX_ESTE
                   and not (RAW / f"{p.stem}_oeste.csv").exists()}
    vistos = set(zip(df.fips, df.mes))
    llenar = ~m.mes.isin(incompletos) | pd.Series([k in vistos for k in zip(m.fips, m.mes)], index=m.index)
    m.loc[llenar, "n_pasadas_ecostress"] = m.loc[llenar, "n_pasadas_ecostress"].fillna(0)
    m["n_pasadas_ecostress"] = m.n_pasadas_ecostress.astype("Int64")
    m["anio"] = m.mes.str[:4].astype(int)
    m = m[["fips", "anio", "mes", "lst_ecostress_c", "et_ecostress_mm_dia", "esi_ecostress", "n_pasadas_ecostress"]]
    for c, d in (("lst_ecostress_c", 2), ("et_ecostress_mm_dia", 3), ("esi_ecostress", 4)):
        m[c] = m[c].round(d)
    return m.sort_values(["fips", "mes"]).reset_index(drop=True)


TEXTO = """
## Fuentes y acceso

- **DOI de los productos de la NASA (colección 2, V002, LP DAAC):**
  - ECO_L2T_LSTE: https://doi.org/10.5067/ECOSTRESS/ECO_L2T_LSTE.002
  - ECO_L3T_JET: https://doi.org/10.5067/ECOSTRESS/ECO_L3T_JET.002
  - ECO_L4T_ESI: https://doi.org/10.5067/ECOSTRESS/ECO_L4T_ESI.002
- Citas completas: `docs/research/citas_nasa.md`.

- **ECOSTRESS colección 2, productos en teselas MGRS de 70 m** de LP DAAC (Earthdata Cloud):
  `ECO_L2T_LSTE.002` (capas `LST`, `QC`, `cloud`), `ECO_L3T_JET.002` (capa `ETdaily`) y
  `ECO_L4T_ESI.002` (capa `ESI`). Nombres de producto y capa verificados en la API de productos de
  AppEEARS (`/api/product/<producto>`) y en los nombres de archivo de CMR.
- `src/ecostress/download.py` busca en CMR las pasadas de `ECO_L3T_JET` de cada mes sobre el bbox de
  los condados de {estados} (un bbox por estado, de `data/reference/condados.gpkg`, con 0,1° de margen), empareja cada
  una con la LSTE y la ESI de la misma órbita, escena y tesela, y lee de
  los COG (lectura por rango HTTP con token de Earthdata, sin bajar la tesela entera) una ventana de
  32x32 píxeles alrededor del punto agrícola de cada condado. Guarda por condado y pasada el número de
  píxeles agrícolas, de píxeles válidos y la media de LST, ETdaily y ESI en
  `data/raw/ecostress/ecostress_extraccion_<AAAA-MM>.csv` (un archivo por mes, se mueve a raw solo
  cuando el mes está completo; el mes en curso queda en `data/interim/ecostress/`).
- `src/ecostress/process.py` une los meses, saca pasadas duplicadas por solape de teselas y promedia
  por condado y mes.

## Supuestos

- **Acceso directo a LP DAAC en lugar de AppEEARS.** La API de AppEEARS pide un login propio con
  usuario y contraseña; el token de Earthdata da 403. Se leen los COG de LP DAAC directo.
- **Ventana de muestra, no el condado entero.** Las teselas completas de 2018 a 2025 son cientos de
  miles de archivos (CMR: ~221 000 granulos LSTE y ~81 000 JET/ESI sobre el bbox de IA, IL e IN) y pasarían de lejos
  los 5 GB. Por condado se usa una ventana de 32x32 píxeles de 70 m (2,24 km de lado) centrada en el
  píxel agrícola (máscara `data/reference/mascara_agricola.tif`, CDL) más cercano al centroide de los
  píxeles agrícolas del condado (`data/interim/ecostress/puntos_condados.csv`). Dentro de la ventana
  solo cuentan los píxeles de 70 m cuyo centro cae en un píxel agrícola de la máscara (muestreo por
  vecino más cercano). Es una muestra local, no la media de todo el condado.
- **Calidad:** cuentan los píxeles con bits 0-1 de `QC` en 00 (mejor calidad) o 01 (nominal), `cloud`
  = 0 y valor finito en rango físico (LST 200-350 K, ETdaily 0-30, ESI 0-2). La máscara de nube y
  calidad de la LSTE se aplica también a ETdaily y ESI de la misma pasada (misma grilla).
- **Pasadas:** solo las escenas con producto JET (pasadas diurnas con ET); ECOSTRESS pasa a horas
  variables (incluye pasadas de madrugada, ~11 UTC), así que la LST mensual mezcla horas distintas.
  Una pasada cuenta si tiene al menos 10 píxeles agrícolas válidos; la media mensual es el promedio
  simple de las pasadas (cada pasada pesa igual).
- **ETdaily en mm/día:** la API de AppEEARS lista la unidad de `ETdaily` como W/m², pero los valores
  (0-6 en julio sobre maíz y soja) son de mm/día, la unidad de la guía de usuario de L3T JET.
- **Meses:** solo abril a octubre (sin nieve y con más pasadas despejadas), de 2018-08 a 2025-10,
  empezando por los más recientes. Los meses de noviembre a marzo no se bajaron.

## Problemas conocidos

- La descarga es larga (~100 pasadas/min con 40 hilos; un mes tiene de ~100 a ~750 pasadas sobre los
  condados): la cobertura crece ronda a ronda. Solo están los meses que aparecen en `data/raw/ecostress/`.
- Condados con poca superficie agrícola cerca del punto tienen pocas píxeles válidos o ninguno.
- El orden de los meses sale de `download.py`, no de `config/config.yaml`.
{oeste}"""

OESTE_IOWA = """- **Oeste de Iowa (corregido en r007).** En r005-r006 el bbox de CMR era `-91.6,37.0,-84.8,43.5` y dejaba
  afuera las teselas del oeste de Iowa (83 condados nunca tenían pasada). Desde r007 el bbox cubre los
  tres estados de la primera tanda. Los meses bajados con el bbox angosto (2025-04 a 2025-10) se completan con
  `ecostress_extraccion_<AAAA-MM>_oeste.csv` (solo las escenas que faltaban); mientras un mes no tenga su
  suplemento, los condados que no aparecen en su extracción quedan con `n_pasadas_ecostress` vacío (no 0).
"""


def data_card(m: pd.DataFrame) -> None:
    lineas = ["# Data card — ecostress", "",
              "Paquete `ecostress` de Field Shift: temperatura de superficie, evapotranspiración y estrés "
              "evaporativo de ECOSTRESS por condado y mes.", "",
              "## Diccionario de columnas", "",
              "| archivo | columna | descripcion | unidad | fuente | id_catalogo | desde | hasta | faltantes_pct |",
              "|---|---|---|---|---|---|---|---|---|"]
    for c, desc, u, f, idc in COLS:
        s = m[c]
        ok = m.loc[s.notna(), "mes"].astype(str)
        desde, hasta = (ok.min(), ok.max()) if len(ok) else ("", "")
        falt = 100 * s.isna().mean()
        lineas.append(f"| ecostress_mensual.csv | {c} | {desc} | {u} | {f} | {idc} | {desde} | {hasta} | {falt:.1f} |")
    CARD.parent.mkdir(parents=True, exist_ok=True)
    texto = TEXTO.format(estados=lista_estados(), oeste=OESTE_IOWA if MESES_BBOX_ESTE else "")
    CARD.write_text("\n".join(lineas) + "\n" + texto, encoding="utf-8")


def main() -> None:
    t = time.time()
    df = cargar()
    if df.empty:
        print("sin datos en data/raw/ecostress/")
        return
    m = mensual(df)
    OUT.mkdir(parents=True, exist_ok=True)
    m.to_csv(OUT / "ecostress_mensual.csv", index=False, lineterminator="\n")
    data_card(m)
    print(f"ecostress_mensual.csv: {len(m)} filas, {m.mes.nunique()} meses ({time.time() - t:.1f} s)")


if __name__ == "__main__":
    main()
