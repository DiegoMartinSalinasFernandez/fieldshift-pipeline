"""Conversiones de unidades de EE.UU. Los factores salen de config/config.yaml."""
from __future__ import annotations

from src.common.config import cargar_config


def bu_ac_a_kgha(cultivo: str) -> float:
    """Factor bu/ac -> kg/ha del cultivo (código de config.yaml: maiz, soja, trigo_invierno, avena).

    Uso: rend_kgha = rend_bu_ac * bu_ac_a_kgha("maiz").
    """
    factores = cargar_config()["conversiones"]["bu_ac_a_kgha"]
    if cultivo not in factores:
        raise KeyError(f"sin factor bu/ac -> kg/ha para '{cultivo}' en config.yaml")
    return float(factores[cultivo])


def acres_a_ha(acres):
    """Acres -> hectáreas (acepta escalares, arrays o Series)."""
    return acres * float(cargar_config()["conversiones"]["acre_a_ha"])
