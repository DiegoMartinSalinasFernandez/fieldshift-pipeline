"""Conteo de cobertura de NASS por condado (tarea T011).

Recorre la base completa de Quick Stats (qs.crops_<fecha>.txt.gz, la baja src/cultivos/download.py) y cuenta,
por estado, cultivo, variable y año, cuántas filas de condado hay con número, con (D) u otro código, y cuántas
son "OTHER (COMBINED) COUNTIES" (county_code 998). Solo lee; no escribe en data/.

Uso: .venv/bin/python -X utf8 docs/research/nass_2024_2025_conteo.py [ruta_qs_crops] > salida.csv
"""
import csv
import gzip
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ESTADOS = {"IA", "IL", "IN", "OH", "NE", "MN", "KS"}
ANIOS = {str(a) for a in range(2018, 2027)}
# commodity, class, util -> cultivo
CULTIVOS = {
    ("CORN", "ALL CLASSES"): "maiz",
    ("SOYBEANS", "ALL CLASSES"): "soja",
    ("WHEAT", "WINTER"): "trigo_invierno",
    ("OATS", "ALL CLASSES"): "avena",
}
# (statisticcat, unit, util aceptada para ese cultivo) -> variable
VARIABLES = {
    ("YIELD", "BU / ACRE"): "rend_bu_ac",
    ("AREA PLANTED", "ACRES"): "sup_sembrada_ac",
    ("AREA HARVESTED", "ACRES"): "sup_cosechada_ac",
    ("PRODUCTION", "BU"): "produccion_bu",
}


def main() -> None:
    if len(sys.argv) > 1:
        ruta = Path(sys.argv[1])
    else:
        ruta = sorted((REPO / "data/raw/cultivos/nass").glob("qs.crops_*.txt.gz"))[-1]
    conteo: Counter = Counter()
    with gzip.open(ruta, "rt", encoding="utf-8", errors="replace") as f:
        lector = csv.reader(f, delimiter="\t")
        cab = next(lector)
        i = {c: k for k, c in enumerate(cab)}
        for fila in lector:
            if fila[i["AGG_LEVEL_DESC"]] != "COUNTY" or fila[i["SOURCE_DESC"]] != "SURVEY":
                continue
            if fila[i["STATE_ALPHA"]] not in ESTADOS or fila[i["YEAR"]] not in ANIOS:
                continue
            if fila[i["PRODN_PRACTICE_DESC"]] != "ALL PRODUCTION PRACTICES":
                continue
            if fila[i["DOMAIN_DESC"]] != "TOTAL" or fila[i["REFERENCE_PERIOD_DESC"]] != "YEAR":
                continue
            cult = CULTIVOS.get((fila[i["COMMODITY_DESC"]], fila[i["CLASS_DESC"]]))
            var = VARIABLES.get((fila[i["STATISTICCAT_DESC"]], fila[i["UNIT_DESC"]]))
            if not cult or not var:
                continue
            util = fila[i["UTIL_PRACTICE_DESC"]]
            # maíz: rendimiento, cosechada y producción de grano; sembrada para todos los usos
            if cult == "maiz":
                esperada = "ALL UTILIZATION PRACTICES" if var == "sup_sembrada_ac" else "GRAIN"
            else:
                esperada = "ALL UTILIZATION PRACTICES"
            if util != esperada:
                continue
            valor = fila[i["VALUE"]].strip()
            if fila[i["COUNTY_CODE"]] == "998":
                tipo = "combinados"
            elif valor.startswith("("):
                tipo = "codigo_" + valor.strip("()")
            else:
                tipo = "con_dato"
            conteo[(fila[i["STATE_ALPHA"]], cult, var, fila[i["YEAR"]], tipo)] += 1
    w = csv.writer(sys.stdout)
    w.writerow(["estado", "cultivo", "variable", "anio", "tipo", "n"])
    for k in sorted(conteo):
        w.writerow([*k, conteo[k]])
    print(f"# archivo: {ruta.name}", file=sys.stderr)


if __name__ == "__main__":
    main()
