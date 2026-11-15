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
