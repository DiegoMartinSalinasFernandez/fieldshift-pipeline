---
id: T047
titulo: 'Research: Crop Sequence Boundaries para los 7 estados'
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
creada: 2026-11-15 04:05
actualizada: 2026-11-15 04:02
---

## Qué hacer

Para `rotacion_secuencia.csv` y el paquete `lotes`, averiguá sin bajar los archivos grandes:

- qué ventanas de CSB hay publicadas (2008–2015 … 2018–2025) y si la última ya cubre 2025;
- cómo se baja por estado (archivo nacional o por estado, formato, tamaño aproximado para OH, NE, MN y KS);
- si los campos (`CSBID`, `CSBACRES`, `CDL<año>`, etc.) son los mismos en todas las ventanas;
- problemas conocidos: lotes con riego de pivote en NE y KS, lotes partidos por límites de condado.

Formato de research de la sección 8 del CLAUDE.md. Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes datasets grandes ni toques `data/`.

Escribí `docs/research/csb_siete_estados.md`.

## Terminada cuando

El research en un PR.

## Notas
- 2026-11-15 04:02 · pro-4: tomada
