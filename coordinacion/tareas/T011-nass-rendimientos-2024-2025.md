---
id: T011
titulo: 'Research: rendimientos de condado de NASS 2024 y 2025 en los 7 estados'
estado: libre
plan_minimo: pro
maquina: null
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
creada: 2026-11-15 01:15
actualizada: 2026-11-15 01:15
---

## Qué hacer

NASS suspendió y después repuso las estimaciones por condado de 2024, y las de 2025 pueden no estar
publicadas todavía. Para los 7 estados y los cultivos de `config.yaml` (maíz, soja, trigo de invierno, avena):
qué años de rendimiento, superficie sembrada y cosechada por condado hay en Quick Stats, cuántos condados
tienen dato por estado y año en 2020–2025, y cuántos están ocultos con `(D)` o en "OTHER (COMBINED)
COUNTIES". Usar la base completa de Quick Stats (`qs.crops_*.txt.gz`, la baja `src/cultivos/download.py`) o
la API si hay `NASS_API_KEY`. Escribir `docs/research/nass_2024_2025.md` con el formato de research (sección
8 del CLAUDE.md), con una tabla por estado y año.

## Terminada cuando

El research escrito, con fuentes, fecha de consulta y confianza, en un PR.

## Notas
