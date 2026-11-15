---
id: T085
titulo: 'Data card de vegetación: cobertura de ndvi_maiz y ndvi_soja por estado y año'
estado: tomada
plan_minimo: pro
maquina: pro-2
estados:
- OH
- NE
- MN
depende_de: []
rama: null
creada: 2026-11-15T06:27
actualizada: 2026-11-15 06:31
---

## Qué hacer

De `docs/qa/oh_ne_mn.md` (T073), problema 3: en `docs/datasets/vegetacion.md`, una tabla con el % de
condado-fechas con `ndvi_maiz` y `ndvi_soja` por estado y año (2008–2025), y la explicación: el umbral de 75 %
de pureza del píxel de 250 m deja pocos píxeles en lotes chicos (OH) y en la soja del oeste. Agregá, como
**propuesta** (sin aplicarla), cuántos condado-fechas se ganarían con un umbral de 50 %, calculado con un script
chico sobre los datos que tengas a mano; si no tenés las máscaras del CDL, decí que no se pudo medir.

## Terminada cuando

El cambio en los data cards en un PR. No cambies código ni esquema.

## Notas
- 2026-11-15 06:31 · pro-2: tomada
