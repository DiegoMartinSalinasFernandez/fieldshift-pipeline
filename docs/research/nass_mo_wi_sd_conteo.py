"""Cobertura de NASS por condado en MO, WI y SD (tarea T063).

No usa la base completa (1,1 GB) ni la clave de la API: pide a la interfaz web de Quick Stats
(https://quickstats.nass.usda.gov) un CSV chico por estado, cultivo y variable, con el mismo mecanismo que el
botón "Get Data" (POST a /uuid/encode y GET a /data/spreadsheet/<uuid>.csv; cada pedido < 50.000 filas).
Los CSV se guardan en la carpeta que se le pasa (fuera del repo) y no se vuelven a bajar si ya están.
Después cuenta, por estado, cultivo, variable y año (2018–2026), condados con dato, códigos entre paréntesis
y filas "OTHER COUNTIES" (condados combinados), y la superficie sembrada de condados vs. el total del estado.

Uso:
  .venv/bin/python -X utf8 docs/research/nass_mo_wi_sd_conteo.py <carpeta_csv> > conteo_mowisd.csv
"""
import csv
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import requests

QS = "https://quickstats.nass.usda.gov"
ESTADOS = {"MO": "MISSOURI", "WI": "WISCONSIN", "SD": "SOUTH DAKOTA"}
COMMODITIES = ["CORN", "SOYBEANS", "WHEAT", "OATS", "HAY", "HAYLAGE", "SUNFLOWER", "SORGHUM"]
STATS = ["YIELD", "AREA PLANTED", "AREA HARVESTED", "PRODUCTION"]
ANIOS = {str(a) for a in range(2018, 2027)}
UA = {"User-Agent": "Mozilla/5.0 (fieldshift-research)"}


def bajar(carpeta: Path, est: str, com: str, stat: str, nivel: str) -> Path:
    destino = carpeta / f"{est}_{com}_{stat.replace(' ', '_')}_{nivel}.csv"
    if destino.exists():
        return destino
    form = {"source_desc": "SURVEY", "sector_desc": "CROPS", "commodity_desc": com, "statisticcat_desc": stat,
            "agg_level_desc": nivel, "state_name": ESTADOS[est], "freq_desc": "ANNUAL",
            "reference_period_desc": "YEAR"}
    n = requests.post(QS + "/row_counts", data=form, headers=UA, timeout=120).json()["rowcnt"]
    if n == 0:
        destino.write_text("")
        return destino
    if n > 50000:  # se piden solo los años del conteo
        form = list(form.items()) + [("year", a) for a in sorted(ANIOS)]
        n = requests.post(QS + "/row_counts", data=form, headers=UA, timeout=120).json()["rowcnt"]
        if n > 50000:
            raise RuntimeError(f"{destino.name}: {n} filas (> 50.000)")
    uuid = requests.post(QS + "/uuid/encode", data=form, headers=UA, timeout=120).json()
    r = requests.get(f"{QS}/data/spreadsheet/{uuid}.csv", headers=UA, timeout=300)
    r.raise_for_status()
    destino.write_bytes(r.content)
    time.sleep(0.5)
    return destino


def main() -> None:
    carpeta = Path(sys.argv[1])
    carpeta.mkdir(parents=True, exist_ok=True)
    conteo: Counter = Counter()
    sup = defaultdict(float)  # (est, data_item, anio, tipo) -> acres
    for est in ESTADOS:
        for com in COMMODITIES:
            for stat in STATS:
                for nivel in ("COUNTY", "STATE"):
                    if nivel == "STATE" and stat != "AREA PLANTED":
                        continue
                    p = bajar(carpeta, est, com, stat, nivel)
                    if p.stat().st_size == 0:
                        continue
                    with open(p, encoding="utf-8") as f:
                        for fila in csv.DictReader(f):
                            if fila["Year"] not in ANIOS or fila["Domain"] != "TOTAL":
                                continue
                            item = fila["Data Item"]
                            val = fila["Value"].strip()
                            if nivel == "STATE":
                                if not val.startswith("("):
                                    sup[(est, item, fila["Year"], "estado")] += float(val.replace(",", ""))
                                continue
                            combinado = fila["County"].startswith("OTHER") or fila["County ANSI"] == ""
                            if combinado:
                                tipo = "combinados"
                            elif val.startswith("("):
                                tipo = "codigo_" + val.strip("()")
                            else:
                                tipo = "con_dato"
                            conteo[(est, item, fila["Year"], tipo)] += 1
                            if stat == "AREA PLANTED" and not val.startswith("("):
                                clave = "combinados" if combinado else "condados"
                                sup[(est, item, fila["Year"], clave)] += float(val.replace(",", ""))
    w = csv.writer(sys.stdout)
    w.writerow(["estado", "data_item", "anio", "tipo", "n"])
    for k in sorted(conteo):
        w.writerow([*k, conteo[k]])
    for k in sorted(sup):
        w.writerow([k[0], k[1], k[2], "acres_" + k[3], round(sup[k])])


if __name__ == "__main__":
    main()
