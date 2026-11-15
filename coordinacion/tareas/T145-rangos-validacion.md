---
id: T145
titulo: Rangos físicos de rendimiento para los 10 estados en `src/common/validacion.py` y el spec (código listo,
  espera OK)
estado: tomada
plan_minimo: pro
maquina: pro-2
estados: []
depende_de: []
rama: null
creada: 2026-11-15T10:17
actualizada: 2026-11-15 10:32
---

## Qué hacer

Fila 24 de `para_decidir.md` y `docs/research/rangos_estados_nuevos.md` (T048): poner en `src/common/validacion.py`
los rangos propuestos (maíz 5–300, soja 2–100, trigo de invierno 5–130, `tmin_c` diaria −55–40, **avena 2–200**,
como corrige la fila). Mirá también los research de MO/WI/SD, ND, MI y KY (`rangos_estados_nuevos*`,
`nass_mo_wi_sd*`, `eventos_extremos_*_rend*`) por si algún mínimo o máximo real de esos estados queda afuera, y
proponé el ajuste citando la fuente. Corré `validar_csv()` con los releases publicados antes y después.

`loop/spec/entregables.yaml` es del loop autónomo y no se toca mientras corre: dejá en el PR el cambio que haría
falta ahí, como texto, para que el humano lo aplique.

**El PR no se une hasta que el humano diga que sí** a la fila #24 de `coordinacion/para_decidir.md`. Escribí al
principio del cuerpo del PR: "Espera el OK de para_decidir #24; no unir antes". Este PR **sí** puede tocar
`src/common/` (o `config/`, si se indica abajo) porque es justamente la propuesta que el humano tiene que aprobar:
dejá en el cuerpo del PR la lista exacta de lo que cambia en esos directorios.

## Terminada cuando

El cambio, las pruebas sin red y la documentación en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 10:32 · pro-2: tomada
