"""agua_estatico.csv (T129), sin red: grilla SMAP chica armada en la prueba.

Dos condados en una grilla de 2 x 4 celdas (EPSG:5070, celdas de 9 km): el condado A ocupa las
columnas 0-1 y el B las columnas 2-3. En la capa SUB:
- A tiene 1 de sus 4 celdas > 0,6 (turba) → frac_celdas_excluidas = 0,25;
- B tiene una celda nodata (lago, -9999), que no cuenta ni arriba ni abajo, y una celda > 0,6 → 1/3.
La capa TOP no entra en la fracción. Además, `agua_diario.csv` sale igual que antes del cambio.

Correr:  python -X utf8 -m pytest -q tests/test_agua_estatico.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

gpd = pytest.importorskip("geopandas")
rasterio = pytest.importorskip("rasterio")
from rasterio.transform import from_origin  # noqa: E402
from shapely.geometry import box  # noqa: E402


def cargar():
    spec = importlib.util.spec_from_file_location("t129_agua_process", REPO / "src/agua/process.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pr = cargar()
X0, Y0, C = 0.0, 18000.0, 9000.0  # esquina noroeste y tamaño de celda
ND = -9999.0


def tif(ruta: Path, a: np.ndarray) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(ruta, "w", driver="GTiff", height=a.shape[0], width=a.shape[1], count=1,
                       dtype="float32", crs="EPSG:5070", transform=from_origin(X0, Y0, C, C),
                       nodata=ND) as dst:
        dst.write(a.astype("float32"), 1)


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    gdf = gpd.GeoDataFrame({"fips": ["27001", "27003"]},
                           geometry=[box(0, 0, 2 * C, 2 * C), box(2 * C, 0, 4 * C, 2 * C)], crs="EPSG:5070")
    gpkg = tmp_path / "condados.gpkg"
    gdf.to_file(gpkg, driver="GPKG")
    raw = tmp_path / "smap"
    sub = np.array([[0.30, 0.70, 0.30, ND],
                    [0.20, 0.30, 0.90, 0.40]])
    top = np.array([[0.95, 0.95, 0.95, 0.95],  # TOP > 0,6 en todo: no tiene que contar
                    [0.10, 0.10, 0.10, 0.10]])
    for dia in ("01", "02"):
        tif(raw / "2019" / f"SMAP-9KM-DAILY-SUB_2019.05.{dia}_013000_FIPS_27.tif", sub)
        tif(raw / "2019" / f"SMAP-9KM-DAILY-TOP_2019.05.{dia}_013000_FIPS_27.tif", top)
    monkeypatch.setattr(pr, "CONDADOS", gpkg)
    monkeypatch.setattr(pr, "SMAP_RAW", raw)
    return sub


def test_frac_celdas_excluidas(entorno):
    exc: list = []
    pr.diario_smap(exc)
    e = pr.estatico_smap(exc)
    assert list(e.columns) == ["fips", "frac_celdas_excluidas"]
    assert list(e["fips"]) == ["27001", "27003"]
    assert e["frac_celdas_excluidas"].tolist() == pytest.approx([0.25, 1 / 3])


def test_diario_no_cambia(entorno):
    sin = pr.diario_smap()
    con = pr.diario_smap([])
    pd.testing.assert_frame_equal(sin, con)
    # medias de SUB con el filtro de siempre: A = (0,3+0,2+0,3)/3, B = (0,3+0,4)/2
    d = sin[sin["fecha"] == "2019-05-01"].set_index("fips")["sm_rootzone_m3m3"]
    assert d.tolist() == pytest.approx([0.8 / 3, 0.35])


def test_frac_excluida_sin_dato():
    W = np.array([[1.0, 1.0], [0.0, 2.0]])
    a = np.array([0.7, ND])
    con_dato, validas = pr.celdas_smap(a, ND)
    f = pr.frac_excluida(W, con_dato, validas)
    assert f[0] == pytest.approx(1.0)
    assert np.isnan(f[1])  # condado sin celdas con dato: vacío, no 0


def test_estatico_vacio():
    e = pr.estatico_smap([])
    assert list(e.columns) == ["fips", "frac_celdas_excluidas"] and e.empty
