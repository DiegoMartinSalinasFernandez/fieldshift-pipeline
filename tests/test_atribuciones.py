"""Pruebas de src/common/atribuciones.py (T146): textos de atribución en data cards y notas del release.

Sin red y sin leer data/. Los textos se comparan con los que recomienda docs/research/licencias_fuentes.md.

Correr desde la raíz:  .venv/bin/python -X utf8 -m pytest tests/test_atribuciones.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.common import atribuciones as at  # noqa: E402

CARDS = REPO / "docs" / "datasets"
RESEARCH = REPO / "docs" / "research" / "licencias_fuentes.md"


def test_textos_del_research():
    research = " ".join(RESEARCH.read_text(encoding="utf-8").split())  # el research corta las líneas a 120
    assert at.COPERNICUS_HLS in research
    assert "Contains modified Copernicus Sentinel data" in at.COPERNICUS_HLS
    assert "CC BY 4.0" in at.COCORAHS_CC_BY and "https://creativecommons.org/licenses/by/4.0/" in at.COCORAHS_CC_BY
    assert "aggregated to county-month by the team" in research


def test_paquetes_con_y_sin_atribucion():
    assert at.lineas("lotes") == (at.COPERNICUS_HLS,)
    assert at.lineas("validacion") == (at.COCORAHS_CC_BY,)
    assert at.lineas("clima") == ()
    assert at.bloque_card("clima") == ""


def test_poner_en_card_inserta_antes_de_la_primera_seccion_y_es_idempotente():
    card = "# Data card — lotes\n\nIntro.\n\n## Fuentes\n\n- algo\n"
    una = at.poner_en_card(card, "lotes")
    assert una.index(at.INICIO) < una.index("## Fuentes")
    assert una.index("Intro.") < una.index(at.INICIO)
    assert at.COPERNICUS_HLS in una
    assert at.poner_en_card(una, "lotes") == una


def test_poner_en_card_reemplaza_texto_viejo():
    viejo = f"# x\n\n{at.INICIO}\n## Atribución\n\n> texto viejo\n{at.FIN}\n\n## Otra\n"
    nuevo = at.poner_en_card(viejo, "validacion")
    assert "texto viejo" not in nuevo
    assert nuevo.count(at.INICIO) == 1 and at.COCORAHS_CC_BY in nuevo


def test_poner_en_card_sin_secciones_y_sin_atribucion():
    assert at.poner_en_card("# x\n\ntexto\n", "lotes").endswith(at.FIN + "\n")
    assert at.poner_en_card("# x\n\n## A\n", "clima") == "# x\n\n## A\n"


def test_cards_del_repo_estan_al_dia():
    for paq in ("lotes", "validacion"):
        texto = (CARDS / f"{paq}.md").read_text(encoding="utf-8").replace("\r\n", "\n")
        assert at.bloque_card(paq) in texto, paq
        assert at.poner_en_card(texto, paq) == texto, paq


def test_seccion_release():
    assert at.seccion_release(["clima", "agua"]) == ""
    s = at.seccion_release(["validacion", "clima", "lotes"])
    assert s.startswith("## Attribution / Atribución\n\n")
    assert s.index("`lotes`") < s.index("`validacion`")
    assert at.COPERNICUS_HLS in s and at.COCORAHS_CC_BY in s
