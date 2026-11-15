---
id: T046
titulo: Pruebas de validar_csv() con los 7 estados (sin cambiar src/common)
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15 04:05
actualizada: 2026-11-15 04:05
---

## Qué hacer

Con 7 estados, `validar_csv()` de `src/common/` tiene que aceptar `fips` de OH (39), NE (31), MN (27) y KS (20) y
rechazar los de otros estados, y los rangos físicos tienen que valer para Kansas (rendimientos de secano más bajos)
y Nebraska (riego). Escribí `tests/test_validar_siete.py` con CSV chicos e inventados que controlen:

- claves duplicadas y `fips` inexistentes, con un `condados.csv` inventado de dos estados nuevos;
- rendimientos en el borde de los rangos del CLAUDE.md §7 (maíz 20–300, soja 5–100 bu/ac);
- faltantes como celda vacía y `flag_nass` con `(D)` y `(Z)`.

**No cambies `src/common/`**: si una regla no sirve para los estados nuevos, marcá la prueba `expectedFailure` y
explicalo en "Para decidir". Las pruebas tienen que pasar en Windows y en Linux.

## Terminada cuando

Las pruebas en un PR.

## Notas
