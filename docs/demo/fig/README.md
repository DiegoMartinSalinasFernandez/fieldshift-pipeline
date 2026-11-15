Las figuras se generan con `docs/demo/figuras.py` a partir de los releases publicados.
No se suben PNG hechos con datos de prueba.

## `*_oh_ne_mn.png` (T074)

Solo Ohio, Nebraska y Minnesota, con los CSV del release `datos-oh-ne-mn` (zips controlados con su `.sha256`).
No incluyen IA, IL, IN ni KS; el pie de cada figura lo aclara. Se regeneran con:

```
.venv/bin/python -X utf8 docs/demo/figuras.py --https --etiquetas datos-oh-ne-mn --sufijo oh_ne_mn \
    --nota "Only Ohio, Nebraska and Minnesota (release datos-oh-ne-mn); IA, IL, IN and KS are not included."
```

`--https` baja con `urllib` desde la URL pública del release (sin `gh` ni token). Los zips quedan en
`data/demo_zips/` (fuera de git).

## `fig6_lluvia_oh_ne_mn.png` (T095)

Lluvia mensual GPM IMERG contra NASA POWER, un punto por condado-mes (`clima_mensual.csv` de
`datos-oh-ne-mn`). `prec_imerg_mm` es GPM IMERG Final V07 servido por la API de NASA POWER (`IMERG_PRECTOT`,
0,1°; Late V07 de 2025-10 a 2025-12), no `GPM_3IMERGDF` de GES DISC (ver `docs/datasets/clima.md`); el pie de
la figura lo dice. Hay un panel por estado, con la recta 1:1, la razón de totales IMERG/POWER y la r de Pearson. Se
genera con el mismo comando de arriba (solo necesita el zip `datos-oh-ne-mn_clima.zip`). No es una validación
contra pluviómetros: esa figura (contra PRISM) espera el release de `validacion`.

## `fig7_county_maps_corn_after_corn_imerg_oh_ne_mn.png` (T121)

Dos mapas de los mismos condados de OH, NE y MN y el mismo año (el último con `pct_maiz_tras_maiz`, hoy 2025):
a la izquierda `pct_maiz_tras_maiz` (`rotacion_anual.csv`, transición CDL píxel a píxel 2024→2025, escala fija
0–100 %), a la derecha `prec_imerg_mm` de julio de ese año (`clima_mensual.csv`, GPM IMERG vía la API de POWER).
Cada condado lleva su valor publicado, sin clases ni suavizado; gris = sin valor (2 condados sin
`pct_maiz_tras_maiz`). Los releases no traen `condados.gpkg` (solo `condados.csv`, con centroides): los
polígonos salen del Census Cartographic Boundary 2024 1:500k (el mismo zip que `src/base/download.py` y
`fig0_mapa.png`), unidos por `fips` = `GEOID`. Se genera con el comando de arriba (baja el zip del Census a
`data/demo_zips/census_cb/` si no está en `data/raw/base/`; `--sin-mapas-condado` la saltea).

## `fig8_county_monthly_smap_imerg_oh_ne_mn.png` (T121)

Serie mensual de un condado, 2019–2023: lluvia GPM IMERG (`prec_imerg_mm`, barras) y humedad SMAP L4 de la zona
radicular (`sm_rootzone_m3m3`, línea), con la media del mismo mes calendario de todos los años SMAP publicados del
condado (2015-04 a 2025-12, media simple) en punteado. El condado es **Stearns, MN (27145)**, agrícola, del
centro de Minnesota; el evento sombreado (mayo a agosto de 2021) es la sequía de 2021 en MN de
`docs/qa/oh_ne_mn.md`. En Stearns la humedad SMAP baja de 0,24 m³/m³ en abril de 2021 a 0,148 en agosto
(`sm_rootzone_anom_z` entre −1,45 y −1,99 de mayo a agosto). El condado, el evento y la ventana son constantes
de `figuras.py` (`SERIE_FIPS`, `SERIE_EVENTO`, `SERIE_DESDE`, `SERIE_HASTA`). Alternativa a `fig3` en la lámina 6.

## `fig0_mapa.png` (T094)

Mapa de la lámina 1: los condados de todos los estados de `config/config.yaml` (Census Cartographic Boundary
2024, 1:500k, el mismo zip que `src/base/download.py`), coloreados por grupo (IA/IL/IN, OH/NE/MN, KS, MO/WI/SD;
paleta Okabe-Ito) y con el estado del release `datos-<estados>`: lleno si está publicado en la página de
releases (API pública de GitHub, sin token), rayado si está en proceso. No lleva sufijo ni nota. Se regenera con:

```
.venv/bin/python -X utf8 docs/demo/figuras.py --solo-mapa
```

Usa el zip de `data/raw/base/` si ya está; si no, lo baja a `data/demo_zips/census_cb/` (fuera de git). Conviene
correrlo de nuevo cada vez que se publica un release.
