---
id: T118
titulo: Fill the [TBD] placeholders in the submission pages, list what only the human can fill
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15T08:24
actualizada: 2026-11-15T08:24
---

## Qué hacer

El envío a Space Apps cierra hoy (2026-11-15, 23:59). En `docs/demo/project_page.md`, `slides.md`, `video.md`,
`limitations.md` y `README.md` quedan unos 68 `[TBD]`. Recorrelos uno por uno:

- Si el repo tiene la respuesta (un número de `coverage.md` o `data_quality.md`, una figura de `docs/demo/fig/`,
  la URL de un release que ya existe, un dato de un data card), completalo citando de dónde sale. Las URL de
  release armalas con `git remote get-url origin` al momento; no escribas el dueño del repo a mano en otros archivos
  que no sean esas páginas, y comprobá cada una con `python -X utf8 scripts/revisar_enlaces.py`.
- Si solo lo puede completar el humano (nombres del equipo, video subido, link del frontend, decisiones de
  `coordinacion/para_decidir.md`), dejalo como está y anotalo en `docs/demo/pendientes_humano.md`: una tabla con
  archivo, línea, qué falta y de quién depende, ordenada por importancia para los jueces.

No inventes nada: si dudás, va a la tabla.

## Terminada cuando

Las páginas completadas y `pendientes_humano.md` en un PR, con `revisar_enlaces.py` sin errores.

## Notas
