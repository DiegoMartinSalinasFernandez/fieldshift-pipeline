---
id: T156
titulo: Llenar en los estados nuevos las 37 columnas que hoy solo tiene IA/IL/IN (aptitud, teledeteccion, validacion,
  ecostress, hidrologia)
estado: libre
plan_minimo: max
maquina: null
estados:
- OH
- NE
- MN
- MO
- WI
- SD
depende_de: []
rama: null
creada: 2026-11-15T15:08Z
actualizada: 2026-11-15 14:58
---

## Qué pasa

T155 juntó los 9 estados con las columnas de la v3 (`tabla_anual` de 110 columnas y `tabla_mensual` de 68).
Las de los 19 archivos por paquete en común coinciden todas. Pero **37 columnas tienen dato solo en IA, IL e
IN**, porque sus paquetes los armó el loop solo para la primera tanda:

| Paquete | Columnas | Contenido |
|---|---|---|
| `aptitud` | 16 | aptitud y rendimiento alcanzable 1981-2010 y 2041-2070 |
| `teledeteccion` | 7 | suelo desnudo, cobertura verde, BSI, NDVI de 30 m |
| `validacion` | 6 | PRISM y CoCoRaHS |
| `ecostress` | 4 | |
| `hidrologia` | 4 | napa y caudales |

## Qué hacer

1. `ecostress`, `teledeteccion` y `validacion` ya están en `src/`: correlos para OH/NE/MN y MO/WI/SD (y KS y ND
   cuando estén) y sumá sus zips a cada release.
2. `aptitud` e `hidrologia` existen solo en el código del loop (ResearchAgent). Pasalos a `src/` con sus pruebas,
   sin cambiar columnas.
3. Antes de bajar, mirá el peso: si pasa de 5 GB por grupo, consultá al humano (regla 6).

## Terminada cuando

Las 37 columnas tienen dato en los estados nuevos, o hay un motivo escrito por el que no se puede. Los releases se
publican de nuevo y se rearma `unido_9_estados`.

## Notas
- 2026-11-15 14:58 · max-1: max-1: aptitud (16 columnas) y PRISM (4) armados para OH/NE/MN, MO/WI/SD, KS y ND con el código del loop sobre los crudos ya bajados (globales/CONUS); van en el zip de 11 estados para ML y front, todavía no en los releases ni en src/ de este repo. Faltan teledeteccion, ecostress, hidrologia y CoCoRaHS.
