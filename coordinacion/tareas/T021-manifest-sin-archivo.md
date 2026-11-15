---
id: T021
titulo: Que las descargas creen manifest.csv si no existe
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: '2026-11-15 02:35'
actualizada: '2026-11-15 02:35'
---

## Qué hacer

En una máquina nueva no hay `manifest.csv` (no va en git), y `registrar()` de `src/cultivos/download.py`
falla porque lo abre para leer antes de crearlo (lo encontró pro-2 en T004: el archivo igual queda en
`data/raw/`, pero no se registra). Revisá **todas** las funciones que escriben `manifest.csv` en
`src/*/download.py` y `src/lotes/` (`grep -rn "manifest" src`) y hacé que, si el archivo no existe, lo creen
con el encabezado de la sección 7 del CLAUDE.md (`paquete, archivo, fuente, producto, version,
fecha_descarga, consulta_o_url`) antes de leerlo.

- No cambies `src/common/` (si la mejor solución es una función común, proponela en "Para decidir" y arreglá
  cada paquete por separado igual).
- No cambies las columnas del manifest ni las filas que ya escribe cada paquete.
- Probá cada función tocada en una carpeta temporal sin `manifest.csv`, sin bajar datos (llamando a la función
  de registro con un archivo chico inventado).

## Terminada cuando

Ningún `registrar` falla sin `manifest.csv`, con la prueba descrita en el PR.

## Notas
