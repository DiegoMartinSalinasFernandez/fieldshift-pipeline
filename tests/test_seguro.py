"""Pruebas sin red del paquete seguro (T124): lectura de colsom y sobtpu y agregación.

Las líneas de ejemplo son copias recortadas de colsom_2023.zip y sobtpu_2023.zip de RMA (Allen, KS,
maíz), más una de Alabama (estado fuera de la lista, se filtra) y una fila del condado 999.

Correr:  python -X utf8 -m pytest -q tests/test_seguro.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.seguro import process as p  # noqa: E402

COLSOM = "\r\n".join([
    "2023|01|AL|001|Autauga                       |0021|Cotton                        |02|RP        |A|H |11|Drought|07|JUL|2023|2|2|98.3000000000|.0000000000|78691.5000000000|6922.0000000000|3114.5000000000|3807.5000000000|.0000000000|.0000000000|.0000000000|98.3000000000|2367.5000000000|.34",
    "2023|20|KS|001|Allen                         |0041|Corn                          |02|RP        |A|H |01|Decline in Price|08|AUG|2023|4|4|494.4244240000|.0000000000|221060.0000000000|42651.0000000000|15355.0000000000|27296.0000000000|.0000000000|.0000000000|.0000000000|494.4244000000|19007.0000000000|.45",
    "2023|20|KS|001|Allen                         |0041|Corn                          |02|RP        |A|H |11|Drought|07|JUL|2023|9|9|1000.0000000000|.0000000000|500000.0000000000|80000.0000000000|20000.0000000000|60000.0000000000|.0000000000|.0000000000|.0000000000|800.0000000000|845414.7500000000|10.57",
    "2023|20|KS|001|Allen                         |0041|Corn                          |02|RP        |A|H |12|Heat|07|JUL|2023|3|3|300.0000000000|.0000000000|150000.0000000000|20000.0000000000|5000.0000000000|15000.0000000000|.0000000000|.0000000000|.0000000000|200.0000000000|13578.0000000000|.68",
    "2023|20|KS|001|Allen                         |0041|Corn                          |02|RP        |A|H |31|Excess Moisture/Precipitation/Rain|05|MAY|2023|1|1|100.0000000000|.0000000000|50000.0000000000|8000.0000000000|2000.0000000000|6000.0000000000|.0000000000|.0000000000|.0000000000|50.0000000000|1000.0000000000|.13",
    "2023|20|KS|001|Allen                         |0041|Corn                          |02|RP        |A|H |XX|All Other Causes|06|JUN|2003|1|1|10.0000000000|.0000000000|5000.0000000000|800.0000000000|200.0000000000|600.0000000000|.0000000000|.0000000000|.0000000000|5.0000000000|500.0000000000|.63",
    "2023|20|KS|999|All Other Counties            |0041|Corn                          |02|RP        |A|H |11|Drought|07|JUL|2023|1|1|10.0000000000|.0000000000|5000.0000000000|800.0000000000|200.0000000000|600.0000000000|.0000000000|.0000000000|.0000000000|5.0000000000|700.0000000000|.88",
]) + "\r\n"

SOBTPU = "\r".join([
    "2023|01|Alabama                       |AL|001|Autauga|0011|Wheat|01|YP|C|.5000|R|000|No Type Specified|000|No Practice Specified|OU|Optional Unit|0|Acres|.0|.0|0|.0|.00|0",
    "2023|20|Kansas                        |KS|001|Allen|0041|Corn|01|YP|A|.7000|R|016|Grain|003|Non-Irrigated|BU|Basic Unit|14|Acres|6935.0|785.0|463|.0|.00|0",
    "2023|20|Kansas                        |KS|001|Allen|0041|Corn|01|YP|A|.7500|R|016|Grain|003|Non-Irrigated|BU|Basic Unit|26|Acres|12081.0|1638.0|901|1840.0|1.12|0",
    "2023|20|Kansas                        |KS|001|Allen|0041|Corn|02|RP|A|.8000|R|016|Grain|002|Irrigated|EU|Enterprise Unit|60|Acres|50000.0|4000.0|2000|20000.0|5.00|0",
    "2023|20|Kansas                        |KS|001|Allen|0041|Corn|32|SCO-RP|A|.8600|R|016|Grain|000|No Practice Specified|EU|Enterprise Unit|0|Acres|3000.0|500.0|300|900.0|1.80|0",
    "2023|20|Kansas                        |KS|001|Allen|0011|Wheat|02|RP|A|.7500|R|011|Winter|005|Summerfallow|EU|Enterprise Unit|30|Acres|9000.0|900.0|500|.0|.00|0",
    "2023|20|Kansas                        |KS|001|Allen|0011|Wheat|02|RP|A|.7500|R|012|Spring|003|Non-Irrigated|EU|Enterprise Unit|10|Acres|3000.0|300.0|150|.0|.00|0",
    "2023|20|Kansas                        |KS|001|Allen|0091|Grain Sorghum|02|RP|A|.7500|R|000|No Type Specified|003|Non-Irrigated|EU|Enterprise Unit|99|Acres|3000.0|300.0|150|.0|.00|0",
]) + "\r"

KS = {"20"}


def leer():
    col = p.preparar(p.leer_lineas(COLSOM, 30, KS, p.COL_COLS))
    sob = p.preparar(p.leer_lineas(SOBTPU, 27, KS, p.SOB_COLS))
    return col, sob


def test_lectura_filtra_estado_y_cultivo():
    col, sob = leer()
    assert set(col["fips"]) == {"20001", "20999"}
    assert set(sob["fips"]) == {"20001"}
    assert set(sob["cultivo"]) == {"maiz", "trigo"}  # el sorgo (0091) queda afuera
    assert col["causa"].iloc[0] == "Decline in Price"  # sin los espacios de relleno


def test_columnas_incorrectas():
    with pytest.raises(ValueError):
        p.leer_lineas("2023|20|KS|001\n", 30, KS, p.COL_COLS)


def test_practica_y_causa():
    assert p.practica_grupo("Non-Irrigated") == "secano"
    assert p.practica_grupo("Organic(Certified) Non-Irr.") == "secano"
    assert p.practica_grupo("Nfac (Irrigated)") == "riego"
    assert p.practica_grupo("Summerfallow(OC)") == "secano"
    assert p.practica_grupo("No Practice Specified") == "sin_especificar"
    assert p.grupo_causa("11") == "sequia"
    assert p.grupo_causa("62") == "calor"
    assert p.grupo_causa("XX") == "otras"
    assert p.grupo_causa("77") == "otras"


def test_anual():
    col, sob = leer()
    col, fuera = p.separar_fuera(col, {"20001", "20003"})
    assert set(fuera["fips"]) == {"20999"}
    a = p.armar_anual(sob, col, ["20001", "20003"], [2022, 2023])
    assert len(a) == 2 * 2 * 4
    assert list(a.columns[:3]) == ["fips", "anio", "cultivo"]
    m = a[(a.fips == "20001") & (a.anio == 2023) & (a.cultivo == "maiz")].iloc[0]
    assert m.sup_asegurada_ac == 100  # el SCO tiene 0 acres
    assert m.sup_asegurada_secano_ac == 40
    assert m.sup_asegurada_riego_ac == 60
    assert m.responsabilidad_usd == pytest.approx(6935 + 12081 + 50000 + 3000)
    assert m.indemnizacion_usd == pytest.approx(1840 + 20000 + 900)
    assert m.loss_ratio == pytest.approx(m.indemnizacion_usd / (785 + 1638 + 4000 + 500))
    assert m.loss_cost == pytest.approx(m.indemnizacion_usd / m.responsabilidad_usd)
    assert m.indem_sequia_usd == pytest.approx(845414.75)
    assert m.indem_precio_usd == pytest.approx(19007)
    assert m.indem_otras_usd == pytest.approx(500)
    assert m.indem_granizo_usd == 0  # con participación y sin filas de granizo: 0 real
    assert m.sup_con_perdida_ac == pytest.approx(494.4244 + 800 + 200 + 50 + 5)
    clima = 845414.75 + 13578 + 1000
    assert m.frac_indem_clima == pytest.approx(clima / (clima + 19007 + 500))
    assert pd.isna(m.trigo_frac_invierno)
    t = a[(a.fips == "20001") & (a.anio == 2023) & (a.cultivo == "trigo")].iloc[0]
    assert t.trigo_frac_invierno == pytest.approx(0.75)
    assert t.indem_sequia_usd == 0 and t.loss_ratio == 0  # prima > 0 e indemnización 0
    vacia = a[(a.fips == "20003") & (a.anio == 2023) & (a.cultivo == "maiz")].iloc[0]
    assert vacia[p.COLS_ANUAL].isna().all()


def test_mensual():
    col, _ = leer()
    col, _ = p.separar_fuera(col, {"20001"})
    m, desc = p.armar_mensual(col, [2022, 2023])
    assert desc["filas_anio_perdida_lejano"] == 1  # pérdida en 2003 de la cosecha 2023
    assert list(m.columns[:4]) == ["fips", "anio", "mes", "cultivo"]
    assert set(m["mes"]) == {"2023-05", "2023-07", "2023-08"}
    jul = m[m.mes == "2023-07"].iloc[0]
    assert jul.indem_sequia_usd == pytest.approx(845414.75)
    assert jul.indem_calor_usd == pytest.approx(13578)
    assert jul.indem_total_usd == pytest.approx(845414.75 + 13578)
    assert (m["anio"] == m["mes"].str[:4].astype(int)).all()
