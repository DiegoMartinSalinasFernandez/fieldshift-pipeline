"""Control de calidad de los CSV publicados de OH, NE y MN (tarea T073). Solo lee; no escribe en data/.

Entrada: la carpeta con los zips de `datos-oh-ne-mn` descomprimidos, uno por subcarpeta
(`<carpeta>/datos-oh-ne-mn_<paquete>/data/processed/<paquete>/*.csv`). Opcional: la base completa de Quick
Stats (`qs.crops_<fecha>.txt.gz`) para comparar la superficie sembrada de condado con la de estado.

Uso:
  .venv/bin/python -X utf8 docs/qa/oh_ne_mn_qa.py data/entregas/oh-ne-mn-ext [qs.crops_<fecha>.txt.gz]

Salida en Markdown por stdout, con secciones: faltantes por estado contra IA/IL/IN, eventos, rangos,
outliers por vecinos y totales de NASS.
"""
from __future__ import annotations

import csv
import gzip
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
EST = {"39": "OH", "31": "NE", "27": "MN"}
CLAVES = {"fips", "fips_estado", "anio", "anio_censo", "fecha", "mes", "cultivo", "ventana"}


def leer(base: Path, paquete: str, archivo: str) -> pd.DataFrame:
    p = base / f"datos-oh-ne-mn_{paquete}" / "data" / "processed" / paquete / archivo
    df = pd.read_csv(p, dtype={"fips": str, "fips_estado": str})
    if "fips" in df:
        df["estado"] = df["fips"].str[:2].map(EST)
    elif "fips_estado" in df:
        df["estado"] = df["fips_estado"].map(EST)
    return df


def faltantes_card(card: Path) -> dict[tuple[str, str], float]:
    """(archivo, columna) -> faltantes_pct del data card (el de main es el de IA/IL/IN)."""
    r = {}
    for linea in card.read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in linea.strip().strip("|").split("|")]
        if len(c) >= 9 and c[0].endswith(".csv"):
            try:
                r[(c[0], c[1])] = float(c[8].replace(",", ".").rstrip("%"))
            except ValueError:
                pass
    return r


def seccion_faltantes(base: Path) -> None:
    print("## Faltantes por columna y estado contra IA/IL/IN\n")
    print("Solo las columnas donde algún estado nuevo supera en más de 15 puntos al data card de IA/IL/IN "
          "(`docs/datasets/<paquete>.md` de `main`).\n")
    print("| paquete | archivo | columna | IA/IL/IN % | OH % | NE % | MN % |")
    print("|---|---|---|---|---|---|---|")
    for d in sorted(base.glob("datos-oh-ne-mn_*")):
        paq = d.name.split("_", 1)[1]
        card = REPO / "docs" / "datasets" / f"{paq}.md"
        ref = faltantes_card(card) if card.exists() else {}
        for p in sorted((d / "data" / "processed" / paq).glob("*.csv")):
            df = leer(base, paq, p.name)
            for col in df.columns:
                if col in CLAVES or col == "estado" or col.startswith("flag_"):
                    continue
                por = df.groupby("estado")[col].apply(lambda s: s.isna().mean() * 100)
                r = ref.get((p.name, col))
                if r is None:
                    continue
                if (por - r).max() > 15:
                    print(f"| {paq} | {p.name} | {col} | {r:.1f} | {por.get('OH', np.nan):.1f} | "
                          f"{por.get('NE', np.nan):.1f} | {por.get('MN', np.nan):.1f} |")
    print()


def media_estado(df, col, filtro=None):
    d = df if filtro is None else df[filtro]
    return d.groupby(["estado", "anio"])[col].mean().unstack("estado")


def seccion_eventos(base: Path) -> None:
    print("## Eventos extremos (medias de condado por estado)\n")
    cm = leer(base, "clima", "clima_mensual.csv")
    cm["m"] = cm["mes"].str[5:7].astype(int)
    ca = leer(base, "clima", "clima_anual.csv")
    vm = leer(base, "vegetacion", "vegetacion_mensual.csv")
    vm["m"] = vm["mes"].str[5:7].astype(int)
    am = leer(base, "agua", "agua_mensual.csv")
    am["m"] = am["mes"].str[5:7].astype(int)
    nm = leer(base, "nldas", "nldas_mensual.csv")
    nm["m"] = nm["mes"].str[5:7].astype(int)
    pa = leer(base, "cultivos", "produccion_anual.csv")

    def tabla(nombre, serie, anios):
        s = serie.reindex(anios)
        print(f"**{nombre}**\n")
        print("| anio | " + " | ".join(s.columns) + " |")
        print("|---|" + "---|" * len(s.columns))
        for a, f in s.iterrows():
            print(f"| {a} | " + " | ".join("" if pd.isna(v) else f"{v:.2f}" for v in f) + " |")
        print()

    anios = [2002, 2004, 2011, 2012, 2013, 2019, 2021, 2022]
    tabla("`spi3` de agosto (jun–ago)", media_estado(cm, "spi3", cm.m == 8), anios)
    tabla("`prec_jul_mm`", media_estado(ca, "prec_jul_mm"), anios)
    tabla("`ndvi_anom_z` de julio–agosto", media_estado(vm, "ndvi_anom_z", vm.m.isin([7, 8])), anios)
    tabla("`sm_0_100cm_anom_z` (NLDAS) de julio–agosto", media_estado(nm, "sm_0_100cm_anom_z",
                                                                        nm.m.isin([7, 8])), anios)
    tabla("`sm_rootzone_anom_z` (SMAP, desde 2015) de julio–agosto",
          media_estado(am, "sm_rootzone_anom_z", am.m.isin([7, 8])), [2015, 2017, 2019, 2020, 2021, 2022, 2023])
    tabla("`prec_power_mm` de mayo+junio (suma, media de condados)",
          cm[cm.m.isin([5, 6])].groupby(["estado", "anio", "fips"])["prec_power_mm"].sum()
          .groupby(["estado", "anio"]).mean().unstack("estado"), [2011, 2013, 2015, 2019, 2021, 2023])
    tabla("`prec_power_mm` de marzo (NE: inundación 2019)", media_estado(cm, "prec_power_mm", cm.m == 3),
          [2017, 2018, 2019, 2020])
    tabla("`doy_primera_helada` (MN 2004: agosto en el norte)", media_estado(ca, "doy_primera_helada"),
          [2003, 2004, 2005, 2021])
    tabla("`tmin_c` de julio (2011)", media_estado(cm, "tmin_c", cm.m == 7), [2010, 2011, 2012])

    # rendimiento de estado implícito: suma de producción / suma de cosechada (condados con ambos)
    for cult in ["maiz", "soja"]:
        d = pa[(pa.cultivo == cult) & pa.produccion_bu.notna() & pa.sup_cosechada_ac.notna()]
        g = d.groupby(["estado", "anio"])[["produccion_bu", "sup_cosechada_ac"]].sum()
        rend = (g.produccion_bu / g.sup_cosechada_ac).unstack("estado")
        prev = rend.shift(1).rolling(5).mean()
        tabla(f"Rendimiento implícito de {cult} (bu/ac, suma de condados)", rend,
              [2001, 2002, 2011, 2012, 2019, 2021, 2022])
        tabla(f"Rendimiento de {cult}: diferencia % contra la media de los 5 años previos",
              (rend / prev - 1) * 100, [2002, 2012, 2019, 2021, 2022])
    # siembra prevenida 2019 en OH: superficie sembrada de maíz (suma de condados)
    tabla("Superficie sembrada de maíz, suma de condados (miles de ac)",
          pa[pa.cultivo == "maiz"].groupby(["estado", "anio"])["sup_sembrada_ac"].sum(min_count=1)
          .unstack("estado") / 1000, [2017, 2018, 2019, 2020, 2021])


def seccion_rangos(base: Path) -> None:
    print("## Rangos\n")
    pa = leer(base, "cultivos", "produccion_anual.csv")
    print("| cultivo | estado | rend mín | rend máx | n |")
    print("|---|---|---|---|---|")
    for (c, e), d in pa.dropna(subset=["rend_bu_ac"]).groupby(["cultivo", "estado"]):
        print(f"| {c} | {e} | {d.rend_bu_ac.min():.1f} | {d.rend_bu_ac.max():.1f} | {len(d)} |")
    print()
    cd = pd.read_csv(base / "datos-oh-ne-mn_clima/data/processed/clima/clima_diario.csv",
                     usecols=["fips", "fecha", "tmin_c", "tmax_c", "prec_power_mm", "prec_imerg_mm"],
                     dtype={"fips": str})
    for col in ["tmin_c", "tmax_c", "prec_power_mm", "prec_imerg_mm"]:
        i_min, i_max = cd[col].idxmin(), cd[col].idxmax()
        print(f"- `{col}` diario: mín {cd.at[i_min, col]} ({cd.at[i_min, 'fips']}, {cd.at[i_min, 'fecha']}), "
              f"máx {cd.at[i_max, col]} ({cd.at[i_max, 'fips']}, {cd.at[i_max, 'fecha']})")
    cm = leer(base, "clima", "clima_mensual.csv")
    for col in ["prec_imerg_mm", "prec_power_mm", "tmax_c", "tmin_c", "gdd_10_30"]:
        print(f"- `{col}` mensual: {cm[col].min()} a {cm[col].max()}")
    tot = cm.groupby(["estado", "fips", "anio"])[["prec_imerg_mm", "prec_power_mm"]].sum(min_count=1)
    r = (tot.prec_imerg_mm / tot.prec_power_mm).groupby("estado").median()
    print("- Cociente lluvia anual IMERG / POWER (mediana): " + ", ".join(f"{k} {v:.2f}" for k, v in r.items()))
    print()


def vecinos(cond: pd.DataFrame, k: int = 6) -> dict[str, list[str]]:
    lat = np.radians(cond.lat_centroide.values)
    lon = np.radians(cond.lon_centroide.values)
    x = np.c_[np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)]
    d = ((x[:, None, :] - x[None, :, :]) ** 2).sum(-1)
    f = cond.fips.values
    return {f[i]: list(f[np.argsort(d[i])[1:k + 1]]) for i in range(len(f))}


def outliers(df: pd.DataFrame, col: str, vec: dict, umbral: float) -> pd.DataFrame:
    """Diferencia robusta de cada condado-año contra la mediana de sus 6 vecinos más cercanos."""
    piv = df.pivot_table(index="anio", columns="fips", values=col)
    filas = []
    for f, vs in vec.items():
        if f not in piv:
            continue
        vs = [v for v in vs if v in piv]
        if len(vs) < 3:
            continue
        med = piv[vs].median(axis=1)
        mad = (piv[vs].sub(med, axis=0)).abs().median(axis=1) * 1.4826
        esc = np.maximum(mad, 0.1 * med.abs())
        z = (piv[f] - med) / esc
        for a in z.index[z.abs() > umbral]:
            filas.append((f, a, piv.at[a, f], med[a], z[a]))
    return pd.DataFrame(filas, columns=["fips", "anio", "valor", "mediana_vecinos", "z"])


def seccion_outliers(base: Path) -> None:
    print("## Outliers por condado contra sus 6 vecinos más cercanos\n")
    cond = pd.read_csv(base / "datos-oh-ne-mn_clima/data/reference/condados.csv", dtype={"fips": str})
    vec = vecinos(cond)
    nombre = dict(zip(cond.fips, cond.condado))
    ca = leer(base, "clima", "clima_anual.csv")
    pa = leer(base, "cultivos", "produccion_anual.csv")
    casos = [("clima_anual", "prec_temporada_mm", ca, 4), ("clima_anual", "gdd_temporada", ca, 4)]
    for c in ["maiz", "soja"]:
        casos.append((f"produccion_anual ({c})", "rend_bu_ac", pa[pa.cultivo == c], 5))
    for arch, col, df, u in casos:
        o = outliers(df, col, vec, u).sort_values("z", key=abs, ascending=False)
        print(f"**{arch} `{col}`** (|z| > {u}): {len(o)} condado-años\n")
        if len(o):
            print("| fips | condado | anio | valor | mediana vecinos | z |")
            print("|---|---|---|---|---|---|")
            for r in o.head(12).itertuples():
                print(f"| {r.fips} | {nombre.get(r.fips, '')} | {r.anio} | {r.valor:.1f} | "
                      f"{r.mediana_vecinos:.1f} | {r.z:.1f} |")
            print()
    # media de largo plazo de la lluvia: condados con media de 2000-2025 muy distinta de sus vecinos
    m = ca.groupby("fips")["prec_temporada_mm"].mean()
    fil = [(f, m[f], m[[v for v in vs if v in m]].median()) for f, vs in vec.items() if f in m]
    fil = [(f, a, b) for f, a, b in fil if abs(a / b - 1) > 0.25]
    print(f"Condados con `prec_temporada_mm` media 2000–2025 a más de 25 % de la mediana de sus vecinos: "
          f"{len(fil)}" + "".join(f"\n- {f} {nombre.get(f, '')}: {a:.0f} contra {b:.0f}" for f, a, b in fil))
    print()


def seccion_nass(base: Path, qs: Path) -> None:
    print("## Superficie sembrada: suma de condados contra NASS a nivel estado\n")
    pa = leer(base, "cultivos", "produccion_anual.csv")
    est = {}
    comm = {"CORN": "maiz", "SOYBEANS": "soja"}
    with gzip.open(qs, "rt", encoding="utf-8", errors="replace") as fh:
        lec = csv.reader(fh, delimiter="\t")
        cab = next(lec)
        i = {c: k for k, c in enumerate(cab)}
        for f in lec:
            if (f[i["AGG_LEVEL_DESC"]] != "STATE" or f[i["SOURCE_DESC"]] != "SURVEY"
                    or f[i["STATE_ALPHA"]] not in ("OH", "NE", "MN") or f[i["COMMODITY_DESC"]] not in comm
                    or f[i["STATISTICCAT_DESC"]] != "AREA PLANTED" or f[i["UNIT_DESC"]] != "ACRES"
                    or f[i["REFERENCE_PERIOD_DESC"]] != "YEAR" or f[i["CLASS_DESC"]] != "ALL CLASSES"
                    or f[i["PRODN_PRACTICE_DESC"]] != "ALL PRODUCTION PRACTICES"
                    or f[i["UTIL_PRACTICE_DESC"]] != "ALL UTILIZATION PRACTICES"):
                continue
            v = re.sub(r"[,\s]", "", f[i["VALUE"]])
            if v.replace(".", "").isdigit():
                est[(f[i["STATE_ALPHA"]], comm[f[i["COMMODITY_DESC"]]], int(f[i["YEAR"]]))] = float(v)
    suma = pa.groupby(["estado", "cultivo", "anio"])["sup_sembrada_ac"].sum(min_count=1)
    filas = []
    for (e, c, a), v in est.items():
        if 2000 <= a <= 2025 and (e, c, a) in suma.index:
            filas.append((e, c, a, v, suma[(e, c, a)]))
    df = pd.DataFrame(filas, columns=["estado", "cultivo", "anio", "nass_estado", "suma_condados"])
    df["pct"] = df.suma_condados / df.nass_estado * 100
    print("| estado | cultivo | n años | % mín (año) | % mediana | % máx (año) |")
    print("|---|---|---|---|---|---|")
    for (e, c), d in df.groupby(["estado", "cultivo"]):
        lo, hi = d.loc[d.pct.idxmin()], d.loc[d.pct.idxmax()]
        print(f"| {e} | {c} | {len(d)} | {lo.pct:.1f} ({lo.anio}) | {d.pct.median():.1f} | "
              f"{hi.pct:.1f} ({hi.anio}) |")
    print()
    malos = df[(df.pct < 85) | (df.pct > 101)].sort_values(["estado", "cultivo", "anio"])
    print(f"Años con la suma de condados fuera de 85–101 % del total de estado: {len(malos)}\n")
    for r in malos.itertuples():
        print(f"- {r.estado} {r.cultivo} {r.anio}: {r.suma_condados:,.0f} de {r.nass_estado:,.0f} ac "
              f"({r.pct:.1f} %)")
    print()


def main() -> None:
    base = Path(sys.argv[1])
    seccion_faltantes(base)
    seccion_eventos(base)
    seccion_rangos(base)
    seccion_outliers(base)
    if len(sys.argv) > 2:
        seccion_nass(base, Path(sys.argv[2]))


if __name__ == "__main__":
    main()
