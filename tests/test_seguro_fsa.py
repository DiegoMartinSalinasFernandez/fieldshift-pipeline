"""Pruebas sin red de la siembra prevenida de FSA (T125): lectura del .xlsx y agregación.

El .xlsx se arma en la prueba con openpyxl, imitando la hoja `county_data` de FSA (2019/2025:
fila de título opcional, `State County Code` como fórmula, celdas vacías) y la `Sheet1` de 2009
(sin `Irrigation Practice`, uso en código).

Correr:  python -X utf8 -m pytest -q tests/test_seguro_fsa.py
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pytest

openpyxl = pytest.importorskip("openpyxl")

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.seguro import fsa_process as p  # noqa: E402

ENC_2012 = ["State Code", "County Code", "Crop Code", "State", "County", "State County Code", "Crop",
            "Crop Type", "Intended Use", "Irrigation Practice", "Planted Acres", "Volunteer Acres",
            "Failed Acres", "Prevented Acres", "Not Planted Acres", "Planted and Failed Acres"]
FILAS_2012 = [
    # Story (IA) no está en los estados pedidos: se filtra
    ["19", "169", "0041", "Iowa", "Story", "=CONCATENATE(A2,B2)", "CORN", "YELLOW", "Grain", "N",
     1000, 0, 0, 50, 0, "=K2+M2"],
    # Allen (KS): maíz de riego y de secano, más pochoclo (afuera)
    ["20", "001", "0041", "Kansas", "Allen", "=CONCATENATE(A3,B3)", "CORN", "YELLOW", "Grain", "N",
     800, 0, 10, 100, 0, "=K3+M3"],
    ["20", "001", "0041", "Kansas", "Allen", "x", "CORN", "YELLOW", "Silage", "I",
     200, 0, None, 50, 0, "x"],
    ["20", "001", "0041", "Kansas", "Allen", "x", "CORN", "POPCORN", "Grain", "N", 99, 0, 0, 99, 0, "x"],
    # trigo: el pastoreo se saca (doble conteo desde 2019); el de primavera no es trigo_invierno
    ["20", "001", "0011", "Kansas", "Allen", "x", "WHEAT", "HARD RED WINTER", "Grain", "N",
     500, 0, 0, 0, 0, "x"],
    ["20", "001", "0011", "Kansas", "Allen", "x", "WHEAT", "HARD RED WINTER", "Grazing", "N",
     500, 0, 0, 0, 0, "x"],
    ["20", "001", "0011", "Kansas", "Allen", "x", "WHEAT", "HARD RED SPRING", "Grain", "N",
     70, 0, 0, 7, 0, "x"],
    # soja sin superficie: denominador 0 -> pct vacío
    ["20", "001", "0081", "Kansas", "Allen", "x", "SOYBEANS", "COMMON", "Grain", "", 0, 0, 0, 0, 0, "x"],
    # condado partido: East Lucas (39094) se suma a Lucas (39095)
    ["39", "094", "0081", "Ohio", "East Lucas", "x", "SOYBEANS", "COMMON", "Grain", "N",
     300, 0, 0, 100, 0, "x"],
    ["39", "095", "0081", "Ohio", "Lucas", "x", "SOYBEANS", "COMMON", "Grain", "N",
     600, 0, 0, 0, 0, "x"],
    # código que no es FIPS ni está en la tabla: no se descarta en silencio
    ["39", "998", "0081", "Ohio", "Raro", "x", "SOYBEANS", "COMMON", "Grain", "N", 10, 0, 0, 5, 0, "x"],
]


def xlsx(encabezado, filas, hoja="county_data", titulo=False) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = hoja
    if titulo:
        ws.append(["2025 ACRES BY COUNTY BY CROP ..."])
    ws.append(encabezado)
    for f in filas:
        ws.append(f)
    otra = wb.create_sheet("plant_and_fail")
    otra.append(["tabla dinámica"])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


ESTADOS = {"20", "39"}
VALIDOS = {"20001", "39095"}
ADMIN = {"39094": "39095", "19156": "19155"}


@pytest.mark.parametrize("titulo", [False, True])
def test_leer_xlsx_2012_en_adelante(titulo):
    df = p.leer_xlsx(xlsx(ENC_2012, FILAS_2012, titulo=titulo), ESTADOS)
    assert set(df["st"]) == ESTADOS
    assert len(df) == len(FILAS_2012) - 1
    assert df.attrs["con_riego"]
    # la celda vacía de Failed Acres queda en 0
    assert df["fallida"].sum() == 10


def test_agregar():
    df = p.leer_xlsx(xlsx(ENC_2012, FILAS_2012), ESTADOS)
    out, conv, sin = p.agregar(df, 2019, ADMIN, VALIDOS)
    out = out.set_index(["fips", "cultivo"])
    m = out.loc[("20001", "maiz")]
    assert m["sup_sembrada_fsa_ac"] == 1000 and m["sup_prevenida_ac"] == 150
    assert m["sup_fallida_ac"] == 10
    assert m["sup_prevenida_riego_ac"] == 50 and m["sup_prevenida_secano_ac"] == 100
    assert m["pct_prevenida"] == pytest.approx(100 * 150 / 1150)
    assert out.loc[("20001", "trigo_invierno"), "sup_sembrada_fsa_ac"] == 500
    assert out.loc[("20001", "trigo_invierno"), "sup_prevenida_ac"] == 0  # 0 real, no faltante
    assert pd.isna(out.loc[("20001", "soja"), "pct_prevenida"])
    s = out.loc[("39095", "soja")]
    assert s["sup_sembrada_fsa_ac"] == 900 and s["sup_prevenida_ac"] == 100
    assert list(conv["codigo"]) == ["39094"]
    assert list(sin["codigo"]) == ["39998"] and sin["prevenida"].sum() == 5
    assert "39998" not in out.index.get_level_values("fips")


def test_2009_sin_riego_y_uso_en_codigo():
    enc = ["State Code", "County Code", "State Name", "County Name", "Crop Code", "Crop Name",
           "Crop Type Name", "Crop Type", "Intended Use", "Planted Acres", "Prevented Acres", "Failed Acres"]
    filas = [["20", "001", "KS", "ALLEN", "0041", "CORN", "YELLOW", "YEL", "GR", 400, 40, 4],
             ["20", "001", "KS", "ALLEN", "0041", "CORN", "SWEET", "SWT", "FH", 9, 9, 9],
             ["20", "001", "KS", "ALLEN", "0016", "OATS", "SPRING", "SPR", "GZ", 30, 3, 0],
             ["20", "001", "KS", "ALLEN", "0016", "OATS", "SPRING", "SPR", "GR", 20, 2, 0]]
    df = p.leer_xlsx(xlsx(enc, filas, hoja="Sheet1"), ESTADOS)
    assert not df.attrs["con_riego"]
    out, _, _ = p.agregar(df, 2009, ADMIN, VALIDOS)
    out = out.set_index("cultivo")
    assert out.loc["maiz", "sup_prevenida_ac"] == 40
    assert pd.isna(out.loc["maiz", "sup_prevenida_riego_ac"])
    assert out.loc["avena", "sup_sembrada_fsa_ac"] == 20  # sin el pastoreo


def test_falta_columna():
    enc = [c for c in ENC_2012 if c != "Prevented Acres"]
    with pytest.raises(ValueError, match="prevenida"):
        p.leer_xlsx(xlsx(enc, []), ESTADOS)


def test_leer_zip(tmp_path):
    z = tmp_path / "fsa_acres_2019_final.zip"
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("2019_fsa_acres_web_010220.xlsx", xlsx(ENC_2012, FILAS_2012))
    df = p.leer_zip(z, ESTADOS)
    assert df.attrs["xlsx"] == "2019_fsa_acres_web_010220.xlsx"


def test_tabla_admin_del_repo():
    t = p.tabla_admin()
    assert t["19156"] == "19155" and t["39094"] == "39095"
    assert all(int(f[2:]) % 2 == 1 for f in t.values())


def test_enlace_zip():
    from src.seguro import fsa_download as d
    html = '<a href="https://www.fsa.usda.gov/sites/default/files/2026-01/DoISjehvQfz9.ZIP">x</a>'
    assert d.enlace_zip(html).endswith("DoISjehvQfz9.ZIP")
    assert d.enlace_zip('<a href="/sites/default/files/a.zip">') == "https://www.fsa.usda.gov/sites/default/files/a.zip"
    assert d.enlace_zip("<html></html>") is None
    assert set(d.FINALES) == set(range(2009, 2026))


def test_2010_columna_state():
    enc = ["State", "County Code", "State Abbrev", "County Name", "Crop Code", "Crop Name",
           "Crop Type Name", "Crop Type", "Intended Use", "Planted Acres", "Prevented Acres", "Failed Acres"]
    filas = [["20", "001", "KS", "ALLEN", "0081", "SOYBEANS", "COMMON", "COM", "GR", 90, 10, 1]]
    out, _, _ = p.agregar(p.leer_xlsx(xlsx(enc, filas, hoja="Sheet1"), ESTADOS), 2010, ADMIN, VALIDOS)
    assert out.iloc[0]["sup_prevenida_ac"] == 10 and out.iloc[0]["pct_prevenida"] == pytest.approx(10)


def test_2011_formato_ancho():
    enc = ["State Code", "County Code", "State Name", "County Name", "Crop Code", "Crop Name", "Crop Type",
           "Crop Type Name", "Intended Use", "Planted\nTotal", "Prevented\nTotal", "Failed\nTotal",
           "Planted\nIrrigated", "Prevented\nIrrigated", "Planted\nNonirrigated", "Prevented\nNonirrigated"]
    filas = [["20", "001", "KANSAS", "ALLEN", "0041", "CORN", "YEL", "YELLOW", "GR", 100, 30, 2, 40, 10, 60, 20]]
    df = p.leer_xlsx(xlsx(enc, filas, hoja="Sheet1"), ESTADOS)
    assert df.attrs["con_riego"]
    r = p.agregar(df, 2011, ADMIN, VALIDOS)[0].iloc[0]
    assert (r["sup_sembrada_fsa_ac"], r["sup_prevenida_ac"], r["sup_fallida_ac"]) == (100, 30, 2)
    assert (r["sup_prevenida_riego_ac"], r["sup_prevenida_secano_ac"]) == (10, 20)


def test_2012_errata_failded():
    enc = [("Failded Acres" if c == "Failed Acres" else c) for c in ENC_2012]
    df = p.leer_xlsx(xlsx(enc, FILAS_2012), ESTADOS)
    assert df["fallida"].sum() == 10
