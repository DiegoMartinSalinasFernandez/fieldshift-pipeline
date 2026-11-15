---
id: T117
titulo: Listas de eventos extremos para el QA de KS y de MO/WI/SD (YAML de qa_release.py)
estado: hecha
plan_minimo: pro
maquina: pro-5
estados:
- KS
- MO
- WI
- SD
depende_de: []
rama: null
creada: 2026-11-15T08:24
actualizada: 2026-11-15 08:46
---

## Qué hacer

`scripts/qa_release.py` revisa que los eventos extremos conocidos se vean en los datos, con una lista en YAML
(ejemplo: `docs/qa/eventos_oh_ne_mn.yaml`). Armá, con el mismo formato, `docs/qa/eventos_ks.yaml` y
`docs/qa/eventos_mo_wi_sd.yaml`, sacando los eventos de `docs/research/eventos_extremos_nuevos.md` (KS) y
`docs/research/eventos_extremos_mo_wi_sd.md` (y su `_rend.csv`). Para cada evento: estado, años, meses, qué
variables deberían moverse y en qué dirección, citando la sección del research. Solo eventos que estén en esos
documentos. Así T007 (KS) y T081 (MO/WI/SD) corren apenas salgan los releases.

Probá que `qa_release.py` lea los dos YAML sin error (por ejemplo, con `datos-oh-ne-mn`: los estados que no estén
en ese release se tienen que saltear con un aviso, no romper). Si el script no saltea bien, arreglalo y agregá una
prueba.

## Terminada cuando

Los dos YAML (y el arreglo, si hizo falta) en un PR.

## Notas
- 2026-11-15 08:40 · pro-5: tomada
- 2026-11-15 08:46 · pro-5: terminada por el trabajador: PR #108, falta la revisión de max-1
