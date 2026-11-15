---
id: T131
titulo: SEETileDrain por píxel en el paquete `lotes` (código listo, espera OK)
estado: tomada
plan_minimo: pro
maquina: pro-1
estados: []
depende_de: []
rama: null
creada: 2026-11-15T09:24
actualizada: 2026-11-15 09:31
---

## Qué hacer

Fila 5 de `para_decidir.md` y `docs/research/drenaje_tile.md` (T017): sumar al paquete `lotes` (`src/lotes/`) las
columnas `tile_prob_seetiledrain` y `tile_seetiledrain` por píxel de 30 m dentro de cada lote (grilla de
`data/reference/mascara_agricola.tif`, EPSG:5070), según lo que diga `loop/spec/entregables.yaml` del paquete
`lotes` para el drenaje opcional. La descarga es de ~3,1 GB una vez: el código la deja lista, pero **bajá solo
la tesela o el recorte que cubra un lote** para probar. Fila en `manifest.csv`. Pruebas sin red con un raster
chico. Data card de `lotes`: fuente, licencia y supuestos del remuestreo.

**El PR no se une hasta que el humano diga que sí** a la fila 5 de `coordinacion/para_decidir.md` (esquema
nuevo). Escribí al principio del cuerpo del PR: "Espera el OK de para_decidir #5; no unir antes".
No cambies ninguna columna que ya existe; no toques `src/common/` ni `config/`.

## Terminada cuando

El código, las pruebas sin red y el data card en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 09:31 · pro-1: tomada
