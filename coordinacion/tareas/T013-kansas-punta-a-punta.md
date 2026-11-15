---
id: T013
titulo: 'Kansas de punta a punta: bajar, procesar y publicar datos-ks'
estado: tomada
plan_minimo: max
minutos: 400
maquina: max-2
estados:
- KS
depende_de: []
rama: null
creada: 2026-11-15 01:25
actualizada: 2026-11-15 03:14
---

## Qué hacer

En la máquina Max con `FIELDSHIFT_ESTADOS=KS` (105 condados), de punta a punta y sin datos previos:

1. **Base:** `src/base/download.py` y `src/base/process.py` (salen `data/reference/condados.*` y `anios.csv`
   de Kansas).
2. **Descargas**, siguiendo la sección 9 del CLAUDE.md. Conviene correrlas en dos carriles en segundo plano y
   revisar solo el final de cada log:
   - `clima` (POWER, y `imerg` aparte) → `suelo_terreno` → `cultivos` → `economia` → `validacion`;
   - `agua` → `vegetacion` → `nldas` → `vegetacion/download_nldas.py` → `paisaje`.
   La base de NASS (`qs.crops_*`, 1,6 GB) y GRACE-DA-DM (todo EE.UU.) son nacionales: se bajan una vez.
   Kansas completo ocupa unos 6 a 8 GB, ya aprobado por el humano junto con el estado.
3. **Procesar** con los `process.py` de cada paquete, en el orden de la sección 9: `cultivos` primero (de ahí
   salen las máscaras del CDL que usa `vegetacion`). Cada CSV tiene que pasar `validar_csv()`. Lo que falle
   por un supuesto de IA/IL/IN, arreglalo en el código (commits chicos, en esta rama) sin cambiar el esquema
   ni `src/common/`. Si no es directo, anotalo y seguí con el resto de los paquetes.
4. **Publicar** con `scripts/entregar.py` (`FIELDSHIFT_ESTADOS=KS`): crea el release `datos-ks` con un zip por
   paquete. Si `gh` no puede subirlo, dejá los zips en `data/entregas/` y anotalo.
5. Actualizar los data cards de los paquetes tocados con la cobertura real de Kansas.

No hacer: `lotes` (es solo para los 10 lotes de demostración), `merge.py` (lo hace max-1 en T008) ni separar
riego y secano (T004).

## Terminada cuando

El release `datos-ks` con los paquetes que procesan, un PR con los arreglos de código y, en el resultado, una
tabla por paquete: bajado sí/no, procesado sí/no, filas, y qué falló y por qué.

## Notas
- 2026-11-15 03:14 · max-2: tomada
