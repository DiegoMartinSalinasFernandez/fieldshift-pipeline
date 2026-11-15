---
id: T031
titulo: 'Research: eventos extremos 2000–2025 en los 7 estados (para control de calidad)'
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
creada: 2026-11-15 03:00
actualizada: 2026-11-15 03:00
---

## Qué hacer

Para controlar los datos (T007) y para que ML entienda los años raros, armá una lista con fuente de los
eventos que movieron el rendimiento o la siembra por estado: sequías (2002, 2012…), primaveras muy húmedas y
siembra prevenida (2019), derecho de Iowa (2020), heladas tempranas o tardías, granizo grande, inundaciones
(2008, 2011, 2019). Para cada uno: estados y, si se sabe, condados afectados; meses; efecto en el rendimiento
del estado (NASS, nivel estado, se puede consultar) y en qué variable de nuestros CSV debería verse (por
ejemplo `spi3` muy negativo en julio de 2012, `prec_temporada_mm` alto en 2019).

Formato de research de la sección 8 del CLAUDE.md (pregunta, respuesta corta, detalle, fuentes con fecha de
consulta, confianza, impacto). Solo fuentes que hayas abierto; lo que no encuentres, se dice. No bajes
datasets grandes ni toques `src/` o `data/`.

Escribí `docs/research/eventos_extremos.md`, con una tabla por evento.

## Terminada cuando

El research en un PR.

## Notas
