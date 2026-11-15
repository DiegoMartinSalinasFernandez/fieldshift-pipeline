"""Riego por condado y año desde LANID (T127), sin red y con rasters chicos armados acá.

Correr:  python -X utf8 -m pytest -q tests/test_riego_lanid.py
"""
from __future__ import annotations

import csv
import importlib.util
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

rasterio = pytest.importorskip("rasterio")
gpd = pytest.importorskip("geopandas")
from rasterio.transform import from_origin  # noqa: E402
from shapely.geometry import box  # noqa: E402


def cargar():
    spec = importlib.util.spec_from_file_location("t127_riego", REPO / "src/cultivos/riego.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rg = cargar()
X0, Y0 = -100000.0, 2000000.0  # esquina noroeste, EPSG:5070


def tif(ruta: Path, a: np.ndarray, x0=X0, y0=Y0, nodata=None):
    with rasterio.open(ruta, "w", driver="GTiff", dtype="uint8", count=1, width=a.shape[1], height=a.shape[0],
                       crs="EPSG:5070", transform=from_origin(x0, y0, 30, 30), nodata=nodata) as d:
        d.write(a.astype("uint8"), 1)


@pytest.fixture
def escena(tmp_path):
    """Grilla de 10×10 a 30 m: condado A (columnas 0–4) y B (columnas 5–9)."""
    ref = tmp_path / "ref"
    ref.mkdir()
    agri = np.zeros((10, 10), np.uint8)
    agri[:, :4] = 1          # A: 40 píxeles agrícolas
    agri[:5, 5:] = 1         # B: 25 píxeles agrícolas
    tif(ref / "mascara_agricola.tif", agri)
    maiz = np.zeros((10, 10), np.uint8)
    maiz[:, :2] = 1          # A: 20 de maíz
    tif(ref / "mascara_maiz_2010.tif", maiz)
    cond = gpd.GeoDataFrame({"fips": ["31001", "31003"]},
                            geometry=[box(X0, Y0 - 300, X0 + 150, Y0), box(X0 + 150, Y0 - 300, X0 + 300, Y0)],
                            crs="EPSG:5070").to_crs(4326)
    return ref, cond


def test_fracciones_por_condado(escena, tmp_path):
    ref, cond = escena
    lanid = np.zeros((10, 10), np.uint8)
    lanid[:, 0] = 1          # A: 10 regados, todos de maíz
    lanid[:5, 5:7] = 1       # B: 10 regados
    tif(tmp_path / "lanid2010.tif", lanid)
    df = rg.riego_anual(ref / "mascara_agricola.tif", cond, {2010: str(tmp_path / "lanid2010.tif")}, [2009, 2010])
    assert df["anio"].tolist() == [2010, 2010]  # 2009 no está en LANID: sin fila
    a = df.set_index("fips").loc["31001"]
    b = df.set_index("fips").loc["31003"]
    assert a["frac_riego_lanid"] == pytest.approx(10 / 40)
    assert a["frac_maiz_regado"] == pytest.approx(10 / 20)
    assert np.isnan(a["frac_soja_regada"])  # no hay mascara_soja_2010.tif
    assert a["frac_pixeles_validos"] == 1.0
    assert b["frac_riego_lanid"] == pytest.approx(10 / 25)
    assert np.isnan(b["frac_maiz_regado"])  # B no tiene maíz: vacío, no 0


def test_grilla_desplazada_y_nodata(escena, tmp_path):
    """LANID con otra extensión (un píxel corrido) y nodata: cuenta en frac_pixeles_validos."""
    ref, cond = escena
    lanid = np.zeros((12, 12), np.uint8)
    lanid[1:11, 1] = 1                 # columna 0 de la grilla de referencia
    lanid[1:6, 6:9] = 255              # B: columnas 5–7, filas 0–4 sin dato
    tif(tmp_path / "lanid2010.tif", lanid, x0=X0 - 30, y0=Y0 + 30, nodata=255)
    df = rg.riego_anual(ref / "mascara_agricola.tif", cond, {2010: str(tmp_path / "lanid2010.tif")}, [2010])
    a = df.set_index("fips").loc["31001"]
    b = df.set_index("fips").loc["31003"]
    assert a["frac_riego_lanid"] == pytest.approx(10 / 40)
    assert b["frac_pixeles_validos"] == pytest.approx(10 / 25)
    assert b["frac_riego_lanid"] == 0.0


def test_fuentes_lanid_zip_y_tif_suelto(tmp_path):
    raw = tmp_path / "lanid"
    raw.mkdir()
    tif(tmp_path / "lanid2004.tif", np.zeros((2, 2)))
    tif(tmp_path / "maxIrrExt.tif", np.zeros((2, 2)))
    with zipfile.ZipFile(raw / "lanid2004-2010.zip", "w") as z:
        z.write(tmp_path / "lanid2004.tif", "lanid2004-2010/lanid2004.tif")
    with zipfile.ZipFile(raw / "irrFreqAndChange.zip", "w") as z:
        z.write(tmp_path / "maxIrrExt.tif", "irrFreqAndChange/maxIrrExt.tif")
    tif(raw / "lanid2018.tif", np.zeros((2, 2)))
    anuales, maximo = rg.fuentes_lanid(raw)
    assert sorted(anuales) == [2004, 2018]
    assert anuales[2004].startswith("/vsizip/")
    assert maximo.endswith("maxIrrExt.tif")
    tif(raw / "maxIrrExt_0020.tif", np.zeros((2, 2)))
    assert rg.fuentes_lanid(raw)[1].endswith("maxIrrExt_0020.tif")  # 2000–2020 tiene prioridad


def test_mascara_riego_max(escena, tmp_path):
    ref, _ = escena
    m = np.zeros((10, 10), np.uint8)
    m[:2, :] = 1
    tif(tmp_path / "maxIrrExt.tif", m)
    salida = tmp_path / "mascara_riego_max.tif"
    assert rg.mascara_riego_max(ref / "mascara_agricola.tif", str(tmp_path / "maxIrrExt.tif"), salida) == 0.2
    with rasterio.open(salida) as s, rasterio.open(ref / "mascara_agricola.tif") as r:
        assert s.transform == r.transform and s.crs == r.crs
        assert s.read(1).sum() == 20


def test_registrar_una_sola_vez(tmp_path):
    man = tmp_path / "manifest.csv"
    p = tmp_path / "lanid2011-2017.zip"
    p.write_bytes(b"x")
    rg.registrar(p, "https://zenodo.org/x", man)
    rg.registrar(p, "https://zenodo.org/x", man)
    filas = list(csv.DictReader(open(man, encoding="utf-8")))
    assert len(filas) == 1 and filas[0]["version"] == "3.0" and filas[0]["paquete"] == "cultivos"


def test_nodata_cero_y_cobertura_parcial(escena, tmp_path):
    """nodata=0 declarado no borra los 'no regado'; fuera de la cobertura de LANID no es válido."""
    ref, cond = escena
    lanid = np.zeros((10, 5), np.uint8)   # cubre solo el condado A
    lanid[:, 0] = 1
    tif(tmp_path / "lanid2010.tif", lanid, nodata=0)
    df = rg.riego_anual(ref / "mascara_agricola.tif", cond, {2010: str(tmp_path / "lanid2010.tif")}, [2010])
    a = df.set_index("fips").loc["31001"]
    b = df.set_index("fips").loc["31003"]
    assert a["frac_pixeles_validos"] == 1.0 and a["frac_riego_lanid"] == pytest.approx(10 / 40)
    assert b["frac_pixeles_validos"] == 0.0 and np.isnan(b["frac_riego_lanid"])
