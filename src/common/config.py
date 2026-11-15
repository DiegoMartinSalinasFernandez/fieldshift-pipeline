"""Lectura de config/config.yaml (los valores no se escriben fijos en el código).

Cada máquina trabaja solo con sus estados: si la variable de entorno FIELDSHIFT_ESTADOS está
definida (por ejemplo "KS" o "OH,NE,MN"), `zona.estados` se filtra a esos estados. Sin la variable
se usan todos los estados de config.yaml. Así todos los scripts bajan y procesan solo lo de la
máquina, sin tocar config.yaml (ver MAQUINAS.md).
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
CONFIG = REPO / "config" / "config.yaml"
VAR_ESTADOS = "FIELDSHIFT_ESTADOS"


def estados_elegidos() -> list[str] | None:
    """Estados de FIELDSHIFT_ESTADOS (códigos de 2 letras), o None si no está definida."""
    v = os.environ.get(VAR_ESTADOS, "").strip()
    return [s.strip().upper() for s in v.split(",") if s.strip()] or None


def cargar_config() -> dict:
    """config.yaml con `zona.estados` filtrado por FIELDSHIFT_ESTADOS.

    La caché usa los estados elegidos como clave: si la variable cambia dentro del mismo proceso
    (un notebook, una prueba), la configuración se recarga sola. `cargar_config.cache_clear()`
    sigue sirviendo para forzar una relectura de config.yaml.
    """
    elegidos = estados_elegidos()
    return _cargar_config(tuple(elegidos) if elegidos else None)


@lru_cache(maxsize=8)
def _cargar_config(elegidos: tuple[str, ...] | None) -> dict:
    with open(CONFIG, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if elegidos:
        todos = cfg["zona"]["estados"]
        faltan = [s for s in elegidos if s not in todos]
        if faltan:
            raise ValueError(f"{VAR_ESTADOS}: estados que no están en config.yaml: {faltan}")
        cfg["zona"]["estados"] = {s: todos[s] for s in elegidos}
    return cfg


cargar_config.cache_clear = _cargar_config.cache_clear  # type: ignore[attr-defined]


def estados_config() -> dict:
    """{alfa: {fips, nombre, condados}} con fips como texto de 2 dígitos."""
    estados = cargar_config()["zona"]["estados"]
    return {alfa: {**e, "fips": str(e["fips"]).zfill(2)} for alfa, e in estados.items()}
