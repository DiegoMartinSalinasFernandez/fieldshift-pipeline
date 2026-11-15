"""Rendimiento por estado de NASS para los años de eventos extremos (tarea T031).

Recorre la base completa de Quick Stats (qs.crops_<fecha>.txt.gz, la baja src/cultivos/download.py) y saca el
rendimiento de nivel estado (SURVEY, ALL PRODUCTION PRACTICES, año completo) de maíz para grano, soja y trigo de
invierno en los 7 estados, 2000-2025, junto con el promedio de los 5 años anteriores (referencia simple, no es
tendencia). Solo lee; no escribe en data/.

Uso: .venv/bin/python -X utf8 docs/research/eventos_extremos_rend_estado.py [ruta_qs_crops] > salida.csv
"""
import csv
import gzip
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ESTADOS = {"IA", "IL", "IN", "OH", "NE", "MN", "KS"}
ANIOS = {str(a) for a in range(1995, 2026)}
# commodity, class, util -> cultivo
CULTIVOS = {
    ("CORN", "ALL CLASSES", "GRAIN"): "maiz",
    ("SOYBEANS", "ALL CLASSES", "ALL UTILIZATION PRACTICES"): "soja",
    ("WHEAT", "WINTER", "ALL UTILIZATION PRACTICES"): "trigo_invierno",
}


def leer(ruta: Path) -> dict:
    rend = {}
    with gzip.open(ruta, "rt", encoding="utf-8", errors="replace") as f:
        lector = csv.reader(f, delimiter="\t")
        cab = next(lector)
        i = {c: k for k, c in enumerate(cab)}
        for fila in lector:
            if fila[i["AGG_LEVEL_DESC"]] != "STATE" or fila[i["SOURCE_DESC"]] != "SURVEY":
                continue
            if fila[i["STATE_ALPHA"]] not in ESTADOS or fila[i["YEAR"]] not in ANIOS:
                continue
            if fila[i["STATISTICCAT_DESC"]] != "YIELD" or fila[i["UNIT_DESC"]] != "BU / ACRE":
                continue
            if fila[i["PRODN_PRACTICE_DESC"]] != "ALL PRODUCTION PRACTICES":
                continue
            if fila[i["DOMAIN_DESC"]] != "TOTAL" or fila[i["REFERENCE_PERIOD_DESC"]] != "YEAR":
                continue
            cult = CULTIVOS.get((fila[i["COMMODITY_DESC"]], fila[i["CLASS_DESC"]], fila[i["UTIL_PRACTICE_DESC"]]))
            valor = fila[i["VALUE"]].strip().replace(",", "")
            if not cult or valor.startswith("("):
                continue
            rend[(fila[i["STATE_ALPHA"]], cult, int(fila[i["YEAR"]]))] = float(valor)
    return rend


def main() -> None:
    if len(sys.argv) > 1:
        ruta = Path(sys.argv[1])
    else:
        ruta = sorted((REPO / "data/raw/cultivos/nass").glob("qs.crops_*.txt.gz"))[-1]
    rend = leer(ruta)
    w = csv.writer(sys.stdout)
    w.writerow(["estado", "cultivo", "anio", "rend_bu_ac", "media_5_previos_bu_ac", "dif_pct"])
    for (est, cult, anio) in sorted(rend):
        if anio < 2000:
            continue
        previos = [rend[(est, cult, a)] for a in range(anio - 5, anio) if (est, cult, a) in rend]
        media = round(sum(previos) / len(previos), 1) if len(previos) == 5 else ""
        dif = round(100 * (rend[(est, cult, anio)] / media - 1), 1) if media else ""
        w.writerow([est, cult, anio, rend[(est, cult, anio)], media, dif])
    print(f"# archivo: {ruta.name}", file=sys.stderr)


if __name__ == "__main__":
    main()
