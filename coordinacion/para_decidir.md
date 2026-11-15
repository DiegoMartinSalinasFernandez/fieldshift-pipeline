# Para decidir (humano)

Lo que las tareas dejaron como propuesta y espera una decisión del humano: cambios de esquema, descargas de
más de 5 GB, cambios en `src/common/` o en `config/`. Lo mantiene `max-1`. Cuando se decide, se anota la
respuesta y se crea la tarea que lo implementa.

| # | De | Propuesta | Por qué importa | Estado |
|---|---|---|---|---|
| 1 | T004 (PR 4), `docs/research/riego_nass.md` | 11 columnas de riego y secano en `produccion_anual.csv` (`sup_sembrada_riego_ac`, `rend_secano_bu_ac`, `pct_sembrada_riego`…), solo maíz, soja y trigo de invierno, NE y KS, 2000–2018 | En NE y KS el rendimiento con riego es 81–103 bu/ac más alto: mezclarlos confunde al modelo. NASS dejó de publicarlo desde 2019 | pendiente |
| 2 | T012 (PR 8), `docs/research/censo_agropecuario.md` | `pct_maiz_regado`, `pct_soja_regada` y `pct_cosechado_regado` (con `flag_nass`) en `practicas_censo.csv`, desde el Censo 2012/2017/2022 | Cubre el riego por cultivo después de 2018, en los 7 estados | pendiente |
| 3 | T010 (PR 5), `src/suelo_terreno/terreno.py` | Umbral de `twi_decil_sup_pct`: (a) fijo, el p90 de la primera tanda, en `config.yaml`; (b) recalcular con todas las máquinas; (c) percentil por condado | Hoy cada máquina usa el p90 de sus estados: la columna no es comparable al unir. Hay que decidirlo antes de T008 | pendiente |
| 4 | T010 (PR 5) | Mover `src/zona_texto.py` a `src/common/` | Orden del código, sin efecto en los datos | pendiente |
| 5 | T017 (PR 9), `docs/research/drenaje_tile.md` | Sumar SEETileDrain al paquete `lotes`: `tile_prob_seetiledrain` y `tile_seetiledrain`, bajando ~3,1 GB una vez | Única fuente de drenaje por píxel que no sale del Censo | pendiente |
| 6 | T016 (PR 10), `docs/research/rma_causa_perdida.md` | Paquete nuevo `seguro` (`seguro_anual.csv`, `seguro_mensual.csv`) con causas de pérdida y superficie asegurada de RMA | Un target de riesgo (sequía, exceso de agua, granizo) por condado y año | pendiente |
| 7 | T011 (PR 6), `docs/research/nass_2024_2025.md` | `produccion_anual.csv` con la grilla completa `fips × anio × cultivo` y celdas vacías, en lugar de solo las filas que publica NASS | No cambia columnas, pero sí cuántas filas hay. En 2024–2025 falta el rendimiento del 35–40 % de los condados | pendiente |
| 8 | T019 (PR 12), `docs/research/crop_progress_estados_nuevos.md` | En `fenologia_estado.csv`: sumar avena y trigo de invierno (con la etapa HEADED), fijar a qué año va el trigo sembrado en otoño y agregar una marca de calidad para los cruces del 50 % interpolados sobre huecos de más de 2 semanas | El cierre del gobierno de 2025 dejó sin reportes de octubre a principios de noviembre, justo en la cosecha de maíz y soja | pendiente |
| 9 | T018 (PR 14), `docs/research/riego_mascaras.md` | Bajar LANID (1,8 GB) y agregar `riego_anual.csv` (% agrícola, de maíz y de soja regado por condado y año) y `mascara_riego_max.tif` para `ndvi_secano`; o, como mínimo, una columna en `rotacion_anual.csv` | Dónde está el riego en el mapa: completa las propuestas 1 y 2 | pendiente |
| 10 | T021 (PR 13) | Pasar `asegurar_manifest()`, hoy repetida en 12 `download.py`, a `src/common/` | Orden del código | pendiente |
