---
id: T035
titulo: Pruebas de src/merge.py con varios estados (tests/test_merge.py)
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15 03:20
actualizada: 2026-11-15 03:20
---

## Qué hacer

T008 va a unir los 7 estados con `src/merge.py` después de apilar los paquetes con `scripts/unir_estados.py`.
Escribí `tests/test_merge.py` (unittest o pytest, ya está en `requirements.txt`) que arme en una carpeta
temporal unos `data/processed/<paquete>/*_anual.csv`, `*_estatico.csv`, `*_mensual.csv` y un archivo por estado
(con `fips_estado`, como `fenologia_estado.csv`) chicos e inventados, con dos estados, y controle que:

- `tabla_anual.csv` tiene una fila por `fips, anio` y las columnas de todos los paquetes;
- los archivos por estado se unen por los dos primeros dígitos de `fips` (sección 7 del CLAUDE.md);
- `tabla_mensual.csv` une por `fips, anio, mes` sin duplicar;
- los faltantes quedan vacíos (no `nan` ni 0) y no entra el paquete `lotes`.

Mirá cómo `src/merge.py` encuentra las carpetas (si usa `REPO`, apuntalo a la carpeta temporal en la prueba).
**No cambies `src/merge.py`**: si encontrás un error, marcá la prueba `expectedFailure`/`xfail` y explicalo en
"Para decidir".

## Terminada cuando

Las pruebas en un PR.

## Notas
