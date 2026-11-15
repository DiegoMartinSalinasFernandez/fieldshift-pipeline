---
id: T036
titulo: Pruebas de scripts/entregar.py (tests/test_entregar.py)
estado: tomada
plan_minimo: pro
maquina: pro-4
estados: []
depende_de: []
rama: null
creada: 2026-11-15 03:20
actualizada: 2026-11-15 03:15
---

## Qué hacer

`scripts/entregar.py` arma un zip por paquete y lo sube a un release. Escribí `tests/test_entregar.py` que, en una
carpeta temporal con un `data/processed/<paquete>/` y un `docs/datasets/<paquete>.md` inventados, corra el modo
`--solo-zip` (nunca el que sube a GitHub) y controle: nombre del zip, que lleve los CSV, el data card,
`condados.csv`, `anios.csv` y las filas de `manifest.csv` del paquete, y que el `.sha256` coincida. Mirá
`tests/test_unir_estados.py`, que ya lee estos zips, para que las dos cosas usen el mismo formato.

**No cambies `scripts/entregar.py`**: si encontrás un error, marcá la prueba y explicalo en "Para decidir".

## Terminada cuando

Las pruebas en un PR.

## Notas
- 2026-11-15 03:15 · pro-4: tomada
