---
id: T148
titulo: 'Rendimiento 0 de NASS sin cosecha para grano: dejarlo vacío con `flag_nass` en `produccion_anual.csv`'
estado: tomada
plan_minimo: pro
maquina: pro-2
estados:
- SD
depende_de: []
rama: null
creada: 2026-11-15T13:47Z
actualizada: 2026-11-15 10:54
---

## Qué pasa

En el release `datos-mo-wi-sd`, 12 filas de maíz del oeste de Dakota del Sur (Harding 46063, Lawrence 46081 y
Stanley 46117, años 2000-2006) tienen `rend_bu_ac` = 0. En el archivo crudo de Quick Stats
(`data/raw/cultivos/nass/qs.crops_*.txt.gz`) NASS publica `CORN, GRAIN - YIELD, MEASURED IN BU / ACRE` = 0 y
**no** publica `CORN, GRAIN - ACRES HARVESTED` para esos años: todo el maíz del condado fue a silo
(`CORN, SILAGE - ACRES HARVESTED` > 0). Ese 0 no es un rendimiento: es "no hubo cosecha para grano". Por la
sección 4 del CLAUDE.md los valores de relleno van vacíos.

## Qué hacer

1. En `src/cultivos/process.py` (no en `src/common/`): cuando NASS da rendimiento 0 y la superficie cosechada
   para grano falta o es 0, dejá `rend_bu_ac` (y `rend_kgha`) vacío y guardá en `flag_nass` un código que lo diga
   (proponé el nombre, por ejemplo `0_sin_cosecha_grano`, y documentalo en el data card). No toques las filas con
   rendimiento bajo pero real (Haakon, Oglala Lakota y Pennington tienen 2,9 a 18,3 bu/ac con superficie
   cosechada: quedan como están).
2. Revisá si el mismo patrón aparece en los otros estados publicados (`datos-ia-il-in` o el checkout principal,
   `datos-oh-ne-mn`, Kansas si está) y en los otros cultivos (soja, trigo, avena). Contá cuántas filas cambian por
   estado y cultivo y ponelo en el PR.
3. Prueba sin red con un caso armado a mano (rendimiento 0 sin superficie → vacío con flag; rendimiento 0 con
   superficie 0 → vacío con flag; rendimiento 4,5 con superficie → queda).
4. Actualizá `docs/datasets/cultivos.md` (sección "Problemas conocidos": ya tiene una nota en el release de
   MO/WI/SD que dice que la corrección va en una tarea aparte; reemplazala por la regla nueva).

No cambia columnas ni tipos: solo valores que hoy son 0 pasan a vacío. Las otras columnas de la fila
(`sup_sembrada_ac`, etc.) quedan iguales.

## Terminada cuando

PR con CI en verde, el conteo por estado y cultivo en el cuerpo, y la prueba nueva. max-1 vuelve a publicar
`cultivos` de MO/WI/SD (y los otros estados si cambian) después de unirlo.

## Notas
- 2026-11-15 10:54 · pro-2: tomada
