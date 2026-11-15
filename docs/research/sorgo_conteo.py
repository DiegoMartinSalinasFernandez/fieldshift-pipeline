"""Conteo de sorgo granífero en NASS (tarea T022).

Recorre la base completa de Quick Stats (qs.crops_<fecha>.txt.gz, la baja src/cultivos/download.py) y escribe
dos tablas a la salida estándar, separadas por una línea vacía:

1. Nivel estado (SURVEY, año calendario, 2015-2025, los 7 estados): superficie sembrada y cosechada de sorgo,
   soja, trigo de invierno y maíz.
2. Nivel condado (SURVEY, ALL PRODUCTION PRACTICES, 2000-2025): por estado y año, cuántos condados tienen
   rendimiento de sorgo granífero publicado, cuántas filas son "OTHER (COMBINED) COUNTIES" (998), cuántas
   filas llevan un código entre paréntesis, y qué parte de la superficie cosechada del estado queda en la 998.

Solo lee; no escribe en data/.
Uso: .venv/bin/python -X utf8 docs/research/sorgo_conteo.py [ruta_qs_crops] > salida.txt
"""
import csv
import gzip
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ESTADOS = ["IA", "IL", "IN", "OH", "NE", "MN", "KS"]
ANIOS_ESTADO = {str(a) for a in range(2015, 2026)}
ANIOS_CONDADO = {str(a) for a in range(2000, 2026)}

# short_desc exactos, nivel estado
SHORT_ESTADO = {
    "SORGHUM - ACRES PLANTED": ("sorgo", "sembrada"),  # grano + silaje
    "SORGHUM, GRAIN - ACRES HARVESTED": ("sorgo", "cosechada"),
    "SORGHUM, SILAGE - ACRES HARVESTED": ("sorgo_silaje", "cosechada"),
    "SOYBEANS - ACRES PLANTED": ("soja", "sembrada"),
    "SOYBEANS - ACRES HARVESTED": ("soja", "cosechada"),
    "WHEAT, WINTER - ACRES PLANTED": ("trigo_invierno", "sembrada"),
    "WHEAT, WINTER - ACRES HARVESTED": ("trigo_invierno", "cosechada"),
    "CORN - ACRES PLANTED": ("maiz", "sembrada"),
    "CORN, GRAIN - ACRES HARVESTED": ("maiz", "cosechada"),
}
# short_desc exactos, nivel condado
SHORT_CONDADO = {
    "SORGHUM, GRAIN - YIELD, MEASURED IN BU / ACRE": "rend",
    "SORGHUM, GRAIN - ACRES HARVESTED": "cosechada",
    "SORGHUM - ACRES PLANTED": "sembrada",
    "SORGHUM, GRAIN - PRODUCTION, MEASURED IN BU": "produccion",
}


def numero(v: str):
    v = v.strip().replace(",", "")
    try:
        return float(v)
    except ValueError:
        return None


def main() -> None:
    if len(sys.argv) > 1:
        ruta = Path(sys.argv[1])
    else:
        ruta = sorted((REPO / "data/raw/cultivos/nass").glob("qs.crops_*.txt.gz"))[-1]
    estado: dict = {}
    cond_n: Counter = Counter()  # (estado, anio, variable, tipo) -> filas
    cond_998_ac: dict = defaultdict(float)  # (estado, anio) -> acres cosechados en la 998
    cond_tot_ac: dict = defaultdict(float)  # (estado, anio) -> acres cosechados en condados + 998
    with gzip.open(ruta, "rt", encoding="utf-8", errors="replace") as f:
        lector = csv.reader(f, delimiter="\t")
        cab = next(lector)
        i = {c: k for k, c in enumerate(cab)}
        for fila in lector:
            if fila[i["SOURCE_DESC"]] != "SURVEY" or fila[i["STATE_ALPHA"]] not in ESTADOS:
                continue
            if fila[i["DOMAIN_DESC"]] != "TOTAL" or fila[i["REFERENCE_PERIOD_DESC"]] != "YEAR":
                continue
            st, anio, sd = fila[i["STATE_ALPHA"]], fila[i["YEAR"]], fila[i["SHORT_DESC"]]
            nivel = fila[i["AGG_LEVEL_DESC"]]
            if nivel == "STATE" and anio in ANIOS_ESTADO and sd in SHORT_ESTADO:
                estado[(st, anio) + SHORT_ESTADO[sd]] = fila[i["VALUE"]].strip()
            elif nivel == "COUNTY" and anio in ANIOS_CONDADO and sd in SHORT_CONDADO:
                var = SHORT_CONDADO[sd]
                v = fila[i["VALUE"]].strip()
                if fila[i["COUNTY_CODE"]] == "998":
                    tipo = "combinada_998"
                elif v.startswith("("):
                    tipo = "codigo"
                else:
                    tipo = "condado"
                cond_n[(st, anio, var, tipo)] += 1
                if var == "cosechada" and numero(v) is not None:
                    cond_tot_ac[(st, anio)] += numero(v)
                    if tipo == "combinada_998":
                        cond_998_ac[(st, anio)] += numero(v)

    w = csv.writer(sys.stdout)
    w.writerow(["estado", "anio", "cultivo", "variable", "acres"])
    for k in sorted(estado):
        st, anio, cult, var = k
        w.writerow([st, anio, cult, var, estado[k]])
    print()
    w.writerow(["estado", "anio", "variable", "condados_con_dato", "filas_codigo", "filas_998",
                "pct_cosechada_en_998"])
    for st in ESTADOS:
        for anio in sorted(ANIOS_CONDADO):
            for var in ["rend", "sembrada", "cosechada", "produccion"]:
                n = [cond_n[(st, anio, var, t)] for t in ("condado", "codigo", "combinada_998")]
                if sum(n) == 0:
                    continue
                tot = cond_tot_ac[(st, anio)]
                pct = f"{100 * cond_998_ac[(st, anio)] / tot:.1f}" if var == "cosechada" and tot else ""
                w.writerow([st, anio, var, *n, pct])


if __name__ == "__main__":
    main()
