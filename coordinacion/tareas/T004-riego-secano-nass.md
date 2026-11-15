---
id: T004
titulo: Separar riego y secano de NASS en NE y KS
estado: libre
plan_minimo: pro
maquina: null
estados:
- NE
- KS
depende_de: []
rama: null
creada: 2026-11-14 23:59
actualizada: 2026-11-14 23:59
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
