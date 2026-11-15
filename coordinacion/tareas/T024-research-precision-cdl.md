---
id: T024
titulo: 'Research: precisión del CDL por estado y año (2008–2025)'
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
creada: 2026-11-15 02:50
actualizada: 2026-11-15 02:50
---

## Qué hacer

Las rotaciones (`rotacion_anual.csv`, `rotacion_secuencia.csv`) y las máscaras salen del CDL. Su precisión
cambia por estado, año y cultivo. Para los 7 estados averiguá en los metadatos oficiales del CDL (las
"accuracy assessments" que NASS publica por estado y año):

- precisión del productor y del usuario para maíz, soja, trigo de invierno, avena, alfalfa y otro heno, por
  estado, al menos para 2008, 2012, 2016, 2020, 2024 y 2025;
- dónde están (URL exacta y formato) y si se pueden bajar todos juntos;
- qué estados o años tienen precisiones bajas que convenga anotar en el data card de `cultivos`.

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets grandes ni toques `src/` o `data/`.

Escribí `docs/research/cdl_precision.md`, con una tabla por cultivo.

## Terminada cuando

El research en un PR.

## Notas
