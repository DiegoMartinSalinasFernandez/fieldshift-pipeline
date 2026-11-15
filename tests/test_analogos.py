"""Pruebas sin red de src/analogos/process.py: alineación de la temporada por hemisferio y lluvia mensual."""

from pathlib import Path

import numpy as np
import pandas as pd

import importlib.util

_ruta = Path(__file__).resolve().parents[1] / "src" / "analogos" / "process.py"
_spec = importlib.util.spec_from_file_location("analogos_process", _ruta)
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)


def serie_juguete(prec_por_mes: dict[int, float]) -> pd.DataFrame:
    filas = []
    for anio in range(2001, 2005):
        for mes in range(1, 13):
            filas.append({"anio": anio, "mes": mes, "tmed": float(mes), "tmax": 30.0 + mes, "tmin": -mes,
                          "prec": prec_por_mes.get(mes, 0.0), "rad": 20.0})
    return pd.DataFrame(filas)


def test_temporada_norte_y_sur_alineadas():
    us = P.variables(serie_juguete({}), P.TEMP_US, P.INV_US, sur=False)
    ar = P.variables(serie_juguete({}), P.TEMP_AR, P.INV_AR, sur=True)
    assert us["tmed_t1"] == 4 and us["tmed_t4"] == 7      # abril y julio
    assert ar["tmed_t1"] == 10 and ar["tmed_t4"] == 1     # octubre y enero
    assert us["tmax_abs_t4"] == 37 and ar["tmax_abs_t4"] == 31
    assert us["x_tmin_abs_t1"] == -4 and ar["x_tmin_abs_t1"] == -10


def test_invierno_y_variabilidad_solo_con_temporadas_completas():
    ar = P.variables(serie_juguete({6: 100.0, 1: 50.0}), P.TEMP_AR, P.INV_AR, sur=True)
    assert ar["prec_invierno"] == 100.0          # mayo-septiembre del mismo año
    us = P.variables(serie_juguete({12: 80.0}), P.TEMP_US, P.INV_US, sur=False)
    assert us["prec_invierno"] == 80.0           # diciembre cuenta para el invierno siguiente
    assert np.isclose(ar["prec_temp_sd"], 0.0)   # la misma lluvia todos los años


def test_lluvia_mm_dia_a_mm_mes(tmp_path, monkeypatch):
    import json
    meses = {f"2004{m:02d}": 2.0 for m in range(1, 13)}
    meses["200413"] = 2.0
    par = {n: dict(meses) for n in ("T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN")}
    par["T2M"]["200403"] = -999.0
    (tmp_path / "power").mkdir()
    (tmp_path / "power" / "x.json").write_text(json.dumps({"properties": {"parameter": par}}), encoding="utf-8")
    monkeypatch.setattr(P, "RAW", tmp_path)
    s = P.serie("x").set_index("mes")
    assert s.loc[2, "prec"] == 58.0              # 2004 es bisiesto: 29 días × 2 mm
    assert s.loc[1, "prec"] == 62.0
    assert np.isnan(s.loc[3, "tmed"])            # relleno de POWER → vacío
    assert 13 not in s.index
