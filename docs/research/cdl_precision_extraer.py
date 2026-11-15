"""Extrae la precisión del CDL por estado, año y cultivo (research T024).

No es parte del pipeline: arma `docs/research/cdl_precision.csv` a partir de las fuentes oficiales de NASS.

- 2008–2023: metadatos FGDC por estado (HTML), tabla "STATEWIDE AGRICULTURAL ACCURACY REPORT".
  https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-<st><aa>
- 2024–2025: NASS ya no publica metadatos por estado; la precisión por estado está en
  `CDL_<año>_accuracy_assessments.zip` (un xlsx por estado, hoja "Summary Table", valores en caché).
  https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/docs/CDL_<año>_accuracy_assessments.zip
  Cada zip pesa ~75 MB (todos los estados); se usan solo los xlsx de los 7 estados.

Uso:
    python -X utf8 docs/research/cdl_precision_extraer.py <dir_trabajo>
`<dir_trabajo>` debe estar fuera del repo: ahí se bajan los HTML y los zip (si no están ya).
Necesita `openpyxl` solo para 2024–2025.
"""
import csv
import html
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

ESTADOS = ["IA", "IL", "IN", "OH", "NE", "MN", "KS"]
ANIOS_HTML = range(2008, 2024)
ANIOS_XLSX = [2024, 2025]
CULTIVOS = {1: "maiz", 5: "soja", 24: "trigo_invierno", 28: "avena", 36: "alfalfa", 37: "otro_heno"}
URL_HTML = "https://www.nass.usda.gov/research-and-science/cropland/metadata/metadata-{st}{aa:02d}"
URL_ZIP = ("https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/docs/"
           "CDL_{anio}_accuracy_assessments.zip")
SALIDA = Path(__file__).with_name("cdl_precision.csv")

NUM = r"([\d,]+)"
PCT = r"([\d.]+)%"
FILA = re.compile(rf"^\s*([A-Za-z][A-Za-z/ .&-]*?)\s+(\d+)\s+{NUM}\s+{PCT}\s+{PCT}\s+([\d.]+|n/a)\s+{PCT}\s+{PCT}")
GLOBAL = re.compile(rf"^\s*(OVERALL ACCURACY\*\*|FSA Crops)\s+{NUM}\s+{PCT}\s+{PCT}\s+([\d.]+)", re.I)


def bajar(url, destino):
    if not destino.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "fieldshift-research"})
        with urllib.request.urlopen(req, timeout=300) as r:
            destino.write_bytes(r.read())
    return destino


def texto_html(ruta):
    t = ruta.read_text(encoding="utf-8", errors="replace")
    t = re.sub(r"<[^>]+>", "\n", t)
    return [l for l in html.unescape(t).split("\n") if l.strip()]


def de_html(st, anio, d):
    ruta = bajar(URL_HTML.format(st=st.lower(), aa=anio % 100), d / f"metadata-{st.lower()}{anio % 100:02d}.html")
    filas, glob = {}, None
    for l in texto_html(ruta):
        m = GLOBAL.match(l)
        if m and glob is None:
            glob = (float(m.group(3)), float(m.group(5)))
            continue
        m = FILA.match(l)
        if m and int(m.group(2)) in CULTIVOS and int(m.group(2)) not in filas:
            filas[int(m.group(2))] = (int(m.group(3).replace(",", "")), float(m.group(4)), float(m.group(7)))
    return glob, filas


def de_xlsx(st, anio, d):
    import openpyxl
    z = bajar(URL_ZIP.format(anio=anio), d / f"CDL_{anio}_accuracy_assessments.zip")
    nombre = f"NASS_CDL_{st}{anio % 100:02d}_accuracy.xlsx"
    with zipfile.ZipFile(z) as zf:
        miembro = next(n for n in zf.namelist() if n.endswith(nombre))
        zf.extract(miembro, d)
    wb = openpyxl.load_workbook(d / miembro, read_only=True, data_only=True)
    filas, glob = {}, None
    for r in wb["Summary Table"].iter_rows(values_only=True):
        if r[0] == "FSA Crops":
            glob = (round(r[4] * 100, 1), round(r[6], 3))
        elif isinstance(r[1], int) and r[1] in CULTIVOS and r[1] not in filas:
            filas[r[1]] = (r[2], round(r[4] * 100, 1), round(r[8] * 100, 1))
    return glob, filas


def main():
    d = Path(sys.argv[1])
    d.mkdir(parents=True, exist_ok=True)
    salida = []
    for anio in list(ANIOS_HTML) + ANIOS_XLSX:
        for st in ESTADOS:
            glob, filas = (de_html if anio < 2024 else de_xlsx)(st, anio, d)
            for cod, cultivo in CULTIVOS.items():
                px, prod, usu = filas.get(cod, (None, None, None))
                salida.append({"estado": st, "anio": anio, "cultivo": cultivo, "codigo_cdl": cod,
                               "px_correctos": px, "precision_productor_pct": prod,
                               "precision_usuario_pct": usu,
                               "global_cultivos_fsa_pct": glob[0] if glob else None,
                               "kappa_global_fsa": glob[1] if glob else None,
                               "fuente": "metadatos_fgdc_html" if anio < 2024 else "accuracy_assessments_xlsx"})
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(salida[0]))
        w.writeheader()
        w.writerows(salida)
    print(f"{len(salida)} filas -> {SALIDA}")


if __name__ == "__main__":
    main()
