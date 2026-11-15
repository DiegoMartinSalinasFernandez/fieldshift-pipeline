"""Pruebas de validar_csv() con los 7 estados del Corn Belt (tarea T046).

No cambian src/common/: usan un condados.csv inventado de dos estados nuevos (Nebraska y Kansas)
y CSV chicos inventados. Los valores son de prueba, no son datos reales.

Lo que no sirve para los estados nuevos se marca `xfail` (expectedFailure) y se explica en la prueba.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.common import config as cfg_mod  # noqa: E402
from src.common import validacion  # noqa: E402
from src.common.config import VAR_ESTADOS  # noqa: E402
from src.common.validacion import validar_csv  # noqa: E402

# condados.csv inventado: dos condados de Nebraska (31) y dos de Kansas (20).
# Los fips existen; el resto de las columnas son valores de prueba.
CONDADOS_NE_KS = (
    "fips,estado,condado,lat_centroide,lon_centroide,area_km2\n"
    "31109,NE,Lancaster,40.78,-96.69,2190.0\n"
    "31079,NE,Hall,40.87,-98.50,1430.0\n"
    "20055,KS,Finney,38.04,-100.74,3380.0\n"
    "20161,KS,Riley,39.30,-96.73,1610.0\n"
)


def _escribir(p: Path, texto: str) -> Path:
    # Bytes con "\n": el mismo archivo en Windows y en Linux (write_text en Windows pondría "\r\n").
    p.write_bytes(texto.encode("utf-8"))
    return p


@pytest.fixture
def repo_falso(tmp_path, monkeypatch):
    """validar_csv() lee REPO/data/reference/condados.csv: apuntamos REPO a un repo falso.

    También borramos FIELDSHIFT_ESTADOS y la caché de la config, para que la prueba use los
    7 estados de config.yaml sin importar la máquina en la que corre.
    """
    ref = tmp_path / "data" / "reference"
    ref.mkdir(parents=True)
    _escribir(ref / "condados.csv", CONDADOS_NE_KS)
    monkeypatch.setattr(validacion, "REPO", tmp_path)
    monkeypatch.delenv(VAR_ESTADOS, raising=False)
    cfg_mod.cargar_config.cache_clear()
    yield tmp_path
    cfg_mod.cargar_config.cache_clear()


def _csv(carpeta: Path, texto: str, nombre: str = "x_anual.csv") -> Path:
    return _escribir(carpeta / nombre, texto)


def _hay(errores: list[str], texto: str) -> bool:
    return any(texto in e for e in errores)


# ---------------------------------------------------------------- fips de los estados nuevos

def test_acepta_fips_de_nebraska_y_kansas(repo_falso):
    p = _csv(repo_falso, "fips,anio,prec_temporada_mm\n"
                         "31109,2023,410.5\n31079,2023,380.0\n"
                         "20055,2023,250.2\n20161,2023,520.0\n")
    assert validar_csv(p) == []


@pytest.mark.parametrize("fips", ["39049", "27053", "19169", "29019", "55025", "08001"])
def test_rechaza_fips_que_no_estan_en_condados(repo_falso, fips):
    # Ohio y Minnesota (no están en este condados.csv), Iowa, y estados fuera de la zona
    # (Misuri 29, Wisconsin 55, Colorado 08).
    p = _csv(repo_falso, f"fips,anio,prec_temporada_mm\n31109,2023,410.5\n{fips},2023,400.0\n")
    errores = validar_csv(p)
    assert _hay(errores, "no están en condados.csv")
    assert any(fips in e for e in errores)


def test_rechaza_fips_sin_ceros_a_la_izquierda(repo_falso):
    p = _csv(repo_falso, "fips,anio,prec_temporada_mm\n8001,2023,400.0\n")
    assert _hay(validar_csv(p), "5 dígitos")


@pytest.mark.parametrize("fips_estado", ["39", "31", "27", "20", "19", "17", "18"])
def test_fips_estado_acepta_los_7_estados(repo_falso, fips_estado):
    p = _csv(repo_falso, "fips_estado,anio,cultivo,doy_50_sembrado\n"
                         f"{fips_estado},2023,maiz,125\n", "fenologia_estado.csv")
    assert validar_csv(p) == []


@pytest.mark.parametrize("fips_estado", ["08", "48", "06", "40"])   # Colorado, Texas, California, Oklahoma
def test_fips_estado_rechaza_otros_estados(repo_falso, fips_estado):
    p = _csv(repo_falso, "fips_estado,anio,cultivo,doy_50_sembrado\n"
                         f"{fips_estado},2023,maiz,125\n", "fenologia_estado.csv")
    assert _hay(validar_csv(p), "fips_estado fuera de los estados")


def test_fips_estado_respeta_fieldshift_estados(repo_falso, monkeypatch):
    # En la máquina de NE,KS, Ohio queda afuera de la config filtrada.
    monkeypatch.setenv(VAR_ESTADOS, "NE,KS")
    cfg_mod.cargar_config.cache_clear()
    ok = _csv(repo_falso, "fips_estado,anio,cultivo,doy_50_sembrado\n20,2023,maiz,120\n31,2023,maiz,121\n")
    oh = _csv(repo_falso, "fips_estado,anio,cultivo,doy_50_sembrado\n39,2023,maiz,130\n", "oh.csv")
    assert validar_csv(ok) == []
    assert _hay(validar_csv(oh), "fips_estado fuera de los estados")


# ---------------------------------------------------------------- claves duplicadas

def test_claves_duplicadas_anual(repo_falso):
    p = _csv(repo_falso, "fips,anio,prec_temporada_mm\n20055,2023,250.2\n20055,2023,251.0\n")
    assert _hay(validar_csv(p), "1 filas con claves duplicadas")


def test_claves_duplicadas_largo_con_cultivo(repo_falso):
    p = _csv(repo_falso, "fips,anio,cultivo,rend_bu_ac,flag_nass\n"
                         "31079,2023,maiz,190.0,\n31079,2023,soja,60.0,\n31079,2023,maiz,191.0,\n")
    assert _hay(validar_csv(p), "1 filas con claves duplicadas")


def test_mismo_fips_y_anio_con_distinto_cultivo_no_es_duplicado(repo_falso):
    p = _csv(repo_falso, "fips,anio,cultivo,rend_bu_ac,flag_nass\n"
                         "31079,2023,maiz,190.0,\n31079,2023,soja,60.0,\n")
    assert validar_csv(p) == []


def test_claves_duplicadas_mensual(repo_falso):
    p = _csv(repo_falso, "fips,anio,mes,tmax_c\n20161,2023,2023-07,33.1\n20161,2023,2023-07,33.4\n",
             "x_mensual.csv")
    assert _hay(validar_csv(p), "claves duplicadas")


def test_claves_duplicadas_fips_estado(repo_falso):
    p = _csv(repo_falso, "fips_estado,anio,cultivo,doy_50_sembrado\n20,2023,maiz,120\n20,2023,maiz,121\n")
    assert _hay(validar_csv(p), "claves duplicadas")


# ---------------------------------------------------------------- rendimientos en el borde

PROD = "fips,anio,cultivo,rend_bu_ac,flag_nass\n"


@pytest.mark.parametrize("cultivo,rend", [
    ("maiz", "2"), ("maiz", "2.0"), ("maiz", "300"), ("maiz", "300.0"),
    ("soja", "2"), ("soja", "2.0"), ("soja", "100"), ("soja", "100.0"),
    ("trigo_invierno", "5"), ("trigo_invierno", "130.0"), ("avena", "2"), ("avena", "200.0"),
])
def test_rendimiento_en_el_borde_se_acepta(repo_falso, cultivo, rend):
    p = _csv(repo_falso, PROD + f"20055,2023,{cultivo},{rend},\n")
    assert validar_csv(p) == []


@pytest.mark.parametrize("cultivo,rend", [
    ("maiz", "1.9"), ("maiz", "300.1"), ("soja", "1.9"), ("soja", "100.1"),
    ("trigo_invierno", "4.9"), ("trigo_invierno", "130.1"), ("avena", "1.9"), ("avena", "200.1"),
])
def test_rendimiento_fuera_del_borde_se_rechaza(repo_falso, cultivo, rend):
    p = _csv(repo_falso, PROD + f"31109,2023,{cultivo},{rend},\n")
    assert _hay(validar_csv(p), f"rend_bu_ac de {cultivo}: 1 valores fuera")


def test_rendimientos_de_kansas_secano_y_nebraska_riego(repo_falso):
    # Valores inventados del orden esperable: maíz de secano bajo en el oeste de Kansas en un año
    # seco, maíz regado alto en Nebraska. Todos entran en los rangos del CLAUDE.md §7.
    p = _csv(repo_falso, PROD +
             "20055,2012,maiz,35.0,\n20055,2012,soja,8.0,\n"
             "20161,2023,maiz,95.0,\n20161,2023,soja,22.0,\n"
             "31079,2023,maiz,235.0,\n31079,2023,soja,72.0,\n"
             "31109,2023,maiz,180.0,\n31109,2023,soja,58.0,\n")
    assert validar_csv(p) == []


def test_rango_solo_se_aplica_al_cultivo_que_corresponde(repo_falso):
    # 3 bu/ac no es válido para trigo, pero sí para soja; 250 no es válido para soja, sí para maíz.
    p = _csv(repo_falso, PROD + "20055,2023,soja,3.0,\n20055,2023,maiz,250.0,\n")
    assert validar_csv(p) == []
    p = _csv(repo_falso, PROD + "20055,2023,trigo_invierno,3.0,\n")
    assert _hay(validar_csv(p), "rend_bu_ac de trigo_invierno: 1 valores fuera")


# Valores reales de la encuesta NASS por condado (qs.crops_20261114, T145).
@pytest.mark.parametrize("cultivo,rend", [
    ("maiz", "4.5"),             # Pennington SD 2002
    ("soja", "2.9"),             # Pennington SD 2003
    ("trigo_invierno", "8.7"),   # Kimball NE 2022
    ("avena", "5.0"),            # Dundy NE 2000
    ("maiz", "253.6"), ("soja", "80.4"), ("trigo_invierno", "117.8"), ("avena", "133.6"),
])
def test_extremos_reales_de_nass_se_aceptan(repo_falso, cultivo, rend):
    p = _csv(repo_falso, PROD + f"31109,2002,{cultivo},{rend},\n")
    assert validar_csv(p) == []


SIN = "fips,anio,cultivo,sup_cosechada_ac,produccion_bu,rend_bu_ac,flag_nass\n"


def test_rendimiento_cero_sin_cosecha_se_acepta(repo_falso):
    # NASS publica 0 bu/ac en condados de SD sin cosecha de grano (Lawrence 2000-2006).
    p = _csv(repo_falso, SIN + "31109,2003,maiz,,,0,\n31109,2003,avena,0,0,0.0,\n")
    assert validar_csv(p) == []


def test_rendimiento_cero_con_cosecha_se_rechaza(repo_falso):
    p = _csv(repo_falso, SIN + "31109,2003,maiz,1200,,0,\n31109,2003,avena,,500,0,\n")
    errores = validar_csv(p)
    assert _hay(errores, "rend_bu_ac de maiz: 1 valores fuera")
    assert _hay(errores, "rend_bu_ac de avena: 1 valores fuera")


def test_rendimiento_cero_sin_columnas_de_cosecha_se_rechaza(repo_falso):
    p = _csv(repo_falso, PROD + "31109,2003,maiz,0,\n")
    assert _hay(validar_csv(p), "rend_bu_ac de maiz: 1 valores fuera")


# ---------------------------------------------------------------- faltantes y flag_nass

def test_faltante_como_celda_vacia_con_flag_d_y_z(repo_falso):
    p = _csv(repo_falso, "fips,anio,cultivo,sup_sembrada_ac,rend_bu_ac,flag_nass\n"
                         "20055,2023,maiz,,,(D)\n"
                         "20161,2023,soja,,,(Z)\n"
                         "31109,2023,maiz,150000,180.0,\n")
    assert validar_csv(p) == []


def test_faltante_al_final_de_la_linea(repo_falso):
    p = _csv(repo_falso, "fips,anio,prec_temporada_mm,tmax_c\n20055,2023,250.2,\n31109,2023,,31.0\n")
    assert validar_csv(p) == []


@pytest.mark.parametrize("codigo", ["(D)", "(Z)"])
def test_codigo_nass_en_columna_numerica_se_rechaza(repo_falso, codigo):
    # (D) y (Z) van vacíos en la columna del valor; el código va en flag_nass.
    p = _csv(repo_falso, PROD + f"20055,2023,maiz,{codigo},{codigo}\n31109,2023,maiz,180.0,\n")
    assert _hay(validar_csv(p), "rend_bu_ac: hay valores no numéricos")


@pytest.mark.parametrize("relleno", ["-999", "-9999", "-9999.9"])
def test_relleno_se_rechaza(repo_falso, relleno):
    p = _csv(repo_falso, f"fips,anio,tmax_c\n20055,2023,{relleno}\n31109,2023,30.5\n")
    assert _hay(validar_csv(p), "valores de relleno")


def test_decimal_con_coma_se_rechaza(repo_falso):
    p = _csv(repo_falso, 'fips,anio,tmax_c\n20055,2023,"30,5"\n')
    assert _hay(validar_csv(p), "decimales con coma")


@pytest.mark.xfail(strict=True, reason=(
    "Si TODOS los valores de una columna numérica son (D) o (Z) (un archivo chico de un estado con "
    "todos los condados ocultos), validar_csv() la toma por columna de texto y no avisa. "
    "Ver 'Para decidir' en el PR de T046."))
def test_columna_numerica_toda_con_codigo_nass_se_rechaza(repo_falso):
    p = _csv(repo_falso, PROD + "20055,2023,avena,(D),(D)\n20161,2023,avena,(D),(D)\n")
    assert _hay(validar_csv(p), "rend_bu_ac")
