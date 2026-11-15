---
id: T120
titulo: 'suelo_terreno: repartir por condado las áreas de levantamiento que no son un condado (necesario para KY)'
estado: libre
plan_minimo: pro
maquina: null
estados:
- KY
depende_de: []
rama: null
creada: 2026-11-15T08:45
actualizada: 2026-11-15T08:45
---

## Qué hacer

`docs/research/suelo_ky.md` (T087): en Kentucky 39 de las 84 áreas de levantamiento de SSURGO juntan dos o tres
condados o son áreas especiales, y `fips_de_area()` de `src/suelo_terreno/process.py` las convierte en FIPS que no
existen: 75 de los 120 condados quedarían sin suelo. Ese research trae una propuesta de reparto (con `laoverlap` /
`muaoverlap` de Soil Data Access): implementala en `src/suelo_terreno/`.

- **Para los 10 estados de hoy el resultado tiene que ser idéntico**: comprobalo con una prueba (por ejemplo, que
  para áreas `XX` + código de condado el reparto nuevo da lo mismo que `fips_de_area()`), y si tenés datos de algún
  estado procesado, compará el `suelo_terreno_estatico.csv` antes y después.
- Pruebas sin red en `tests/` para un área que junta dos condados y para un área especial.
- No toques `src/common/` ni `config/` (KY no está aprobado en `config.yaml`; esto deja el código listo).
- Data card de `suelo_terreno`: el supuesto del reparto.

## Terminada cuando

El cambio y las pruebas en un PR, con CI en verde.

## Notas
