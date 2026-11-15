---
id: T128
titulo: 'Ventanas de floración y llenado por estado y año en `clima_anual.csv`: código listo, espera OK'
estado: tomada
plan_minimo: pro
maquina: pro-5
estados: []
depende_de: []
rama: null
creada: 2026-11-15T09:11
actualizada: 2026-11-15 09:23
---

## Qué hacer

Implementá la propuesta de T038 (fila 23 de `para_decidir.md`): mantener las columnas de julio y agosto y
**agregar** en `clima_anual.csv` columnas calculadas sobre la ventana real de cada estado y año:
`prec_floracion_maiz_mm`, `tmax_floracion_maiz_c`, `dias_tmax_gt35_floracion_maiz`, `prec_llenado_soja_mm` y las
demás que lista la fila 23 y `docs/research/ventanas_por_estado.md`.

- Las fechas salen de las semanas de Crop Progress (25–75 % *silking* del maíz; 50 % *setting pods* → 25 %
  *dropping leaves* de la soja). Mirá si `src/cultivos` ya baja esas etapas para `fenologia_estado.csv`; si no,
  reusá la lectura de `docs/research/ventanas_por_estado.py` (con el arreglo de T116) o la API de Quick Stats,
  y dejalo en `src/clima/` o `src/cultivos/` según convenga, documentado.
- Estado-años sin cruce (ver la lista del research): celda vacía, nunca la ventana de otro año.
- No cambies ninguna columna que ya existe.
- Pruebas sin red: una ventana armada a mano y su suma diaria. Data card de `clima`: las columnas nuevas con su
  definición.

Probalo con un estado (los datos diarios de POWER de cualquier release publicado alcanzan) y contá en el PR
cuánto difieren `prec_floracion_maiz_mm` y `prec_jul_mm` en un año temprano y uno tardío.

**El PR no se une hasta que el humano diga que sí** a la fila 23 de `coordinacion/para_decidir.md` (esquema
nuevo). Escribí al principio del cuerpo del PR: "Espera el OK de para_decidir #23; no unir antes". Así, si
dice que sí al despertarse, está listo para unir y correr en las máquinas Max.

## Terminada cuando

El código, las pruebas y el data card en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 09:23 · pro-5: tomada
