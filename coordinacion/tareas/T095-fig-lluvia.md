---
id: T095
titulo: 'Figura de la demo: lluvia mensual IMERG contra POWER por estado (OH, NE, MN)'
estado: libre
plan_minimo: pro
maquina: null
estados:
- OH
- NE
- MN
depende_de: []
rama: null
creada: 2026-11-15T06:55
actualizada: 2026-11-15T06:55
---

## Qué hacer

La lámina 6 pide un scatter de lluvia contra PRISM, pero `validacion` no tiene release. Mientras tanto, con
`clima_mensual.csv` de `datos-oh-ne-mn`, hacé `fig6_lluvia.png`: `prec_imerg_mm` contra `prec_power_mm` por
condado-mes, un panel por estado, con la recta 1:1 y la razón media (OH da ~1,18 según `docs/qa/oh_ne_mn.md`).
Agregala a `docs/demo/figuras.py`, subí el PNG a `docs/demo/fig/` y actualizá la lámina 6 diciendo qué compara.

Los zips de los releases son públicos: bajalos con `curl -L` desde `https://github.com/<dueño>/<repo>/releases/download/<release>/<archivo>` (dueño y repo salen de `git remote get-url origin`; no los escribas en ningún archivo). Controlá el `.sha256`. Van a `data/` (fuera de git), nunca al repo. **Solo datos reales del release** en las figuras.

## Terminada cuando

El script, el PNG y la lámina en un PR.

## Notas
