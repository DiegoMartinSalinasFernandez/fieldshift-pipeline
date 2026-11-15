---
id: T010
titulo: Sacar del código y los data cards los supuestos de IA, IL e IN
estado: libre
plan_minimo: pro
maquina: null
estados:
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

El código viene de ResearchAgent, que trabajó solo con Iowa, Illinois e Indiana. Hay textos y quizás lógica
que dan por hecho esos tres estados (por ejemplo "IA, IL e IN", "IA/IL/IN" o "tres estados" en
`src/*/data_card.py`, `src/clima/celdas.py`, `src/ecostress/`, `src/paisaje/process.py`,
`src/suelo_terreno/`). Antes de procesar los estados nuevos (T003):

1. Buscar todos esos supuestos en `src/` (textos, listas fijas de estados o FIPS, cajas o coordenadas fijas,
   comentarios que afirman algo solo cierto para 3 estados, como "todos los condados tienen al menos 3
   centros").
2. Los textos de los data cards: que salgan de `config.yaml` (filtrado por `FIELDSHIFT_ESTADOS`) en lugar de
   estar escritos fijos.
3. La lógica que asuma 3 estados: arreglarla si es directo; si no, describir el problema en el resultado.
4. No cambiar `src/common/` ni el esquema de ningún CSV. No correr los `process.py` completos (no hay datos
   de los estados nuevos en esta máquina): alcanza con que compilen y con probar las funciones tocadas.

## Terminada cuando

Un PR con los arreglos y, en el resultado, la lista de lo que se encontró y lo que queda para T003.

## Notas
