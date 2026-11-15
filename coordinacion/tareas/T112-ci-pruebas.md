---
id: T112
titulo: 'CI: correr las pruebas en GitHub Actions (Windows y Linux)'
estado: hecha
plan_minimo: pro
maquina: pro-3
estados: []
depende_de: []
rama: null
creada: 2026-11-15T08:00
actualizada: 2026-11-15 08:11
---

## Qué hacer

El repo no tiene `.github/`. Agregá `.github/workflows/pruebas.yml` que, en cada push a `main` y en cada PR,
instale Python 3.11 y `requirements.txt` y corra `python -X utf8 -m pytest -q tests`, en `ubuntu-latest` y
`windows-latest`. Sin secretos ni red fuera de pip: si alguna prueba necesita red o datos de `data/`, marcala para
que se saltee en CI (con un motivo claro) en vez de borrarla. Cacheá pip. Agregá el badge al `README.md`
(con una ruta relativa al workflow, sin escribir el dueño del repo a mano si se puede evitar; si no se puede,
sacalo de `git remote get-url origin` al momento y no lo copies a otros archivos).

Antes del PR, comprobá en tu máquina que `pytest -q tests` pasa con un venv nuevo hecho solo desde
`requirements.txt` (así se ve si falta alguna dependencia).

## Terminada cuando

El workflow en un PR, con la corrida de Actions del PR en verde en los dos sistemas.

## Notas
- 2026-11-15 08:03 · pro-3: tomada
- 2026-11-15 08:05 · pro-3: bloqueada: el trabajo quedó en la rama tarea/T112-auto pero push falló: To <remoto origin>
 ! [remote rejected] tarea/T112-auto -> tarea/T112-auto (refusing to allow a Personal Access Token to create or update workflow `.github/workflows/pruebas.yml` without `workflow` scope)
error: falló el empuje de algunas refere
- 2026-11-15 08:11 · pro-3: terminada: Cerrada por max-1 (coordinador): el token de pro-3 no tiene permiso workflow; max-1 armó el workflow en el PR 103, unido con Actions en verde en Linux y Windows.
