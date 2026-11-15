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
`datos-oh-ne-mn`), un panel por estado, con la recta 1:1, la razón de totales IMERG/POWER y la r de Pearson. Se
genera con el mismo comando de arriba (solo necesita el zip `datos-oh-ne-mn_clima.zip`). No es una validación
contra pluviómetros: esa figura (contra PRISM) espera el release de `validacion`.

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
