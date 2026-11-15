# merge — tablas unidas

Generado por `python src/merge.py` (CLAUDE.md §7). No baja nada: lee solo `data/processed/`.
Tarda ~1 s y es determinista (mismo md5 en dos corridas).

## Salidas

| archivo | claves | filas (2026-11-14) | columnas | contenido |
|---|---|---|---|---|
| `data/processed/tabla_anual.csv` | `fips, anio, cultivo` | 25070 | 73 | filas de `produccion_anual.csv` + columnas de `clima_anual`, `rotacion_anual`, `fenologia_anual` (por `fips, anio`), `fenologia_estado` (por `fips[:2], anio, cultivo`) y `suelo_terreno_estatico` (por `fips`) |
| `data/processed/tabla_mensual.csv` | `fips, anio, mes` | 91416 | 48 | unión externa de `clima_mensual`, `vegetacion_mensual` y `agua_mensual` |

El diccionario de cada columna está en el data card de su paquete (`docs/datasets/<paquete>.md`):
los nombres no cambian al unir.

## Supuestos

- `tabla_anual` usa *left join* sobre `produccion_anual.csv`: los años de clima/vegetación sin
  fila de producción (y los condados sin datos NASS) no aparecen. Las variables de clima,
  rotación, fenología y suelo se repiten en las filas de cada cultivo del mismo condado y año.
- `fenologia_estado` se une por estado (`fips_estado = fips[:2]`), año y cultivo: solo tiene
  maíz y soja, así que en alfalfa, avena, heno y trigo de invierno las columnas `doy_50_*`
  quedan vacías. La columna `fips_estado` no se guarda (es `fips[:2]`).
- `tabla_mensual` usa *outer join*: un mes aparece si está en cualquiera de los tres paquetes;
  SMAP empieza en 2015-04, así que antes las columnas de `agua` quedan vacías.
- Los valores se copian como texto, sin reformatear. Si dos paquetes tuvieran una columna con
  el mismo nombre, la segunda se renombra `<paquete>_<columna>` (hoy no hay colisiones).
- `rotacion_secuencia.csv` (por ventana de 8 años) y `practicas_censo.csv` (por año de censo)
  quedan aparte por tener otra granularidad.

## Problemas conocidos

- Las tablas reflejan el estado de los CSV de cada paquete al correr `merge.py`: si un paquete
  se reprocesa, hay que volver a correrlo.
- `rotacion_anual` empieza en 2008 (CDL nacional): de 2000 a 2007 esas columnas están vacías.
