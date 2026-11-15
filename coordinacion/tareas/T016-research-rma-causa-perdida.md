---
id: T016
titulo: 'Research: causas de pérdida del seguro agrícola (USDA RMA) por condado'
estado: libre
plan_minimo: pro
maquina: null
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
creada: 2026-11-15 01:40
actualizada: 2026-11-15 01:40
---

## Qué hacer

El USDA Risk Management Agency publica "Cause of Loss" por condado, cultivo, año y causa (sequía, exceso de
humedad, granizo, helada…), con superficie indemnizada y montos. Podría ser un target de riesgo o una forma
de validar el clima. Averiguá:

- dónde se baja (URL exacta, formato, años disponibles, cómo vienen los códigos de estado, condado, cultivo y
  causa) y si hay un diccionario oficial de columnas;
- también el "Summary of Business" por condado (superficie asegurada, primas), que sirve de denominador;
- si sirve para maíz, soja, trigo de invierno y avena en los 7 estados, y qué tan completo está por condado;
- licencia y cualquier limitación (datos ocultos, cambios de códigos entre años).

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets ni toques `src/` o `data/`.

Escribí `docs/research/rma_causa_perdida.md`.

## Terminada cuando

El research en un PR, con una propuesta concreta de qué columnas bajar (sin bajarlas).

## Notas
