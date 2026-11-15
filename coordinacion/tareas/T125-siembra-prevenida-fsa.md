---
id: T125
titulo: 'Siembra prevenida de FSA por condado (`seguro`): código listo, espera OK'
estado: tomada
plan_minimo: pro
maquina: pro-4
estados: []
depende_de:
- T124
rama: null
creada: 2026-11-15T09:11
actualizada: 2026-11-15 09:32
---

## Qué hacer

Depende de T124 (mismo paquete `seguro`): partí de su rama o de `main` si ya se unió. Implementá lo que propone
`docs/research/siembra_prevenida.md` (T032):

- `src/seguro/download.py`: bajar los zips de FSA Crop Acreage Data (el archivo final de cada año, 2009–2025) a
  `data/raw/seguro/fsa/`, con su fila en `manifest.csv`.
- `src/seguro/process.py`: `siembra_prevenida_anual.csv` con `fips, anio, cultivo` y `sup_sembrada_fsa_ac`,
  `sup_prevenida_ac`, `sup_fallida_ac`, `pct_prevenida` (prevenida / (sembrada + prevenida)). Riego y secano
  sumados; si el research lo recomienda, columnas aparte.
- Los códigos de condado administrativos de FSA que no son FIPS (19156 West Pottawattamie, 27112, 27120, 27138…,
  ver el research): mapearlos al FIPS del Census con una tabla en `data/reference/` armada desde el research, y
  documentarlo. Nunca descartarlos en silencio.
- `openpyxl` a `requirements.txt` si no está.
- Pruebas sin red con un `.xlsx` mínimo armado en la prueba. Data card de `seguro`: sección nueva.

Probalo con 2019 (año récord) en un estado y compará el total con el que da el research.

**El PR no se une hasta que el humano diga que sí** a la fila 17 de `coordinacion/para_decidir.md` (esquema
nuevo). Escribí al principio del cuerpo del PR: "Espera el OK de para_decidir #17; no unir antes". Así, si
dice que sí al despertarse, está listo para unir y correr en las máquinas Max.

## Terminada cuando

El código, las pruebas y el data card en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 09:32 · pro-4: tomada
