"""Extremos climáticos de NASA POWER (diario, comunidad AG) en puntos extremos de los estados nuevos (T048).

Pide la serie diaria 1981-2025 de unos pocos puntos (los rincones más fríos, secos, cálidos y lluviosos de
OH, NE, MN y KS, más un punto de control en Iowa) y calcula, con las mismas definiciones que el paquete clima:
lluvia anual y de temporada (abr-sep), tmax/tmin diarias extremas, medias mensuales extremas, GDD 10/30 mensual y
de temporada, y tmax media de julio. No escribe en data/: el JSON queda en un directorio temporal.

Uso:
    .venv/bin/python -X utf8 docs/research/rangos_estados_nuevos_power.py > /tmp/rangos_power.csv
"""
from __future__ import annotations

import csv
import json
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

import requests

PUNTOS = {  # nombre: (lat, lon) -- centroides aproximados de condados elegidos por ser extremos
    "KS_Morton_SO_seco_calido": (37.19, -101.80),
    "KS_Cherokee_SE_lluvioso": (37.17, -94.85),
    "NE_Kimball_O_alto_seco": (41.20, -103.71),
    "NE_Richardson_SE": (40.13, -95.72),
    "MN_Kittson_NO_frio": (48.78, -96.78),
    "MN_StLouis_NE_frio": (47.60, -92.45),
    "OH_Lawrence_S_lluvioso": (38.60, -82.54),
    "OH_Ashtabula_NE": (41.71, -80.75),
    "IA_Story_control": (42.04, -93.46),
}
URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS = "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR"
CACHE = Path(tempfile.gettempdir()) / "t048_power"


def bajar(nombre: str, lat: float, lon: float) -> dict:
    CACHE.mkdir(exist_ok=True)
    p = CACHE / f"{nombre}.json"
    if not p.exists():
        r = requests.get(URL, params={"parameters": PARAMS, "community": "AG", "latitude": lat, "longitude": lon,
                                      "start": "19810101", "end": "20251231", "format": "JSON"}, timeout=300)
        r.raise_for_status()
        p.write_text(r.text)
        time.sleep(1)
    return json.loads(p.read_text())["properties"]["parameter"]


def gdd(tx: float, tn: float) -> float:
    tx, tn = min(max(tx, 10), 30), min(max(tn, 10), 30)
    return (tx + tn) / 2 - 10


def main() -> None:
    w = csv.writer(sys.stdout)
    w.writerow(["punto", "variable", "min", "cuando_min", "max", "cuando_max", "periodo"])
    for nombre, (lat, lon) in PUNTOS.items():
        try:
            d = bajar(nombre, lat, lon)
        except Exception as e:  # noqa: BLE001
            print(f"{nombre}: falló la descarga ({e})", file=sys.stderr)
            continue
        pr, tx, tn, tm = d["PRECTOTCORR"], d["T2M_MAX"], d["T2M_MIN"], d["T2M"]
        dias = [k for k in sorted(pr) if pr[k] > -900 and tx[k] > -900 and tn[k] > -900 and tm[k] > -900]
        anual, temp = defaultdict(float), defaultdict(float)
        gdd_t, mes_p, mes_tx, mes_tn, mes_g = defaultdict(float), defaultdict(float), defaultdict(list), \
            defaultdict(list), defaultdict(float)
        maxp1 = (0.0, "")
        for k in dias:
            a, m = int(k[:4]), int(k[4:6])
            ym = f"{a}-{m:02d}"
            anual[a] += pr[k]
            mes_p[ym] += pr[k]
            mes_tx[ym].append(tx[k])
            mes_tn[ym].append(tn[k])
            g = gdd(tx[k], tn[k])
            mes_g[ym] += g
            if 4 <= m <= 9:
                temp[a] += pr[k]
                gdd_t[a] += g
            if pr[k] > maxp1[0]:
                maxp1 = (pr[k], k)

        def fila(var, serie, periodo):
            kmin = min(serie, key=serie.get)
            kmax = max(serie, key=serie.get)
            w.writerow([nombre, var, round(serie[kmin], 1), kmin, round(serie[kmax], 1), kmax, periodo])

        fila("tmax_c_diaria", {k: tx[k] for k in dias}, "1981-2025")
        fila("tmin_c_diaria", {k: tn[k] for k in dias}, "1981-2025")
        fila("tmed_c_diaria", {k: tm[k] for k in dias}, "1981-2025")
        w.writerow([nombre, "prec_mm_diaria_max", "", "", round(maxp1[0], 1), maxp1[1], "1981-2025"])
        rec = lambda s: {k: v for k, v in s.items() if int(str(k)[:4]) >= 2000}  # noqa: E731
        fila("prec_anual_mm", rec(anual), "2000-2025")
        fila("prec_temporada_mm", rec(temp), "2000-2025")
        fila("gdd_temporada", rec(gdd_t), "2000-2025")
        fila("prec_mensual_mm", rec(mes_p), "2000-2025")
        fila("gdd_10_30_mensual", rec(mes_g), "2000-2025")
        fila("tmax_c_media_mensual", rec({k: sum(v) / len(v) for k, v in mes_tx.items()}), "2000-2025")
        fila("tmin_c_media_mensual", rec({k: sum(v) / len(v) for k, v in mes_tn.items()}), "2000-2025")
        fila("tmax_jul_c", rec({k: sum(v) / len(v) for k, v in mes_tx.items() if k.endswith("-07")}), "2000-2025")
        fila("dias_tmax_gt35_mes", rec({k: sum(t > 35 for t in v) for k, v in mes_tx.items()}), "2000-2025")
        fila("dias_tmin_le0_mes", rec({k: sum(t <= 0 for t in v) for k, v in mes_tn.items()}), "2000-2025")


if __name__ == "__main__":
    main()
