---
id: T127
titulo: 'Riego por condado y año desde LANID (`cultivos`): código listo, espera OK'
estado: libre
plan_minimo: pro
maquina: null
estados:
- NE
- KS
depende_de: []
rama: null
creada: 2026-11-15T09:11
actualizada: 2026-11-15T09:11
---

## Qué hacer

Implementá lo que proponen `docs/research/riego_mascaras.md` (T018) y `docs/research/riego_ne_ks.md`: bajar LANID
(~1,8 GB de Zenodo, más los TIF 2018–2020 del USGS si el research lo indica) a `data/raw/cultivos/lanid/` con su
fila en `manifest.csv`, y por condado y año (2000–2020, o lo que cubra) calcular sobre la grilla del CDL
(EPSG:5070):

- `riego_anual.csv`: `fips, anio, frac_riego_lanid` (fracción del área agrícola regada), `frac_maiz_regado`,
  `frac_soja_regada` (con las máscaras de maíz y soja del CDL de ese año), `frac_pixeles_validos`.
- `data/reference/mascara_riego_max.tif` (píxel regado en algún año), si el research lo recomienda, para que
  vegetación pueda calcular `ndvi_secano` más adelante (eso no se hace en esta tarea).

Va en `src/cultivos/` como módulo aparte (`riego.py`) para no chocar con otros cambios. Pruebas sin red con
rasters chicos armados en la prueba. Data card de `cultivos`: sección nueva.

Si tu máquina tiene espacio, probalo con Nebraska (el estado con más riego) y compará con el Censo 2017/2022
(`practicas_censo.csv`, `pct_riego`); si no, con un recorte. No bajes más de 5 GB.

**El PR no se une hasta que el humano diga que sí** a la fila 9 y 28 de `coordinacion/para_decidir.md` (esquema
nuevo). Escribí al principio del cuerpo del PR: "Espera el OK de para_decidir #9 y 28; no unir antes". Así, si
dice que sí al despertarse, está listo para unir y correr en las máquinas Max.

## Terminada cuando

El código, las pruebas y el data card en un PR con CI en verde, retenido como dice arriba.

## Notas
