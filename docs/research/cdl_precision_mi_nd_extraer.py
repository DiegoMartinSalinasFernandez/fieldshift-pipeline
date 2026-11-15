"""Precisión del CDL en MI y ND, 2008–2025 (research T068).

Reutiliza `cdl_precision_mo_wi_sd_extraer.py` (T064) con otros estados y más clases: trigo de
primavera (23), girasol (6) y canola (31). No es parte del pipeline. Arma
`docs/research/cdl_precision_mi_nd.csv`.

Uso:
    python -X utf8 docs/research/cdl_precision_mi_nd_extraer.py <dir_trabajo>
`<dir_trabajo>` fuera del repo: ahí se bajan los HTML (~110 kB c/u) y los zip de 2024–2025 (~75 MB c/u).
"""
import csv
import importlib.util
import sys
import urllib.error
from pathlib import Path

_spec = importlib.util.spec_from_file_location("t064", Path(__file__).with_name("cdl_precision_mo_wi_sd_extraer.py"))
t064 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(t064)
base = t064.base

base.ESTADOS = ["MI", "ND"]
base.CULTIVOS = {1: "maiz", 5: "soja", 6: "girasol", 23: "trigo_primavera", 24: "trigo_invierno",
                 26: "doble_trigo_soja", 28: "avena", 31: "canola", 36: "alfalfa", 37: "otro_heno",
                 61: "barbecho", 62: "pastura_pasto", 176: "pastizal_pastura"}
# Si la ruta de siempre da 404, se prueba la que usa WI 2013 (ver T064).
URL_ALT = ("https://www.nass.usda.gov/sites/default/files/Research_and_Science/Cropland/metadata/"
           "metadata_{st}{aa:02d}.htm")
SALIDA = Path(__file__).with_name("cdl_precision_mi_nd.csv")


def asegurar_html(st, anio, d):
    destino = d / f"metadata-{st.lower()}{anio % 100:02d}.html"
    try:
        base.bajar(base.URL_HTML.format(st=st.lower(), aa=anio % 100), destino)
    except urllib.error.HTTPError as e:
        print(f"{st} {anio}: {e.code} en la ruta de siempre; pruebo la alternativa")
        base.bajar(URL_ALT.format(st=st.lower(), aa=anio % 100), destino)


def main():
    d = Path(sys.argv[1])
    d.mkdir(parents=True, exist_ok=True)
    salida = []
    for anio in list(base.ANIOS_HTML) + base.ANIOS_XLSX:
        for st in base.ESTADOS:
            if anio < 2024:
                asegurar_html(st, anio, d)
            glob, filas = (t064.de_html if anio < 2024 else t064.de_xlsx)(st, anio, d)
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
