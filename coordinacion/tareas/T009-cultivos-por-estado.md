---
id: T009
titulo: Fechas de siembra y cosecha por estado (config/cultivos_estado.csv)
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
creada: 2026-11-15 01:07
actualizada: 2026-11-15 01:07
---

## Qué hacer

Aprobado por el humano el 2026-11-15. Con 7 estados, una fila por cultivo en `config/cultivos.csv` queda muy
ancha: los extremos los ponen estados donde el cultivo casi no se siembra (trigo de invierno de Minnesota,
avena de Kansas). Crear `config/cultivos_estado.csv`, en formato largo, una fila por cultivo y estado:

`cultivo, estado, siembra_inicio, siembra_activa_inicio, siembra_activa_fin, siembra_fin, cosecha_inicio,
cosecha_activa_inicio, cosecha_activa_fin, cosecha_fin, fuente, pagina`

- Fechas `MM-DD`, como en `cultivos.csv`. `estado` con el código de 2 letras de `config.yaml`. Los códigos de
  `cultivo` son los de `cultivos.csv`.
- Fuente: USDA Agricultural Handbook 628 (2010), la tabla de cada estado. Las tablas de los 7 estados ya
  están en `docs/research/cultivos_zona.md` (T006). Sumar el período más activo (*most active*), que hoy
  no está.
- Lo que el Handbook no trae (dice "(NA)" o no lista el cultivo) queda vacío. No completar con otro estado.
- Cada celda con su cita en `docs/research/cultivos_fuentes.csv`, como en T006.
- `config/cultivos.csv` **no cambia**: sigue con los rasgos de cada cultivo y el rango general.
- Agregar una sección "Fechas por estado" en `docs/research/cultivos_zona.md` que explique para qué sirve
  cada archivo. Para el modelo, las fechas reales de cada año están en `fenologia_estado.csv` (Crop Progress).
  Este archivo es la referencia "habitual" y sirve para armar las ventanas fijas de cada estado.

## Terminada cuando

`config/cultivos_estado.csv` con los 7 estados y los 6 cultivos con fechas (maíz, soja, trigo de invierno,
avena, alfalfa, heno), cada celda con su cita, y un PR a `main`.

## Notas
