"""Precisión del CDL en KY, 2008–2025 (research T078).

Reutiliza `cdl_precision_mi_nd_extraer.py` (T068), que a su vez reusa los de T064 y T024, con otro
estado y otras clases: agrega tabaco (11) y saca girasol, trigo de primavera y canola. No es parte del
pipeline. Arma `docs/research/cdl_precision_ky.csv`.

Uso:
    python -X utf8 docs/research/cdl_precision_ky_extraer.py <dir_trabajo>
`<dir_trabajo>` fuera del repo: ahí se bajan los HTML (~110 kB c/u) y los zip de 2024–2025 (~75 MB c/u).
Necesita `openpyxl` para 2024–2025.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("t068", Path(__file__).with_name("cdl_precision_mi_nd_extraer.py"))
t068 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(t068)

t068.base.ESTADOS = ["KY"]
t068.base.CULTIVOS = {1: "maiz", 5: "soja", 11: "tabaco", 24: "trigo_invierno", 26: "doble_trigo_soja",
                      28: "avena", 36: "alfalfa", 37: "otro_heno", 61: "barbecho", 62: "pastura_pasto",
                      176: "pastizal_pastura"}
t068.SALIDA = Path(__file__).with_name("cdl_precision_ky.csv")

if __name__ == "__main__":
    t068.main()
