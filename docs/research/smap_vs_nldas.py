"""T092: humedad del suelo de SMAP (Crop-CASMA) contra NLDAS-2 Noah en OH, NE y MN, 2015-2025.

Solo describe: correlación, sesgo y anomalías por condado. No entrena modelos.

Entrada: `agua_mensual.csv` y `nldas_mensual.csv` del release `datos-oh-ne-mn`, descomprimidos fuera de git:

    python -X utf8 docs/research/smap_vs_nldas.py data/interim/t092

(busca `**/agua_mensual.csv` y `**/nldas_mensual.csv` debajo de esa carpeta). Escribe tablas en la misma
carpeta (`smap_vs_nldas_condados.csv`) e imprime los resúmenes que van en `smap_vs_nldas.md`.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ESTADOS = {"27": "MN", "31": "NE", "39": "OH"}
# Condados con celdas > 0,6 m3/m3 excluidas del promedio de SMAP (turba / suelos orgánicos),
# de docs/research/smap_costas.md.
TURBA = {
    "27071": "Koochiching", "27137": "St. Louis", "27007": "Beltrami", "27001": "Aitkin",
    "27061": "Itasca", "27077": "Lake of the Woods", "27079": "Le Sueur", "27053": "Hennepin",
    "27161": "Waseca", "39149": "Shelby", "39011": "Auglaize", "39037": "Darke", "39003": "Allen",
}
MIN_MESES = 24


def zscore(df, col, base=None):
    """z por condado y mes calendario; base = (anio_desde, anio_hasta) o None para todo."""
    ref = df if base is None else df[df["anio"].between(*base)]
    st = ref.groupby(["fips", "m"])[col].agg(["mean", "std"]).reset_index()
    out = df.merge(st, on=["fips", "m"], how="left")
    return ((out[col] - out["mean"]) / out["std"]).values


def corr(a, b):
    ok = a.notna() & b.notna()
    if ok.sum() < MIN_MESES:
        return np.nan
    return float(np.corrcoef(a[ok], b[ok])[0, 1])


def corr_n(a, b, minimo=8):
    ok = a.notna() & b.notna()
    return float(np.corrcoef(a[ok], b[ok])[0, 1]) if ok.sum() >= minimo else np.nan


def main(carpeta):
    carpeta = Path(carpeta)
    fa = next(carpeta.rglob("agua_mensual.csv"))
    fn = next(carpeta.rglob("nldas_mensual.csv"))
    a = pd.read_csv(fa, dtype={"fips": str})
    n = pd.read_csv(fn, dtype={"fips": str})
    n["m"] = n["mes"].str[5:7].astype(int)
    a["m"] = a["mes"].str[5:7].astype(int)

    # Anomalía de NLDAS recalculada con la misma base que SMAP (2015-2025), para separar el efecto de la base.
    n["sm_0_100cm_anom_z_1525"] = zscore(n, "sm_0_100cm_m3m3", base=(2015, 2025))
    # Anomalía en m3/m3 (sin dividir por el desvío), base común 2015-2025.
    for df, col in ((a, "sm_rootzone_m3m3"), (n, "sm_0_100cm_m3m3")):
        ref = df[df["anio"].between(2015, 2025)].groupby(["fips", "m"])[col].mean().rename("clim")
        df[col + "_anom"] = df[col] - df.join(ref, on=["fips", "m"])["clim"]

    d = a.merge(n, on=["fips", "anio", "mes", "m"], how="inner")
    d = d[d["sm_rootzone_m3m3"].notna() & d["sm_0_100cm_m3m3"].notna()].copy()
    d["estado"] = d["fips"].str[:2].map(ESTADOS)
    d["dif"] = d["sm_rootzone_m3m3"] - d["sm_0_100cm_m3m3"]
    print(f"Pares condado-mes: {len(d)}  condados: {d.fips.nunique()}  "
          f"meses: {d.mes.min()} a {d.mes.max()}")
    print("Pares por estado:", d.groupby("estado").size().to_dict())
    print(f"Meses de SMAP vacíos: {a['sm_rootzone_m3m3'].isna().sum()} de {len(a)}:",
          a.loc[a['sm_rootzone_m3m3'].isna(), 'mes'].value_counts().to_dict())

    filas = []
    for f, g in d.groupby("fips"):
        filas.append({
            "fips": f, "estado": g["estado"].iat[0], "n_meses": len(g),
            "turba": TURBA.get(f, ""),
            "smap_media": g["sm_rootzone_m3m3"].mean(), "nldas_media": g["sm_0_100cm_m3m3"].mean(),
            "sesgo": g["dif"].mean(), "rmse": float(np.sqrt((g["dif"] ** 2).mean())),
            "sd_smap": g["sm_rootzone_m3m3"].std(), "sd_nldas": g["sm_0_100cm_m3m3"].std(),
            "r_nivel": corr(g["sm_rootzone_m3m3"], g["sm_0_100cm_m3m3"]),
            "r_anom_m3m3": corr(g["sm_rootzone_m3m3_anom"], g["sm_0_100cm_m3m3_anom"]),
            "r_anom_z": corr(g["sm_rootzone_anom_z"], g["sm_0_100cm_anom_z"]),
            "r_anom_z_1525": corr(g["sm_rootzone_anom_z"], g["sm_0_100cm_anom_z_1525"]),
            "z_nldas_media_1991": g["sm_0_100cm_anom_z"].mean(),
        })
    c = pd.DataFrame(filas)
    c.to_csv(carpeta / "smap_vs_nldas_condados.csv", index=False, float_format="%.4f")

    cols = ["smap_media", "nldas_media", "sesgo", "rmse", "sd_smap", "sd_nldas",
            "r_nivel", "r_anom_m3m3", "r_anom_z", "r_anom_z_1525", "z_nldas_media_1991"]
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    print("\n== Mediana por estado (sobre condados) ==")
    print(c.groupby("estado")[cols].median().round(3))
    print("\n== Todos ==")
    print(c[cols].median().round(3))
    print("\n== Percentiles 10 y 90 sobre condados ==")
    print(c[cols].quantile([0.1, 0.9]).round(3))
    print("\nCondados con r_nivel < 0.5:", (c.r_nivel < 0.5).sum(), " r_anom_z < 0.5:", (c.r_anom_z < 0.5).sum())

    print("\n== Correlación espacial de las medias de condado (SMAP vs NLDAS) ==")
    for e, g in c.groupby("estado"):
        print(e, round(np.corrcoef(g.smap_media, g.nldas_media)[0, 1], 3))
    print("todos", round(np.corrcoef(c.smap_media, c.nldas_media)[0, 1], 3))

    show = ["fips", "estado", "turba", "smap_media", "nldas_media", "sesgo", "r_nivel", "r_anom_z"]
    print("\n== 12 condados con menor r_anom_z ==")
    print(c.nsmallest(12, "r_anom_z")[show].round(3).to_string(index=False))
    print("\n== 8 condados con mayor sesgo positivo / negativo ==")
    print(c.nlargest(8, "sesgo")[show].round(3).to_string(index=False))
    print(c.nsmallest(8, "sesgo")[show].round(3).to_string(index=False))
    print("\n== Condados con turba (smap_costas.md) ==")
    t = c[c.turba != ""]
    print(t[show].round(3).to_string(index=False))
    print("Mediana turba vs resto:")
    print(c.assign(grupo=np.where(c.turba != "", "turba", "resto"))
          .groupby(["grupo"])[["sesgo", "r_nivel", "r_anom_m3m3", "r_anom_z"]].median().round(3))

    print("\n== Por mes calendario (mediana sobre condados de r de anomalía z y sesgo) ==")
    filas = []
    for (f, m), g in d.groupby(["fips", "m"]):
        ok = g["sm_rootzone_anom_z"].notna() & g["sm_0_100cm_anom_z"].notna()
        r = np.corrcoef(g.loc[ok, "sm_rootzone_anom_z"], g.loc[ok, "sm_0_100cm_anom_z"])[0, 1] if ok.sum() >= 8 else np.nan
        filas.append({"fips": f, "estado": g["estado"].iat[0], "m": m, "r": r, "sesgo": g["dif"].mean()})
        # 8+ años por mes calendario
    pm = pd.DataFrame(filas)
    print(pm.pivot_table(index="m", columns="estado", values="r", aggfunc="median").round(2))
    print(pm.pivot_table(index="m", columns="estado", values="sesgo", aggfunc="median").round(3))

    print("\n== Anomalía de NLDAS: base 1991-2020 vs 2015-2025 ==")
    nn = n[n.anio.between(2015, 2025)]
    print("r(z_1991, z_1525) mediana por condado:",
          round(nn.groupby("fips").apply(lambda g: corr(g.sm_0_100cm_anom_z, g.sm_0_100cm_anom_z_1525)).median(), 3))
    print("media de z_1991 en 2015-2025 por estado:",
          nn.assign(e=nn.fips.str[:2].map(ESTADOS)).groupby("e").sm_0_100cm_anom_z.mean().round(3).to_dict())

    print("\n== Serie anual de la media regional (NLDAS 2000-2025 y SMAP 2015-2025, m3/m3) ==")
    na = n.assign(e=n.fips.str[:2].map(ESTADOS)).groupby(["e", "anio"]).sm_0_100cm_m3m3.mean().unstack(0)
    sa = a.assign(e=a.fips.str[:2].map(ESTADOS)).groupby(["e", "anio"]).sm_rootzone_m3m3.mean().unstack(0)
    print(na.join(sa, lsuffix="_nldas", rsuffix="_smap").round(3).to_string())

    print("\n== Correlación de los promedios de abril-septiembre por condado-año ==")
    ga = d[d.m.between(4, 9)].groupby(["fips", "anio"])[["sm_rootzone_anom_z", "sm_0_100cm_anom_z"]].mean()
    ga = ga.reset_index()
    rr = ga.groupby("fips").apply(lambda g: corr_n(g["sm_rootzone_anom_z"], g["sm_0_100cm_anom_z"]))
    print("mediana r temporada (anual, n<=11 años):", round(rr.median(), 3),
          " p10:", round(rr.quantile(0.1), 3), " p90:", round(rr.quantile(0.9), 3))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/interim/t092")
