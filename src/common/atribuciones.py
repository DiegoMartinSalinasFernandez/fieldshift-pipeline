"""Textos de atribución obligatoria por paquete: un solo lugar para los data cards y las notas del release.

Los textos salen de `docs/research/licencias_fuentes.md` (T060, para_decidir #30):

- `lotes`: el Legal Notice de Copernicus pide "Contains modified Copernicus Sentinel data [Year]" cuando los datos
  de Sentinel se adaptan o modifican (HLS S30 es Sentinel-2 reprocesado por NASA, y de ahí salen los índices). El
  rango 2016–2025 es el de las columnas HLS S30 de `docs/datasets/lotes.md`.
- `validacion`: CoCoRaHS publica sus datos con licencia CC BY 4.0; la licencia pide crédito, enlace a la licencia
  y decir si hubo cambios (la agregación a condado y mes lo es).

Si cambia un texto, se cambia acá: `src/lotes/process.py`, `src/validacion/process.py` y `scripts/entregar.py` lo
toman de este módulo.
"""
from __future__ import annotations

import re

COPERNICUS_HLS = "Contains modified Copernicus Sentinel data 2016–2025, processed by NASA (HLS S30 v2.0)."
COCORAHS_CC_BY = ("Community Collaborative Rain, Hail and Snow Network (CoCoRaHS), Colorado Climate Center, "
                  "https://www.cocorahs.org. Licensed under CC BY 4.0 "
                  "(https://creativecommons.org/licenses/by/4.0/). Data aggregated to county-month by the team.")

# paquete -> líneas de atribución (en inglés, tal como las recomienda el research).
ATRIBUCIONES: dict[str, tuple[str, ...]] = {
    "lotes": (COPERNICUS_HLS,),
    "validacion": (COCORAHS_CC_BY,),
}

INICIO = "<!-- ATRIBUCION:INICIO -->"
FIN = "<!-- ATRIBUCION:FIN -->"


def lineas(paquete: str) -> tuple[str, ...]:
    """Líneas de atribución del paquete (vacío si no tiene ninguna obligatoria)."""
    return ATRIBUCIONES.get(paquete, ())


def bloque_card(paquete: str) -> str:
    """Sección `## Atribución` del data card, entre marcas para poder reemplazarla. Vacío si no hay atribución."""
    ls = lineas(paquete)
    if not ls:
        return ""
    cuerpo = "\n".join(f"> {l}" for l in ls)
    return (f"{INICIO}\n## Atribución\n\nTexto obligatorio al distribuir o mostrar estos datos (copiar tal cual; "
            f"ver `docs/research/licencias_fuentes.md`):\n\n{cuerpo}\n{FIN}")


def poner_en_card(texto: str, paquete: str) -> str:
    """Devuelve `texto` con la sección de atribución al día.

    Si el card ya tiene el bloque entre marcas, lo reemplaza; si no, lo inserta antes del primer `## ` que no sea el
    título (o al final si no hay ninguno). Idempotente.
    """
    bloque = bloque_card(paquete)
    patron = re.compile(re.escape(INICIO) + r".*?" + re.escape(FIN), re.S)
    if patron.search(texto):
        return patron.sub(lambda _: bloque, texto)
    if not bloque:
        return texto
    m = re.search(r"^## ", texto, re.M)
    if m is None:
        return texto.rstrip("\n") + "\n\n" + bloque + "\n"
    return texto[:m.start()] + bloque + "\n\n" + texto[m.start():]


def seccion_release(paquetes: list[str]) -> str:
    """Sección `## Attribution / Atribución` de las notas del release, o vacío si ningún paquete la necesita."""
    filas = [f"- `{p}`: {l}" for p in sorted(paquetes) for l in lineas(p)]
    if not filas:
        return ""
    return "## Attribution / Atribución\n\n" + "\n".join(filas) + "\n\n"
