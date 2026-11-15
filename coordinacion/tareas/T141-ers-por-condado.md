---
id: T141
titulo: Costos del ERS asignados por condado con `reglink.xls` (código listo, espera OK)
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

Fila 21 de `para_decidir.md` y `docs/research/regiones_ers.md`: hoy `economia_anual.csv` usa costos del ERS por
región, ponderados por área. ERS publica la región de cada condado en `reglink.xls`. Implementá la asignación por
condado (cada condado toma los costos de su región ERS), con la tabla de `reglink.xls` bajada a
`data/raw/economia/` (fila en `manifest.csv`) y, si hace falta, una tabla chica en `data/reference/`. Agregá las
columnas nuevas sin cambiar las de hoy (o, si el research propone reemplazarlas, dejalo explicado y que el humano
elija). Pruebas sin red. Data card de `economia`: el supuesto y la diferencia con el método actual en un par de
condados de borde entre regiones.

**El PR no se une hasta que el humano diga que sí** a la fila 21. Escribí al principio del cuerpo del PR:
"Espera el OK de para_decidir #21; no unir antes". No toques `src/common/` ni `config/`.

## Terminada cuando

El código, las pruebas y el data card en un PR con CI en verde, retenido como dice arriba.

## Notas
