---
id: T025
titulo: Script para controlar un zip de entrega contra el contrato (scripts/verificar_entrega.py)
estado: hecha
plan_minimo: pro
maquina: pro-4
estados: []
depende_de: []
rama: null
creada: 2026-11-15 02:50
actualizada: 2026-11-15 02:35
---

## Qué hacer

T007 (control de calidad de los estados nuevos) y T008 (unión) van a recibir zips de `scripts/entregar.py`.
Escribí `scripts/verificar_entrega.py`, que recibe uno o varios zips (o una carpeta `data/unido/<paquete>/` de
`scripts/unir_estados.py`) y controla, sin bajar nada:

- formato de la sección 4 del CLAUDE.md: UTF-8, separador `,`, encabezado; claves primero (`fips` de 5
  dígitos con ceros, `anio` entero, `fecha` `YYYY-MM-DD`, `mes` `YYYY-MM`); nombres en `snake_case`;
- faltantes: ningún `0` sospechoso no se puede saber, pero sí que no haya `-999`, `-9999`, `NaN`, `nan`,
  `None` ni `(D)` escritos como texto;
- claves sin duplicados y `fips` presentes en el `condados.csv` del zip;
- rangos físicos usando `validar_csv()` de `src/common/` (llamala, no la cambies);
- que el data card del zip tenga una fila por columna de cada CSV.

Salida: un informe en Markdown por paquete (APTO / NO APTO con la lista de problemas) y código de salida 1 si
hay algún NO APTO. Pruebas en `tests/test_verificar_entrega.py` con zips chicos inventados (uno bueno y uno con
cada tipo de error). Mirá `scripts/entregar.py` y `tests/test_unir_estados.py` para el formato de los zips.

## Terminada cuando

El script y sus pruebas en un PR.

## Notas
- 2026-11-15 02:32 · pro-4: tomada
- 2026-11-15 02:35 · pro-4: terminada: PR #11 (scripts/verificar_entrega.py + tests/test_verificar_entrega.py, 24 pruebas OK)
