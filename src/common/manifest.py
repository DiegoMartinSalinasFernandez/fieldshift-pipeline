"""manifest.csv: una fila por archivo bajado (CLAUDE.md §7).

Antes cada `download.py` tenía su copia de `asegurar_manifest()` (T021); desde T143 está solo acá.
"""
from __future__ import annotations

from pathlib import Path

CAMPOS_MANIFEST = ["paquete", "archivo", "fuente", "producto", "version", "fecha_descarga", "consulta_o_url"]


def asegurar_manifest(man: Path) -> None:
    """En una máquina nueva no hay manifest.csv (no va en git): lo crea con el encabezado (CLAUDE.md §7)."""
    man = Path(man)
    if not man.exists() or man.stat().st_size == 0:
        man.write_text(",".join(CAMPOS_MANIFEST) + "\n", encoding="utf-8")
