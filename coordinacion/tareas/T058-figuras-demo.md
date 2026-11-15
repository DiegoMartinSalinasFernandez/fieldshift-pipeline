---
id: T058
titulo: Script de figuras para la demo con los datos publicados
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15 04:30
actualizada: 2026-11-15 04:30
---

## Qué hacer

Escribí `docs/demo/figuras.py`: baja con `gh release download` los zips publicados (`datos-ia-il-in`, y
`datos-ks` o `datos-oh-ne-mn` si ya están), los lee sin descomprimir a disco y guarda en `docs/demo/fig/` 3 a 5
PNG simples (matplotlib), por ejemplo:

- rendimiento de maíz por condado en 2012 contra un año normal, con la lluvia de julio (`clima_anual.csv`);
- NDVI máximo contra rendimiento (`fenologia_anual.csv` y `produccion_anual.csv`);
- humedad de suelo SMAP de mayo y día de siembra del 50 % (`agua_mensual.csv`, `fenologia_estado.csv`);
- área en maíz tras soja contra maíz tras maíz (`rotacion_anual.csv`).

Ejes y títulos en inglés, con la fuente al pie. No hagas modelos ni tendencias: solo los datos. Si un zip o una
columna no está, la figura se saltea con un aviso. Subí el script y los PNG que salgan.

El envío a Space Apps cierra el **domingo 2026-11-15 a las 23:59 hora del evento local** (Project Submission Guide, verificado el 2026-11-15). Partí de `docs/research/space_apps_criterios.md`. Todo en inglés. **No inventes cifras ni resultados**: cada número sale de un data card, de un CSV publicado o de un documento del repo, y se dice de cuál. Lo que no esté, queda marcado `[TBD]` para el equipo.

## Terminada cuando

El script y las figuras en un PR.

## Notas
