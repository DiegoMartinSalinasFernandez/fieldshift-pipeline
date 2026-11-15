"""Riego (Censo 2022) y soja de segunda (encuesta 2020-2024) por estado, para la tarea T044.

Lee la base completa de Quick Stats (qs.crops_<fecha>.txt.gz) y escribe a la salida estándar:
- superficie cosechada de maíz grano y soja, total y con riego, Censo 2022, nivel estado;
- % de la soja sembrada que es de segunda (`SOYBEANS, FOLLOWING ANOTHER CROP (DOUBLE CROPPED)`), 2020-2024.
Solo lee; no escribe en data/.

Uso:
  .venv/bin/python -X utf8 docs/research/proximos_estados_riego.py ruta/qs.crops_<fecha>.txt.gz
"""
import csv
import gzip
import sys

ESTADOS = {"IA", "IL", "IN", "OH", "NE", "MN", "KS", "SD", "WI", "MO", "MI", "ND"}
CENSO = {
    "CORN, GRAIN - ACRES HARVESTED",
    "CORN, GRAIN, IRRIGATED - ACRES HARVESTED",
    "SOYBEANS - ACRES HARVESTED",
    "SOYBEANS, IRRIGATED - ACRES HARVESTED",
}
SEGUNDA = "SOYBEANS, FOLLOWING ANOTHER CROP (DOUBLE CROPPED) - AREA PLANTED, MEASURED IN PCT"
ANIOS = {str(a) for a in range(2020, 2025)}


def main() -> None:
    censo, segunda = {}, {}
    with gzip.open(sys.argv[1], "rt", encoding="utf-8", errors="replace") as f:
        lector = csv.reader(f, delimiter="\t")
        i = {c: k for k, c in enumerate(next(lector))}
        for x in lector:
            st, sd = x[i["STATE_ALPHA"]], x[i["SHORT_DESC"]]
            if st not in ESTADOS or x[i["AGG_LEVEL_DESC"]] != "STATE":
                continue
            fuente, anio = x[i["SOURCE_DESC"]], x[i["YEAR"]]
            if fuente == "CENSUS" and anio == "2022" and x[i["DOMAIN_DESC"]] == "TOTAL" and sd in CENSO:
                censo[(st, sd)] = x[i["VALUE"]]
            elif fuente == "SURVEY" and sd == SEGUNDA and anio in ANIOS and x[i["REFERENCE_PERIOD_DESC"]] == "YEAR":
                segunda[(st, anio)] = x[i["VALUE"]]
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(["tabla", "estado", "short_desc_o_anio", "valor"])
    for (st, sd), v in sorted(censo.items()):
        w.writerow(["censo2022", st, sd, v])
    for (st, a), v in sorted(segunda.items()):
        w.writerow(["soja_segunda_pct", st, a, v])


if __name__ == "__main__":
    main()
