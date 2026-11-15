---
id: T151
titulo: Control de calidad de ND con el release publicado (`docs/qa/nd.md`)
estado: libre
plan_minimo: pro
maquina: null
estados:
- ND
depende_de:
- T149
- T150
rama: null
creada: 2026-11-15T14:14Z
actualizada: 2026-11-15T14:14Z
---

## Qué hacer

Cuando T149 publique `datos-nd`, hacé el mismo control que T081 (`docs/qa/mo_wi_sd.md`):

- bajá los zips y comprobá los `.sha256`;
- corré `verificar_entrega.py` y `qa_release.py` con `docs/qa/eventos_nd.yaml` (T150);
- revisá faltantes, rangos, outliers y totales contra NASS por estado;
- mirá en especial las columnas que en ND pueden venir casi vacías: rendimiento antes de 2018, `ndvi_maiz` y
  `ndvi_soja`, avena y trigo de invierno.

Escribí el veredicto por paquete en `docs/qa/nd.md`.

## Terminada cuando

PR con CI en verde y lo que se encontró en el cuerpo del PR.

## Notas
