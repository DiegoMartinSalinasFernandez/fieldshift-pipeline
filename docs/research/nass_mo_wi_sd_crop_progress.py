"""Crop Progress de MO, WI y SD desde los reportes semanales de texto de NASS (tarea T063).

Lee una carpeta con los reportes `.txt` de la publicación Crop Progress (archivo ESMIS:
https://esmis.nal.usda.gov/publication/crop-progress) y saca, para cada tabla de etapa
("Corn Planted - Selected States" o, antes de ~2010, "Corn:  Percent Planted,"), el valor de la
semana actual de Missouri, Wisconsin y Dakota del Sur. No usa Quick Stats ni claves. No escribe en data/.

Formato viejo (estados abreviados): la primera columna es la semana actual.
Formato nuevo (nombres completos "Missouri ......:"): la tercera columna es la semana actual.
La semana termina el domingo anterior a la fecha "Released ..." del reporte.

Uso:
  .venv/bin/python -X utf8 docs/research/nass_mo_wi_sd_crop_progress.py <carpeta_txt> > cp_mowisd.csv
Salida: estado, cultivo, etapa, semana (YYYY-MM-DD), valor (número, 0 si "-", vacío si "(NA)").
"""
import csv
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ESTADOS = {"MO": "Missouri", "WI": "Wisconsin", "SD": "South Dakota"}
NOMBRES = {v: k for k, v in ESTADOS.items()}
CULTIVOS = ["Winter Wheat", "Spring Wheat", "Soybeans", "Sunflowers", "Sorghum", "Barley", "Oats", "Corn",
            "Cotton", "Rice"]
NUEVO = re.compile(r"^(%s) ([A-Za-z ]+?) - Selected States\s*$" % "|".join(CULTIVOS))
VIEJO = re.compile(r"^\s*(%s):\s+Percent ([A-Za-z ]+?),?\s*$" % "|".join(CULTIVOS))
REL = re.compile(r"Released\s+([A-Z][a-z]+)\.?\s+(\d{1,2}),\s+(\d{4})")
FIN = re.compile(r"- Selected States|^\s*[A-Z][A-Za-z ]+:\s+Percent [A-Z]|Condition|Days Suitable|Moisture|^1/|"
                 r"^\s*\d+ States|^\s*Total")
NUM =re.compile(r"\(NA\)|-|\d+")


def fecha_semana(texto: str) -> date | None:
    m = REL.search(texto)
    if not m:
        return None
    mes = m.group(1)[:3]
    d = datetime.strptime(f"{mes} {m.group(2)} {m.group(3)}", "%b %d %Y").date()
    return d - timedelta(days=(d.weekday() + 1) % 7 or 7)  # domingo anterior


def main() -> None:
    w = csv.writer(sys.stdout)
    w.writerow(["estado", "cultivo", "etapa", "semana", "valor", "archivo"])
    for p in sorted(Path(sys.argv[1]).glob("*.txt")):
        texto = p.read_text(encoding="latin-1")
        sem = fecha_semana(texto)
        if sem is None:
            print(f"sin fecha: {p.name}", file=sys.stderr)
            continue
        tabla = None
        for linea in texto.splitlines():
            m = NUEVO.match(linea) or VIEJO.match(linea)
            if m:
                tabla = (m.group(1), m.group(2).strip().upper(), bool(NUEVO.match(linea)))
                continue
            if FIN.search(linea):  # título de otra tabla o nota al pie: se cierra la tabla actual
                tabla = None
                continue
            if tabla is None or ":" not in linea:
                continue
            if "Condition" in tabla[1]:
                continue
            izq, der = linea.split(":", 1)
            nombre = izq.strip().rstrip(".").strip()
            est = NOMBRES.get(nombre) if tabla[2] else (nombre if nombre in ESTADOS else None)
            if not est:
                if nombre.startswith(("Total", "18 States", "Total ")):
                    tabla = None
                continue
            vals = NUM.findall(der)
            if len(vals) < 3:
                continue
            v = vals[2] if tabla[2] else vals[0]
            v = "" if v == "(NA)" else ("0" if v == "-" else v)
            w.writerow([est, tabla[0], tabla[1], sem.isoformat(), v, p.name])


if __name__ == "__main__":
    main()
