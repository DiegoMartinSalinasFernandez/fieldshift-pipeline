"""Comparar OH/NE/MN con IA/IL/IN: mediana y percentiles 10 y 90 por grupo (T076).

Solo describe: no entrena modelos ni calcula tendencias.

Uso:
    python docs/research/comparar_grupos.py <dir_release_oh_ne_mn> [<dir_release_ia_il_in>]

Cada directorio es la carpeta donde se descomprimieron los zips de un release (`<paquete>/data/processed/...`
o directamente `data/processed/...`). Si no se pasa el de IA/IL/IN, esas columnas salen vacías y se usan,
para IA/IL/IN, las tablas que ya están en el repo:
  - docs/research/rangos_estados_nuevos_censo.csv (rendimiento implícito del Censo 2012, 2017, 2022)
  - docs/research/ventanas_por_estado.csv (día del 50 % de floración, Crop Progress, 2008-2025)

Imprime tablas en Markdown por la salida estándar. Las unidades de cálculo son condado-año (o estado-año en
fenología, condado en suelo), sin ponderar por superficie.
"""
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
GRUPOS = {"IA/IL/IN": {"19": "IA", "17": "IL", "18": "IN"},
          "OH/NE/MN": {"39": "OH", "31": "NE", "27": "MN"}}
ESTADO_FIPS = {v: k for g in GRUPOS.values() for k, v in g.items()}


def buscar(dirs, nombre):
    """Concatena el CSV `nombre` de todos los directorios de release donde aparezca."""
    partes = []
    for d in dirs:
        if d is None:
            continue
        for p in sorted(Path(d).rglob(nombre)):
            if "processed" in p.parts:
                partes.append(pd.read_csv(p, dtype={"fips": str, "fips_estado": str}))
    if not partes:
        return None
    return pd.concat(partes, ignore_index=True).drop_duplicates()


def con_estado(df, col="fips"):
    df = df.copy()
    df["fips_estado"] = df[col].str.zfill(5).str[:2] if col == "fips" else df[col].str.zfill(2)
    todos = {k: v for g in GRUPOS.values() for k, v in g.items()}
    df["estado"] = df["fips_estado"].map(todos)
    df["grupo"] = df["fips_estado"].map({k: g for g, m in GRUPOS.items() for k in m})
    return df[df["grupo"].notna()]


def resumen(df, col, por=("grupo",)):
    """n, p10, mediana y p90 de `col` agrupando por `por`; filas vacías se descartan."""
    d = df[df[col].notna()]
    out = d.groupby(list(por))[col].agg(
        n="count", p10=lambda s: s.quantile(0.1), mediana="median", p90=lambda s: s.quantile(0.9))
    return out


def tabla(titulo, df, col, decimales=1, extra_por=None):
    """Imprime una tabla Markdown: una fila por grupo y por estado."""
    print(f"\n### {titulo}\n")
    print("| Grupo / estado | n | p10 | mediana | p90 |")
    print("|---|---|---|---|---|")
    if df is None or col not in df:
        print("| (sin datos) | | | | |")
        return
    por_grupo = resumen(df, col, ("grupo",))
    por_estado = resumen(df, col, ("grupo", "estado"))
    for g, estados in GRUPOS.items():
        if g not in por_grupo.index:
            print(f"| **{g}** | 0 | | | |")
            continue
        r = por_grupo.loc[g]
        print(f"| **{g}** | {int(r.n)} | {r.p10:.{decimales}f} | {r.mediana:.{decimales}f} | {r.p90:.{decimales}f} |")
        for e in estados.values():
            if (g, e) in por_estado.index:
                r = por_estado.loc[(g, e)]
                print(f"| {e} | {int(r.n)} | {r.p10:.{decimales}f} | {r.mediana:.{decimales}f} | "
                      f"{r.p90:.{decimales}f} |")


def a_markdown(df):
    """DataFrame (índice incluido) a tabla Markdown, sin depender de tabulate."""
    df = df.reset_index()
    filas = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    filas += ["| " + " | ".join("" if pd.isna(x) else str(x) for x in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(filas)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    dirs = [sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None]

    print("# Salida de comparar_grupos.py")
    print(f"\nReleases: OH/NE/MN = `{Path(dirs[0]).name}`; IA/IL/IN = "
          f"`{Path(dirs[1]).name if dirs[1] else '(sin release)'}`")

    prod = buscar(dirs, "produccion_anual.csv")
    if prod is not None:
        prod = con_estado(prod)
        for cultivo in ("maiz", "soja"):
            d = prod[prod["cultivo"] == cultivo]
            tabla(f"Rendimiento de {cultivo} (rend_bu_ac, condado-año 2000-2025)", d, "rend_bu_ac")
            tabla(f"Rendimiento de {cultivo} en años de censo (2012, 2017, 2022, encuesta)",
                  d[d["anio"].isin([2012, 2017, 2022])], "rend_bu_ac")
        d = prod[(prod["cultivo"] == "maiz") & (prod["anio"] != 2012)]
        tabla("Rendimiento de maíz sin 2012 (sequía), condado-año", d, "rend_bu_ac")

    clima = buscar(dirs, "clima_anual.csv")
    if clima is not None:
        clima = con_estado(clima)
        clima = clima[clima["anio"].between(2000, 2025)]
        tabla("Lluvia de temporada abril-septiembre (prec_temporada_mm, POWER)", clima, "prec_temporada_mm", 0)
        tabla("GDD 10/30 de temporada (gdd_temporada, °C·día)", clima, "gdd_temporada", 0)
        tabla("Déficit de temporada lluvia - ETo (deficit_temporada_mm)", clima, "deficit_temporada_mm", 0)
        tabla("Período libre de heladas (días)", clima, "periodo_libre_heladas_dias", 0)

    censo = buscar(dirs, "practicas_censo.csv")
    if censo is not None:
        censo = con_estado(censo)
        for a in sorted(censo["anio_censo"].unique()):
            tabla(f"Riego: % de la tierra de cultivo regada (pct_riego, Censo {a})",
                  censo[censo["anio_censo"] == a], "pct_riego")
        tabla("Drenaje con caños: % de la tierra de cultivo (pct_drenaje_tile, Censo 2017 y 2022)",
              censo, "pct_drenaje_tile")

    feno = buscar(dirs, "fenologia_estado.csv")
    if feno is not None:
        feno = con_estado(feno, "fips_estado")
        for cultivo in ("maiz", "soja"):
            d = feno[feno["cultivo"] == cultivo]
            for c in ("doy_50_sembrado", "doy_50_floracion", "doy_50_cosechado"):
                tabla(f"{c} de {cultivo} (estado-año 2000-2025, día del año)", d, c)

    vent = RAIZ / "docs/research/ventanas_por_estado.csv"
    if vent.exists():
        v = pd.read_csv(vent)
        v = v[v["estado"].isin(ESTADO_FIPS)].copy()
        v["fips_estado"] = v["estado"].map(ESTADO_FIPS)
        v = con_estado(v, "fips_estado")
        for etapa in ("maiz_silking", "soja_blooming"):
            tabla(f"Día del 50 % de {etapa} (ventanas_por_estado.csv, estado-año 2008-2025)",
                  v[v["etapa"] == etapa], "doy50")

    suelo = buscar(dirs, "suelo_terreno_estatico.csv")
    if suelo is not None:
        suelo = con_estado(suelo)
        for c, dec in (("aws0_150_mm", 0), ("nccpi_maiz", 3), ("nccpi_soja", 3), ("soc0_30_gm2", 0),
                       ("materia_organica_pct", 1), ("arcilla_pct", 1), ("arena_pct", 1), ("ph_agua", 2),
                       ("pendiente_media_pct", 2), ("twi_medio", 2), ("elevacion_media_m", 0)):
            tabla(f"Suelo y terreno: {c} (condado)", suelo, c, dec)
        print("\n### Clase de drenaje dominante (condados por clase)\n")
        print(a_markdown(suelo.groupby(["grupo", "estado"])["clase_drenaje"].value_counts()
                         .unstack(fill_value=0)))

    rot = buscar(dirs, "rotacion_anual.csv")
    if rot is not None:
        rot = con_estado(rot)
        tabla("Maíz tras maíz: % del maíz con maíz el año anterior (pct_maiz_tras_maiz, 2009-2025)",
              rot, "pct_maiz_tras_maiz")
        tabla("Soja tras soja (pct_soja_tras_soja, 2009-2025)", rot, "pct_soja_tras_soja")
        tabla("% del área agrícola con maíz (pct_maiz, 2008-2025)", rot, "pct_maiz")
        tabla("% del área agrícola con trigo (pct_trigo, 2008-2025)", rot, "pct_trigo")

    cen = RAIZ / "docs/research/rangos_estados_nuevos_censo.csv"
    if cen.exists():
        c = pd.read_csv(cen)
        c = c[c["estado"].isin(ESTADO_FIPS) & c["cultivo"].isin(["maiz", "soja"])]
        print("\n### Rendimiento implícito del Censo por estado (rangos_estados_nuevos_censo.csv, bu/ac)\n")
        print("Mediana de condados (mín.-máx.), todas las prácticas, condados con >= 500 ac cosechados.\n")
        c["txt"] = c.apply(lambda r: f"{r.mediana_bu_ac:.1f} ({r.min_bu_ac:.1f}-{r.max_bu_ac:.1f})", axis=1)
        print(a_markdown(c.pivot_table(index=["cultivo", "estado"], columns="anio", values="txt",
                                     aggfunc="first")))


if __name__ == "__main__":
    main()
