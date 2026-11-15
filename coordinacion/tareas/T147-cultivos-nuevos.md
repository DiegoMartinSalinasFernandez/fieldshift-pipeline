---
id: T147
titulo: Sumar cultivos nuevos al esquema (maíz para silo, trigo de primavera, cebada, girasol, canola, frijol seco)
  (código listo, espera OK)
estado: tomada
plan_minimo: pro
maquina: pro-1
estados:
- ND
- MN
- SD
- WI
depende_de: []
rama: null
creada: 2026-11-15T10:17
actualizada: 2026-11-15 10:17
---

## Qué hacer

Fila 34 de `para_decidir.md` (y la 29, que es un subconjunto) y `docs/research/propuesta_cultivos.md` (T103), con
`propuesta_cultivos_items.csv`: implementá lo que propone el research para sumar al esquema maíz para silo, trigo de
primavera (y durum, si el research lo recomienda), cebada, girasol aceitero, canola y frijol seco:
`config/config.yaml` (lista de cultivos), `src/common/conversiones.py` (unidades: lb, cwt, ton), `validacion.py`
(rangos), `GRUPOS_CDL`, las columnas nuevas de `produccion_anual.csv` (`rend_lb_ac`, `produccion_lb`,
`produccion_cwt`, `rend_ton_ac`, `produccion_ton`) y `rotacion_anual.csv`. Los cultivos de hoy tienen que salir
idénticos: comprobalo con un release publicado.

Este PR puede tocar `config/config.yaml` y `src/common/`. Probalo con un estado donde estos cultivos pesen (SD o
MN, si tenés el archivo de Quick Stats) y contá filas y faltantes por cultivo. Si es demasiado para una sola
tarea, hacé primero maíz para silo y trigo de primavera (fila 29) y dejá el resto anotado.

**El PR no se une hasta que el humano diga que sí** a la fila #34 y #29 de `coordinacion/para_decidir.md`. Escribí al
principio del cuerpo del PR: "Espera el OK de para_decidir #34 y #29; no unir antes". Este PR **sí** puede tocar
`src/common/` (o `config/`, si se indica abajo) porque es justamente la propuesta que el humano tiene que aprobar:
dejá en el cuerpo del PR la lista exacta de lo que cambia en esos directorios.

## Terminada cuando

El cambio, las pruebas sin red y la documentación en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 10:17 · pro-1: tomada
