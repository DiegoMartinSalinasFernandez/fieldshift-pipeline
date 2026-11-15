---
id: T085
titulo: 'Data card de vegetación: cobertura de ndvi_maiz y ndvi_soja por estado y año'
estado: bloqueada
plan_minimo: pro
maquina: pro-2
estados:
- OH
- NE
- MN
depende_de: []
rama: null
creada: 2026-11-15T06:27
actualizada: 2026-11-15 06:43
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
- 2026-11-15 06:34 · pro-2: soltada: quedó a medias, PR #76. INCOMPLETA: falta la tabla de estado por año (2008–2025) y la medición del umbral de 50 %. Esta máquina (pro-2, NE y KS) no tiene vegetacion_16d.csv, las máscaras del CDL ni MOD13Q1 de OH, NE y MN, y no pudo bajar el release. Para completarla, correr `scripts/cobertura_ndvi_cultivo.py --umbral 0.5` 
- 2026-11-15 06:34 · pro-2: tomada
- 2026-11-15 06:35 · pro-2: soltada: quedó a medias, PR #76 actualizado. INCOMPLETA: el data card tiene la explicación, los rangos por estado del QA y la propuesta del 50 %, pero falta la tabla estado × año (2008–2025) y medir el umbral del 50 %. pro-2 (NE, KS) no tiene vegetacion_16d.csv, las máscaras del CDL ni MOD13Q1 de OH, NE y MN, y en esta corrida no tuvo permiso 
- 2026-11-15 06:35 · pro-2: tomada
- 2026-11-15 06:37 · pro-2: soltada: quedó a medias, PR #76 actualizado. INCOMPLETA: falta la tabla estado × año (2008–2025) de OH, NE y MN y medir el umbral del 50 %. pro-2 no tiene `vegetacion_16d.csv`, las máscaras del CDL ni MOD13Q1 de esos estados, y esta corrida no tuvo permiso para bajar el release `datos-oh-ne-mn` (ni con `gh` ni con `curl`). La tiene que termina
- 2026-11-15 06:38 · pro-2: tomada
- 2026-11-15 06:39 · pro-2: soltada: quedó a medias, PR #76 actualizado. INCOMPLETA: falta la tabla estado × año (2008–2025) de OH, NE y MN y medir el umbral del 50 %. pro-2 (NE, KS) no tiene vegetacion_16d.csv, las máscaras del CDL ni MOD13Q1 de esos estados, y en esta corrida (la quinta) tampoco tuvo permiso para bajar el release `datos-oh-ne-mn` con `gh`. Las únicas e
- 2026-11-15 06:39 · pro-2: tomada
- 2026-11-15 06:40 · pro-2: bloqueada: el trabajo quedó en la rama tarea/T085-auto pero push falló: To github.com:DiegoMartinSalinasFernandez/fieldshift-pipeline.git
 ! [rejected]        tarea/T085-auto -> tarea/T085-auto (stale info)
error: failed to push some refs to 'github.com:DiegoMartinSalinasFernandez/fieldshift-pipeline.git'
- 2026-11-15 06:42 · max-1: max-1 tiene vegetacion_16d.csv de OH/NE/MN en su worktree: completa la tabla por año cuando termine de reprocesar 2014 (faltaba enero–abril de 2014 en el release).
- 2026-11-15 06:42 · max-1: max-1 tiene vegetacion_16d.csv de OH/NE/MN en su worktree: completa la tabla por año cuando termine de reprocesar 2014 (faltaba enero–abril de 2014 en el release).
- 2026-11-15 06:43 · max-1: max-1 tiene vegetacion_16d.csv de OH/NE/MN en su worktree: completa la tabla por año cuando termine de reprocesar 2014 (faltaba enero–abril de 2014 en el release).
- 2026-11-15 06:43 · max-1: max-1 tiene vegetacion_16d.csv de OH/NE/MN en su worktree: completa la tabla por año cuando termine de reprocesar 2014 (faltaba enero–abril de 2014 en el release).
- 2026-11-15 06:43 · max-1: max-1 tiene vegetacion_16d.csv de OH/NE/MN en su worktree: completa la tabla por año cuando termine de reprocesar 2014 (faltaba enero–abril de 2014 en el release).
