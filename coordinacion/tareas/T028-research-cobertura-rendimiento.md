---
id: T028
titulo: 'Research: efecto de los cultivos de cobertura en el rendimiento siguiente'
estado: tomada
plan_minimo: pro
maquina: pro-4
estados:
- IA
- IL
- IN
- OH
- NE
- MN
- KS
depende_de: []
rama: null
creada: 2026-11-15 03:00
actualizada: 2026-11-15 02:49
---

## Qué hacer

La herramienta compara rotaciones, y lo que el modelo no predice (suelo, nitrógeno, carbono, erosión,
agua) sale de reglas con fuente (skill de ML, sección 8). Este research arma una de esas reglas.

Para el Corn Belt, en ensayos y metaanálisis con revisión:

- cuánto cambia el rendimiento del maíz y de la soja después de centeno de cobertura (y de avena o trébol),
  con el rango y de qué depende (fecha de terminación, N, clima, años de uso);
- efecto sobre la humedad del suelo en primavera, la erosión y el nitrato lixiviado;
- si hay diferencias entre el norte (MN) y el sur (KS) de la zona.

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets grandes ni toques `src/` o `data/`.

Escribí `docs/research/cobertura_rendimiento.md`, con una tabla de estudios.

## Terminada cuando

El research en un PR, con valores citados usables como reglas y su incertidumbre.

## Notas
- 2026-11-15 02:49 · pro-4: tomada
