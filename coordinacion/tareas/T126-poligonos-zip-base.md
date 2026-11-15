---
id: T126
titulo: Sumar `condados.gpkg` al zip de base de los releases (scripts/entregar.py)
estado: tomada
plan_minimo: pro
maquina: pro-1
estados: []
depende_de: []
rama: null
creada: 2026-11-15T09:11
actualizada: 2026-11-15 09:22
---

## Qué hacer

En PR 112 (T121) apareció que los releases solo traen `condados.csv` con centroides, sin polígonos: para el mapa
hubo que bajar aparte el Census Cartographic Boundary. El frontend y ML necesitan los polígonos.

1. Hoy `scripts/entregar.py` (línea ~89) mete `condados.csv` y `anios.csv` en cada zip de paquete. Sumá un asset
   más, `<etiqueta>_base.zip` (con su `.sha256`, como los demás), con `data/reference/condados.gpkg` (EPSG:4326,
   el que escribe `src/base/process.py`, filtrado a los estados del release si trae más), `condados.csv`,
   `anios.csv` y un README corto. Los zips de paquete no cambian. Revisá que `paquetes_de_assets()` y las notas
   del release (T122) lo traten bien.
2. Prueba sin red en `tests/test_entregar.py` (un gpkg chico armado en la prueba, o simulando el archivo).
3. `docs/demo/figuras.py`: si el release trae `_base.zip`, usar su `condados.gpkg` para fig7 en vez del Census; si no (releases
   viejos), seguir como hoy.
4. `scripts/verificar_entrega.py`: que revise también el zip de base si está.
5. Donde se documente el contenido de los releases (`MAQUINAS.md`, `docs/demo/add_a_state.md`, data cards).

No toques releases publicados: el coordinador sube el zip de base a `datos-oh-ne-mn` cuando esto esté unido
(dejá el comando en el PR).

## Terminada cuando

El cambio y la prueba en un PR, con CI en verde.

## Notas
- 2026-11-15 09:22 · pro-1: tomada
