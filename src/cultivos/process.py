"""Procesa cultivos desde la base completa de NASS Quick Stats (data/raw/cultivos/nass/).

Salidas (data/processed/cultivos/):
- produccion_anual.csv  (fips, anio, cultivo, ...) — encuesta por condado.
- fenologia_estado.csv  (fips_estado, anio, cultivo, doy_50_*, flag_hueco_50) — Crop Progress por estado
  (maíz, soja, avena y trigo de invierno; ver src/cultivos/fenologia.py).
- practicas_censo.csv   (fips, anio_censo, pct_*) — Censo Agropecuario 2012/2017/2022.

Paso intermedio: cada archivo de raw se filtra una vez a los estados de config.yaml y se guarda
en data/interim/cultivos/<archivo>.filtrado.tsv (se reusa si ya existe; es determinístico).
"""
from __future__ import annotations

import csv
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.common.config import cargar_config, estados_config  # noqa: E402
from src.common.conversiones import acres_a_ha, bu_ac_a_kgha  # noqa: E402
from src.cultivos.fenologia import fenologia_estado  # noqa: E402

RAW = REPO / "data" / "raw" / "cultivos" / "nass"
INTERIM = REPO / "data" / "interim" / "cultivos"
OUT = REPO / "data" / "processed" / "cultivos"

COLS = ["SOURCE_DESC", "COMMODITY_DESC", "CLASS_DESC", "PRODN_PRACTICE_DESC",
        "UTIL_PRACTICE_DESC", "STATISTICCAT_DESC", "UNIT_DESC", "SHORT_DESC", "DOMAIN_DESC",
        "AGG_LEVEL_DESC", "STATE_FIPS_CODE", "STATE_ALPHA", "COUNTY_CODE", "YEAR",
        "FREQ_DESC", "REFERENCE_PERIOD_DESC", "WEEK_ENDING", "VALUE"]

# cultivo (código de config.yaml) -> (COMMODITY_DESC, CLASS_DESC, UTIL de cosecha/producción)
NASS_CULTIVOS = {
    "maiz": ("CORN", "ALL CLASSES", "GRAIN"),
    "soja": ("SOYBEANS", "ALL CLASSES", "ALL UTILIZATION PRACTICES"),
    "trigo_invierno": ("WHEAT", "WINTER", "ALL UTILIZATION PRACTICES"),
    "avena": ("OATS", "ALL CLASSES", "ALL UTILIZATION PRACTICES"),
    "alfalfa": ("HAY", "ALFALFA", "ALL UTILIZATION PRACTICES"),
    "heno": ("HAY", "(EXCL ALFALFA)", "ALL UTILIZATION PRACTICES"),
}
CODIGOS_OCULTOS = {"(D)", "(Z)", "(NA)", "(X)", "(S)", "(L)", "(H)"}


def filtrar(raw: Path) -> pd.DataFrame:
    """Filas de los estados de config.yaml a nivel condado o estado (cacheado en interim)."""
    cache = INTERIM / (raw.name.replace(".txt.gz", "") + ".filtrado.tsv")
    if cache.exists():
        return pd.read_csv(cache, sep="\t", dtype=str, keep_default_na=False)
    estados = set(estados_config())
    partes = []
    for ch in pd.read_csv(raw, sep="\t", dtype=str, usecols=COLS, keep_default_na=False,
                          quoting=csv.QUOTE_NONE, chunksize=500_000, encoding="utf-8",
                          encoding_errors="replace"):
        ch = ch[ch["STATE_ALPHA"].isin(estados) & ch["AGG_LEVEL_DESC"].isin(["COUNTY", "STATE"])]
        if len(ch):
            partes.append(ch)
    df = pd.concat(partes, ignore_index=True)
    INTERIM.mkdir(parents=True, exist_ok=True)
    tmp = cache.with_suffix(".part")
    df.to_csv(tmp, sep="\t", index=False)
    tmp.replace(cache)
    return df


def valor(s: pd.Series) -> tuple[pd.Series, pd.Series]:
    """VALUE de NASS -> (número o NaN, flag con el código original si estaba oculto)."""
    v = s.str.strip()
    flag = v.where(v.isin(CODIGOS_OCULTOS), "")
    num = pd.to_numeric(v.str.replace(",", "", regex=False), errors="coerce")
    return num, flag


def produccion(crops: pd.DataFrame) -> pd.DataFrame:
    cfg = cargar_config()["periodo"]
    d = crops[(crops["SOURCE_DESC"] == "SURVEY") & (crops["AGG_LEVEL_DESC"] == "COUNTY")
              & (crops["PRODN_PRACTICE_DESC"] == "ALL PRODUCTION PRACTICES")
              & (crops["DOMAIN_DESC"] == "TOTAL") & (crops["FREQ_DESC"] == "ANNUAL")
              & (crops["REFERENCE_PERIOD_DESC"] == "YEAR")
              & (crops["COUNTY_CODE"] != "998") & (crops["COUNTY_CODE"] != "")]
    d = d.assign(anio=pd.to_numeric(d["YEAR"]))
    d = d[(d["anio"] >= cfg["anio_inicio"]) & (d["anio"] <= cfg["anio_fin"])]
    variables = {  # (STATISTICCAT_DESC, UNIT_DESC, usa util de cosecha)
        "sup_sembrada_ac": ("AREA PLANTED", "ACRES", False),
        "sup_cosechada_ac": ("AREA HARVESTED", "ACRES", True),
        "produccion_bu": ("PRODUCTION", "BU", True),
        "rend_bu_ac": ("YIELD", "BU / ACRE", True),
    }
    filas = []
    for cultivo, (com, clase, util_cos) in NASS_CULTIVOS.items():
        dc = d[(d["COMMODITY_DESC"] == com) & (d["CLASS_DESC"] == clase)]
        for var, (stat, unidad, cos) in variables.items():
            util = util_cos if cos else "ALL UTILIZATION PRACTICES"
            dv = dc[(dc["STATISTICCAT_DESC"] == stat) & (dc["UNIT_DESC"] == unidad)
                    & (dc["UTIL_PRACTICE_DESC"] == util)]
            if dv.empty:
                continue
            num, flag = valor(dv["VALUE"])
            filas.append(pd.DataFrame({
                "fips": dv["STATE_FIPS_CODE"].str.zfill(2) + dv["COUNTY_CODE"].str.zfill(3),
                "anio": dv["anio"].astype(int), "cultivo": cultivo, "variable": var,
                "valor": num.values, "flag": flag.values}))
    largo = pd.concat(filas, ignore_index=True)
    largo = largo.drop_duplicates(["fips", "anio", "cultivo", "variable"])
    ancho = largo.pivot(index=["fips", "anio", "cultivo"], columns="variable", values="valor")
    flags = (largo[largo["flag"] != ""].sort_values("variable")
             .groupby(["fips", "anio", "cultivo"])["flag"]
             .agg(lambda x: ";".join(sorted(set(x)))))
    ancho = ancho.reindex(columns=list(variables)).join(flags.rename("flag_nass"))
    ancho = ancho.reset_index()
    ancho["rend_kgha"] = np.nan
    for cultivo in ("maiz", "soja", "trigo_invierno", "avena"):
        m = ancho["cultivo"] == cultivo
        ancho.loc[m, "rend_kgha"] = (ancho.loc[m, "rend_bu_ac"] * bu_ac_a_kgha(cultivo)).round(1)
    ancho["sup_sembrada_ha"] = acres_a_ha(ancho["sup_sembrada_ac"]).round(1)
    ancho["ratio_cosechada"] = (ancho["sup_cosechada_ac"] / ancho["sup_sembrada_ac"]).round(4)
    fips_ok = set(pd.read_csv(REPO / "data" / "reference" / "condados.csv", dtype={"fips": str})["fips"])
    ancho = ancho[ancho["fips"].isin(fips_ok)]
    cols = ["fips", "anio", "cultivo", "sup_sembrada_ac", "sup_cosechada_ac", "produccion_bu",
            "rend_bu_ac", "rend_kgha", "sup_sembrada_ha", "ratio_cosechada", "flag_nass"]
    return ancho[cols].sort_values(["fips", "anio", "cultivo"]).reset_index(drop=True)


def fenologia(crops: pd.DataFrame) -> pd.DataFrame:
    """fenologia_estado.csv: la lógica está en src/cultivos/fenologia.py (T135)."""
    cfg = cargar_config()["periodo"]
    return fenologia_estado(crops, cfg["anio_inicio"], cfg["anio_fin"])


# Censo: columna -> SHORT_DESC del numerador (acres). Denominador: tierra de cultivo total.
CENSO_NUM = {
    "pct_cobertura": ["PRACTICES, LAND USE, CROPLAND, COVER CROP PLANTED, (EXCL CRP) - ACRES"],
    "pct_labranza_cero": ["PRACTICES, LAND USE, CROPLAND, CONSERVATION TILLAGE, NO-TILL - ACRES",
                          "PRACTICES, LAND USE, CROPLAND, NO TILL - ACRES"],
    "pct_drenaje_tile": ["PRACTICES, LAND USE, DRAINED BY TILE - ACRES"],
    "pct_riego": ["AG LAND, IRRIGATED - ACRES"],
}
CENSO_DEN = "AG LAND, CROPLAND - ACRES"


def practicas(censos: list[tuple[int, pd.DataFrame]]) -> pd.DataFrame:
    filas = []
    fips_ok = set(pd.read_csv(REPO / "data" / "reference" / "condados.csv", dtype={"fips": str})["fips"])
    for anio, c in censos:
        c = c[(c["AGG_LEVEL_DESC"] == "COUNTY") & (c["DOMAIN_DESC"] == "TOTAL")
              & (c["COUNTY_CODE"] != "998") & (c["YEAR"] == str(anio))]
        c = c.assign(fips=c["STATE_FIPS_CODE"].str.zfill(2) + c["COUNTY_CODE"].str.zfill(3),
                     num=valor(c["VALUE"])[0])
        den = c[c["SHORT_DESC"] == CENSO_DEN].drop_duplicates("fips").set_index("fips")["num"]
        res = pd.DataFrame(index=sorted(fips_ok))
        for col, descs in CENSO_NUM.items():
            for desc in descs:
                n = c[c["SHORT_DESC"] == desc].drop_duplicates("fips").set_index("fips")["num"]
                if len(n):
                    break
            res[col] = (100 * n / den).reindex(res.index).round(2)
        res = res.where((res >= 0) & (res <= 100))
        res.insert(0, "anio_censo", anio)
        filas.append(res.rename_axis("fips").reset_index())
    return pd.concat(filas, ignore_index=True).sort_values(["fips", "anio_censo"]).reset_index(drop=True)


RAW_CDL = REPO / "data" / "raw" / "cultivos" / "cdl"
CULTIVADO = 2  # valor de "cultivated" en la Cultivated Layer (1 = no cultivado)
MASCARA = REPO / "data" / "reference" / "mascara_agricola.tif"


def mascara_agricola(zip_cdl: Path) -> None:
    """Recorta la Cultivated Layer nacional del CDL a los condados de config.yaml (EPSG:5070).

    Salida: GeoTIFF de 1 bit (1 = cultivado, 0 = no cultivado o fuera de la zona), 30 m.
    """
    import geopandas as gpd
    import rasterio
    from rasterio.features import geometry_mask
    from rasterio.windows import from_bounds

    tifs = [n for n in __import__("zipfile").ZipFile(zip_cdl).namelist() if n.lower().endswith(".tif")]
    ruta = f"/vsizip/{zip_cdl.as_posix()}/{tifs[0]}"
    with rasterio.open(ruta) as src:
        cond = gpd.read_file(REPO / "data" / "reference" / "condados.gpkg").to_crs(src.crs)
        win = from_bounds(*cond.total_bounds, transform=src.transform).round_offsets().round_lengths()
        a = src.read(1, window=win)
        tr = src.window_transform(win)
        fuera = geometry_mask(cond.geometry, out_shape=a.shape, transform=tr)
        m = ((a == CULTIVADO) & ~fuera).astype("uint8")
        perfil = {"driver": "GTiff", "dtype": "uint8", "count": 1, "width": m.shape[1],
                  "height": m.shape[0], "crs": src.crs, "transform": tr, "nodata": None,
                  "compress": "deflate", "zlevel": 9, "nbits": 1,
                  "tiled": True, "blockxsize": 512, "blockysize": 512}
    MASCARA.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(MASCARA, "w", **perfil) as dst:
        dst.write(m, 1)
    print(f"mascara_agricola.tif {m.shape}, {MASCARA.stat().st_size / 1e6:.1f} MB, "
          f"{100 * m.mean():.1f} % cultivado")


CLASES = REPO / "data" / "reference" / "clases_cdl.csv"
# grupo de cada clase del CDL que usa el proyecto (§6.2 del plan); el resto: otro
GRUPOS_CDL = {1: "maiz", 5: "soja", 24: "trigo_invierno", 26: "doble_trigo_soja", 28: "avena",
              36: "alfalfa", 37: "heno", 61: "barbecho", 176: "pastizal"}


def clases_cdl(meta: Path) -> None:
    """Tabla de clases del CDL desde los metadatos oficiales (código, nombre, grupo)."""
    import html
    import re
    t = html.unescape(re.sub(r"<[^>]+>", " ", meta.read_text(encoding="utf-8", errors="replace")))
    t = re.sub(r"\s+", " ", t)
    filas = {}
    for bloque in t.split("Categorization Code Land Cover")[1:]:
        bloque = re.split(r"Raster Attribute Domain Values|Distribution_Information", bloque)[0]
        for cod, nombre in re.findall(r'"(\d+)"\s+([^"]+)', bloque):
            filas.setdefault(int(cod), nombre.strip())
    df = pd.DataFrame(sorted(filas.items()), columns=["codigo", "nombre"])
    df["grupo"] = df["codigo"].map(GRUPOS_CDL).fillna("otro")
    df.to_csv(CLASES, index=False, encoding="utf-8")
    print(f"clases_cdl.csv: {len(df)} clases")


RAW_TESELAS = RAW_CDL / "teselas"
# Clases del CDL que cuentan como área agrícola (cultivos anuales, frutales y barbecho;
# no pasturas 62/176 ni clases no agrícolas 63-65 y 81-195).
AGRICOLA = list(range(1, 62)) + list(range(66, 78)) + list(range(204, 255))
PCT_CLASES = {"pct_maiz": [1], "pct_soja": [5], "pct_trigo": [24, 26], "pct_alfalfa": [36],
              "pct_heno": [37], "pct_doble_trigo_soja": [26], "pct_barbecho": [61]}
TRANSICIONES = {"pct_maiz_tras_soja": (5, 1), "pct_maiz_tras_maiz": (1, 1),
                "pct_soja_tras_maiz": (1, 5), "pct_soja_tras_soja": (5, 5)}


def teselas_por_anio() -> dict[int, dict[str, Path]]:
    """{anio: {clave x_y: ruta}} de las teselas del CDL en raw."""
    out: dict[int, dict[str, Path]] = {}
    for p in sorted(RAW_TESELAS.glob("*_30m_cdls_*.tif")):
        partes = p.stem.split("_")
        out.setdefault(int(partes[0]), {})["_".join(partes[3:])] = p
    return out


def teselas_esperadas(cond, vistas: set[str]) -> set[str]:
    """Claves 'x_y_90000' de la grilla de 90 km del CDL que tocan los condados.

    La grilla sale de una tesela cualquiera ya bajada: x es el borde oeste e y el borde norte
    (−30 m) en EPSG:5070.
    """
    from shapely.geometry import box

    x0, y0, lado = (int(v) for v in sorted(vistas)[0].split("_"))
    zona = cond.union_all() if hasattr(cond, "union_all") else cond.unary_union
    xmin, ymin, xmax, ymax = zona.bounds
    out = set()
    i0, i1 = int(np.floor((xmin - x0) / lado)), int(np.floor((xmax - x0) / lado))
    j0, j1 = int(np.floor((ymin - y0) / lado)), int(np.floor((ymax - y0) / lado)) + 1
    for i in range(i0, i1 + 1):
        for j in range(j0, j1 + 1):
            x, y = x0 + i * lado, y0 + j * lado
            if box(x, y + 30 - lado, x + lado, y + 30).intersects(zona):
                out.add(f"{x}_{y}_{lado}")
    return out


def rotacion_anual() -> pd.DataFrame | None:
    """% del área agrícola por cultivo y transiciones por píxel, por condado y año.

    Solo años con todas las teselas (las de 2008 definen el conjunto esperado).
    """
    import geopandas as gpd
    import rasterio
    from rasterio.features import rasterize

    tes = teselas_por_anio()
    if not tes:
        return None
    cond = gpd.read_file(REPO / "data" / "reference" / "condados.gpkg").to_crs(5070)
    claves = teselas_esperadas(cond, set().union(*[set(t) for t in tes.values()]))
    completos = sorted(a for a, t in tes.items() if claves <= set(t))
    if not completos:
        return None
    fips = cond["fips"].astype(str).str.zfill(5).tolist()
    n = len(fips)
    formas = [(g, i + 1) for i, g in enumerate(cond.geometry)]
    cuenta = {a: np.zeros((n + 1, 256), np.int64) for a in completos}
    # transiciones entre maíz (1) y soja (5): columna = 2 * (previo es soja) + (actual es soja)
    trans = {a: np.zeros((n + 1, 4), np.int64) for a in completos}
    # denominador: píxeles de maíz o soja del año que el año anterior eran agrícolas, para que
    # los bordes de lote que cambian de clase entre productos (30 m hasta 2023, 10 m remuestreado
    # desde 2024) no cuenten como transiciones desde pasto o camino. Columna = actual es soja.
    base = {a: np.zeros((n + 1, 2), np.int64) for a in completos}
    es_agricola = np.zeros(256, dtype=bool)
    es_agricola[AGRICOLA] = True
    for clave in sorted(claves):
        ids = None
        previo = None
        for a in range(completos[0], completos[-1] + 1):
            if a not in completos:
                previo = None
                continue
            with rasterio.open(tes[a][clave]) as src:
                x = src.read(1)
                if ids is None:
                    ids = rasterize(formas, out_shape=x.shape, transform=src.transform,
                                    fill=0, dtype="int32").ravel()
            x = x.ravel().astype(np.int64)
            cuenta[a] += np.bincount(ids * 256 + x, minlength=(n + 1) * 256).reshape(n + 1, 256)
            if previo is not None and previo.shape == x.shape:
                sel = np.isin(x, [1, 5]) & np.isin(previo, [1, 5])
                trans[a] += np.bincount(ids[sel] * 4 + (previo[sel] == 5) * 2 + (x[sel] == 5),
                                        minlength=(n + 1) * 4).reshape(n + 1, 4)
                selb = np.isin(x, [1, 5]) & es_agricola[previo]
                base[a] += np.bincount(ids[selb] * 2 + (x[selb] == 5),
                                       minlength=(n + 1) * 2).reshape(n + 1, 2)
            previo = x
    filas = []
    for a in completos:
        c = cuenta[a][1:]
        agr = c[:, AGRICOLA].sum(axis=1)
        fila = {"fips": fips, "anio": a}
        for col, cls in PCT_CLASES.items():
            fila[col] = np.where(agr > 0, 100 * c[:, cls].sum(axis=1) / np.maximum(agr, 1), np.nan)
        t = trans[a][1:]
        b = base[a][1:]
        for col, (antes, ahora) in TRANSICIONES.items():
            total = b[:, int(ahora == 5)]  # píxeles del cultivo actual que en anio − 1 eran agrícolas
            val = 100 * t[:, 2 * (antes == 5) + (ahora == 5)] / np.maximum(total, 1)
            fila[col] = np.where((total > 0) & ((a - 1) in completos), val, np.nan)
        filas.append(pd.DataFrame(fila))
    df = pd.concat(filas, ignore_index=True)
    num = df.columns[2:]
    df[num] = df[num].round(3)
    return df.sort_values(["fips", "anio"]).reset_index(drop=True)


TRIGO = [22, 23, 24, 26, 225, 230, 234, 236, 238]  # trigo solo o en doble cultivo (nombres del CDL)
FALLOW = 61
VENTANA = 8


def lut_cdl() -> tuple[np.ndarray, np.ndarray]:
    """Tablas por código CDL: es agrícola (bool) y n° de cultivos en el año (0 barbecho, 2 doble)."""
    agr = np.zeros(256, bool)
    agr[AGRICOLA] = True
    n = agr.astype(np.int8)
    n[FALLOW] = 0
    cl = pd.read_csv(CLASES)
    n[cl.loc[cl["nombre"].str.startswith("Dbl Crop"), "codigo"].to_numpy()] = 2
    return agr, n


def _racha3(b):  # mismo cultivo 3 años seguidos o más (R13)
    return (b[:-2] & b[1:-1] & b[2:]).any(axis=0)


def _secuencia_tesela(args) -> dict:
    """Sumas por condado (bincount) de los indicadores de secuencia de una tesela, por ventana."""
    import rasterio
    from rasterio.features import rasterize

    rutas, formas, anios, ventanas, n, agr, ncult, es_trigo, ind = args
    pila = []
    for ruta in rutas:
        with rasterio.open(ruta) as src:
            pila.append(src.read(1).ravel())
            if len(pila) == 1:
                ids = rasterize(formas, out_shape=(src.height, src.width), transform=src.transform,
                                fill=0, dtype="int32").ravel()
    dentro = ids > 0
    pila = np.stack([p[dentro] for p in pila])
    ids = ids[dentro]
    out = {}
    for v in ventanas:
        s = pila[anios.index(v):anios.index(v) + VENTANA]
        ok = agr[s].all(axis=0)
        s, i = s[:, ok], ids[ok]
        ms, mm = (s == 5), (s == 1)
        alterna = (ms | mm).all(axis=0) & (s[1:] != s[:-1]).all(axis=0)
        # Shannon por píxel sobre las clases de la secuencia: ln(N) - sum(c ln c) / N
        srt = np.sort(s, axis=0)
        clogc = np.zeros(s.shape[1])
        r = np.ones(s.shape[1])
        for k in range(1, VENTANA):
            igual = srt[k] == srt[k - 1]
            clogc += np.where(igual, 0, r * np.log(r))
            r = np.where(igual, r + 1, 1)
        clogc += r * np.log(r)
        vals = {"base": np.ones(s.shape[1]), "alternado": alterna, "maiz_cont": _racha3(mm),
                "soja_cont": _racha3(ms), "trigo": es_trigo[s].any(axis=0),
                "alfalfa": (s == 36).any(axis=0), "cultivos": ncult[s].sum(axis=0) / VENTANA,
                "shannon": np.log(VENTANA) - clogc / VENTANA}
        out[v] = {k: np.bincount(i, weights=vals[k].astype(float), minlength=n + 1) for k in ind}
    return out


def rotacion_secuencia() -> pd.DataFrame | None:
    """Indicadores de la secuencia de 8 años por píxel del CDL, agregados por condado y ventana.

    Denominador: píxeles con clase agrícola en los 8 años de la ventana.
    """
    import geopandas as gpd

    tes = teselas_por_anio()
    if not tes:
        return None
    cond = gpd.read_file(REPO / "data" / "reference" / "condados.gpkg").to_crs(5070)
    claves = teselas_esperadas(cond, set().union(*[set(t) for t in tes.values()]))
    completos = sorted(a for a, t in tes.items() if claves <= set(t))
    ventanas = [a for a in completos if all(a + k in completos for k in range(VENTANA))]
    if not ventanas:
        return None
    anios = sorted({a + k for a in ventanas for k in range(VENTANA)})
    fips = cond["fips"].astype(str).str.zfill(5).tolist()
    n = len(fips)
    formas = [(g, i + 1) for i, g in enumerate(cond.geometry)]
    agr, ncult = lut_cdl()
    es_trigo = np.zeros(256, bool)
    es_trigo[TRIGO] = True
    ind = ["base", "alternado", "maiz_cont", "soja_cont", "trigo", "alfalfa", "cultivos", "shannon"]
    acc = {v: {k: np.zeros(n + 1) for k in ind} for v in ventanas}

    trabajos = [([tes[a][clave] for a in anios], formas, anios, ventanas, n, agr, ncult, es_trigo, ind)
                for clave in sorted(claves)]
    # una tesela por proceso; las sumas se hacen en el orden fijo de las teselas (reproducible)
    with ProcessPoolExecutor(max_workers=min(6, os.cpu_count() or 1)) as ex:
        for parcial in ex.map(_secuencia_tesela, trabajos):
            for v in ventanas:
                for k in ind:
                    acc[v][k] += parcial[v][k]
    filas = []
    for v in ventanas:
        b = acc[v]["base"][1:]

        def media(k, factor=100):
            return np.where(b > 0, factor * acc[v][k][1:] / np.maximum(b, 1), np.nan)

        filas.append(pd.DataFrame({
            "fips": fips, "ventana": f"{v}-{v + VENTANA - 1}",
            "pct_maiz_soja_alternado": media("alternado"), "pct_maiz_continuo": media("maiz_cont"),
            "pct_soja_continua": media("soja_cont"), "pct_rotacion_trigo": media("trigo"),
            "pct_rotacion_alfalfa": media("alfalfa"), "cultivos_por_anio": media("cultivos", 1),
            "diversidad_shannon": media("shannon", 1)}))
    df = pd.concat(filas, ignore_index=True)
    num = df.columns[2:]
    df[num] = df[num].round(4)
    return df.sort_values(["fips", "ventana"]).reset_index(drop=True)


def mascaras_cultivo() -> None:
    """mascara_maiz_<anio>.tif y mascara_soja_<anio>.tif (1 bit, 30 m, EPSG:5070).

    Misma grilla que mascara_agricola.tif; 1 = píxel con ese cultivo en el CDL del año y dentro de
    los condados. Solo años con todas las teselas; las máscaras que ya existen no se rehacen.
    """
    import geopandas as gpd
    import rasterio
    from rasterio.features import rasterize

    tes = teselas_por_anio()
    if not tes or not MASCARA.exists():
        return
    cond = gpd.read_file(REPO / "data" / "reference" / "condados.gpkg").to_crs(5070)
    claves = teselas_esperadas(cond, set().union(*[set(t) for t in tes.values()]))
    with rasterio.open(MASCARA) as ref:
        perfil, tr, alto, ancho = ref.profile.copy(), ref.transform, ref.height, ref.width
    perfil.update(nbits=1, compress="deflate", zlevel=6)
    formas = [(g, 1) for g in cond.geometry]
    dentro = {}
    for a in sorted(a for a, t in tes.items() if claves <= set(t)):
        salidas = {c: MASCARA.parent / f"mascara_{nom}_{a}.tif" for c, nom in ((1, "maiz"), (5, "soja"))}
        if all(p.exists() for p in salidas.values()):
            continue
        arr = {c: np.zeros((alto, ancho), np.uint8) for c in salidas}
        for clave in sorted(claves):
            with rasterio.open(tes[a][clave]) as src:
                x = src.read(1)
                t = src.transform
            if clave not in dentro:
                dentro[clave] = rasterize(formas, out_shape=x.shape, transform=t, fill=0, dtype="uint8") > 0
            c0, f0 = round((t.c - tr.c) / tr.a), round((t.f - tr.f) / tr.e)
            # recorte de la tesela a la grilla de la máscara
            fa, fb = max(f0, 0), min(f0 + x.shape[0], alto)
            ca, cb = max(c0, 0), min(c0 + x.shape[1], ancho)
            if fa >= fb or ca >= cb:
                continue
            sub = (slice(fa - f0, fb - f0), slice(ca - c0, cb - c0))
            for c in salidas:
                arr[c][fa:fb, ca:cb] |= ((x[sub] == c) & dentro[clave][sub]).astype(np.uint8)
        for c, p in salidas.items():
            with rasterio.open(p, "w", **perfil) as dst:
                dst.write(arr[c], 1)
        del arr
        print(f"máscaras maíz/soja {a} listas", flush=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    meta = RAW_CDL / "metadata_wa23.htm"
    if meta.exists():
        clases_cdl(meta)
    rot = rotacion_anual()
    if rot is not None:
        rot.to_csv(OUT / "rotacion_anual.csv", index=False, encoding="utf-8")
        print(f"rotacion_anual.csv: años {sorted(rot['anio'].unique())}")
    cdl_cult = sorted(RAW_CDL.glob("*_cultivated_layer.zip"))
    if cdl_cult:
        mascara_agricola(cdl_cult[-1])
    seq = rotacion_secuencia()
    if seq is not None:
        seq.to_csv(OUT / "rotacion_secuencia.csv", index=False, encoding="utf-8")
        print(f"rotacion_secuencia.csv: ventanas {sorted(seq['ventana'].unique())}")
    mascaras_cultivo()
    crops_raw = sorted(RAW.glob("qs.crops_*.txt.gz"))
    if crops_raw:
        crops = filtrar(crops_raw[-1])
        produccion(crops).to_csv(OUT / "produccion_anual.csv", index=False, encoding="utf-8")
        fenologia(crops).to_csv(OUT / "fenologia_estado.csv", index=False, encoding="utf-8")
        print("produccion_anual.csv y fenologia_estado.csv listos")
    censos = []
    for anio in cargar_config()["periodo"]["censos"]:
        raw = RAW / f"qs.census{anio}.txt.gz"
        if raw.exists():
            censos.append((anio, filtrar(raw)))
    if censos:
        practicas(censos).to_csv(OUT / "practicas_censo.csv", index=False, encoding="utf-8")
        print("practicas_censo.csv listo")


if __name__ == "__main__":
    main()
