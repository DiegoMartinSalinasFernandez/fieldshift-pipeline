"""Conteo de NASS para los estados candidatos (tarea T044).

Lee la base completa de Quick Stats (qs.crops_<fecha>.txt.gz) desde un archivo local o, si se le pasa una URL,
en streaming desde nass.usda.gov sin guardarla en disco. Solo lee; no escribe en data/.

Escribe a la salida estándar tres tablas CSV separadas por una línea vacía:

1. `estado`: superficie sembrada (y cosechada) de nivel estado, SURVEY, año calendario, 2020-2024, por estado y
   cultivo, más la superficie cosechada bajo riego cuando NASS la publica.
2. `condado`: por estado, cultivo (maíz grano y soja) y año 2000-2025, cuántos condados tienen rendimiento con
   número, cuántas filas llevan un código entre paréntesis ((D), (Z), ...) y cuántas son "OTHER (COMBINED)
   COUNTIES" (county_code 998).
3. `peso998`: por estado, cultivo y año, la superficie cosechada de condado total y la que cae en la 998.

Uso:
  .venv/bin/python -X utf8 docs/research/proximos_estados_conteo.py [ruta_o_url_qs_crops] > salida.csv
"""
import csv
import gzip
import io
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ACTUALES = ["IA", "IL", "IN", "OH", "NE", "MN", "KS"]
CANDIDATOS = ["SD", "WI", "MO", "MI", "ND"]
ESTADOS = set(ACTUALES + CANDIDATOS)
ANIOS_ESTADO = {str(a) for a in range(2020, 2025)}
ANIOS_CONDADO = {str(a) for a in range(2000, 2026)}

# short_desc de nivel estado que interesan (sembrada salvo donde NASS solo publica cosechada)
SHORT_ESTADO = {
    "CORN - ACRES PLANTED": "maiz",
    "SOYBEANS - ACRES PLANTED": "soja",
    "WHEAT, WINTER - ACRES PLANTED": "trigo_invierno",
    "WHEAT, SPRING, (EXCL DURUM) - ACRES PLANTED": "trigo_primavera",
    "WHEAT, SPRING, DURUM - ACRES PLANTED": "trigo_durum",
    "OATS - ACRES PLANTED": "avena",
    "BARLEY - ACRES PLANTED": "cebada",
    "SORGHUM - ACRES PLANTED": "sorgo",
    "SUNFLOWER - ACRES PLANTED": "girasol",
    "BEANS, DRY EDIBLE, (EXCL CHICKPEAS) - ACRES PLANTED": "poroto_seco",
    "BEANS, DRY EDIBLE, INCL CHICKPEAS - ACRES PLANTED": "poroto_seco_incl_garbanzo",
    "SUGARBEETS - ACRES PLANTED": "remolacha",
    "POTATOES - ACRES PLANTED": "papa",
    "CANOLA - ACRES PLANTED": "canola",
    "COTTON - ACRES PLANTED": "algodon",
    "RICE - ACRES PLANTED": "arroz",
    "HAY & HAYLAGE, ALFALFA - ACRES HARVESTED": "alfalfa_cosechada",
    "HAY, ALFALFA - ACRES HARVESTED": "alfalfa_heno_cosechada",
    "HAY - ACRES HARVESTED": "heno_cosechada",
    "CORN, SILAGE - ACRES HARVESTED": "maiz_silaje_cosechada",
    "CORN, GRAIN - ACRES HARVESTED": "maiz_grano_cosechada",
    "SOYBEANS - ACRES HARVESTED": "soja_cosechada",
    "CORN, GRAIN, IRRIGATED - ACRES HARVESTED": "maiz_grano_riego_cosechada",
    "SOYBEANS, IRRIGATED - ACRES HARVESTED": "soja_riego_cosechada",
}

# condado: rendimiento y cosechada de maíz grano y soja
SHORT_REND = {"CORN, GRAIN - YIELD, MEASURED IN BU / ACRE": "maiz", "SOYBEANS - YIELD, MEASURED IN BU / ACRE": "soja"}
SHORT_COS = {"CORN, GRAIN - ACRES HARVESTED": "maiz", "SOYBEANS - ACRES HARVESTED": "soja"}


def numero(v: str) -> float | None:
    v = v.strip().replace(",", "")
    try:
        return float(v)
    except ValueError:
        return None


def abrir(fuente: str):
    if fuente.startswith("http"):
        import requests

        r = requests.get(fuente, stream=True, timeout=120)
        r.raise_for_status()
        r.raw.decode_content = False
        return io.TextIOWrapper(gzip.GzipFile(fileobj=r.raw), encoding="utf-8", errors="replace")
    return gzip.open(fuente, "rt", encoding="utf-8", errors="replace")


def main() -> None:
    if len(sys.argv) > 1:
        fuente = sys.argv[1]
    else:
        fuente = str(sorted((REPO / "data/raw/cultivos/nass").glob("qs.crops_*.txt.gz"))[-1])

    estado = defaultdict(list)  # (st, cultivo) -> [valor por año]
    estado_anios = defaultdict(set)
    cond = Counter()  # (st, cultivo, año, tipo) -> n
    cos = defaultdict(float)  # (st, cultivo, año, total|998) -> acres

    with abrir(fuente) as f:
        lector = csv.reader(f, delimiter="\t")
        i = {c: k for k, c in enumerate(next(lector))}
        for fila in lector:
            st = fila[i["STATE_ALPHA"]]
            if st not in ESTADOS or fila[i["SOURCE_DESC"]] != "SURVEY":
                continue
            if fila[i["DOMAIN_DESC"]] != "TOTAL" or fila[i["REFERENCE_PERIOD_DESC"]] != "YEAR":
                continue
            nivel, anio, sd = fila[i["AGG_LEVEL_DESC"]], fila[i["YEAR"]], fila[i["SHORT_DESC"]]
            if nivel == "STATE" and anio in ANIOS_ESTADO and sd in SHORT_ESTADO:
                v = numero(fila[i["VALUE"]])
                if v is not None and anio not in estado_anios[(st, SHORT_ESTADO[sd])]:
                    estado_anios[(st, SHORT_ESTADO[sd])].add(anio)
                    estado[(st, SHORT_ESTADO[sd])].append(v)
            elif nivel == "COUNTY" and anio in ANIOS_CONDADO:
                if fila[i["PRODN_PRACTICE_DESC"]] not in ("ALL PRODUCTION PRACTICES", ""):
                    continue
                es998 = fila[i["COUNTY_CODE"]] == "998"
                if sd in SHORT_REND:
                    c = SHORT_REND[sd]
                    if es998:
                        cond[(st, c, anio, "filas_998")] += 1
                    elif numero(fila[i["VALUE"]]) is not None:
                        cond[(st, c, anio, "condados_con_rend")] += 1
                    else:
                        cond[(st, c, anio, "filas_codigo")] += 1
                elif sd in SHORT_COS:
                    v = numero(fila[i["VALUE"]])
                    if v is not None:
                        c = SHORT_COS[sd]
                        cos[(st, c, anio, "total")] += v
                        if es998:
                            cos[(st, c, anio, "998")] += v

    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(["tabla", "estado", "cultivo", "n_anios", "media_2020_2024_ac"])
    for (st, c), vals in sorted(estado.items()):
        w.writerow(["estado", st, c, len(vals), round(sum(vals) / len(vals))])
    print()
    w.writerow(["tabla", "estado", "cultivo", "anio", "condados_con_rend", "filas_codigo", "filas_998"])
    for st in sorted(ESTADOS):
        for c in ("maiz", "soja"):
            for a in sorted(ANIOS_CONDADO):
                fila = [cond[(st, c, a, t)] for t in ("condados_con_rend", "filas_codigo", "filas_998")]
                w.writerow(["condado", st, c, a, *fila])
    print()
    w.writerow(["tabla", "estado", "cultivo", "anio", "cosechada_condados_ac", "cosechada_998_ac", "pct_998"])
    for st in sorted(ESTADOS):
        for c in ("maiz", "soja"):
            for a in sorted(ANIOS_CONDADO):
                tot, o = cos[(st, c, a, "total")], cos[(st, c, a, "998")]
                pct = round(100 * o / tot, 1) if tot else ""
                w.writerow(["peso998", st, c, a, round(tot), round(o), pct])


if __name__ == "__main__":
    main()
