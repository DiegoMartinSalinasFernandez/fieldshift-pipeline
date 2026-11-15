---
id: T140
titulo: 'Rama de integración con todos los PR retenidos (117 a 126 y los que sigan): conflictos y pruebas'
estado: tomada
plan_minimo: pro
maquina: pro-2
estados: []
depende_de: []
rama: null
creada: 2026-11-15T09:59
actualizada: 2026-11-15 10:28
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
- 2026-11-15 10:11 · pro-2: tomada
- 2026-11-15 10:16 · pro-2: soltada: quedó a medias, PR #133. INCOMPLETA: la combinación de los 15 PR retenidos (117–131) está resuelta y probada (416 pasan), pero solo como simulación. En esta sesión `git merge` y `gh` estaban bloqueados por permisos, y el trabajador no puede cambiar de rama ni abrir PR. Falta crear la rama `integracion/retenidos`, hacer los 
- 2026-11-15 10:17 · pro-2: tomada
- 2026-11-15 10:20 · max-1: max-1 armó la rama real integracion/retenidos con la tabla del PR 133 (merges de los PR 117-132; 414 pruebas pasan) y abrió el PR en borrador 135. PR 133 cerrado.
- 2026-11-15 10:20 · pro-2: terminada: Hecha por max-1: PR en borrador 135 (integracion/retenidos).
- 2026-11-15 10:20 · pro-2: soltada: quedó a medias, PR #136. INCOMPLETA: la combinación de los 16 PR retenidos (117–132) está resuelta y probada (422 pasan), pero sigue siendo una simulación. En las dos sesiones `git merge`, `git worktree` y `gh` estuvieron bloqueados por permisos, y el trabajador no puede cambiar de rama ni abrir PR. Falta crear la rama `int
- 2026-11-15 10:21 · pro-2: tomada
- 2026-11-15 10:23 · pro-2: soltada: quedó a medias, PR #137. INCOMPLETA: falta sumar el PR 134 (T141) a la rama real `integracion/retenidos` y agregar su fila al PR 135. El merge está probado (limpio, 430 pruebas pasan), pero esta sesión no puede cambiar de rama, crear commits en otra rama, hacer push ni usar `gh`. Son 4 comandos y están en `docs/qa/integraci
- 2026-11-15 10:23 · pro-2: tomada
- 2026-11-15 10:24 · pro-2: soltada: quedó a medias, PR #137 actualizado. INCOMPLETA: falta sumar el PR 134 (T141, para_decidir #21) a la rama real `integracion/retenidos` y agregar su fila a la tabla del PR en borrador 135. La unión está probada y sale limpia. El trabajador no puede cambiar de rama, hacer push ni usar `gh` (`gh` además está bloqueado por permisos), así q
- 2026-11-15 10:25 · pro-2: tomada
- 2026-11-15 10:26 · pro-2: soltada: quedó a medias, PR #137 actualizado. INCOMPLETA: falta sumar el PR 134 (T141, para_decidir #21) a la rama real `integracion/retenidos` y agregar su fila a la tabla del PR en borrador 135. El merge sigue saliendo limpio (`git merge-tree` da el árbol `2a4377d2b5`). En esta sesión se pudo crear un worktree, pero `git merge`, `gh` y el pus
- 2026-11-15 10:26 · pro-2: tomada
- 2026-11-15 10:27 · pro-2: soltada: quedó a medias, PR #137 actualizado. INCOMPLETA: falta sumar el PR 134 (T141, para_decidir #21) a la rama real `integracion/retenidos` y agregar su fila a la tabla del PR en borrador 135. El merge sigue saliendo limpio (`git merge-tree` da el árbol `2a4377d2b5`). En esta sesión también estuvieron bloqueados por permisos `git worktree a
- 2026-11-15 10:28 · pro-2: tomada
