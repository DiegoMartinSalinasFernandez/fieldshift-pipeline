"""T102: SSURGO (Soil Data Access) y NASADEM en Dakota del Norte y Michigan. No toca data/ ni config/.

Mismas consultas que docs/research/suelo_ky_sda.py (T087), con el estado como parámetro y en paralelo
(SDA tarda ~1 min por consulta). Además compara las áreas de levantamiento con los FIPS de condado del
Census para ver cuáles convertiría bien fips_de_area() de src/suelo_terreno/process.py.

Uso: .venv/bin/python -X utf8 docs/research/suelo_nd_mi_sda.py ND,MI [carpeta_con_cb_2023_us_county_500k.shp]
"""
import json
import math
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

URL = "https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest"
FIPS = {"ND": "38", "MI": "26", "KY": "21", "KS": "20"}


def sda(sql):
    for i in range(4):
        try:
            r = requests.post(URL, data={"query": sql, "format": "JSON+COLUMNNAME"}, timeout=600)
            r.raise_for_status()
            t = r.json().get("Table", [])
            return [dict(zip(t[0], f)) for f in t[1:]] if t else []
        except Exception as e:  # noqa: BLE001
            print(f"  reintento {i + 1}: {str(e)[:200]}", file=sys.stderr)
            time.sleep(5 * (i + 1))
    return {"error": "SDA no respondió"}


NOTCOM = "(m.musym = 'NOTCOM' OR m.muname LIKE 'Not complete%' OR m.muname LIKE 'NOTCOM%')"

CONSULTAS_T = {
    "areas": "SELECT areasymbol, areaname, saverest FROM sacatalog WHERE areasymbol LIKE '{E}%' "
             "ORDER BY areasymbol",
    "notcom": "SELECT l.areasymbol, m.mukey, m.musym, m.muname, m.muacres FROM mapunit m "
              "INNER JOIN legend l ON l.lkey = m.lkey WHERE l.areasymbol LIKE '{E}%' AND " + NOTCOM,
    "cobertura_area": (
        "SELECT l.areasymbol, l.areaacres, COUNT(m.mukey) AS n_mukey, SUM(m.muacres) AS muacres, "
        "SUM(CASE WHEN " + NOTCOM + " THEN m.muacres ELSE 0 END) AS muacres_notcom, "
        "SUM(CASE WHEN m.muname LIKE 'Water%' THEN m.muacres ELSE 0 END) AS muacres_agua "
        "FROM legend l LEFT JOIN mapunit m ON m.lkey = l.lkey WHERE l.areasymbol LIKE '{E}%' "
        "GROUP BY l.areasymbol, l.areaacres ORDER BY l.areasymbol"),
    "cobertura_condado": (
        "SELECT lo.areasymbol AS condado, lo.areaname, lo.areaovacres AS acres_condado, "
        "SUM(mo.areaovacres) AS acres_mukey, "
        "SUM(CASE WHEN " + NOTCOM + " THEN mo.areaovacres ELSE 0 END) AS acres_notcom, "
        "COUNT(DISTINCT l.areasymbol) AS n_areas "
        "FROM laoverlap lo INNER JOIN legend l ON l.lkey = lo.lkey "
        "INNER JOIN muaoverlap mo ON mo.lareaovkey = lo.lareaovkey "
        "INNER JOIN mapunit m ON m.mukey = mo.mukey "
        "WHERE l.areasymbol LIKE '{E}%' AND lo.areatypename = 'County or Parish' "
        "GROUP BY lo.areasymbol, lo.areaname, lo.areaovacres ORDER BY lo.areasymbol"),
    "muaggatt": (
        "SELECT COUNT(*) AS n, SUM(m.muacres) AS acres, "
        + ", ".join(f"SUM(CASE WHEN a.{c} IS NOT NULL THEN 1 ELSE 0 END) AS n_{c}, "
                    f"SUM(CASE WHEN a.{c} IS NOT NULL THEN m.muacres ELSE 0 END) AS ac_{c}"
                    for c in ["aws0100wta", "aws0150wta", "drclassdcd", "hydgrpdcd", "wtdepannmin"])
        + " FROM mapunit m INNER JOIN legend l ON l.lkey = m.lkey "
          "LEFT JOIN muaggatt a ON a.mukey = m.mukey WHERE l.areasymbol LIKE '{E}%' AND NOT " + NOTCOM
        + " AND m.muname NOT LIKE 'Water%'"),
    "chorizon": (
        "SELECT COUNT(*) AS n_horiz, "
        + ", ".join(f"SUM(CASE WHEN h.{c} IS NOT NULL THEN 1 ELSE 0 END) AS n_{c}"
                    for c in ["hzdept_r", "hzdepb_r", "sandtotal_r", "silttotal_r", "claytotal_r",
                              "om_r", "ph1to1h2o_r", "kwfact", "dbthirdbar_r"])
        + " FROM chorizon h INNER JOIN component c ON c.cokey = h.cokey "
          "INNER JOIN mapunit m ON m.mukey = c.mukey INNER JOIN legend l ON l.lkey = m.lkey "
          "WHERE l.areasymbol LIKE '{E}%' AND c.majcompflag = 'Yes' AND h.hzdept_r < 30"),
    "componentes_sin_horiz": (
        "SELECT COUNT(*) AS n_comp_mayor, SUM(CASE WHEN hz.cokey IS NULL THEN 1 ELSE 0 END) AS n_sin_horiz "
        "FROM component c INNER JOIN mapunit m ON m.mukey = c.mukey INNER JOIN legend l ON l.lkey = m.lkey "
        "LEFT JOIN (SELECT DISTINCT cokey FROM chorizon) hz ON hz.cokey = c.cokey "
        "WHERE l.areasymbol LIKE '{E}%' AND c.majcompflag = 'Yes'"),
    "areas_condados": (
        "SELECT l.areasymbol, lo.areasymbol AS condado FROM laoverlap lo INNER JOIN legend l ON l.lkey = lo.lkey "
        "WHERE l.areasymbol LIKE '{E}%' AND lo.areatypename = 'County or Parish' ORDER BY l.areasymbol"),
    "nccpi_y_horiz_area": (
        "SELECT SUM(CASE WHEN i.interphr IS NOT NULL THEN CAST(c.comppct_r AS FLOAT) * m.muacres ELSE 0 END) "
        "/ SUM(CAST(c.comppct_r AS FLOAT) * m.muacres) AS frac_ac_nccpi, "
        "SUM(CASE WHEN hz.cokey IS NULL THEN CAST(c.comppct_r AS FLOAT) * m.muacres ELSE 0 END) "
        "/ SUM(CAST(c.comppct_r AS FLOAT) * m.muacres) AS frac_ac_sin_horiz "
        "FROM component c INNER JOIN mapunit m ON m.mukey = c.mukey INNER JOIN legend l ON l.lkey = m.lkey "
        "LEFT JOIN cointerp i ON i.cokey = c.cokey "
        "AND i.mrulename = 'NCCPI - National Commodity Crop Productivity Index (Ver 3.0)' "
        "AND i.rulename = 'NCCPI - National Commodity Crop Productivity Index (Ver 3.0)' "
        "LEFT JOIN (SELECT DISTINCT cokey FROM chorizon) hz ON hz.cokey = c.cokey "
        "WHERE l.areasymbol LIKE '{E}%' AND c.majcompflag = 'Yes'"),
    "sin_horiz_nombres": (
        "SELECT TOP 15 c.compname, SUM(c.comppct_r * m.muacres) / 100 AS acres FROM component c "
        "INNER JOIN mapunit m ON m.mukey = c.mukey INNER JOIN legend l ON l.lkey = m.lkey "
        "LEFT JOIN (SELECT DISTINCT cokey FROM chorizon) hz ON hz.cokey = c.cokey "
        "WHERE l.areasymbol LIKE '{E}%' AND c.majcompflag = 'Yes' AND hz.cokey IS NULL "
        "GROUP BY c.compname ORDER BY acres DESC"),
    "nccpi": (
        "SELECT i.rulename, COUNT(*) AS n, SUM(CASE WHEN i.interphr IS NOT NULL THEN 1 ELSE 0 END) AS n_valor "
        "FROM cointerp i INNER JOIN component c ON c.cokey = i.cokey "
        "INNER JOIN mapunit m ON m.mukey = c.mukey INNER JOIN legend l ON l.lkey = m.lkey "
        "WHERE l.areasymbol LIKE '{E}%' "
        "AND i.mrulename = 'NCCPI - National Commodity Crop Productivity Index (Ver 3.0)' "
        "AND i.rulename IN ('NCCPI - National Commodity Crop Productivity Index (Ver 3.0)', "
        "'NCCPI - NCCPI Corn Submodel (I)', 'NCCPI - NCCPI Soybeans Submodel (I)') GROUP BY i.rulename"),
}

def consultas(e):
    return {k: q.replace("{E}", e) for k, q in CONSULTAS_T.items()}


def nasadem(carpeta, e):
    import geopandas as gpd
    from shapely.geometry import box

    c = gpd.read_file(next(Path(carpeta).glob("cb_2023_us_county_500k.shp"))).to_crs(4326)
    union = c[c["STATEFP"] == FIPS[e]].union_all()
    xmin, ymin, xmax, ymax = union.bounds
    tok = requests.get("https://planetarycomputer.microsoft.com/api/sas/v1/token/nasadem", timeout=60).json()["token"]
    out = []
    for lat in range(math.floor(ymin), math.ceil(ymax)):
        for lon in range(math.floor(xmin), math.ceil(xmax)):
            if union.intersects(box(lon, lat, lon + 1, lat + 1)):
                t = f"n{lat:02d}w{-lon:03d}"
                r = requests.head("https://nasademeuwest.blob.core.windows.net/nasadem-cog/v001/"
                                  f"NASADEM_HGT_{t}.tif?{tok}", timeout=60)
                out.append({"tesela": t, "status": r.status_code,
                            "bytes": int(r.headers.get("Content-Length", 0))})
    return out


def condados(carpeta, e):
    import geopandas as gpd

    c = gpd.read_file(next(Path(carpeta).glob("cb_2023_us_county_500k.shp")))
    c = c[c["STATEFP"] == FIPS[e]]
    return {r.GEOID: {"nombre": r.NAME, "aland_ac": r.ALAND / 4046.8564224, "awater_ac": r.AWATER / 4046.8564224}
            for r in c.itertuples()}


def main():
    estados = sys.argv[1].split(",")
    carpeta = sys.argv[2] if len(sys.argv) > 2 else None
    tareas = {(e, k): q for e in estados for k, q in consultas(e).items()}
    with ThreadPoolExecutor(8) as ex:
        fut = {k: ex.submit(sda, q) for k, q in tareas.items()}
        res = {e: {k: fut[(e, k)].result() for (e2, k) in tareas if e2 == e} for e in estados}
    if carpeta:
        for e in estados:
            res[e]["nasadem"] = nasadem(carpeta, e)
            res[e]["condados_census"] = condados(carpeta, e)
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
