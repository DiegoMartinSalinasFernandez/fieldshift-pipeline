# Pendientes del humano antes del envío (T118)

Estado al 2026-11-15. El envío cierra hoy a las 23:59 (hora del evento local). Esta tabla lista los `[TBD]` de
`README.md`, `docs/demo/project_page.md`, `slides.md`, `video.md` y `limitations.md` que el repo **no** puede
responder. Los que sí tenían respuesta en el repo ya se completaron, con su fuente al lado (ver más abajo).

Las líneas son las de esta rama. Están ordenadas por importancia para los jueces: primero lo que el formulario
exige (sin eso el proyecto no entra a Global Judging), después lo que cambia lo que se afirma, y al final lo cosmético.

## Bloqueantes del formulario

| # | Archivo | Línea | Qué falta | Depende de |
|---|---|---|---|---|
| 1 | `project_page.md` | 70 | Link público a la demo: video de ≤ 30 s **o** hasta 7 láminas, fuera del sitio de Space Apps | Equipo (subir el video o las láminas) |
| 2 | `project_page.md` | 31 | Nombre final del proyecto (título provisorio: *Field Shift: Rotations Read from Space*) | Equipo |
| 3 | `project_page.md` | 34–35 | Nombre del equipo, integrantes (6 como máximo) y evento local | Equipo |
| 4 | `slides.md` | 34, 37 | Lo mismo en la lámina 1: nombre, lema, equipo, integrantes y evento | Equipo |
| 5 | `slides.md` | 265–266 | Guion del video: nombres del equipo, del proyecto y lema | Equipo |
| 6 | `video.md` | 48–51, 139, 152 | Nombre del equipo y del proyecto en la toma 1, la narración y los subtítulos | Equipo |
| 7 | `project_page.md` | 196 | Si alguna imagen, voz o video de la demo está hecho con IA (lleva entonces la marca de agua "AI-generated") | Equipo (quien arme el video) |

## Cambian lo que se afirma

| # | Archivo | Línea | Qué falta | Depende de |
|---|---|---|---|---|
| 8 | `project_page.md` | 219; `slides.md` 219, 177, 145, 268 | Si se publican los releases de IA/IL/IN, `lotes` y `ecostress`. Si no, sacar ECOSTRESS, HLS, los 10 lotes y la validación contra PRISM del formulario y de las láminas | Humano: `coordinacion/para_decidir.md` #33 (publicar `datos-ia-il-in` y `fieldshift_lotes_v1`) |
| 9 | `project_page.md` | 135 | Publicar `fieldshift_lotes_v1` o sacar el punto 4 ("Field level") | Humano, `para_decidir.md` #33 |
| 10 | `project_page.md` | 201 | La página dice que la declaración de IA está "en la metadata de los releases". El README la tiene, pero las notas que escribe `scripts/entregar.py` no. Agregarla a mano en las notas de `datos-oh-ne-mn` o sacar esa frase | Humano (editar el release) |
| 11 | `project_page.md` | 24, 145; `limitations.md` 24, 136; `slides.md` 123, 267 | Modelo, validación, rangos de incertidumbre e interfaz, con números propios | Equipo de ML / frontend |
| 12 | `project_page.md` | 89, 175, 63 | Link de la herramienta o frontend (si hay), stack de ML/frontend y una frase sobre qué ve el usuario | Equipo de frontend / ML |
| 13 | `slides.md` | 153 | Mapa de sectores (loma seca / media loma / bajo húmedo) | Equipo de ML (y release `lotes`) |
| 14 | `limitations.md` | 22, 133 | Lista final de estados y condados entregados | Humano / max-1 (releases de IA/IL/IN y KS) |
| 15 | `project_page.md` | 122; `README.md` 40; `limitations.md` 135 | Tamaño y % de faltantes de las tablas unidas de los 7 estados | max-1 (T008, `merge.py`) |
| 16 | `limitations.md` | 45, 134 | Cobertura final de ECOSTRESS y `teledeteccion` | Release de IA/IL/IN (`para_decidir.md` #33) |
| 17 | `slides.md` | 200 | Dispersión de lluvia contra PRISM (necesita `validacion` publicado) | Release de IA/IL/IN |
| 18 | `slides.md` | 242 | Confirmar la redacción de la línea de IA de la lámina 7 | Equipo |

## Opcionales o cosméticos

| # | Archivo | Línea | Qué falta | Depende de |
|---|---|---|---|---|
| 19 | `project_page.md` | 161 | Metas de corto y largo plazo | Equipo |
| 20 | `project_page.md` | 312, 323 | Otros papers usados en la demo o la herramienta; herramientas de frontend, ML, video y láminas, e imágenes o íconos abiertos | Equipo |
| 21 | `project_page.md` | 258 | Si se menciona Landsat también en "NASA Data" como "USGS/NASA Landsat" | Equipo |
| 22 | `slides.md` | 98 | Mapas por condado de `pct_maiz_tras_maiz` y de una capa NASA (no existen como PNG) | Tarea nueva de figuras, si el equipo la quiere |
| 23 | `slides.md` | 194 | Serie mensual de un condado (SMAP e IMERG) como alternativa a fig3 | Tarea nueva de figuras, opcional |
| 24 | `slides.md` | 298 | Resumen de pendientes al final de las láminas: se cierra solo cuando se cierren los de arriba | — |

Las líneas 13 de `project_page.md`, 14 de `slides.md`, 10 de `limitations.md`, 20 y 147 de `video.md` y la casilla
de la línea 332 de `project_page.md` explican qué significa `[TBD]`. No son pendientes.

## Qué completó T118 desde el repo

| Archivo | Qué | De dónde sale |
|---|---|---|
| `project_page.md` §4, `slides.md` lámina 7 y video, `video.md` toma 7 | URL del repo | `git remote get-url origin` (2026-11-15) |
| `project_page.md` §4, `slides.md` lámina 7, `README.md` | URL del release publicado `datos-oh-ne-mn` y de la página de releases | `docs/demo/coverage.md` (único release publicado al 2026-11-15) |
| `project_page.md` §4 | Link a `docs/datasets/README_en.md` | El archivo existe en el repo |
| `project_page.md` §7, `slides.md` lámina 7 | POWER: versión `Daily 2.10.3` y fecha de acceso `2026/11/14` | `manifest.csv` de los zips de `datos-oh-ne-mn`: todos los pedidos a POWER del 2026-11-14; los de `IMERG_PRECTOT` registran "POWER API v2.10.3" y los de meteorología solo "v2 (API)". **Revisar** si se suman releases bajados otro día |
| `project_page.md` §8, `slides.md` lámina 7 | Atribución de Copernicus: "Contains modified Copernicus Sentinel data 2016–2025, processed by NASA (HLS S30 v2.0)." | `docs/research/licencias_fuentes.md` (T060, hecha). Solo si HLS queda en la lista |
| `project_page.md` §2 | Números de la penalización por rotación (−4,3 % / −1,7 % maíz continuo; −10,3 % / −9,6 % soja continua) | `docs/research/efecto_rotacion.md` §2 (Seifert et al. 2017) |
| `project_page.md` §6 | El README tiene la declaración de IA (sección "Use of AI") | `README.md` |
| `README.md`, `limitations.md` 0.2 | Estado de los releases al 2026-11-15 (solo OH/NE/MN publicado; MO/WI/SD, IA/IL/IN y KS en proceso) | `docs/demo/coverage.md` |
| `slides.md` | Se sacó de la lista de pendientes el mapa de la lámina 1: `fig/fig0_mapa.png` ya existe (T094) | `docs/demo/fig/README.md` |
