"""T090/T105: fechas y teselas de MODIS v061 por año, Planetary Computer (STAC) vs. LP DAAC (CMR).

Solo metadatos: no baja ningún archivo. Uso:
    .venv/bin/python -X utf8 docs/research/modis_fechas.py [anio0 anio1] [producto] [diez] > salida.txt
producto: MOD13Q1 (por defecto, T090) o MOD11A2 (T105). "diez" usa el bbox de los 10 estados.
"""
import sys
from collections import defaultdict

import requests

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
# Siete estados del Corn Belt (IA, IL, IN, OH, NE, MN, KS) con 0,05° de margen, como download.py
BBOX = [-104.11, 36.94, -80.47, 49.44]
# Diez estados (suma MO, WI y SD): MO llega a 35,995° N en el bootheel; WI y SD quedan dentro del resto
BBOX_DIEZ = [-104.11, 35.94, -80.47, 49.44]
COLECCION = {"MOD13Q1": "modis-13Q1-061", "MOD11A2": "modis-11A2-061"}
PRODUCTO = "MOD13Q1"


def pc(anio):
    body = {"collections": [COLECCION[PRODUCTO]], "bbox": BBOX,
            "datetime": f"{anio}-01-01T00:00:00Z/{anio}-12-31T23:59:59Z", "limit": 500}
    url, out = STAC, set()
    while url:
        r = requests.post(url, json=body, timeout=120)
        r.raise_for_status()
        j = r.json()
        for f in j["features"]:
            p = f["id"].split(".")  # MOD13Q1.A2023001.h10v04.061.<prod>
            if p[0] == PRODUCTO and p[1].startswith(f"A{anio}"):
                out.add((p[1], p[2]))
        nxt = [l for l in j.get("links", []) if l.get("rel") == "next"]
        url, body = (nxt[0]["href"], nxt[0].get("body", body)) if nxt else (None, None)
    return out


def cmr(anio):
    out, page = set(), 1
    while True:
        r = requests.get(CMR, params={"short_name": PRODUCTO, "version": "061",
                                      "bounding_box": ",".join(map(str, BBOX)),
                                      "temporal": f"{anio}-01-01T00:00:00Z,{anio}-12-31T23:59:59Z",
                                      "page_size": 2000, "page_num": page}, timeout=120)
        r.raise_for_status()
        es = r.json()["feed"]["entry"]
        for e in es:
            p = e["producer_granule_id"].split(".")
            if p[1].startswith(f"A{anio}"):  # la búsqueda temporal trae también el compuesto que cruza el año
                out.add((p[1], p[2]))
        if len(es) < 2000:
            return out
        page += 1


def resumen(s):
    return sorted({a for a, _ in s}), sorted({t for _, t in s})


def main():
    global PRODUCTO, BBOX
    a0, a1 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (2020, 2025)
    if len(sys.argv) > 3:
        PRODUCTO = sys.argv[3]
    if len(sys.argv) > 4 and sys.argv[4] == "diez":
        BBOX = BBOX_DIEZ
    for anio in range(a0, a1 + 1):
        p, c = pc(anio), cmr(anio)
        fp, tp = resumen(p)
        fc, tc = resumen(c)
        print(f"== {anio}: PC {len(p)} granulos, {len(fp)} fechas, {len(tp)} teselas | "
              f"CMR {len(c)} granulos, {len(fc)} fechas, {len(tc)} teselas")
        print(f"   teselas PC : {' '.join(tp)}")
        print(f"   teselas CMR: {' '.join(tc)}")
        print(f"   fechas CMR que no estan en PC: {' '.join(sorted(set(fc) - set(fp))) or '-'}")
        print(f"   fechas PC que no estan en CMR: {' '.join(sorted(set(fp) - set(fc))) or '-'}")
        falt = defaultdict(list)
        for a, t in sorted(c - p):
            falt[t].append(a)
        for t, fs in sorted(falt.items()):
            print(f"   en CMR y no en PC, {t}: {len(fs)} -> {' '.join(fs)}")
        for a, t in sorted(p - c):
            print(f"   en PC y no en CMR: {a} {t}")
        porf = defaultdict(set)
        for a, t in c:
            porf[a].add(t)
        inc = {a: sorted(set(tc) - ts) for a, ts in porf.items() if set(tc) - ts}
        for a, ts in sorted(inc.items()):
            print(f"   CMR fecha {a} sin teselas: {' '.join(ts)}")


if __name__ == "__main__":
    main()
