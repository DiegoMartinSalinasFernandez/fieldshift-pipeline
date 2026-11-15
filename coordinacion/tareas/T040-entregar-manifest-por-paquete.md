---
id: T040
titulo: 'scripts/entregar.py: manifest solo del paquete y rechazo de claves'
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15 04:00
actualizada: 2026-11-15 03:26
---

## Qué hacer

T036 (PR 30) encontró dos cosas en `scripts/entregar.py`:

- `armar_zip` copia el `manifest.csv` entero en cada zip. El docstring dice "las filas de los archivos bajados"
  del paquete. Cambialo para que escriba al zip solo las filas con `paquete == <paquete>`
  (`zf.writestr("manifest.csv", ...)`, mismo encabezado, mismo orden de filas, UTF-8 y `\n`).
- Red de seguridad: si alguna fila del manifest del paquete tiene en `consulta_o_url` algo como `key=`,
  `api_key=`, `token=` o `apikey=`, que `entregar.py` corte con un error claro **sin imprimir el valor**.

Sacá el `@unittest.expectedFailure` de `test_manifest_solo_filas_del_paquete` en `tests/test_entregar.py` y
agregá una prueba para el rechazo de claves (con un valor inventado). Controlá que `tests/test_unir_estados.py`
siga pasando: `unir_estados.py` lee estos zips.

No cambies `src/common/` ni `config/`.

## Terminada cuando

El cambio y las pruebas en un PR; `pytest tests/` pasa.

## Notas
- 2026-11-15 03:24 · pro-2: tomada
- 2026-11-15 03:25 · pro-2: soltada: quedó a medias, PR #33. INCOMPLETA: el agente no dejó resultado.
- 2026-11-15 03:25 · pro-2: tomada
- 2026-11-15 03:25 · pro-2: soltada: quedó a medias, PR #33 actualizado. INCOMPLETA: el agente no dejó resultado.
- 2026-11-15 03:26 · pro-2: tomada
- 2026-11-15 03:26 · pro-2: soltada: quedó a medias, PR #33 actualizado. INCOMPLETA: el agente no dejó resultado.
