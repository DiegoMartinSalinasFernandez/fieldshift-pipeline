"""SSURGO por Soil Data Access (sin login) para los lotes: polígonos de las unidades cartográficas que cortan el
recuadro de cada lote y las tablas de esas unidades (mismas consultas que src/suelo_terreno/download.py, más
las columnas que pide lotes). Se guarda tal cual en data/raw/lotes/ssurgo/.

Uso: python src/lotes/download.py ssurgo
"""
from __future__ import annotations

import datetime as dt
import json
import os
import urllib.parse
from pathlib import Path

import pandas as pd
import requests
from pyproj import Transformer

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw" / "lotes" / "ssurgo"
INTERIM = RAIZ / "data" / "interim" / "lotes"
URL = "https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest"

TABLAS = {
    "mapunit": ("SELECT m.mukey, m.muname, a.aws0100wta, a.aws0150wta, a.drclassdcd, a.drclasswettest, a.hydgrpdcd, "
                "a.hydclprs, a.flodfreqdcd, a.pondfreqprs, a.wtdepannmin, a.slopegraddcp, a.slopegradwta FROM mapunit m "
                "LEFT JOIN muaggatt a ON a.mukey = m.mukey WHERE m.mukey IN ({mukeys})"),
    "component": ("SELECT c.mukey, c.cokey, c.compname, c.comppct_r, c.majcompflag, c.slope_r, c.erocl, c.hydricrating "
                  "FROM component c WHERE c.mukey IN ({mukeys})"),
    "chorizon": ("SELECT h.cokey, h.chkey, h.hzdept_r, h.hzdepb_r, h.sandtotal_r, h.silttotal_r, h.claytotal_r, "
                 "h.om_r, h.ph1to1h2o_r, h.kwfact, h.dbthirdbar_r, "
                 "(SELECT SUM(f.fragvol_r) FROM chfrags f WHERE f.chkey = h.chkey) AS fragvol_r "
                 "FROM chorizon h INNER JOIN component c ON c.cokey = h.cokey WHERE c.mukey IN ({mukeys})"),
    "restricciones": ("SELECT r.cokey, r.reskind, r.resdept_r FROM corestrictions r "
                      "INNER JOIN component c ON c.cokey = r.cokey WHERE c.mukey IN ({mukeys})"),
    "nccpi": ("SELECT i.cokey, i.rulename, i.interphr FROM cointerp i INNER JOIN component c ON c.cokey = i.cokey "
              "WHERE c.mukey IN ({mukeys}) AND i.rulename LIKE 'NCCPI%' AND i.ruledepth = 0"),
    # los submodelos de maíz y soja están en ruledepth > 0 (misma consulta que src/suelo_terreno/download.py)
    "nccpi_submodelos": ("SELECT i.cokey, i.rulename, i.interphr FROM cointerp i INNER JOIN component c ON c.cokey = i.cokey "
                         "WHERE c.mukey IN ({mukeys}) "
                         "AND i.mrulename = 'NCCPI - National Commodity Crop Productivity Index (Ver 3.0)' "
                         "AND i.rulename IN ('NCCPI - National Commodity Crop Productivity Index (Ver 3.0)', "
                         "'NCCPI - NCCPI Corn Submodel (I)', 'NCCPI - NCCPI Soybeans Submodel (I)')"),
}


def sda(sql: str) -> pd.DataFrame:
    r = requests.post(URL, data={"query": sql, "format": "JSON+COLUMNNAME"}, timeout=600)
    r.raise_for_status()
    t = r.json().get("Table", [])
    if not t:
        return pd.DataFrame()
    return pd.DataFrame(t[1:], columns=t[0])


def escribir(df: pd.DataFrame, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = INTERIM / "parciales" / (destino.name + ".part")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(tmp, index=False, encoding="utf-8", lineterminator="\n")
    os.replace(tmp, destino)


def bajar(upsert) -> None:
    import landsat
    rec = landsat.recuadros()
    a4326 = Transformer.from_crs(5070, 4326, always_xy=True)
    filas, mukeys = [], set()
    hoy = dt.date.today().isoformat()
    for r in rec.itertuples():
        destino = RAW / f"poligonos_{r.id_lote}.csv"
        x1, y1 = r.x0 - 60, r.y0 + 60
        x2, y2 = r.x0 + r.ancho * 30 + 60, r.y0 - r.alto * 30 - 60
        xs, ys = a4326.transform([x1, x2, x2, x1, x1], [y1, y1, y2, y2, y1])
        wkt = "POLYGON((" + ", ".join(f"{x:.6f} {y:.6f}" for x, y in zip(xs, ys)) + "))"
        # recortado en origen al recuadro: los polígonos completos pesan ~20 MB por lote
        g = f"geometry::STGeomFromText('{wkt}', 4326)"
        sql = (f"SELECT mupolygonkey, mukey, mupolygongeo.STIntersection({g}).STAsText() AS wkt FROM mupolygon "
               f"WHERE mupolygongeo.STIntersects({g}) = 1 ORDER BY mupolygonkey")
        if not destino.exists():
            escribir(sda(sql), destino)
        mukeys |= set(pd.read_csv(destino, dtype={"mukey": str})["mukey"])
        filas.append({"paquete": "lotes", "archivo": destino.relative_to(RAIZ).as_posix(),
                      "fuente": "USDA NRCS Soil Data Access", "producto": "SSURGO mupolygon (recuadro del lote + 60 m)",
                      "version": "SSURGO (SDA, consultado " + hoy + ")", "fecha_descarga": hoy,
                      "consulta_o_url": URL + "?query=" + urllib.parse.quote(sql)})
    lista = ",".join(f"'{m}'" for m in sorted(mukeys))
    for tabla, plantilla in TABLAS.items():
        destino = RAW / f"{tabla}.csv"
        sql = plantilla.format(mukeys=lista)
        if not destino.exists():
            escribir(sda(sql), destino)
        filas.append({"paquete": "lotes", "archivo": destino.relative_to(RAIZ).as_posix(),
                      "fuente": "USDA NRCS Soil Data Access", "producto": f"SSURGO {tabla} de los mukeys de los lotes",
                      "version": "SSURGO (SDA, consultado " + hoy + ")", "fecha_descarga": hoy,
                      "consulta_o_url": URL + "?query=" + urllib.parse.quote(plantilla.format(mukeys="<mukeys de poligonos_*.csv>"))})
    upsert(filas)
    print(json.dumps({"mukeys": len(mukeys)}))
