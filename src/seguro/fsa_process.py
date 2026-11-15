"""Paquete seguro — siembra prevenida por condado desde FSA Crop Acreage Data (T125).

Entrada: data/raw/seguro/fsa/fsa_acres_<AAAA>_final.zip (de src/seguro/fsa_download.py). Cada zip
trae un .xlsx nacional. Desde 2012 la hoja es `county_data` (con una fila de título antes del
encabezado en algunos años); en 2009–2011 es la primera hoja y no tiene `Irrigation Practice`.
El encabezado se busca por la celda `State Code`, así no importa en qué fila esté.

Salida: data/processed/seguro/siembra_prevenida_anual.csv
    fips, anio, cultivo, sup_sembrada_fsa_ac, sup_prevenida_ac, sup_fallida_ac,
    sup_prevenida_riego_ac, sup_prevenida_secano_ac, pct_prevenida
y docs/datasets/seguro_siembra_prevenida.md (sección del data card de `seguro`, generada).

Reglas (docs/research/siembra_prevenida.md):
- Estados de config.yaml filtrados por FIELDSHIFT_ESTADOS.
- fips = State Code + County Code. Los códigos administrativos de FSA que no son FIPS (condados
  partidos en dos oficinas) se suman al FIPS del Census con data/reference/fsa_condados_admin.csv.
  Los códigos que no están ni en condados.csv ni en esa tabla se listan en el data card con sus
  acres: no se descartan en silencio.
- Cultivos: maíz 0041 sin pochoclo, dulce ni ornamental; soja 0081 sin edamame; trigo de invierno
  0011 con "WINTER" en el tipo; avena 0016. Se suman todos los usos (grano, silo, semilla...) y
  riego + secano, salvo `Grazing` en trigo y avena: desde 2019 FSA cuenta dos veces el acre que se
  pastorea y se cosecha (nota de la página de FSA); se saca en todos los años para que la serie sea
  pareja.
- pct_prevenida = 100 × prevenida / (sembrada + prevenida); vacío si el denominador es 0.
- Riego y secano por separado solo para la prevenida: desde 2012 con `Irrigation Practice`, en
  2011 con las columnas `Prevented Irrigated` / `Nonirrigated`; en 2009–2010 no hay, vacío. Las filas con la práctica en blanco cuentan en el total y en
  ninguna de las dos.
- Un 0 es un 0 real (el condado declaró el cultivo y no tuvo siembra prevenida).

Uso: python src/seguro/fsa_process.py [--anios 2019]
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.common.config import estados_config  # noqa: E402
from src.common.validacion import validar_csv  # noqa: E402

RAW = REPO / "data" / "raw" / "seguro" / "fsa"
OUT = REPO / "data" / "processed" / "seguro"
SALIDA = OUT / "siembra_prevenida_anual.csv"
CARD = REPO / "docs" / "datasets" / "seguro_siembra_prevenida.md"
CONDADOS = REPO / "data" / "reference" / "condados.csv"
TABLA_ADMIN = REPO / "data" / "reference" / "fsa_condados_admin.csv"

COLUMNAS = ["fips", "anio", "cultivo", "sup_sembrada_fsa_ac", "sup_prevenida_ac", "sup_fallida_ac",
            "sup_prevenida_riego_ac", "sup_prevenida_secano_ac", "pct_prevenida"]

# Nombre de columna en el .xlsx (en minúsculas) -> nombre interno. En 2009 `Crop Type` es un
# código y el nombre del tipo está en `Crop Type Name`: se prefiere el nombre.
ENCABEZADOS = {
    "state code": "st", "county code": "cty", "crop code": "cod_cultivo",
    "crop type name": "tipo_nombre", "crop type": "tipo",
    "intended use": "uso", "irrigation practice": "riego",
    "planted acres": "sembrada", "prevented acres": "prevenida", "failed acres": "fallida",
    "failded acres": "fallida",  # así, con la errata, en 2012
    # 2011: formato ancho, total y por práctica
    "planted total": "sembrada", "prevented total": "prevenida", "failed total": "fallida",
    "prevented irrigated": "prev_riego", "prevented nonirrigated": "prev_secano",
}
# 2010: la primera columna se llama `State` (el código); en los otros años `State` es el nombre.
ENCABEZADO_ESTADO_2010 = "state"
OBLIGATORIAS = ["st", "cty", "cod_cultivo", "sembrada", "prevenida", "fallida"]
USO_PASTOREO = {"GRAZING", "GZ"}


def cultivo_de(cod: str, tipo: str) -> str | None:
    """Cultivo del proyecto para un código de cultivo y un tipo de FSA (None = no se usa)."""
    t = (tipo or "").upper()
    if cod == "0041":
        return None if any(x in t for x in ("POPCORN", "SWEET", "ORNAMENTAL")) else "maiz"
    if cod == "0081":
        return None if "EDAMAME" in t else "soja"
    if cod == "0011":
        return "trigo_invierno" if "WINTER" in t else None
    if cod == "0016":
        return "avena"
    return None


def _texto(v, ancho: int) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v).strip()
    return s.zfill(ancho) if s.isdigit() else s


def leer_xlsx(contenido: bytes, estados_fips: set[str]) -> pd.DataFrame:
    """Lee la hoja por condado de un .xlsx de FSA; devuelve las filas de los estados pedidos."""
    import openpyxl

    wb = openpyxl.load_workbook(io.BytesIO(contenido), read_only=True, data_only=False)
    hoja = "county_data" if "county_data" in wb.sheetnames else wb.sheetnames[0]
    ws = wb[hoja]
    idx: dict[str, int] | None = None
    filas = []
    for r in ws.iter_rows(values_only=True):
        if idx is None:
            cab = [" ".join(str(h or "").split()).lower() for h in r] if r else []
            if cab and cab[0] in ("state code", ENCABEZADO_ESTADO_2010) and "county code" in cab:
                idx = {}
                for i, h in enumerate(cab):
                    k = ENCABEZADOS.get(h)
                    if k and k not in idx:
                        idx[k] = i
                if "st" not in idx:
                    idx["st"] = 0
                faltan = [c for c in OBLIGATORIAS if c not in idx]
                if faltan:
                    raise ValueError(f"hoja {hoja}: faltan columnas {faltan}")
            continue
        if not r or r[idx["st"]] is None:
            continue
        st = _texto(r[idx["st"]], 2)
        if st not in estados_fips:
            continue
        tipo_i = idx.get("tipo_nombre", idx.get("tipo"))
        prev = r[idx["prevenida"]]
        if "prev_riego" in idx:  # 2011, formato ancho
            pr, ps = r[idx["prev_riego"]], r[idx.get("prev_secano")] if "prev_secano" in idx else None
        elif "riego" in idx:
            practica = _texto(r[idx["riego"]], 0).upper()
            pr = prev if practica == "I" else 0
            ps = prev if practica == "N" else 0
        else:
            pr = ps = None
        filas.append({
            "st": st,
            "cty": _texto(r[idx["cty"]], 3),
            "cod_cultivo": _texto(r[idx["cod_cultivo"]], 4),
            "tipo": _texto(r[tipo_i], 0) if tipo_i is not None else "",
            "uso": _texto(r[idx["uso"]], 0) if "uso" in idx else "",
            "sembrada": r[idx["sembrada"]], "prevenida": prev, "fallida": r[idx["fallida"]],
            "prev_riego": pr, "prev_secano": ps,
        })
    wb.close()
    if idx is None:
        raise ValueError(f"hoja {hoja}: no encontré la fila de encabezado (`State Code`)")
    df = pd.DataFrame(filas, columns=["st", "cty", "cod_cultivo", "tipo", "uso", "sembrada",
                                      "prevenida", "fallida", "prev_riego", "prev_secano"])
    con_riego = "riego" in idx or "prev_riego" in idx
    for c in ("sembrada", "prevenida", "fallida") + (("prev_riego", "prev_secano") if con_riego else ()):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    df.attrs["con_riego"] = con_riego
    return df


def leer_zip(ruta: Path, estados_fips: set[str]) -> pd.DataFrame:
    with zipfile.ZipFile(ruta) as z:
        xs = [n for n in z.namelist() if n.lower().endswith(".xlsx")]
        if len(xs) != 1:
            raise ValueError(f"{ruta.name}: se esperaba un .xlsx y hay {xs}")
        df = leer_xlsx(z.read(xs[0]), estados_fips)
        df.attrs["xlsx"] = xs[0]
    return df


def tabla_admin(ruta: Path = TABLA_ADMIN) -> dict[str, str]:
    t = pd.read_csv(ruta, dtype=str)
    return dict(zip(t["codigo_fsa"].str.zfill(5), t["fips"].str.zfill(5)))


def agregar(df: pd.DataFrame, anio: int, admin: dict[str, str], validos: set[str]
            ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Devuelve (tabla anual, códigos convertidos, códigos sin FIPS) para un año."""
    d = df.copy()
    d["cultivo"] = [cultivo_de(c, t) for c, t in zip(d["cod_cultivo"], d["tipo"])]
    d = d[d["cultivo"].notna()]
    pastoreo = d["cultivo"].isin(["trigo_invierno", "avena"]) & d["uso"].str.upper().isin(USO_PASTOREO)
    d = d[~pastoreo]
    d["codigo"] = d["st"] + d["cty"]
    d["fips"] = d["codigo"].map(lambda c: admin.get(c, c))
    sumas = ["sembrada", "prevenida", "fallida"]
    convertidos = (d[d["codigo"] != d["fips"]].groupby(["codigo", "fips", "cultivo"], as_index=False)[sumas]
                   .sum().assign(anio=anio))
    sin_fips = d[~d["fips"].isin(validos)]
    sin_fips = sin_fips.groupby(["codigo", "cultivo"], as_index=False)[sumas].sum().assign(anio=anio)
    d = d[d["fips"].isin(validos)]
    con_riego = df.attrs.get("con_riego", False)
    if not con_riego:
        d["prev_riego"] = d["prev_secano"] = 0.0
    g = d.groupby(["fips", "cultivo"], as_index=False)[sumas + ["prev_riego", "prev_secano"]].sum()
    out = pd.DataFrame({
        "fips": g["fips"], "anio": anio, "cultivo": g["cultivo"],
        "sup_sembrada_fsa_ac": g["sembrada"], "sup_prevenida_ac": g["prevenida"],
        "sup_fallida_ac": g["fallida"],
        "sup_prevenida_riego_ac": g["prev_riego"] if con_riego else np.nan,
        "sup_prevenida_secano_ac": g["prev_secano"] if con_riego else np.nan,
    })
    den = out["sup_sembrada_fsa_ac"] + out["sup_prevenida_ac"]
    out["pct_prevenida"] = np.where(den > 0, 100 * out["sup_prevenida_ac"] / den.where(den > 0), np.nan)
    return out[COLUMNAS], convertidos, sin_fips


def redondear(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in COLUMNAS[3:]:
        df[c] = df[c].round(2 if c != "pct_prevenida" else 3)
    return df


def tabla_md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lineas = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in df.itertuples(index=False):
        lineas.append("| " + " | ".join("" if pd.isna(v) else (f"{v:,.0f}" if isinstance(v, float) else str(v))
                                         for v in r) + " |")
    return "\n".join(lineas)


def escribir_card(out: pd.DataFrame, conv: pd.DataFrame, sin: pd.DataFrame, info: list[dict],
                  fallas: list[str], validos: set[str] = frozenset()) -> None:
    faltantes = pd.DataFrame({
        "columna": COLUMNAS[3:],
        "pct_faltante": [round(100 * out[c].isna().mean(), 1) if len(out) else None for c in COLUMNAS[3:]],
    })
    tot = (out.assign(estado=out["fips"].str[:2]).groupby(["anio", "estado", "cultivo"], as_index=False)
           [["sup_sembrada_fsa_ac", "sup_prevenida_ac"]].sum()) if len(out) else pd.DataFrame()
    t2019 = tot[tot["anio"] == 2019].drop(columns="anio") if len(tot) else tot
    partes = [
        "<!-- generado por src/seguro/fsa_process.py: no editar a mano -->",
        "## Siembra prevenida (FSA Crop Acreage Data) — `siembra_prevenida_anual.csv`",
        "",
        "Fuente: USDA Farm Service Agency, Crop Acreage Data, archivo final de cada año (2009–2025), "
        "hoja por condado. Research: `docs/research/siembra_prevenida.md` (T032). Código: "
        "`src/seguro/fsa_download.py` y `src/seguro/fsa_process.py`. **Esquema nuevo: espera el OK de "
        "`coordinacion/para_decidir.md` #17.**",
        "",
        "### Columnas",
        "",
        "| Columna | Descripción | Unidad | Fuente |",
        "|---|---|---|---|",
        "| `fips`, `anio`, `cultivo` | condado (FIPS del Census), año de cosecha (crop year del archivo), "
        "cultivo (`maiz`, `soja`, `trigo_invierno`, `avena`) | | |",
        "| `sup_sembrada_fsa_ac` | superficie sembrada declarada a FSA, todos los usos, riego + secano | acres | "
        "FSA `Planted Acres` |",
        "| `sup_prevenida_ac` | superficie con siembra prevenida | acres | FSA `Prevented Acres` |",
        "| `sup_fallida_ac` | superficie sembrada y perdida | acres | FSA `Failed Acres` |",
        "| `sup_prevenida_riego_ac`, `sup_prevenida_secano_ac` | prevenida con `Irrigation Practice` I / N "
        "(2011: columnas Irrigated / Nonirrigated; vacío en 2009–2010) | acres | FSA |",
        "| `pct_prevenida` | 100 × prevenida / (sembrada + prevenida); vacío si el denominador es 0 | % | "
        "cálculo |",
        "",
        "### Archivos leídos",
        "",
        tabla_md(pd.DataFrame(info)) if info else "(ninguno)",
        "",
    ]
    if fallas:
        partes += ["Años sin archivo o que no se pudieron leer: " + "; ".join(fallas), ""]
    partes += [
        "### % de faltantes por columna",
        "",
        tabla_md(faltantes),
        "",
        "### Códigos de condado de FSA convertidos a FIPS",
        "",
        "Con `data/reference/fsa_condados_admin.csv` (condados partidos en dos oficinas de FSA; la "
        "correspondencia es una inferencia por el nombre, confianza media). Acres que se sumaron:",
        "",
        tabla_md(conv.groupby(["codigo", "fips", "cultivo"], as_index=False)[["sembrada", "prevenida"]].sum()
                 .assign(anios=conv.groupby(["codigo", "fips", "cultivo"])["anio"].nunique().values))
        if len(conv) else "(ninguno)",
        "",
        "### Condados sin ninguna fila",
        "",
        ("Condados de condados.csv sin maíz, soja, trigo de invierno ni avena en ningún año de FSA: "
         + (", ".join(sorted(set(validos) - set(out["fips"]))) or "ninguno") + "."),
        "",
        "### Códigos sin FIPS (quedan afuera del CSV)",
        "",
        tabla_md(sin) if len(sin) else "Ninguno: todos los códigos de los estados pedidos se convirtieron.",
        "",
        "### Totales de 2019 por estado (control contra el research)",
        "",
        tabla_md(t2019) if len(t2019) else "(2019 no se procesó)",
        "",
        "### Supuestos",
        "",
        "- Maíz sin pochoclo, dulce ni ornamental; soja sin edamame; trigo solo de invierno (tipo con "
        "`WINTER`). El research sumó todos los tipos, así que sus totales de maíz son algo mayores.",
        "- Se suman todos los usos (grano, silo, semilla, forraje...) salvo `Grazing` en trigo y avena, "
        "que FSA cuenta dos veces desde 2019 cuando el mismo acre se pastorea y se cosecha.",
        "- Riego y secano sumados en las columnas de superficie; la prevenida además por práctica.",
        "- 0 es un 0 real: el condado declaró el cultivo y no tuvo siembra prevenida. Un condado sin "
        "filas del cultivo no aparece.",
        "- Se toma el archivo final de cada año; FSA no dice si los revisa después de publicarlos.",
        "",
        "### Problemas conocidos",
        "",
        "- La siembra prevenida depende también de reglas del seguro (fecha final de siembra, regla 1 de 4) "
        "y de los precios, no solo del clima. En KS una parte es por sequía (para separarla: RMA, etapas "
        "P2/PF/PT y causa).",
        "- El encabezado cambia entre años: 2010 llama `State` al código de estado, 2011 viene en formato "
        "ancho (`Planted Total`, `Prevented Irrigated`...), 2012 dice `Failded Acres`. El lector busca las "
        "columnas por nombre y falla con un mensaje claro si falta alguna.",
        "- En 2012 hay un uso `Grain/Graze` (un solo acre con los dos usos): se cuenta una vez.",
        "",
    ]
    CARD.write_text("\n".join(partes), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anios", type=int, nargs="*", default=None)
    args = ap.parse_args()
    estados = estados_config()
    estados_fips = {e["fips"] for e in estados.values()}
    validos = set(pd.read_csv(CONDADOS, dtype={"fips": str})["fips"].str.zfill(5))
    validos = {f for f in validos if f[:2] in estados_fips}
    admin = tabla_admin()
    zips = sorted(RAW.glob("fsa_acres_*_final.zip"))
    if args.anios:
        zips = [z for z in zips if int(re.search(r"(\d{4})", z.name).group(1)) in args.anios]
    partes, convs, sins, info, fallas = [], [], [], [], []
    for z in zips:
        anio = int(re.search(r"(\d{4})", z.name).group(1))
        try:
            df = leer_zip(z, estados_fips)
        except Exception as e:  # noqa: BLE001
            print(f"{z.name}: {e}")
            fallas.append(f"{anio} ({e})")
            continue
        out, conv, sin = agregar(df, anio, admin, validos)
        partes.append(out)
        convs.append(conv)
        sins.append(sin)
        info.append({"anio": anio, "xlsx": df.attrs.get("xlsx", ""), "filas_estados": len(df),
                     "con_riego": "sí" if df.attrs.get("con_riego") else "no", "filas_csv": len(out)})
        print(f"{anio}: {len(df)} filas de FSA -> {len(out)} filas")
    OUT.mkdir(parents=True, exist_ok=True)
    out = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(columns=COLUMNAS)
    out = redondear(out).sort_values(["fips", "anio", "cultivo"]).reset_index(drop=True)
    out.to_csv(SALIDA, index=False, encoding="utf-8")
    conv = pd.concat(convs, ignore_index=True) if convs else pd.DataFrame()
    sin = pd.concat(sins, ignore_index=True) if sins else pd.DataFrame()
    escribir_card(out, conv, sin, info, fallas, validos)
    errores = validar_csv(SALIDA)
    print(f"{SALIDA.relative_to(REPO)}: {len(out)} filas; validar_csv: {errores or 'ok'}")
    if errores:
        sys.exit(1)


if __name__ == "__main__":
    main()
