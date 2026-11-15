---
id: T044
titulo: 'Research: candidatos para sumar estados (SD, WI, MO, MI)'
estado: libre
plan_minimo: pro
maquina: null
estados:
- SD
- WI
- MO
- MI
depende_de: []
rama: null
creada: 2026-11-15 03:45
actualizada: 2026-11-15 03:45
---

## Qué hacer

El humano va a decidir si suma estados después de los 7 actuales. Para cada candidato (Dakota del Sur, Wisconsin,
Misuri, Míchigan, y otro si lo justificás):

- cantidad de condados y área sembrada de maíz y soja (NASS, promedio 2020–2024) frente a los 7 actuales;
- cobertura de rendimientos de condado en NASS 2000–2025 (cuántos condados con dato por año, peso de
  "OTHER (COMBINED) COUNTIES" y de `(D)`);
- qué cambia respecto de los 7: riego, doble cultivo, cultivos que habría que sumar a `config/` (por ejemplo
  trigo de primavera en SD o papa en WI), teselas extra de MODIS, gSSURGO disponible;
- tamaño estimado de la descarga (referencia medida: OH+NE+MN ≈ 21 GB, KS ≈ 11 GB) y cuál aporta más para que el
  modelo generalice a zonas nuevas.

Formato de research de la sección 8 del CLAUDE.md. Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes datasets grandes ni toques `data/`.

Escribí `docs/research/proximos_estados.md`. **No cambies `config/`**: es una propuesta para el humano.

## Terminada cuando

El research en un PR, con un orden recomendado.

## Notas
