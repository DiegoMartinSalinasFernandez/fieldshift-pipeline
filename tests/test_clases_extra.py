"""Pruebas de src/cultivos/clases_extra.py (T139: clases 0, 27 y 58 del CDL).

Sin red: rasters chicos inventados como arrays de numpy y una tabla de clases en una carpeta
temporal. La única lectura del repo es `data/reference/clases_cdl.csv` (en git).

Correr desde la raíz:  .venv/bin/python -X utf8 -m pytest tests/test_clases_extra.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.cultivos import clases_extra as ce  # noqa: E402
from src.cultivos import process as proc  # noqa: E402


def _tabla():
    return pd.DataFrame({"codigo": [0, 1, 27, 58, 176],
                         "nombre": ["Background", "Corn", "Rye", "Clover/Wildflowers",
                                    "Grassland/Pasture"],
                         "grupo": ["otro", "maiz", "otro", "otro", "pastizal"]})


def test_aplicar_grupos_e_idempotente():
    a = ce.aplicar_grupos(_tabla())
    assert dict(zip(a["codigo"], a["grupo"])) == {0: "sin_dato", 1: "maiz", 27: "centeno",
                                                  58: "trebol", 176: "pastizal"}
    pd.testing.assert_frame_equal(ce.aplicar_grupos(a), a)


def test_no_inventa_filas_ni_acepta_nombres_raros():
    with pytest.raises(ValueError, match="falta el código 27"):
        ce.aplicar_grupos(_tabla()[lambda d: d["codigo"] != 27])
    t = _tabla()
    t.loc[t["codigo"] == 58, "nombre"] = "Sod/Grass Seed"
    with pytest.raises(ValueError, match="58"):
        ce.aplicar_grupos(t)


def test_escribir_conserva_crlf(tmp_path):
    p = tmp_path / "clases.csv"
    p.write_bytes(_tabla().to_csv(index=False, lineterminator="\r\n").encode())
    ce.escribir_clases(p)
    b = p.read_bytes()
    assert b.count(b"\r\n") == 6 and b"27,Rye,centeno\r\n" in b
    ce.escribir_clases(p)
    assert p.read_bytes() == b


def test_tabla_del_repo_y_process_coinciden():
    t = pd.read_csv(REPO / "data" / "reference" / "clases_cdl.csv")
    g = dict(zip(t["codigo"], t["grupo"]))
    assert (g[0], g[27], g[58]) == ("sin_dato", "centeno", "trebol")
    # si process.py regenera la tabla desde los metadatos, los grupos no se pierden
    for cod, grupo in proc.GRUPOS_CDL.items():
        assert g[cod] == grupo
    # las listas copiadas en clases_extra siguen iguales a las de process.py
    assert ce.AGRICOLA == proc.AGRICOLA and ce.PCT_CLASES == proc.PCT_CLASES


def _cuenta():
    # condado 1: 4 maíz, 2 centeno, 1 trébol, 1 pastizal, 2 fondo; condado 2: 3 soja, 1 fondo
    cdl = np.array([[1, 1, 1, 1, 27, 27, 58, 176, 0, 0],
                    [5, 5, 5, 0, 0, 0, 0, 0, 0, 0]], dtype=np.uint8)
    ids = np.array([[1] * 10, [2, 2, 2, 2, 0, 0, 0, 0, 0, 0]], dtype=np.int32)
    return ce.conteo_por_condado(cdl, ids, 2)


def test_conteo_por_condado():
    c = _cuenta()
    assert c.shape == (3, 256)
    assert c[1, 1] == 4 and c[1, 27] == 2 and c[1, 0] == 2 and c[2, 5] == 3 and c[2, 0] == 1
    assert c[0, 0] == 6  # fuera de los condados


def test_efecto_por_escenario():
    d = ce.efecto(_cuenta()).set_index(["escenario", "id"])
    act, a, b = d.loc[("actual", 1)], d.loc[("A_grupos", 1)], d.loc[("B_cobertura", 1)]
    # actual y A: 27 y 58 dentro del área agrícola (4 + 2 + 1 = 7 px)
    assert act["px_agricolas"] == 7 and act["pct_maiz"] == pytest.approx(100 * 4 / 7, abs=1e-4)
    assert a["pct_centeno"] == pytest.approx(100 * 2 / 7, abs=1e-4)
    for col in ce.PCT_CLASES:
        assert a[col] == act[col] or (np.isnan(a[col]) and np.isnan(act[col]))
    # el 0 deja de contar como válido: 8 de 10 px
    assert act["frac_pixeles_validos"] == 1 and a["frac_pixeles_validos"] == pytest.approx(0.8)
    assert d.loc[("A_grupos", 2), "frac_pixeles_validos"] == pytest.approx(0.75)
    # B: 27 y 58 salen del denominador
    assert b["px_agricolas"] == 4 and b["pct_maiz"] == 100


def test_efecto_descarta_condados_sin_pixeles():
    c = np.zeros((3, 256), np.int64)
    c[1, 1] = 5
    d = ce.efecto(c)
    assert set(d["id"]) == {1}
