"""Alias por compatibilidad: el módulo se mudó a `src/common/zona_texto.py` (T143).

Los scripts viejos que hacen `from src.zona_texto import ...` siguen andando; el código nuevo importa de
`src.common.zona_texto`.
"""
from src.common.zona_texto import lista_estados, n_condados, n_estados, unir  # noqa: F401

__all__ = ["unir", "lista_estados", "n_estados", "n_condados"]
