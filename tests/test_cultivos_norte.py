"""Pruebas sin red de T147: cultivos del norte (maíz para silo, trigo de primavera, durum, cebada, girasol,
canola y frijol seco) en conversiones, produccion_anual.csv, GRUPOS_CDL y validar_csv."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.common import validacion  # noqa: E402
from src.common.config import VAR_ESTADOS, cargar_config  # noqa: E402
from src.common.conversiones import bu_ac_a_kgha, rend_a_kgha  # noqa: E402
from src.common.validacion import validar_csv  # noqa: E402
from src.cultivos import process as proc  # noqa: E402

NUEVOS = ["maiz_silo", "trigo_primavera", "trigo_durum", "cebada", "girasol", "canola", "frijol_seco"]
VIEJOS = ["maiz", "soja", "trigo_invierno", "avena", "alfalfa", "heno"]


@pytest.fixture(autouse=True)
def config_limpia(monkeypatch):
    monkeypatch.delenv(VAR_ESTADOS, raising=False)
    cargar_config.cache_clear()
    yield
    cargar_config.cache_clear()


# ---------------------------------------------------------------- config y conversiones

def test_config_tiene_los_cultivos_en_orden():
    assert list(cargar_config()["cultivos"]) == VIEJOS + NUEVOS
    assert set(proc.NASS_CULTIVOS) == set(VIEJOS + NUEVOS)
    assert set(proc.UNIDADES) == set(VIEJOS + NUEVOS)


@pytest.mark.parametrize("cultivo, unidad, factor", [
    ("maiz", "BU / ACRE", 62.77), ("soja", "BU / ACRE", 67.25),
    ("trigo_primavera", "BU / ACRE", 67.25), ("trigo_durum", "BU / ACRE", 67.25), ("cebada", "BU / ACRE", 53.80),
    ("girasol", "LB / ACRE", 1.12085), ("canola", "LB / ACRE", 1.12085), ("frijol_seco", "LB / ACRE", 1.12085),
    ("maiz_silo", "TONS / ACRE", 2241.7),
])
def test_rend_a_kgha(cultivo, unidad, factor):
    assert rend_a_kgha(cultivo, unidad) == pytest.approx(factor)


def test_rend_a_kgha_coincide_con_bu_ac_a_kgha_y_con_ah697():
    for c in ("maiz", "soja", "trigo_invierno", "avena"):
        assert rend_a_kgha(c, "BU / ACRE") == bu_ac_a_kgha(c)
    # AH-697: 1 lb/ac = 1,12085 kg/ha; bushel de cebada 48 lb, de trigo 60 lb; tonelada corta 2.000 lb
    assert rend_a_kgha("cebada", "BU / ACRE") == pytest.approx(48 * 1.12085, abs=0.01)
    assert rend_a_kgha("trigo_primavera", "BU / ACRE") == pytest.approx(60 * 1.12085, abs=0.01)
    assert rend_a_kgha("maiz_silo", "TONS / ACRE") == pytest.approx(2000 * 1.12085, abs=0.1)


def test_rend_a_kgha_unidad_desconocida():
    with pytest.raises(KeyError):
        rend_a_kgha("maiz", "CWT / ACRE")


# ---------------------------------------------------------------- produccion()

def _fila(com, clase, util, stat, unidad, valor, anio="2020", cond="053", estado="27"):
    return {"SOURCE_DESC": "SURVEY", "COMMODITY_DESC": com, "CLASS_DESC": clase,
            "PRODN_PRACTICE_DESC": "ALL PRODUCTION PRACTICES", "UTIL_PRACTICE_DESC": util,
            "STATISTICCAT_DESC": stat, "UNIT_DESC": unidad, "SHORT_DESC": "", "DOMAIN_DESC": "TOTAL",
            "AGG_LEVEL_DESC": "COUNTY", "STATE_FIPS_CODE": estado, "STATE_ALPHA": "MN",
            "COUNTY_CODE": cond, "YEAR": anio, "FREQ_DESC": "ANNUAL", "REFERENCE_PERIOD_DESC": "YEAR",
            "WEEK_ENDING": "", "VALUE": valor}


@pytest.fixture
def repo_cultivos(tmp_path, monkeypatch):
    ref = tmp_path / "data" / "reference"
    ref.mkdir(parents=True)
    (ref / "condados.csv").write_text("fips,estado,condado,lat_centroide,lon_centroide,area_km2\n"
                                      "27053,MN,Hennepin,45.0,-93.48,1571.3\n", encoding="utf-8")
    monkeypatch.setattr(proc, "REPO", tmp_path)
    monkeypatch.setattr(validacion, "REPO", tmp_path)
    return tmp_path


AU = "ALL UTILIZATION PRACTICES"
CROPS = [
    # maíz grano: igual que antes de T147
    _fila("CORN", "ALL CLASSES", AU, "AREA PLANTED", "ACRES", "1,000"),
    _fila("CORN", "ALL CLASSES", "GRAIN", "AREA HARVESTED", "ACRES", "900"),
    _fila("CORN", "ALL CLASSES", "GRAIN", "YIELD", "BU / ACRE", "180"),
    _fila("CORN", "ALL CLASSES", "GRAIN", "PRODUCTION", "BU", "162,000"),
    # maíz para silo: la sembrada de CORN (todos los usos) no se le asigna
    _fila("CORN", "ALL CLASSES", "SILAGE", "AREA HARVESTED", "ACRES", "50"),
    _fila("CORN", "ALL CLASSES", "SILAGE", "YIELD", "TONS / ACRE", "20.0"),
    _fila("CORN", "ALL CLASSES", "SILAGE", "PRODUCTION", "TONS", "1,000"),
    # heno: NASS lo da en TONS, pero el esquema de antes no lo incluía y sigue sin incluirlo
    _fila("HAY", "(EXCL ALFALFA)", AU, "AREA HARVESTED", "ACRES", "300"),
    _fila("HAY", "(EXCL ALFALFA)", AU, "YIELD", "TONS / ACRE", "2.1"),
    # trigo de primavera y cebada en bu/ac
    _fila("WHEAT", "SPRING, (EXCL DURUM)", AU, "AREA PLANTED", "ACRES", "400"),
    _fila("WHEAT", "SPRING, (EXCL DURUM)", AU, "YIELD", "BU / ACRE", "60"),
    _fila("BARLEY", "ALL CLASSES", AU, "YIELD", "BU / ACRE", "(D)"),
    # canola en lb/ac
    _fila("CANOLA", "ALL CLASSES", AU, "YIELD", "LB / ACRE", "2,000"),
    _fila("CANOLA", "ALL CLASSES", AU, "PRODUCTION", "LB", "400,000"),
    # frijol: clase vieja (2018) y nueva (2020; si están las dos gana la nueva)
    _fila("BEANS", "DRY EDIBLE, INCL CHICKPEAS", AU, "YIELD", "LB / ACRE", "1,900", anio="2018"),
    _fila("BEANS", "DRY EDIBLE, INCL CHICKPEAS", AU, "YIELD", "LB / ACRE", "1,111"),
    _fila("BEANS", "DRY EDIBLE, (EXCL CHICKPEAS)", AU, "YIELD", "LB / ACRE", "2,100"),
    _fila("BEANS", "DRY EDIBLE, (EXCL CHICKPEAS)", AU, "PRODUCTION", "CWT", "5,000"),
    # condado combinado 998: afuera
    _fila("CANOLA", "ALL CLASSES", AU, "YIELD", "LB / ACRE", "1,500", cond="998"),
]


def test_produccion_cultivos_nuevos(repo_cultivos):
    df = proc.produccion(pd.DataFrame(CROPS))
    assert list(df.columns[:11]) == ["fips", "anio", "cultivo", "sup_sembrada_ac", "sup_cosechada_ac",
                                     "produccion_bu", "rend_bu_ac", "rend_kgha", "sup_sembrada_ha",
                                     "ratio_cosechada", "flag_nass"]
    assert list(df.columns[11:]) == ["rend_lb_ac", "produccion_lb", "produccion_cwt", "rend_ton_ac",
                                     "produccion_ton"]
    f = df.set_index(["anio", "cultivo"])

    maiz = f.loc[(2020, "maiz")]
    assert maiz["rend_bu_ac"] == 180 and maiz["rend_kgha"] == pytest.approx(round(180 * 62.77, 1))
    assert maiz["sup_sembrada_ac"] == 1000 and maiz["ratio_cosechada"] == pytest.approx(0.9)
    assert pd.isna(maiz["rend_ton_ac"]) and pd.isna(maiz["rend_lb_ac"])

    silo = f.loc[(2020, "maiz_silo")]
    assert pd.isna(silo["sup_sembrada_ac"]) and pd.isna(silo["ratio_cosechada"])
    assert silo["rend_ton_ac"] == 20 and silo["produccion_ton"] == 1000
    assert silo["rend_kgha"] == pytest.approx(round(20 * 2241.7, 1))
    assert pd.isna(silo["rend_bu_ac"]) and pd.isna(silo["produccion_bu"])

    heno = f.loc[(2020, "heno")]
    assert heno["sup_cosechada_ac"] == 300
    assert pd.isna(heno["rend_ton_ac"]) and pd.isna(heno["rend_kgha"])

    tp = f.loc[(2020, "trigo_primavera")]
    assert tp["rend_kgha"] == pytest.approx(round(60 * 67.25, 1))

    ceb = f.loc[(2020, "cebada")]
    assert pd.isna(ceb["rend_bu_ac"]) and ceb["flag_nass"] == "(D)"

    can = f.loc[(2020, "canola")]
    assert can["rend_lb_ac"] == 2000 and can["produccion_lb"] == 400000
    assert can["rend_kgha"] == pytest.approx(round(2000 * 1.12085, 1))

    assert f.loc[(2020, "frijol_seco"), "rend_lb_ac"] == 2100
    assert f.loc[(2020, "frijol_seco"), "produccion_cwt"] == 5000
    assert f.loc[(2018, "frijol_seco"), "rend_lb_ac"] == 1900
    assert (df["fips"] == "27053").all()


def test_produccion_valida(repo_cultivos, tmp_path):
    p = tmp_path / "produccion_anual.csv"
    proc.produccion(pd.DataFrame(CROPS)).to_csv(p, index=False)
    assert validar_csv(p) == []


# ---------------------------------------------------------------- CDL

def test_grupos_cdl_nuevos():
    g = proc.GRUPOS_CDL
    assert {6: "girasol", 21: "cebada", 22: "trigo_durum", 23: "trigo_primavera", 31: "canola",
            42: "frijol_seco"}.items() <= g.items()
    # los de antes no cambian
    assert {1: "maiz", 5: "soja", 24: "trigo_invierno", 26: "doble_trigo_soja", 28: "avena", 36: "alfalfa",
            37: "heno", 61: "barbecho", 176: "pastizal"}.items() <= g.items()
    assert proc.PCT_CLASES["pct_trigo"] == [24, 26]
    for cls in proc.PCT_CLASES_NORTE.values():
        assert set(cls) <= set(proc.AGRICOLA)  # la máscara agrícola no cambia


# ---------------------------------------------------------------- validar_csv: rangos por cultivo

@pytest.mark.parametrize("col, cultivo, rend", [
    ("rend_bu_ac", "trigo_primavera", "150"), ("rend_bu_ac", "cebada", "1"),
    ("rend_lb_ac", "canola", "9000"), ("rend_lb_ac", "girasol", "10"),
    ("rend_ton_ac", "maiz_silo", "60"),
])
def test_validar_csv_rendimiento_nuevos_fuera_de_rango(repo_cultivos, tmp_path, col, cultivo, rend):
    p = tmp_path / "x_anual.csv"
    p.write_text(f"fips,anio,cultivo,{col}\n27053,2022,{cultivo},{rend}\n", encoding="utf-8")
    errores = validar_csv(p)
    assert any(col in e and cultivo in e for e in errores), errores
