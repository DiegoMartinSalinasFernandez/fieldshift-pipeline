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


# UNIT_DESC del rendimiento de NASS -> columna del valor original en produccion_anual.csv
COLUMNA_RENDIMIENTO = {"BU / ACRE": "rend_bu_ac", "LB / ACRE": "rend_lb_ac", "TONS / ACRE": "rend_ton_ac"}


def rend_a_kgha(cultivo: str, unidad_nass: str) -> float:
    """Factor del rendimiento de NASS -> kg/ha según su UNIT_DESC (AH-697 del USDA ERS).

    BU / ACRE   -> bu_ac_a_kgha(cultivo) (peso del bushel de cada cultivo)
    LB / ACRE   -> lb_ac_a_kgha (girasol, canola, frijol seco)
    TONS / ACRE -> ton_ac_a_tha × 1000 (maíz para silo: tonelada corta, peso húmedo)

    Uso: rend_kgha = rend_lb_ac * rend_a_kgha("canola", "LB / ACRE").
    """
    conv = cargar_config()["conversiones"]
    if unidad_nass == "BU / ACRE":
        return bu_ac_a_kgha(cultivo)
    if unidad_nass == "LB / ACRE":
        return float(conv["lb_ac_a_kgha"])
    if unidad_nass == "TONS / ACRE":
        return float(conv["ton_ac_a_tha"]) * 1000
    raise KeyError(f"sin factor a kg/ha para la unidad '{unidad_nass}' ({cultivo})")
