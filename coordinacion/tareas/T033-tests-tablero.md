---
id: T033
titulo: Pruebas del tablero (tests/test_tareas.py)
estado: hecha
plan_minimo: pro
maquina: pro-1
estados: []
depende_de: []
rama: null
creada: 2026-11-15 03:00
actualizada: 2026-11-15 03:01
---

## Qué hacer

`scripts/tareas.py` coordina las seis máquinas y no tiene pruebas. Escribí `tests/test_tareas.py` (unittest,
como `tests/test_unir_estados.py`) que corra todo en una carpeta temporal con un remoto git local (`git init
--bare`), nunca contra GitHub:

- `nueva`, `tomar`, `nota`, `soltar`, `bloquear` y `terminar` cambian el estado y las notas como dice
  MAQUINAS.md;
- dos máquinas que toman la misma tarea casi a la vez: una gana y la otra recibe el aviso (push rechazado);
- `nota` no cambia el estado; `tomar` no deja tomar una tarea con `depende_de` sin terminar;
- el tablero se publica desde `.tablero/` sin arrastrar commits de la rama de trabajo.

Si una prueba muestra un error real, marcala `expectedFailure` y explicalo en "Para decidir": **no cambies
`scripts/tareas.py`** en esta tarea.

## Terminada cuando

Las pruebas en un PR, pasando (salvo las marcadas).

## Notas
- 2026-11-15 02:57 · pro-1: tomada
- 2026-11-15 03:01 · pro-1: terminada por el trabajador: PR #26, falta la revisión de max-1
