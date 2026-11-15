"""Descarga de MODIS sin red: un token SAS por año con pendientes y código de salida (T055, PR 39).

`src/vegetacion/download.py` pide un token SAS nuevo por cada año que tiene archivos sin bajar y termina con
código 1 si alguno falló. Acá se corre `main()` con todo lo que sale a la red reemplazado por mocks:
`requests.get` (el token), `buscar` (la búsqueda STAC), `bajar_item`, `grupos_bbox` (lee condados.gpkg) y
`registrar_manifest` (escribe en el manifest.csv del repo). `RAW` e `INTERIM` apuntan a una carpeta temporal.

Correr:  python -X utf8 -m unittest tests/test_vegetacion_download.py   (o con pytest)
"""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def cargar():
    spec = importlib.util.spec_from_file_location("t055_vegetacion_download", REPO / "src/vegetacion/download.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dl = cargar()
PROD = "mod13q1"
PREFIJO = dl.PRODUCTOS[PROD]["prefijo"]
TESELAS = ["h10v04", "h11v04"]
BBOX = [-100.0, 40.0, -95.0, 43.0]


def item(anio: int, tesela: str) -> dict:
    return {"id": f"{PREFIJO}.A{anio}001.{tesela}.061.2021000000000", "assets": {}, "properties": {}}


def buscar_falso(coleccion, prefijo, bbox, anio):
    return [item(anio, t) for t in TESELAS]


def respuesta_token(*_a, **_k):
    respuesta_token.n += 1
    r = mock.Mock()
    r.json.return_value = {"token": f"tok{respuesta_token.n}"}
    return r


class DescargaVegetacion(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.raw = self.tmp / "raw"
        respuesta_token.n = 0
        self.get = mock.Mock(side_effect=respuesta_token)
        self.bajar = mock.Mock(return_value="ok")
        parches = [
            mock.patch.object(dl, "RAW", self.raw),
            mock.patch.object(dl, "INTERIM", self.tmp / "interim"),
            mock.patch.object(dl, "grupos_bbox", return_value=[(("NE",), BBOX)]),
            mock.patch.object(dl, "buscar", side_effect=buscar_falso),
            mock.patch.object(dl, "bajar_item", self.bajar),
            mock.patch.object(dl, "registrar_manifest"),
            mock.patch.object(dl.lpdaac, "sesion_earthdata", return_value=None),  # T119: sin LP DAAC
            mock.patch.object(dl, "cargar_config",
                              return_value={"periodo": {"anio_inicio": 2014, "anio_fin": 2016}}),
            mock.patch.object(dl.requests, "get", self.get),
            mock.patch.object(dl.requests, "post", side_effect=AssertionError("no debería ir a la red")),
            mock.patch.object(sys, "argv", ["download.py", PROD, "2014", "2016"]),
        ]
        for p in parches:
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self._tmp.cleanup)

    def ya_bajado(self, anio: int, tesela: str) -> None:
        it = item(anio, tesela)
        p = self.raw / PREFIJO.lower() / str(anio) / f"{it['id']}.tif"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"x")

    def test_un_token_por_anio_con_pendientes(self):
        for t in TESELAS:  # 2014 completo
            self.ya_bajado(2014, t)
        self.ya_bajado(2015, TESELAS[0])  # 2015 a medias, 2016 sin nada
        dl.main()
        self.assertEqual(self.get.call_count, 2)  # 2015 y 2016, ninguno para 2014
        for c in self.get.call_args_list:
            self.assertEqual(c.args[0], dl.SAS)
        # cada año usa su propio token: el de 2015 es el primero pedido, el de 2016 el segundo
        tokens = {c.args[0]["id"].split(".")[1][1:5]: c.args[3] for c in self.bajar.call_args_list}
        self.assertEqual(tokens, {"2015": "tok1", "2016": "tok2"})

    def test_sin_pendientes_no_pide_token(self):
        for a in (2014, 2015, 2016):
            for t in TESELAS:
                self.ya_bajado(a, t)
        dl.main()
        self.get.assert_not_called()
        self.bajar.assert_not_called()

    def test_no_repide_lo_que_ya_esta_en_raw(self):
        self.ya_bajado(2014, TESELAS[0])
        self.ya_bajado(2016, TESELAS[1])
        dl.main()
        pedidos = sorted(c.args[0]["id"] for c in self.bajar.call_args_list)
        esperados = sorted(item(a, t)["id"] for a, t in
                           [(2014, TESELAS[1]), (2015, TESELAS[0]), (2015, TESELAS[1]), (2016, TESELAS[0])])
        self.assertEqual(pedidos, esperados)

    def test_falla_en_un_archivo_sale_con_1(self):
        fallido = item(2015, TESELAS[1])["id"]

        def bajar(it, prod, bbox, token):
            if it["id"] == fallido:
                raise RuntimeError("HTTP 403")
            return "ok"

        self.bajar.side_effect = bajar
        with self.assertRaises(SystemExit) as cm:
            dl.main()
        self.assertEqual(cm.exception.code, 1)
        # los demás años se siguen bajando aunque uno falle
        self.assertEqual(self.bajar.call_count, 6)
        log = (self.tmp / "interim" / "download.log").read_text(encoding="utf-8")
        self.assertIn(f"ERROR {fallido}", log)

    def test_todo_baja_sin_error(self):
        dl.main()  # no levanta SystemExit
        self.assertEqual(self.bajar.call_count, 6)
        self.assertEqual(self.get.call_count, 3)


if __name__ == "__main__":
    unittest.main()


class RellenoLpdaacApagado(DescargaVegetacion):
    """El relleno de LP DAAC pasa los 5 GB: sin FIELDSHIFT_RELLENO_LPDAAC=1 no se pide sesión ni se baja nada."""

    def test_sin_variable_no_rellena(self):
        sesion = mock.Mock(side_effect=AssertionError("no debería pedir sesión de Earthdata"))
        rellenar = mock.Mock(side_effect=AssertionError("no debería rellenar"))
        with mock.patch.dict(os.environ, {}, clear=False),                 mock.patch.object(dl.lpdaac, "sesion_earthdata", sesion),                 mock.patch.object(dl, "rellenar_lpdaac", rellenar):
            os.environ.pop("FIELDSHIFT_RELLENO_LPDAAC", None)
            dl.main()
        sesion.assert_not_called()
        rellenar.assert_not_called()

    def test_con_variable_pide_sesion(self):
        with mock.patch.dict(os.environ, {"FIELDSHIFT_RELLENO_LPDAAC": "1"}):
            dl.main()  # sesion_earthdata está parcheada a None en setUp: avisa y sigue solo con PC
        dl.lpdaac.sesion_earthdata.assert_called_once()
