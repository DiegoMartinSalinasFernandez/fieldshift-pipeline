"""Rendimiento por estado de NASS en MO, WI y SD para los eventos extremos (tarea T065).

Reutiliza `eventos_extremos_rend_estado.py` (T031) cambiando solo la lista de estados. Lee la base completa de
Quick Stats (qs.crops_<fecha>.txt.gz) y escribe por stdout: estado, cultivo, año, rendimiento y media de los 5
años anteriores. Solo lee; no escribe en data/.

Uso: .venv/bin/python -X utf8 docs/research/eventos_extremos_mo_wi_sd_rend.py [ruta_qs_crops] > salida.csv
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eventos_extremos_rend_estado as base  # noqa: E402

base.ESTADOS = {"MO", "WI", "SD"}

if __name__ == "__main__":
    base.main()
