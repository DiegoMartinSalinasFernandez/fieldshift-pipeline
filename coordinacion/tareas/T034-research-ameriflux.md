---
id: T034
titulo: 'Research: sitios AmeriFlux del Corn Belt para validar la ET'
estado: tomada
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
creada: 2026-11-15 03:20
actualizada: 2026-11-15 03:04
---

## Qué hacer

T030 (`docs/research/agua_por_cultivo.md`) propone validar la ET de MODIS, ECOSTRESS y NLDAS con torres de flujo.
Averiguá, sin bajar datos:

- qué sitios de AmeriFlux hay en cultivos de los 7 estados (US-Ne1, US-Ne2, US-Ne3, US-Bo1, US-Br1, US-Ro1… y
  los que encuentres), con cultivo por año, años con datos, variables (LE, ET, GPP) y versión (FLUXNET o BASE);
- cómo se bajan (si piden registro o aceptar una política de uso, y cuál es la licencia, por ejemplo CC-BY-4.0);
- qué condado (`fips`) tiene cada torre y qué columnas de nuestros CSV se podrían comparar.

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets grandes ni toques `src/` o `data/`.

Escribí `docs/research/ameriflux.md`, con una tabla por sitio.

## Terminada cuando

El research en un PR, con una propuesta de qué sitios usar. La descarga, si pide registro, la hace el humano.

## Notas
- 2026-11-15 03:04 · pro-4: tomada
