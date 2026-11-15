---
id: T014
titulo: Script para juntar los releases de cada estado (scripts/unir_estados.py)
estado: hecha
plan_minimo: pro
maquina: pro-2
estados:
- IA
- IL
- IN
- OH
- NE
- MN
- KS
depende_de: []
rama: null
creada: 2026-11-15 01:40
actualizada: 2026-11-15 02:21
---

## Qué hacer

`max-1` va a juntar los datos de todos los estados (T008). Cada máquina publica sus paquetes en un release
`datos-<estados>` con `scripts/entregar.py` (un zip por paquete con los CSV procesados, el data card,
`condados.csv`, `anios.csv` y `manifest.csv`). Escribí `scripts/unir_estados.py`:

1. `--releases datos-ia-il-in,datos-oh-ne-mn,datos-ks` (o `--dir` con zips ya bajados): baja los zips con
   `gh release download` a `data/entregas/<release>/` y verifica el `.sha256` de cada uno.
2. Por paquete, apila por filas los CSV del mismo nombre de todos los releases en `data/unido/<paquete>/`.
   Mismo encabezado en todos (si no, error claro que diga qué columnas difieren). `fips` y `fips_estado` se
   leen como texto.
3. Chequeos: sin claves duplicadas después de apilar (las claves son las primeras columnas, sección 4 del
   CLAUDE.md), cada `fips` aparece en un solo release, `condados.csv` y `manifest.csv` unidos sin repetir.
4. Un resumen corto: filas por paquete y por estado.

No corre `src/merge.py` ni toca `src/common/`. Probalo con zips chicos armados a mano en una carpeta temporal
(dos "estados" falsos con 2 o 3 condados), sin datos reales: dejá esa prueba en `tests/test_unir_estados.py`.
Mirá `scripts/entregar.py` para saber cómo vienen los zips.

## Terminada cuando

El script y su prueba en un PR, con el uso en el docstring.

## Notas
- 2026-11-15 02:19 · pro-2: tomada
- 2026-11-15 02:21 · pro-2: terminada por el trabajador: PR #7, falta la revisión de max-1
