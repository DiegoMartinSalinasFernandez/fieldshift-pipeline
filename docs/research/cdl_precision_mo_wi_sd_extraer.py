"""Precisión del CDL en MO, WI y SD, 2008–2025 (research T064).

Reutiliza las funciones de `cdl_precision_extraer.py` (T024) con otros estados y más clases:
doble cultivo trigo/soja (26), barbecho (61), pastura/pasto (62) y pastizal/pastura (176).
No es parte del pipeline. Arma `docs/research/cdl_precision_mo_wi_sd.csv`.

Uso:
    python -X utf8 docs/research/cdl_precision_mo_wi_sd_extraer.py <dir_trabajo>
`<dir_trabajo>` fuera del repo: ahí se bajan los HTML (~110 kB c/u) y los zip de 2024–2025 (~75 MB c/u).
"""
import csv
import importlib.util
import re
import sys
import zipfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location("base", Path(__file__).with_name("cdl_precision_extraer.py"))
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

base.ESTADOS = ["MO", "WI", "SD"]
base.CULTIVOS = {1: "maiz", 5: "soja", 24: "trigo_invierno", 26: "doble_trigo_soja", 28: "avena",
                 36: "alfalfa", 37: "otro_heno", 61: "barbecho", 62: "pastura_pasto", 176: "pastizal_pastura"}
# WI 2013 no está en la ruta de siempre (404): la página de metadatos enlaza este .htm.
URL_WI13 = ("https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/metadata/"
            "metadata_wi13.htm")
SALIDA = Path(__file__).with_name("cdl_precision_mo_wi_sd.csv")

# Como `base.FILA`, pero acepta "n/a" en la precisión del usuario (clase sin píxeles clasificados).
FILA = re.compile(r"^\s*([A-Za-z][A-Za-z/ .&-]*?)\s+(\d+)\s+([\d,]+)\s+([\d.]+)%\s+([\d.]+)%\s+([\d.]+|n/a)"
                  r"\s+(?:([\d.]+)%|n/a)\s+(?:([\d.]+)%|n/a)")


def de_html(st, anio, d):
    ruta = base.bajar(base.URL_HTML.format(st=st.lower(), aa=anio % 100),
                      d / f"metadata-{st.lower()}{anio % 100:02d}.html")
    filas, glob = {}, None
    for l in base.texto_html(ruta):
        m = base.GLOBAL.match(l)
        if m and glob is None:
            glob = (float(m.group(3)), float(m.group(5)))
            continue
        m = FILA.match(l)
        if m and int(m.group(2)) in base.CULTIVOS and int(m.group(2)) not in filas:
            usu = float(m.group(7)) if m.group(7) else None
            filas[int(m.group(2))] = (int(m.group(3).replace(",", "")), float(m.group(4)), usu)
    return glob, filas


def _pct(v):
    return round(v * 100, 1) if isinstance(v, (int, float)) else None


def de_xlsx(st, anio, d):
    """Como `base.de_xlsx`, pero deja vacía la precisión cuando la celda es texto (p. ej. "n/a")."""
    import openpyxl
    z = base.bajar(base.URL_ZIP.format(anio=anio), d / f"CDL_{anio}_accuracy_assessments.zip")
    nombre = f"NASS_CDL_{st}{anio % 100:02d}_accuracy.xlsx"
    with zipfile.ZipFile(z) as zf:
        miembro = next(n for n in zf.namelist() if n.endswith(nombre))
        zf.extract(miembro, d)
    wb = openpyxl.load_workbook(d / miembro, read_only=True, data_only=True)
    filas, glob = {}, None
    for r in wb["Summary Table"].iter_rows(values_only=True):
        if r[0] == "FSA Crops":
            glob = (_pct(r[4]), round(r[6], 3))
        elif isinstance(r[1], int) and r[1] in base.CULTIVOS and r[1] not in filas:
            filas[r[1]] = (r[2], _pct(r[4]), _pct(r[8]))
    return glob, filas


def main():
    d = Path(sys.argv[1])
    d.mkdir(parents=True, exist_ok=True)
    base.bajar(URL_WI13, d / "metadata-wi13.html")
    salida = []
    for anio in list(base.ANIOS_HTML) + base.ANIOS_XLSX:
        for st in base.ESTADOS:
            glob, filas = (de_html if anio < 2024 else de_xlsx)(st, anio, d)
            for cod, cultivo in base.CULTIVOS.items():
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
