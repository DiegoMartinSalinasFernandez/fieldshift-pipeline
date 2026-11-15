"""Rendimiento por estado de NASS en MI y ND para los eventos extremos (tarea T069).

Reutiliza `eventos_extremos_rend_estado.py` (T031) cambiando la lista de estados y sumando el trigo de primavera
(sin durum), que en ND pesa más que el de invierno. Lee la base completa de Quick Stats
(qs.crops_<fecha>.txt.gz) y escribe por stdout: estado, cultivo, año, rendimiento y media de los 5 años
anteriores. Solo lee; no escribe en data/.

No se corrió en T069: la máquina no tenía la base completa (1,1 GB) y la tarea pide no bajar datasets grandes.
La clase `SPRING, (EXCL DURUM)` es la que usa Quick Stats para el trigo de primavera; si sale vacía, revisar el
CLASS_DESC en el archivo.

Uso: .venv/bin/python -X utf8 docs/research/eventos_extremos_mi_nd_rend.py [ruta_qs_crops] > salida.csv
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eventos_extremos_rend_estado as base  # noqa: E402

base.ESTADOS = {"MI", "ND"}
base.CULTIVOS[("WHEAT", "SPRING, (EXCL DURUM)", "ALL UTILIZATION PRACTICES")] = "trigo_primavera"

if __name__ == "__main__":
    base.main()
