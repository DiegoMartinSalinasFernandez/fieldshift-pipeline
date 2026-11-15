"""Pruebas de src/common/ (conversiones, fechas y ventanas, validar_csv, cargar_config).

Usan datos chicos inventados solo para la prueba (condados y CSV falsos en una carpeta temporal);
no leen ni escriben data/ del repo.

Correr desde la raíz:  .venv/bin/python -X utf8 -m pytest tests/test_common.py
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.common import config as cfg_mod  # noqa: E402
from src.common import validacion  # noqa: E402
from src.common.config import VAR_ESTADOS, cargar_config, estados_config  # noqa: E402
from src.common.conversiones import acres_a_ha, bu_ac_a_kgha  # noqa: E402
from src.common.fechas import fecha_a_anio  # noqa: E402
from src.common.validacion import validar_csv  # noqa: E402


@pytest.fixture(autouse=True)
def config_limpia(monkeypatch):
    """Cada prueba arranca sin FIELDSHIFT_ESTADOS y sin la config cacheada (lru_cache)."""
    monkeypatch.delenv(VAR_ESTADOS, raising=False)
    cargar_config.cache_clear()
    yield
    cargar_config.cache_clear()


# ---------------------------------------------------------------- conversiones (CLAUDE.md §4)

@pytest.mark.parametrize("cultivo, factor", [
    ("maiz", 62.77), ("soja", 67.25), ("trigo_invierno", 67.25), ("avena", 35.87),
])
def test_bu_ac_a_kgha(cultivo, factor):
    assert bu_ac_a_kgha(cultivo) == pytest.approx(factor)
    # 180 bu/ac de maíz ≈ 11.299 kg/ha, etc.
    assert 100 * bu_ac_a_kgha(cultivo) == pytest.approx(100 * factor)


def test_bu_ac_a_kgha_cultivo_desconocido():
    with pytest.raises(KeyError):
        bu_ac_a_kgha("alfalfa")


def test_acres_a_ha_escalar_array_y_serie():
    assert acres_a_ha(1) == pytest.approx(0.4047)
    assert acres_a_ha(1000.0) == pytest.approx(404.7)
    np.testing.assert_allclose(acres_a_ha(np.array([0.0, 10.0])), [0.0, 4.047])
    s = acres_a_ha(pd.Series([2.0, 100.0], index=["a", "b"]))
    assert isinstance(s, pd.Series)
    assert list(s.index) == ["a", "b"]
    np.testing.assert_allclose(s.to_numpy(), [0.8094, 40.47])


def test_acres_a_ha_respeta_faltantes():
    s = acres_a_ha(pd.Series([1.0, np.nan]))
    assert np.isnan(s.iloc[1])


# ---------------------------------------------------------------- fechas

@pytest.mark.parametrize("fecha, anio", [
    ("2023-07-15", 2023),
    ("2023-07", 2023),
    (" 2023-12-31 ", 2023),
    ("2000-01-01", 2000),
    (dt.date(2021, 3, 31), 2021),
    (dt.datetime(2019, 11, 1, 12, 30), 2019),
    (pd.Timestamp("2024-02-29"), 2024),
])
def test_fecha_a_anio(fecha, anio):
    r = fecha_a_anio(fecha)
    assert r == anio
    assert isinstance(r, int)


def test_fecha_a_anio_es_anio_calendario_no_de_cosecha():
    # §4: en archivos diarios/mensuales `anio` es el año calendario de la fecha, aunque diciembre
    # pertenezca al invierno previo de la cosecha siguiente.
    assert fecha_a_anio("2022-12-15") == 2022


def test_fecha_a_anio_invalida():
    with pytest.raises(ValueError):
        fecha_a_anio("no-es-fecha")


# ---------------------------------------------------------------- ventanas de anios.csv

def test_ventanas_config():
    v = cargar_config()["ventanas"]
    assert v["temporada"] == {"desde": "04-01", "hasta": "09-30"}
    assert v["invierno_previo"] == {"desde": "11-01", "hasta": "03-31"}
    assert v["meses_criticos"] == {"julio": 7, "agosto": 8}


def test_anios_csv(tmp_path, monkeypatch):
    """src/base/process.py:anios() arma anios.csv con las ventanas de config.yaml."""
    pytest.importorskip("geopandas")
    from src.base import process as base

    monkeypatch.setattr(base, "REF", tmp_path)
    base.anios()
    df = pd.read_csv(tmp_path / "anios.csv", dtype=str)
    assert list(df.columns) == ["anio", "inicio_temporada", "fin_temporada",
                                "inicio_invierno_previo", "fin_invierno_previo"]
    per = cargar_config()["periodo"]
    assert df["anio"].astype(int).tolist() == list(range(per["anio_inicio"], per["anio_fin"] + 1))
    fila = df.set_index("anio").loc["2023"]
    assert fila["inicio_temporada"] == "2023-04-01"
    assert fila["fin_temporada"] == "2023-09-30"
    assert fila["inicio_invierno_previo"] == "2022-11-01"   # noviembre del año anterior
    assert fila["fin_invierno_previo"] == "2023-03-31"
    # Todas las fechas son válidas y cada ventana empieza antes de terminar.
    for c in df.columns[1:]:
        pd.to_datetime(df[c], format="%Y-%m-%d")
    assert (pd.to_datetime(df["inicio_temporada"]) < pd.to_datetime(df["fin_temporada"])).all()
    assert (pd.to_datetime(df["inicio_invierno_previo"]) < pd.to_datetime(df["fin_invierno_previo"])).all()
    # El invierno previo termina antes de que arranque la temporada del mismo año.
    assert (pd.to_datetime(df["fin_invierno_previo"]) < pd.to_datetime(df["inicio_temporada"])).all()
    # fecha_a_anio de las puntas: el invierno previo cruza el año.
    assert fecha_a_anio(fila["inicio_invierno_previo"]) == 2022
    assert fecha_a_anio(fila["fin_invierno_previo"]) == 2023


# ---------------------------------------------------------------- validar_csv

CONDADOS = "fips,estado,condado,lat_centroide,lon_centroide,area_km2\n" \
           "39049,OH,Franklin,39.97,-83.01,1408.5\n" \
           "27053,MN,Hennepin,45.0,-93.48,1571.3\n"


@pytest.fixture
def repo_falso(tmp_path, monkeypatch):
    """validar_csv() lee condados.csv desde REPO/data/reference: apuntamos REPO a un repo falso."""
    ref = tmp_path / "data" / "reference"
    ref.mkdir(parents=True)
    (ref / "condados.csv").write_text(CONDADOS, encoding="utf-8")
    monkeypatch.setattr(validacion, "REPO", tmp_path)
    return tmp_path


def _csv(tmp_path: Path, texto: str, nombre: str = "x_anual.csv") -> Path:
    p = tmp_path / nombre
    p.write_text(texto, encoding="utf-8")
    return p


def test_validar_csv_correcto_anual(repo_falso):
    p = _csv(repo_falso, "fips,anio,prec_temporada_mm,ndvi,pct_maiz\n"
                         "39049,2022,510.2,0.71,40\n"
                         "39049,2023,,0.65,38.5\n"
                         "27053,2022,480,,\n")
    assert validar_csv(p) == []


def test_validar_csv_correcto_largo_con_cultivo(repo_falso):
    p = _csv(repo_falso, "fips,anio,cultivo,rend_bu_ac,sup_sembrada_ac,flag_nass\n"
                         "39049,2022,maiz,180.5,120000,\n"
                         "39049,2022,soja,55,90000,\n"
                         "27053,2022,maiz,,,(D)\n")
    assert validar_csv(p) == []


def test_validar_csv_correcto_mensual_y_diario(repo_falso):
    m = _csv(repo_falso, "fips,anio,mes,tmax_c\n39049,2023,2023-07,30.1\n39049,2023,2023-08,29.4\n",
             "x_mensual.csv")
    d = _csv(repo_falso, "fips,anio,fecha,tmax_c\n39049,2023,2023-07-15,31\n27053,2023,2023-07-15,28\n",
             "x_diario.csv")
    assert validar_csv(m) == []
    assert validar_csv(d) == []


def test_validar_csv_claves_duplicadas(repo_falso):
    p = _csv(repo_falso, "fips,anio,prec_temporada_mm\n"
                         "39049,2022,500\n"
                         "39049,2022,501\n")
    errores = validar_csv(p)
    assert any("duplicadas" in e for e in errores), errores


def test_validar_csv_misma_clave_distinto_cultivo_no_es_duplicado(repo_falso):
    p = _csv(repo_falso, "fips,anio,cultivo,rend_bu_ac\n39049,2022,maiz,180\n39049,2022,soja,55\n")
    assert not any("duplicadas" in e for e in validar_csv(p))


def test_validar_csv_fips_inexistente(repo_falso):
    p = _csv(repo_falso, "fips,anio,prec_temporada_mm\n39049,2022,500\n19169,2022,600\n")
    errores = validar_csv(p)
    assert any("condados.csv" in e and "19169" in e for e in errores), errores


def test_validar_csv_fips_sin_ceros(repo_falso):
    p = _csv(repo_falso, "fips,anio,x\n1001,2022,1\n")
    errores = validar_csv(p)
    assert any("5 dígitos" in e for e in errores), errores


def test_validar_csv_sin_condados_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(validacion, "REPO", tmp_path)
    p = _csv(tmp_path, "fips,anio,x\n39049,2022,1\n")
    assert any("no existe data/reference/condados.csv" in e for e in validar_csv(p))


@pytest.mark.parametrize("col, valor", [
    ("prec_temporada_mm", "-3"),
    ("ndvi", "1.2"),
    ("sm_rootzone_m3m3", "0.7"),
    ("pct_maiz", "101"),
    ("dias_tmax_gt35", "400"),
    ("frac_pixeles_validos", "1.5"),
])
def test_validar_csv_fuera_de_rango(repo_falso, col, valor):
    p = _csv(repo_falso, f"fips,anio,{col}\n39049,2022,{valor}\n")
    errores = validar_csv(p)
    assert any(col in e and "rango" in e for e in errores), errores


@pytest.mark.parametrize("cultivo, rend", [("maiz", "15"), ("maiz", "310"), ("soja", "4"), ("soja", "101")])
def test_validar_csv_rendimiento_fuera_de_rango(repo_falso, cultivo, rend):
    p = _csv(repo_falso, f"fips,anio,cultivo,rend_bu_ac\n39049,2022,{cultivo},{rend}\n")
    errores = validar_csv(p)
    assert any("rend_bu_ac" in e and cultivo in e for e in errores), errores


@pytest.mark.parametrize("valor", ["-999", "-9999"])
def test_validar_csv_relleno(repo_falso, valor):
    p = _csv(repo_falso, f"fips,anio,tmax_c\n39049,2022,{valor}\n")
    assert any("relleno" in e for e in validar_csv(p))


def test_validar_csv_decimal_con_coma(repo_falso):
    p = _csv(repo_falso, 'fips,anio,tmax_c\n39049,2022,"30,5"\n')
    assert any("coma" in e for e in validar_csv(p))


def test_validar_csv_claves_no_primeras(repo_falso):
    p = _csv(repo_falso, "anio,fips,x\n2022,39049,1\n")
    assert any("primeras columnas" in e for e in validar_csv(p))


def test_validar_csv_anio_no_coincide_con_fecha(repo_falso):
    p = _csv(repo_falso, "fips,anio,fecha,x\n39049,2022,2023-01-05,1\n", "x_diario.csv")
    assert any("anio no coincide" in e for e in validar_csv(p))


def test_validar_csv_fips_estado(repo_falso, monkeypatch):
    monkeypatch.setenv(VAR_ESTADOS, "OH,MN")
    bien = _csv(repo_falso, "fips_estado,anio,cultivo,doy_50_sembrado\n39,2023,maiz,130\n27,2023,maiz,135\n",
                "fenologia_estado.csv")
    assert validar_csv(bien) == []
    mal = _csv(repo_falso, "fips_estado,anio,cultivo,doy_50_sembrado\n19,2023,maiz,128\n", "otro.csv")
    assert any("fips_estado" in e for e in validar_csv(mal))


# ---------------------------------------------------------------- cargar_config y FIELDSHIFT_ESTADOS

def test_cargar_config_sin_variable_trae_todos():
    estados = cargar_config()["zona"]["estados"]
    assert set(estados) == {"IA", "IL", "IN", "OH", "NE", "MN", "KS"}


def test_cargar_config_filtra(monkeypatch):
    monkeypatch.setenv(VAR_ESTADOS, " oh , MN ")
    estados = cargar_config()["zona"]["estados"]
    assert list(estados) == ["OH", "MN"]
    assert estados["OH"]["fips"] == "39"
    ec = estados_config()
    assert {k: v["fips"] for k, v in ec.items()} == {"OH": "39", "MN": "27"}


def test_cargar_config_un_estado(monkeypatch):
    monkeypatch.setenv(VAR_ESTADOS, "KS")
    assert list(cargar_config()["zona"]["estados"]) == ["KS"]


def test_cargar_config_variable_vacia_trae_todos(monkeypatch):
    monkeypatch.setenv(VAR_ESTADOS, " , ")
    assert len(cargar_config()["zona"]["estados"]) == 7


def test_cargar_config_estado_desconocido(monkeypatch):
    monkeypatch.setenv(VAR_ESTADOS, "OH,TX")
    with pytest.raises(ValueError, match="TX"):
        cargar_config()


def test_cargar_config_cache_ignora_cambio_de_variable(monkeypatch):
    """cargar_config() está cacheada: cambiar FIELDSHIFT_ESTADOS en el mismo proceso no la recarga.

    No es un error para los scripts (leen la variable una sola vez), pero quien cambie la variable
    en un mismo proceso (pruebas, notebooks) tiene que llamar a cargar_config.cache_clear().
    """
    monkeypatch.setenv(VAR_ESTADOS, "OH")
    assert list(cargar_config()["zona"]["estados"]) == ["OH"]
    monkeypatch.setenv(VAR_ESTADOS, "MN")
    assert list(cargar_config()["zona"]["estados"]) == ["OH"]
    cargar_config.cache_clear()
    assert list(cargar_config()["zona"]["estados"]) == ["MN"]


def test_ruta_config_es_del_repo():
    assert cfg_mod.CONFIG == REPO / "config" / "config.yaml"
