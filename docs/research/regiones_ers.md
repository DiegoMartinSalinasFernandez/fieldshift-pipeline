# Regiones de ERS (Farm Resource Regions) para los estados de la zona

Tarea T005 (pro-2), 2026-11-15.

**Pregunta.** `src/economia/process.py` asignaba la región Heartland de ERS a todos los estados.
¿En qué Farm Resource Region cae cada estado de la zona (OH, NE, MN y KS, y de paso IA, IL e IN)?
¿Hay una tabla oficial condado → región? ¿Qué conviene usar para los costos por estado?

## Respuesta corta

ERS publica la región de **cada condado** en `reglink.xls` ("Aggregating counties to ERS resource
regions"), enlazada desde la documentación de Commodity Costs and Returns. Con esa tabla:

| estado | condados | regiones (condados) |
|---|---|---|
| IA (19) | 99 | Heartland 99 |
| IL (17) | 102 | Heartland 102 |
| IN (18) | 92 | Heartland 92 |
| OH (39) | 88 | Heartland 48, Northern Crescent 22, Eastern Uplands 18 |
| NE (31) | 93 | Prairie Gateway 37, Heartland 29, Northern Great Plains 27 |
| MN (27) | 87 | Heartland 41, Northern Crescent 35, Northern Great Plains 11 |
| KS (20) | 105 | Prairie Gateway 105 |

- **IA, IL e IN** son enteramente Heartland: lo que ya hacía `economia` era correcto para ellos.
- **KS** es enteramente Prairie Gateway: no debe usar Heartland.
- **OH, NE y MN** se reparten en tres regiones cada uno. No hay una sola región "correcta" por
  estado.

**Propuesta (implementada en la rama `tarea/T005-regiones-ers`).** Como la clave del paquete es
`fips_estado` y ERS no publica por estado, cada estado recibe el **promedio de los costos
regionales de ERS ponderado por el área sembrada del cultivo** en los condados de cada región
(suma de `ACRES PLANTED` de NASS por condado en 2000–2025). Para IA, IL, IN y KS el peso es 1 y
el resultado es exactamente el valor de su región. Ver los pesos más abajo.

Alternativa descartada por ahora: entregar costos por condado (`fips_condado` → región ERS). Es
más preciso pero cambia el esquema del CSV (clave por condado), y eso lo decide el humano. Con
`reglink.xls` y `pesos_region_ers.csv` el equipo de ML puede hacerlo después si lo necesita.

## Series de ERS disponibles por región (CSV bajados el 2026-11-15)

Unidad `dollars per planted acre`.

| región | maíz | soja | trigo | avena |
|---|---|---|---|---|
| Heartland | 1996–2025 | 1997–2025 | 1998–2025 | 2005–2025 |
| Northern Crescent | 1996–2025 | 1997–2025 | 1998–2025 | 2005–2025 |
| Northern Great Plains | 1996–2025 | 1997–2025 | 1998–2025 | 2005–2025 |
| Prairie Gateway | 1996–2025 | 1997–2025 | 1998–2025 | 2005–2022 |
| Eastern Uplands | 1996–2025 | 1997–2025 | no hay | 2023–2025 |

Cuando una región del estado no tiene serie un año, `process.py` repondera entre las regiones
con dato si cubren al menos el 50 % del peso; si no, deja el año vacío.

## Pesos por estado y cultivo

Participación de cada región en el área sembrada 2000–2025 (`ACRES PLANTED` de NASS por condado).
IA, IL e IN: 1,00 Heartland en los cuatro cultivos (la avena de IN, sin área por condado en NASS,
se pondera por cantidad de condados: también 100 % Heartland). KS: 1,00 Prairie Gateway.

| estado | región | maíz | soja | trigo de invierno | avena |
|---|---|---|---|---|---|
| OH | Heartland | 0,75 | 0,78 | 0,73 | 0,13 |
| OH | Northern Crescent | 0,21 | 0,20 | 0,25 | 0,61 |
| OH | Eastern Uplands | 0,04 | 0,02 | 0,02 | 0,27 |
| NE | Prairie Gateway | 0,51 | 0,42 | 0,52 | 0,26 |
| NE | Heartland | 0,41 | 0,55 | 0,02 | 0,46 |
| NE | Northern Great Plains | 0,08 | 0,03 | 0,46 | 0,28 |
| MN | Heartland | 0,74 | 0,66 | 0,06 | 0,44 |
| MN | Northern Crescent | 0,21 | 0,15 | 0,07 | 0,41 |
| MN | Northern Great Plains | 0,05 | 0,19 | 0,87 | 0,15 |

## Fuentes

- USDA ERS, `reglink.xls`, "Aggregating counties to ERS resource regions"
  (https://www.ers.usda.gov/sites/default/files/images/reglink.xls), consultada 2026-11-15.
  Columnas `Fips` y `ERS resource region` (códigos 1 a 9); la clave de la misma planilla:
  1 Heartland, 2 Northern Crescent, 3 Northern Great Plains, 4 Prairie Gateway, 5 Eastern
  Uplands, 6 Southern Seaboard, 7 Fruitful Rim, 8 Basin and Range, 9 Mississippi Portal. Metadatos
  del archivo: creado en 2008, última modificación en 2017.
- USDA ERS, Commodity Costs and Returns — Documentation
  (https://www.ers.usda.gov/data-products/commodity-costs-and-returns/documentation), consultada
  2026-11-15: las estimaciones "recent" usan las Farm Resource Regions de ERS y enlazan
  `reglink.xls`.
- USDA ERS, Commodity Costs and Returns, CSV de maíz, soja, trigo y avena
  (https://www.ers.usda.gov/data-products/commodity-costs-and-returns), versiones registradas en
  `manifest.csv` (2026-11-15).
- USDA NASS Quick Stats, volcado `qs.crops_20261114.txt.gz`, `ACRES PLANTED` por condado.

Confianza: alta para la región de cada condado (tabla oficial de ERS) y para las series
disponibles (salen de los CSV). Media para el método de ponderación: es una decisión nuestra,
razonable pero no un producto de ERS.
