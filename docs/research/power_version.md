# Versión de la API de NASA POWER

Pregunta: ¿la respuesta de la API de NASA POWER trae la versión del servicio? ¿Dónde, y sirve para el
formato CSV que usa `src/clima/download.py`?

Respuesta corta: sí. En JSON viene en `header.api.version` (`"v2.10.3"` el 2026-11-15). En CSV no está en el
texto, pero toda respuesta trae el encabezado HTTP `x-app-version: v2.10.3`. `download.py` lo lee de ahí desde
T123 y escribe `POWER API <versión>` en la columna `version` de `manifest.csv`.

Detalle:

Pedido de prueba (un punto en Iowa, un mes), 2026-11-15:

```
GET https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PRECTOTCORR&community=AG
    &longitude=-93.5&latitude=42.0&start=20230701&end=20230731&format=JSON
```

`header` de la respuesta JSON:

```json
{
 "title": "NASA/POWER Source Native Resolution Daily Data",
 "api": {"version": "v2.10.3", "name": "POWER Daily API"},
 "sources": ["MERRA2"],
 "fill_value": -999.0,
 "time_standard": "LST",
 "start": "20230701",
 "end": "20230731"
}
```

`messages` llega vacío. El mismo pedido con `format=CSV` (el formato que baja el paquete) devuelve un
encabezado de texto (`-BEGIN HEADER-` … `-END HEADER-`) con título, fechas, lugar, elevación, valor de relleno
(-999) y parámetros, **sin** versión. Los encabezados HTTP de esa respuesta sí la traen:

```
content-type: text/csv
x-app-name: daily
x-app-version: v2.10.3
x-data-sources: merra2
```

Las rutas que se probaron para pedir solo la versión (`/api/system/version`, `/api/system/manager/version`,
`/api/openapi.json`) devuelven la página web (HTML), no un JSON: no sirven.

Qué significa la versión: es la del software de la API (el servicio que arma la respuesta), no la de los datos
de entrada. Las fuentes de cada parámetro van aparte (`sources` en JSON, `x-data-sources` en HTTP:
`merra2` para meteorología, IMERG para `IMERG_PRECTOT`). Para citar, alcanza con: NASA POWER, API diaria por
punto `v2.10.3`, comunidad AG, fecha de acceso (columna `fecha_descarga` del manifest).

Filas viejas del manifest: las bajadas de meteorología anteriores a T123 dicen `v2 (API)` y las de IMERG
`POWER API v2.10.3` (texto fijo en el código). No se reescriben: la versión con la que se bajaron no quedó
guardada. Las de IMERG coinciden con la versión vigente hoy, pero eso no prueba que fuera la misma el día de la
bajada. Si a un archivo de `raw/` le falta su fila, ahora se registra como `v2 (API, versión no registrada)`.

Fuentes: [POWER API — respuesta de `temporal/daily/point`](https://power.larc.nasa.gov/api/temporal/daily/point),
consultado 2026-11-15; [POWER Docs — referencing](https://power.larc.nasa.gov/docs/referencing/), consultado
2026-11-15

Confianza: alta (observado en la respuesta de la API; el nombre del encabezado HTTP no está documentado y podría
cambiar: si falta, el código escribe `v2 (API, versión no registrada)` en vez de inventar una versión).

Impacto: `src/clima/download.py` (columna `version` de `manifest.csv`), data card de `clima`
(`src/clima/data_card.py` → `docs/datasets/clima.md`, sección Fuentes).
