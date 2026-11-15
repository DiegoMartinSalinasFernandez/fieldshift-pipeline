# Integración de los PR retenidos (T140)

Fecha: 2026-11-15. Base: `origin/main` en `9f67fe6` (PR 117–131) y `25328e0` (PR 132; entre las dos solo cambió `coordinacion/`). Hecha por pro-2 **como simulación** fuera de git: en esta
sesión (y otra vez en la segunda, 10:17) `git merge`, `git worktree` y `gh` estaban bloqueados por permisos, así que la combinación se armó con
`git merge-tree` y `git merge-file` en `/tmp`, sin tocar ninguna rama. Esta nota sirve para que quien
pueda unir de verdad (humano o max-1) repita la resolución en minutos.

## PR retenidos (abiertos, rama aún fuera de `main`)

Identificados con `git ls-remote origin 'refs/pull/*/head'` cruzado con las ramas `tarea/*` y la columna
"código listo en PR N" de `coordinacion/para_decidir.md`. `main` (`bf5a503`) ya anota "código listo en PR 131 y 132" en las filas #19 y #5.
El PR 133 es esta misma tarea (T140) y no se suma.

| PR | Rama | para_decidir | Choca con | Archivos que chocan | Resolución |
|---|---|---|---|---|---|
| 117 | `tarea/T128-auto` | #23 | — | — | limpia |
| 118 | `tarea/T129-auto` | #31 | — | — | limpia |
| 119 | `tarea/T124-auto` | #6 | — | — | limpia |
| 120 | `tarea/T130-auto` | #32 | — | — | limpia |
| 121 | `tarea/T127-auto` | #9 y #28 | — | — | limpia |
| 122 | `tarea/T125-auto` | #17 | — | — | limpia |
| 123 | `tarea/T132-auto` | #2 | — | — | limpia (sobre 117–122) |
| 124 | `tarea/T133-auto` | #13 | 123 | `docs/datasets/cultivos.md` | las dos secciones nuevas, una tras otra |
| 125 | `tarea/T134-auto` | #1 | 123, 124 | `docs/datasets/cultivos.md` | ídem |
| 126 | `tarea/T135-auto` | #8 | 123–125 | `cultivos.md`, `glosario_en.csv`, `src/cultivos/data_card.py`, `src/cultivos/process.py` | `cultivos.md`, glosario y `data_card.py`: se conservan los dos lados (filas y secciones agregadas). `process.py` (docstring): línea de `fenologia_estado.csv` de T135 + línea de `practicas_censo.csv` con `flag_nass` de T132 |
| 127 | `tarea/T137-auto` | #11 | 123–126 | `docs/datasets/cultivos.md` | las dos secciones |
| 128 | `tarea/T136-auto` | #27 | — | — | limpia |
| 129 | `tarea/T138-auto` | #7 | 123–127 | `cultivos.md`, `src/cultivos/process.py` | `cultivos.md`: las dos secciones. `process.py`: los dos imports (`fenologia_estado` y `completar_desde_config`) y, en `main()`, `prod = completar_desde_config(produccion(crops))` **seguido** del bloque de riego de T134 (`agregar_riego` + `chequear_coherencia`) |
| 130 | `tarea/T142-auto` | #22 | — | — | limpia (solo `docs/research/`) |
| 131 | `tarea/T139-auto` | #19 | 123–129 | `cultivos.md`, `src/cultivos/data_card.py` | las dos secciones |
| 132 | `tarea/T131-auto` | #5 | — | — | limpia sobre los 15 anteriores (`glosario_en.csv`, `glosario_en.py`, `lotes.md`, `src/lotes/download.py` y `process.py` se combinan solos; `src/lotes/drenaje.py` y su prueba son nuevos) |

Orden de las secciones finales de `docs/datasets/cultivos.md`: Riego desde LANID (T127), Riego por cultivo del
Censo (T132), precisión del CDL (T133), Riego y secano (T134), Fenología de avena y trigo (T135), Sorgo (T137),
Grilla completa (T138), Clases 0, 27 y 58 (T139). Sin líneas duplicadas que no estuvieran ya en algún PR.

## Lo único que no es solo "juntar los dos lados"

`src/cultivos/process.py`, `main()`, con 125 (T134) y 129 (T138):

```python
        prod = completar_desde_config(produccion(crops))  # grilla completa (T138)
        from src.cultivos.riego_nass import agregar_riego, chequear_coherencia  # T134
        prod = agregar_riego(prod, crops)
        incoherentes = chequear_coherencia(prod)
        if len(incoherentes):
            print(f"aviso: {len(incoherentes)} filas con riego + secano != sembrada total (> 1 %)")
```

La grilla va primero y el riego se pega con `merge(how="left", validate="one_to_one")`, que no agrega filas.
Diferencia con correr solo T134: si NASS publicara un dato por práctica sin la fila de "ALL PRODUCTION
PRACTICES", antes se descartaba y ahora queda en la fila vacía de la grilla. El research de T004 no encontró
ese caso en NE y KS. No hay prueba que cubra esa combinación.

## Pruebas (`python -X utf8 -m pytest -q tests`)

| Árbol | Resultado |
|---|---|
| `main` | 307 passed, 3 skipped, 3 xfailed |
| `main` + 117–123, 128, 130 | 365 passed, 3 skipped, 1 xfailed |
| `main` + los 15 (117–131) con la resolución de arriba | 416 passed, 3 skipped, 1 xfailed |
| `main` + los 16 (117–132) | **422 passed, 3 skipped, 1 xfailed** |

El xfail que queda (`test_validar_siete.py::test_columna_numerica_toda_con_codigo_nass_se_rechaza`) ya está en
`main` (para_decidir #25). Las dos xfail de `test_merge.py` que hay en `main` pasan con el PR 128.

## Cómo repetirlo con permiso de merge

```bash
git switch -c integracion/retenidos origin/main
for b in T128 T129 T124 T130 T127 T125 T132 T133 T134 T135 T137 T136 T138 T142 T139 T131; do
  git merge --no-ff --no-edit origin/tarea/$b-auto || break   # resolver según la tabla y seguir
done
python -X utf8 -m pytest -q tests
```
