---
id: T099
titulo: Volver a correr coverage.py tras el zip de vegetación corregido
estado: hecha
plan_minimo: pro
maquina: pro-1
estados:
- OH
- NE
- MN
depende_de: []
rama: null
creada: 2026-11-15T06:55
actualizada: 2026-11-15 07:03
---

## Qué hacer

El zip `datos-oh-ne-mn_vegetacion.zip` se republicó el 2026-11-15 a las 06:50 con enero–abril de 2014 (antes
faltaba). Volvé a correr `docs/demo/coverage.py` (baja de nuevo ese zip si el `.sha256` cambió) y subí
`docs/demo/coverage.md` actualizado. Revisá también que los `.sha256` del release ahora tengan LF
(`sha256sum -c` directo, sin `tr`) y anotalo en `docs/qa/oh_ne_mn.md`, problema 4, como resuelto.

Los zips de los releases son públicos: bajalos con `curl -L` desde `https://github.com/<dueño>/<repo>/releases/download/<release>/<archivo>` (dueño y repo salen de `git remote get-url origin`; no los escribas en ningún archivo). Controlá el `.sha256`. Van a `data/` (fuera de git), nunca al repo. **Solo datos reales del release** en las figuras.

## Terminada cuando

La página actualizada en un PR.

## Notas
- 2026-11-15 07:00 · pro-1: tomada
- 2026-11-15 07:03 · pro-1: terminada por el trabajador: PR #90, falta la revisión de max-1
