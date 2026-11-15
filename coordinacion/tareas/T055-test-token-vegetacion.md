---
id: T055
titulo: 'Prueba de la descarga de MODIS: token renovado y código de salida'
estado: hecha
plan_minimo: pro
maquina: pro-4
estados: []
depende_de: []
rama: null
creada: 2026-11-15 04:17
actualizada: 2026-11-15 04:29
---

## Qué hacer

`src/vegetacion/download.py` ahora pide un token SAS nuevo por año y sale con código 1 si quedan archivos sin
bajar (PR 39: antes, con un solo token, todo daba 403 desde el 2014 y salía con código 0). Escribí
`tests/test_vegetacion_download.py` que, sin red (con `unittest.mock` sobre `requests.get`, la búsqueda STAC y
`bajar_item`), controle:

- que se pide un token por cada año con archivos pendientes y ninguno para los años completos;
- que si `bajar_item` falla en algún archivo, `main()` termina con `SystemExit(1)`, y si todo baja, sin error;
- que los archivos que ya existen en `data/raw/` no se vuelven a pedir (con un directorio temporal).

No cambies `src/vegetacion/download.py` salvo que la prueba muestre un error; si lo cambiás, explicalo en el
PR. Las pruebas tienen que pasar en Windows y en Linux.

## Terminada cuando

Las pruebas en un PR.

## Notas
- 2026-11-15 04:28 · pro-4: tomada
- 2026-11-15 04:29 · pro-4: terminada por el trabajador: PR #48, falta la revisión de max-1
