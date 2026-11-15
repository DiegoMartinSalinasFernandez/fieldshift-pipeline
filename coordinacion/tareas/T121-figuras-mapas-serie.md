---
id: T121
titulo: 'Demo figures: county maps (corn after corn, one NASA layer) and one county''s monthly SMAP/IMERG series'
estado: tomada
plan_minimo: pro
maquina: pro-5
estados:
- OH
- NE
- MN
depende_de: []
rama: null
creada: 2026-11-15T08:55
actualizada: 2026-11-15 08:58
---

## Qué hacer

`docs/demo/pendientes_humano.md` #22 y #23: a las láminas les faltan figuras que no existen como PNG.

1. **Mapas por condado** (lámina de `slides.md` línea ~98): `pct_maiz_tras_maiz` de un año reciente y una capa
   NASA (por ejemplo `prec_imerg_mm` de julio o `ndvi_max` del mismo año), con los polígonos del release
   `datos-oh-ne-mn` (`condados.gpkg` o el `.csv` del zip de base). Escala de color con leyenda y unidad, y año en el título.
2. **Serie mensual de un condado** (lámina ~194, alternativa a fig3): SMAP (`sm_rootzone_m3m3`) e IMERG
   (`prec_imerg_mm`) de un condado con un evento conocido de `docs/qa/oh_ne_mn.md` (por ejemplo, la sequía de 2021
   en MN o la de 2012), marcando el evento.

Agregalas como funciones nuevas en `docs/demo/figuras.py`, con el mismo estilo y pie de fuentes que las otras
(`pie()`), leyendo solo de los zips publicados. Sumalas a `docs/demo/fig/README.md`, actualizá las láminas y sacá
#22 y #23 de `pendientes_humano.md`. Si `tests/test_demo_scripts.py` cubre `figuras.py`, extendé la prueba sin red.

## Terminada cuando

Los PNG, el código y las láminas en un PR, con CI en verde. (Los PNG de `docs/demo/fig/` sí van al repo: son
figuras, no datos.)

## Notas
- 2026-11-15 08:58 · pro-5: tomada
