---
id: T015
titulo: Pruebas de src/common (tests/test_common.py)
estado: tomada
plan_minimo: pro
maquina: pro-1
estados: []
depende_de: []
rama: null
creada: 2026-11-15 01:40
actualizada: 2026-11-15 02:55
---

## Qué hacer

`src/common/` lo usan todos los paquetes y no tiene pruebas. Escribí `tests/test_common.py` con pytest
(agregalo a `requirements.txt` si falta) que cubra, con datos chicos inventados solo para la prueba:

- conversiones de la sección 4 del CLAUDE.md: maíz 62,77; soja y trigo 67,25; avena 35,87 kg/ha por bu/ac;
  1 acre = 0,4047 ha;
- `fecha_a_anio()` y las ventanas de `anios.csv` (temporada abril–septiembre, invierno previo noviembre del
  año anterior a marzo);
- `validar_csv()`: detecta claves duplicadas, `fips` que no están en `condados.csv`, valores fuera de rango, y
  acepta un CSV correcto;
- `cargar_config()` con `FIELDSHIFT_ESTADOS` (filtra, y da error con un estado desconocido).

**No cambies `src/common/`.** Si una prueba muestra un error real, dejala marcada con `xfail` y explicalo en
"Para decidir".

## Terminada cuando

`pytest tests/test_common.py` pasa (o solo falla lo marcado `xfail`), en un PR.

## Notas
- 2026-11-15 02:55 · pro-1: tomada
