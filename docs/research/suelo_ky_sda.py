"""T087: SSURGO (Soil Data Access) y NASADEM en Kentucky. No toca data/ ni config/.

Consultas chicas a SDA (agregadas en el servidor, como src/suelo_terreno/download.py pero sin bajar tablas):
1. sacatalog: áreas de levantamiento KY%, nombre y versión publicada (saverest).
2. Unidades NOTCOM (musym 'NOTCOM' o muname 'Not Complete%') por área.
3. Cobertura por condado: Σ muacres de unidades que no son NOTCOM / areaacres del área (legend), y
   la misma cuenta con laoverlap ('County or Parish') para ver si las áreas coinciden con los condados.
4. Dato en las columnas de muaggatt, Valu1 y chorizon que usa suelo_terreno: % de mukeys (y de acres)
   con valor no nulo.
5. Qué condados toca cada área (laoverlap), NCCPI y componentes mayores sin horizontes ponderados por
   área (KY y KS como referencia).
6. NASADEM: HEAD de las teselas de 1° que tocan KY (misma regla que src/suelo_terreno/download.py),
   con el shapefile de condados del Census pasado como argumento.

Uso: .venv/bin/python -X utf8 docs/research/suelo_ky_sda.py [carpeta_con_cb_2023_us_county_500k.shp]
"""
import json
import math
import sys
import time
from pathlib import Path

import requests

URL = "https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest"


def sda(sql):
    for i in range(4):
        try:
            r = requests.post(URL, data={"query": sql, "format": "JSON+COLUMNNAME"}, timeout=300)
            r.raise_for_status()
            t = r.json().get("Table", [])
            return [dict(zip(t[0], f)) for f in t[1:]] if t else []
        except Exception as e:  # noqa: BLE001
            print(f"  reintento {i + 1}: {str(e)[:200]}", file=sys.stderr)
            time.sleep(5 * (i + 1))
    raise RuntimeError("SDA no respondió")


NOTCOM = "(m.musym = 'NOTCOM' OR m.muname LIKE 'Not complete%' OR m.muname LIKE 'NOTCOM%')"

CONSULTAS = {
    "areas": "SELECT areasymbol, areaname, saverest FROM sacatalog WHERE areasymbol LIKE 'KY%' "
             "ORDER BY areasymbol",
    "notcom": "SELECT l.areasymbol, m.mukey, m.musym, m.muname, m.muacres FROM mapunit m "
              "INNER JOIN legend l ON l.lkey = m.lkey WHERE l.areasymbol LIKE 'KY%' AND " + NOTCOM,
    "cobertura_area": (
        "SELECT l.areasymbol, l.areaacres, COUNT(m.mukey) AS n_mukey, SUM(m.muacres) AS muacres, "
        "SUM(CASE WHEN " + NOTCOM + " THEN m.muacres ELSE 0 END) AS muacres_notcom, "
        "SUM(CASE WHEN m.muname LIKE 'Water%' THEN m.muacres ELSE 0 END) AS muacres_agua "
        "FROM legend l LEFT JOIN mapunit m ON m.lkey = l.lkey WHERE l.areasymbol LIKE 'KY%' "
        "GROUP BY l.areasymbol, l.areaacres ORDER BY l.areasymbol"),
    "cobertura_condado": (
        "SELECT lo.areasymbol AS condado, lo.areaname, lo.areaovacres AS acres_condado, "
        "SUM(mo.areaovacres) AS acres_mukey, "
        "SUM(CASE WHEN " + NOTCOM + " THEN mo.areaovacres ELSE 0 END) AS acres_notcom, "
        "COUNT(DISTINCT l.areasymbol) AS n_areas "
        "FROM laoverlap lo INNER JOIN legend l ON l.lkey = lo.lkey "
        "INNER JOIN muaoverlap mo ON mo.lareaovkey = lo.lareaovkey "
        "INNER JOIN mapunit m ON m.mukey = mo.mukey "
        "WHERE l.areasymbol LIKE 'KY%' AND lo.areatypename = 'County or Parish' "
        "GROUP BY lo.areasymbol, lo.areaname, lo.areaovacres ORDER BY lo.areasymbol"),
    "muaggatt": (
        "SELECT COUNT(*) AS n, SUM(m.muacres) AS acres, "
        + ", ".join(f"SUM(CASE WHEN a.{c} IS NOT NULL THEN 1 ELSE 0 END) AS n_{c}, "
                    f"SUM(CASE WHEN a.{c} IS NOT NULL THEN m.muacres ELSE 0 END) AS ac_{c}"
                    for c in ["aws0100wta", "aws0150wta", "drclassdcd", "hydgrpdcd", "wtdepannmin"])
        + " FROM mapunit m INNER JOIN legend l ON l.lkey = m.lkey "
          "LEFT JOIN muaggatt a ON a.mukey = m.mukey WHERE l.areasymbol LIKE 'KY%' AND NOT " + NOTCOM
        + " AND m.muname NOT LIKE 'Water%'"),
    "chorizon": (
        "SELECT COUNT(*) AS n_horiz, "
        + ", ".join(f"SUM(CASE WHEN h.{c} IS NOT NULL THEN 1 ELSE 0 END) AS n_{c}"
                    for c in ["hzdept_r", "hzdepb_r", "sandtotal_r", "silttotal_r", "claytotal_r",
                              "om_r", "ph1to1h2o_r", "kwfact", "dbthirdbar_r"])
        + " FROM chorizon h INNER JOIN component c ON c.cokey = h.cokey "
          "INNER JOIN mapunit m ON m.mukey = c.mukey INNER JOIN legend l ON l.lkey = m.lkey "
          "WHERE l.areasymbol LIKE 'KY%' AND c.majcompflag = 'Yes' AND h.hzdept_r < 30"),
    "componentes_sin_horiz": (
        "SELECT COUNT(*) AS n_comp_mayor, SUM(CASE WHEN hz.cokey IS NULL THEN 1 ELSE 0 END) AS n_sin_horiz "
        "FROM component c INNER JOIN mapunit m ON m.mukey = c.mukey INNER JOIN legend l ON l.lkey = m.lkey "
        "LEFT JOIN (SELECT DISTINCT cokey FROM chorizon) hz ON hz.cokey = c.cokey "
        "WHERE l.areasymbol LIKE 'KY%' AND c.majcompflag = 'Yes'"),
    "areas_condados": (
        "SELECT l.areasymbol, lo.areasymbol AS condado FROM laoverlap lo INNER JOIN legend l ON l.lkey = lo.lkey "
        "WHERE l.areasymbol LIKE 'KY%' AND lo.areatypename = 'County or Parish' ORDER BY l.areasymbol"),
    "nccpi_y_horiz_area_KY": (
        "SELECT SUM(CASE WHEN i.interphr IS NOT NULL THEN CAST(c.comppct_r AS FLOAT) * m.muacres ELSE 0 END) "
        "/ SUM(CAST(c.comppct_r AS FLOAT) * m.muacres) AS frac_ac_nccpi, "
        "SUM(CASE WHEN hz.cokey IS NULL THEN CAST(c.comppct_r AS FLOAT) * m.muacres ELSE 0 END) "
        "/ SUM(CAST(c.comppct_r AS FLOAT) * m.muacres) AS frac_ac_sin_horiz "
        "FROM component c INNER JOIN mapunit m ON m.mukey = c.mukey INNER JOIN legend l ON l.lkey = m.lkey "
        "LEFT JOIN cointerp i ON i.cokey = c.cokey "
        "AND i.mrulename = 'NCCPI - National Commodity Crop Productivity Index (Ver 3.0)' "
        "AND i.rulename = 'NCCPI - National Commodity Crop Productivity Index (Ver 3.0)' "
        "LEFT JOIN (SELECT DISTINCT cokey FROM chorizon) hz ON hz.cokey = c.cokey "
        "WHERE l.areasymbol LIKE 'KY%' AND c.majcompflag = 'Yes'"),
    "nccpi_y_horiz_area_KS": (
        "SELECT SUM(CASE WHEN i.interphr IS NOT NULL THEN CAST(c.comppct_r AS FLOAT) * m.muacres ELSE 0 END) "
        "/ SUM(CAST(c.comppct_r AS FLOAT) * m.muacres) AS frac_ac_nccpi, "
        "SUM(CASE WHEN hz.cokey IS NULL THEN CAST(c.comppct_r AS FLOAT) * m.muacres ELSE 0 END) "
        "/ SUM(CAST(c.comppct_r AS FLOAT) * m.muacres) AS frac_ac_sin_horiz "
        "FROM component c INNER JOIN mapunit m ON m.mukey = c.mukey INNER JOIN legend l ON l.lkey = m.lkey "
        "LEFT JOIN cointerp i ON i.cokey = c.cokey "
        "AND i.mrulename = 'NCCPI - National Commodity Crop Productivity Index (Ver 3.0)' "
        "AND i.rulename = 'NCCPI - National Commodity Crop Productivity Index (Ver 3.0)' "
        "LEFT JOIN (SELECT DISTINCT cokey FROM chorizon) hz ON hz.cokey = c.cokey "
        "WHERE l.areasymbol LIKE 'KS%' AND c.majcompflag = 'Yes'"),
    "sin_horiz_nombres": (
        "SELECT TOP 15 c.compname, SUM(c.comppct_r * m.muacres) / 100 AS acres FROM component c "
        "INNER JOIN mapunit m ON m.mukey = c.mukey INNER JOIN legend l ON l.lkey = m.lkey "
        "LEFT JOIN (SELECT DISTINCT cokey FROM chorizon) hz ON hz.cokey = c.cokey "
        "WHERE l.areasymbol LIKE 'KY%' AND c.majcompflag = 'Yes' AND hz.cokey IS NULL "
        "GROUP BY c.compname ORDER BY acres DESC"),
    "nccpi": (
        "SELECT i.rulename, COUNT(*) AS n, SUM(CASE WHEN i.interphr IS NOT NULL THEN 1 ELSE 0 END) AS n_valor "
        "FROM cointerp i INNER JOIN component c ON c.cokey = i.cokey "
        "INNER JOIN mapunit m ON m.mukey = c.mukey INNER JOIN legend l ON l.lkey = m.lkey "
        "WHERE l.areasymbol LIKE 'KY%' "
        "AND i.mrulename = 'NCCPI - National Commodity Crop Productivity Index (Ver 3.0)' "
        "AND i.rulename IN ('NCCPI - National Commodity Crop Productivity Index (Ver 3.0)', "
        "'NCCPI - NCCPI Corn Submodel (I)', 'NCCPI - NCCPI Soybeans Submodel (I)') GROUP BY i.rulename"),
}


def nasadem(carpeta):
    import geopandas as gpd
    from shapely.geometry import box

    c = gpd.read_file(next(Path(carpeta).glob("cb_2023_us_county_500k.shp"))).to_crs(4326)
    union = c[c["STATEFP"] == "21"].union_all()
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


def main():
    res = {k: sda(q) for k, q in CONSULTAS.items()}
    if len(sys.argv) > 1:
        res["nasadem"] = nasadem(sys.argv[1])
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
