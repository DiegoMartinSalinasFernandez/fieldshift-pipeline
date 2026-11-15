"""Pruebas sin red de los análogos de Buenos Aires: calendario corrido, MAGyP, suelo ponderado y medidas."""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def cargar(nombre: str):
    spec = importlib.util.spec_from_file_location(f"analogos_{nombre}", RAIZ / "src" / "analogos" / f"{nombre}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_calendario_corrido_6_meses():
    C = cargar("clima_ba")
    f = pd.Series(pd.to_datetime(["2023-07-01", "2023-10-01", "2024-01-15", "2024-03-31", "2024-06-30"]))
    c = C.correr(f)
    assert c["anio_c"].tolist() == [2024] * 5
    assert c["mes_c"].tolist() == [1, 4, 7, 9, 12]       # oct → abril, ene → julio, mar → septiembre
    assert c["doy_c"].tolist()[0] == 1 and c["doy_c"].tolist()[2] == 184 + 15
    assert c["doy_c"].tolist()[-1] == 366                # julio 2023 a junio 2024: febrero bisiesto


def test_magyp_limpieza():
    R = cargar("rendimiento")
    d = pd.DataFrame({
        "cultivo": ["maíz", "maíz", "soja total", "trigo total", "girasol", "maíz"],
        "anio": [2023, 2023, 2023, 1999, 2023, 2010],
        "campania": ["2023/2024", "2023/2024", "2023/2024", "1999/2000", "2023/2024", "2010/2011"],
        "departamento_id": ["06007", "06000", "06217", "06007", "06007", "06014"],
        "superficie_sembrada_ha": [100, 5, 50, 10, 10, 20], "superficie_cosechada_ha": [90, 5, 50, 10, 10, 0],
        "produccion_tm": [720, 10, 150, 20, 20, 0], "rendimiento_kgxha": [8000, 2000, 3000, 2000, 2000, 0]})
    a = R.limpiar(d).set_index(["id_depto_indec", "cultivo"])
    assert len(a) == 3                                    # sin "sin definir", sin girasol, sin campañas < 2000/01
    assert a.loc[("06007", "maiz"), "anio"] == 2024       # año de cosecha = segundo año de la campaña
    assert a.loc[("06218", "soja"), "flag_magyp"] == "codigo_06217"
    assert np.isnan(a.loc[("06014", "maiz"), "rend_kgha"])
    assert a.loc[("06014", "maiz"), "flag_magyp"] == "0_sin_cosecha"
    assert np.isclose(a.loc[("06007", "maiz"), "ratio_cosechada"], 0.9)


def test_suelo_ponderado_0_30(tmp_path, monkeypatch):
    import geopandas as gpd
    import rasterio
    from rasterio.transform import from_origin
    from shapely.geometry import box

    S = cargar("suelo")
    (tmp_path / "soilgrids").mkdir()
    tr = from_origin(0, 4000, 1000, 1000)                 # 4 × 4 píxeles de 1 km
    valores = {"0-5cm": 100, "5-15cm": 200, "15-30cm": 400}
    for prop in S.PROPS:
        for prof, v in valores.items():
            a = np.full((4, 4), v, dtype="int16")
            a[0, 0] = S.NODATA
            with rasterio.open(tmp_path / "soilgrids" / f"{prop}_{prof}_mean_1000_x.tif", "w", driver="GTiff",
                               width=4, height=4, count=1, dtype="int16", crs="ESRI:54052", transform=tr,
                               nodata=S.NODATA) as dst:
                dst.write(a, 1)
    monkeypatch.setattr(S, "RAW", tmp_path)
    pol = gpd.GeoDataFrame({"id": ["a"], "lado": ["ar"]}, geometry=[box(0, 2000, 2000, 4000)], crs="ESRI:54052")
    r = S.medias_region(pol, "x").iloc[0]
    # (5 × 100 + 10 × 200 + 15 × 400) / 30 = 283.3 g/kg → 28.33 %
    assert np.isclose(r["arcilla_sg_pct"], 283.333 / 10, atol=1e-3)
    assert r["n_pixeles"] == 4 and np.isclose(r["frac_pixeles_validos"], 0.75)


def test_medir_departamento_igual_a_un_condado():
    P = cargar("process")
    rng = np.random.default_rng(0)
    us = pd.DataFrame(rng.normal(size=(50, 4)), columns=list("abcd"), index=[f"{i:05d}" for i in range(50)])
    ar = pd.DataFrame([us.iloc[7].to_numpy(), us.max().to_numpy() + 1], columns=list("abcd"), index=["x", "y"])
    r = P.medir(us, ar)
    assert r["orden"][0, 0] == 7 and np.isclose(r["d_ar"][0], 0)
    assert not r["fuera"].loc["x"].any() and r["fuera"].loc["y"].all()
