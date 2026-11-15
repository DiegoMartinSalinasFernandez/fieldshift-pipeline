"""Superficie de maíz y soja por condado de Kentucky en NASS (tarea T077).

Lee los CSV de Quick Stats que bajó `nass_ky_conteo.py` (carpeta fuera del repo) y la lista de condados del
Census 2020 (`st21_ky_cou2020.txt`, https://www2.census.gov/geo/docs/reference/codes2020/cou/st21_ky_cou2020.txt).
Para cada condado calcula la superficie sembrada media de maíz y de soja en 2000–2006 (años en que NASS publica
casi el 100 % de la superficie por condado) y en 2020–2025, y en cuántos años 2020–2025 tiene rendimiento
de maíz o de soja. Imprime el resumen por distrito agrícola y la lista de condados con menos de 1.000 acres
de maíz + soja.

Uso:
  .venv/bin/python -X utf8 docs/research/nass_ky_condados.py <carpeta_csv> <st21_ky_cou2020.txt>
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

UMBRAL_AC = 1000


def leer(p: Path):
    with open(p, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            if fila["Domain"] != "TOTAL" or fila["County ANSI"] == "":
                continue
            v = fila["Value"].strip()
            if v.startswith("("):
                continue
            yield fila, float(v.replace(",", ""))


def main() -> None:
    carpeta, lista = Path(sys.argv[1]), Path(sys.argv[2])
    nombres = {}
    with open(lista, encoding="utf-8") as f:
        for fila in csv.DictReader(f, delimiter="|"):
            nombres["21" + fila["COUNTYFP"]] = fila["COUNTYNAME"]
    sup = defaultdict(lambda: defaultdict(float))  # fips -> (periodo, cultivo) -> suma
    anios_rend = defaultdict(set)
    distrito = {}
    for cultivo in ("CORN", "SOYBEANS"):
        item = f"{cultivo} - ACRES PLANTED"
        for fila, v in leer(carpeta / f"KY_{cultivo}_AREA_PLANTED_COUNTY.csv"):
            if fila["Data Item"] != item:
                continue
            fips = "21" + fila["County ANSI"]
            distrito[fips] = fila["Ag District"]
            a = int(fila["Year"])
            if 2000 <= a <= 2006:
                sup[fips][("0006", cultivo)] += v / 7
            elif 2020 <= a <= 2025:
                sup[fips][("2025", cultivo)] += v / 6
        for fila, v in leer(carpeta / f"KY_{cultivo}_YIELD_COUNTY.csv"):
            if "YIELD" in fila["Data Item"] and "IRRIGATED" not in fila["Data Item"] and \
                    2020 <= int(fila["Year"]) <= 2025:
                anios_rend["21" + fila["County ANSI"]].add(fila["Year"])
    print(f"condados Census 2020: {len(nombres)}; con alguna fila de condado de maíz o soja (cualquier año): {len(distrito)}")
    sin_fila = sorted(set(nombres) - set(distrito))
    print("sin ninguna fila de maíz ni soja:", ", ".join(f"{f} {nombres[f]}" for f in sin_fila) or "ninguno")
    w = csv.writer(sys.stdout)
    w.writerow(["fips", "condado", "distrito", "maiz_soja_ac_2000_06", "maiz_soja_ac_2020_25",
                "anios_rend_2020_25"])
    por_dist = defaultdict(lambda: [0, 0, 0.0, 0.0])
    for fips in sorted(nombres):
        s0 = sup[fips][("0006", "CORN")] + sup[fips][("0006", "SOYBEANS")]
        s1 = sup[fips][("2025", "CORN")] + sup[fips][("2025", "SOYBEANS")]
        d = distrito.get(fips, "?")
        por_dist[d][0] += 1
        por_dist[d][1] += s0 < UMBRAL_AC
        por_dist[d][2] += s0
        por_dist[d][3] += s1
        if s0 < UMBRAL_AC:
            w.writerow([fips, nombres[fips], d, round(s0), round(s1), len(anios_rend[fips])])
    print()
    w.writerow(["distrito", "condados", f"condados_lt{UMBRAL_AC}ac_2000_06", "maiz_soja_ac_2000_06",
                "maiz_soja_ac_2020_25_publicados"])
    for d, (n, bajos, s0, s1) in sorted(por_dist.items()):
        w.writerow([d, n, bajos, round(s0), round(s1)])
    print("condados con rendimiento de maíz o soja en 2020–2025:",
          sum(1 for f in nombres if anios_rend[f]))


if __name__ == "__main__":
    main()
