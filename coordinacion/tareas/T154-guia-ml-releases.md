---
id: T154
titulo: 'Guía para ML: qué trae cada release publicado y cómo juntarlos (`docs/guia_tablas.md`)'
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15T14:14Z
actualizada: 2026-11-15T14:14Z
---

## Qué hacer

El equipo de ML va a recibir varios releases por grupo de estados: `datos-oh-ne-mn`, `datos-mo-wi-sd` y después
`datos-ks` y `datos-nd`. Actualizá `docs/guia_tablas.md` y `docs/estructura_csv.md` con lo que hace falta para
usarlos juntos:

- qué estados, años y paquetes trae cada release;
- cómo juntarlos con `scripts/unir_estados.py`;
- qué columnas cambian de cobertura entre estados: rendimiento de ND desde 2018, riego en NE y KS, `ndvi_soja` de
  WI casi vacío y `flag_nass` = `0_sin_cosecha_grano` (T148).

Tomá cada dato de los QA (`docs/qa/*.md`) y de los data cards. Sin números a mano.

## Terminada cuando

PR con CI en verde y lo que se encontró en el cuerpo del PR.

## Notas
