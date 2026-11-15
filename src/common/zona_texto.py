"""Textos de la zona de estudio para data cards y logs, armados desde config.yaml.

Los estados salen de `estados_config()` (config.yaml filtrado por FIELDSHIFT_ESTADOS), así los data
cards dicen los estados que procesó cada máquina en lugar de "IA, IL e IN" escrito fijo.
"""
from __future__ import annotations

from src.common.config import estados_config


def unir(items: list[str]) -> str:
    """["IA", "IL", "IN"] -> "IA, IL e IN" (castellano: "e" antes de palabra que suena /i/)."""
    items = list(items)
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    conj = "e" if items[-1].upper().startswith(("I", "HI")) else "y"
    return f"{', '.join(items[:-1])} {conj} {items[-1]}"


def lista_estados() -> str:
    """Códigos de los estados en uso, por ejemplo "OH y MN"."""
    return unir(list(estados_config()))


def n_estados() -> int:
    return len(estados_config())


def n_condados() -> int:
    """Condados de los estados en uso según config.yaml (clave `condados` de cada estado)."""
    return sum(int(e["condados"]) for e in estados_config().values())
