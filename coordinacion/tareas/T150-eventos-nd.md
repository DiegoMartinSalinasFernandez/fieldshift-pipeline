---
id: T150
titulo: Lista de eventos extremos de Dakota del Norte para el QA (`docs/qa/eventos_nd.yaml`)
estado: libre
plan_minimo: pro
maquina: null
estados:
- ND
depende_de: []
rama: null
creada: 2026-11-15T14:14Z
actualizada: 2026-11-15T14:14Z
---

## Qué hacer

ND es la cuarta tanda (T149, en max-1). Prepará la lista de eventos para `scripts/qa_release.py`. Seguí el formato
de `docs/qa/eventos_mo_wi_sd.yaml` (T117) y tomá los eventos de `docs/research/eventos_extremos_mi_nd.md` (T069),
con la serie, el año, los condados o el estado y la dirección esperada. Ejemplos: sequía de 2017 y 2021, siembra
prevenida de 2011, 2013 y 2019, e inundaciones del Red River.

El rendimiento de condado de maíz y soja de ND existe recién desde 2018 (T067). Usá superficie, `ratio_cosechada`,
clima, agua o NDVI para los eventos de antes. No inventes eventos: cada uno cita su fuente del research.

Probá que `qa_release.py` lee el YAML: una prueba sin red o una corrida con datos de juguete.

## Terminada cuando

PR con CI en verde y lo que se encontró en el cuerpo del PR.

## Notas
