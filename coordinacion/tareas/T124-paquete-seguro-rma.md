---
id: T124
titulo: 'Paquete nuevo `seguro`: causas de pérdida y superficie asegurada de RMA por condado (código listo, espera
  OK)'
estado: hecha
plan_minimo: pro
maquina: pro-4
estados: []
depende_de: []
rama: null
creada: 2026-11-15T09:11
actualizada: 2026-11-15 09:32
---

## Qué hacer

Implementá lo que propone `docs/research/rma_causa_perdida.md` (T016) como paquete nuevo `seguro`:
`src/seguro/download.py`, `src/seguro/process.py`, `docs/datasets/seguro.md`, siguiendo el contrato de la
sección 4 del CLAUDE.md y el estilo de los paquetes que ya existen (`asegurar_manifest`, idempotencia,
`FIELDSHIFT_ESTADOS`, `validar_csv()`).

- Bajar `colsom_<AAAA>.zip` (Cause of Loss) y `sobtpu_<AAAA>.zip` (Summary of Business con práctica) de 2000 a
  2025 a `data/raw/seguro/`, una fila por archivo en `manifest.csv`. Filtrar por los estados de la configuración
  al procesar, no al bajar.
- `seguro_anual.csv`: `fips, anio, cultivo` (maíz, soja, trigo de invierno, avena; los códigos RMA salen del
  research) con superficie asegurada, responsabilidad, prima, indemnización, `loss_ratio` y la indemnización
  por grupo de causa (sequía, exceso de humedad, calor, granizo, helada, otras). Unidades originales (acres,
  USD) en la columna.
- `seguro_mensual.csv`: `fips, anio, mes, cultivo`, indemnización por grupo de causa según el mes de la pérdida.
- Pruebas sin red en `tests/` con unas líneas de ejemplo de cada archivo (separador `|`, sin encabezado).
- Data card completo, con la tabla de causas → grupos, y cómo se tratan los condados que RMA no tiene en
  `condados.csv`.

Probalo de punta a punta con **un** estado (el que tengas a mano; los zips son chicos) y contá en el PR filas,
años y % de faltantes. No toques `src/common/`, `config/` ni `src/merge.py`.

**El PR no se une hasta que el humano diga que sí** a la fila 6 de `coordinacion/para_decidir.md` (esquema
nuevo). Escribí al principio del cuerpo del PR: "Espera el OK de para_decidir #6; no unir antes". Así, si
dice que sí al despertarse, está listo para unir y correr en las máquinas Max.

## Terminada cuando

El código, las pruebas y el data card en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 09:21 · pro-4: tomada
- 2026-11-15 09:32 · pro-4: terminada por el trabajador: PR #119, falta la revisión de max-1
