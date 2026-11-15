---
id: T032
titulo: 'Research: superficie con siembra prevenida por condado (FSA y RMA)'
estado: hecha
plan_minimo: pro
maquina: pro-4
estados:
- IA
- IL
- IN
- OH
- NE
- MN
- KS
depende_de: []
rama: null
creada: 2026-11-15 03:00
actualizada: 2026-11-15 03:04
---

## Qué hacer

En el Corn Belt el exceso de agua en primavera impide sembrar (2019 fue récord). Averiguá:

- los datos de FSA "Crop Acreage Data" (siembra prevenida, *prevented planting*) por condado y cultivo: años,
  formato, dónde se bajan y columnas;
- qué agrega RMA sobre siembra prevenida (causa de pérdida y tipo de cobertura) frente a FSA, sin repetir lo
  de `docs/research/rma_causa_perdida.md`;
- si sirve como target de riesgo por exceso de agua y cómo se uniría por `fips, anio`.

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets grandes ni toques `src/` o `data/`.

Escribí `docs/research/siembra_prevenida.md`.

## Terminada cuando

El research en un PR, con una propuesta concreta (que el humano decide).

## Notas
- 2026-11-15 02:53 · pro-4: tomada
- 2026-11-15 03:04 · pro-4: terminada por el trabajador: PR #27, falta la revisión de max-1
