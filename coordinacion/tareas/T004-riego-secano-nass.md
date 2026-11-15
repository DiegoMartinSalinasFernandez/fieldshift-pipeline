---
id: T004
titulo: Separar riego y secano de NASS en NE y KS
estado: hecha
plan_minimo: pro
maquina: pro-2
estados:
- NE
- KS
depende_de: []
rama: null
creada: 2026-11-14 23:59
actualizada: 2026-11-15 02:13
---

## Qué hacer

En Nebraska y Kansas una parte grande del maíz y la soja se riega, y el rendimiento de `ALL PRODUCTION
PRACTICES` mezcla las dos cosas. Investigar en la base de NASS los `prodn_practice_desc` `IRRIGATED` y
`NON-IRRIGATED` por condado (qué años y cultivos tienen dato, cuánto ocultan con `(D)`), escribir la respuesta
en `docs/research/riego_nass.md` con el formato de research y proponer cómo agregarlo a
`produccion_anual.csv`. **Agregar columnas o filas cambia el esquema: proponerlo y esperar el OK del humano
antes de tocar `src/cultivos/`.**

## Terminada cuando

Research escrito con fuentes y confianza, y una propuesta concreta de columnas aprobada o rechazada.

## Notas
- 2026-11-15 02:00 · pro-2: tomada
- 2026-11-15 02:13 · pro-2: terminada por el trabajador: PR #4, falta la revisión de max-1
