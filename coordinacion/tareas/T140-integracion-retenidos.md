---
id: T140
titulo: 'Rama de integración con todos los PR retenidos (117 a 126 y los que sigan): conflictos y pruebas'
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15T09:59
actualizada: 2026-11-15T09:59
---

## Qué hacer

Hay unos diez PR abiertos con código listo que esperan el OK del humano (cada uno dice "Espera el OK de
para_decidir #N"; la fila de `coordinacion/para_decidir.md` dice "código listo en PR N"). Varios tocan los mismos
archivos (`docs/datasets/glosario_en.csv`, `docs/datasets/cultivos.md`, `src/cultivos/process.py`,
`src/cultivos/data_card.py`, `scripts/entregar.py`), así que si el humano dice que sí a varios, unirlos uno por uno
va a dar conflictos.

1. Armá una rama `integracion/retenidos` desde `main` y uní, en orden de número, todos los PR abiertos cuyo
   cuerpo empiece con "Espera el OK de para_decidir" (`gh pr list --state open`). Resolvé los conflictos sin
   perder nada de ninguno de los dos lados.
2. Corré `python -X utf8 -m pytest -q tests` y arreglá lo que rompa la combinación (no lo que ya estaba roto en
   cada PR por separado; eso anotalo).
3. Abrí un PR **en borrador** (`gh pr create --draft`) de `integracion/retenidos` a `main` que diga al principio
   "No unir: es para probar la combinación de los PR retenidos". En el cuerpo: una tabla con cada PR, su fila de
   `para_decidir.md`, qué archivos chocaron y cómo se resolvió, y el resultado de las pruebas.
4. Si después de abrirlo aparecen PR retenidos nuevos, sumalos a la misma rama y actualizá la tabla.

No toques `main` ni los PR originales. No cambies código de los PR más allá de lo necesario para resolver
conflictos.

## Terminada cuando

El PR en borrador abierto con la tabla y las pruebas en verde (o la lista exacta de lo que falla).

## Notas
