# Research agent de Field Shift

Un agente que arma los datasets de Field Shift solo, durante horas, sin que nadie lo mire.
Sigue el método de Karpathy (*autoresearch*) con el "loop sobre el loop" de AI LABS:

- **Checks bloqueados.** `loop/spec/*.yaml` y `loop/checks/score.py` definen qué es "mejor":
  archivos, columnas, rangos, cobertura, documentación verificada contra los datos, citas
  verificadas contra sus fuentes. Los aprueba el humano y el agente no los puede tocar.
- **Rondas con commit o reset.** Cada ronda la hace un agente nuevo (`claude -p`) con
  `loop/program.md` y una tarjeta de la tarea. Al terminar, el orquestador corre los checks
  con su copia privada: si el puntaje total sube y nada de lo que ya sumaba baja, commit; si
  no, `git reset`. Solo sobrevive la bitácora (`loop/notes/`).
- **Reflexión.** Cada 5 rondas (o cuando una tarea se traba) otro agente lee los resultados y
  reescribe la sección "Cómo trabajar" de `program.md`. Las reglas fijas no cambian.

## Qué necesita

- Windows, `git`, [`uv`](https://docs.astral.sh/uv/) y Claude Code (`claude`) con sesión iniciada.
- Credenciales (las crea el humano; el agente nunca las lee):
  - Earthdata: `~/.netrc` con `machine urs.earthdata.nasa.gov login <usuario> password <clave>`.
  - NASS Quick Stats: `.env` en la raíz con `NASS_API_KEY=<clave>` (gratis en quickstats.nass.usda.gov/api).
  Sin ellas el loop corre igual: busca accesos públicos o marca esas partes como bloqueadas, y
  las retoma solo cuando aparecen las credenciales.

## Cómo se usa

```
python loop/aprobar_checks.py --resumen     # los checks en palabras simples
python loop/aprobar_checks.py --aprobar     # los bloquea (LOCK.json) y hace commit
python loop/run.py --hours 8                # en una terminal propia, no dentro de Claude
```

- Frenar sin cortar una ronda a la mitad: crear el archivo `loop/STOP`.
- Retomar: `python loop/run.py --resume <tag> --hours 4`.
- Prueba corta: `python loop/run.py --hours 0.5 --max-rounds 1 --only base`.
- Ver el puntaje en cualquier momento (solo lectura): `python loop/puntaje.py --tarea clima`.
- Si falta `pyyaml`, `run.py` y `aprobar_checks.py` se relanzan solos con `uv`.

El orquestador trabaja en la rama `autoresearch/<tag>` y deja todo en `loop/runs/<tag>/`
(prompt, log y reporte de cada ronda, `results.tsv`, `run.log`). Al final escribe
`loop/reports/<tag>.md`.

## Registro de rondas (Excel)

`loop/runs/registro_rondas.xlsx` se rehace solo después de cada ronda (lo arma
`loop/registro.py`, que también se puede correr a mano o dejar mirando con `--watch`).
Si está abierto en Excel cuando termina una ronda, se actualiza en la siguiente: cerralo o
abrilo en solo lectura. Hojas:

- **Resumen**: qué está haciendo ahora, puntaje, credenciales y una fila por corrida.
- **Rondas**: una fila por ronda: tarea, resultado, puntos, minutos, costo, qué hizo y qué
  decidió el agente.
- **Tareas**: avance de cada paquete y tema de research, en qué está y qué le falta.
- **Fuentes**: los recursos del desafío (pestaña Resources), cuáles se usan, cuáles están
  bloqueados por credenciales y por qué no se usan los otros.
- **Decisiones**: lo que el agente dejó para el humano en `loop/notes/decisiones.md`.
- **Datos**: los CSV procesados y lo que se bajó por paquete.

## Paquetes de los recursos del desafío

Además de los seis paquetes del CLAUDE.md §6, `loop/spec/entregables.yaml` tiene ocho que
suman los "NASA Data & Resources" del desafío, con el mismo contrato de CSV:

| Paquete | Fuentes | Archivo |
|---|---|---|
| `economia` | USDA NASS (precio recibido), USDA ERS (costos y retornos) | `economia_anual.csv`, `economia_forrajes_anual.csv` (por estado) |
| `aptitud` | FAO GAEZ v4 | `aptitud_estatico.csv` |
| `paisaje` | USGS NLCD | `paisaje_anual.csv` |
| `teledeteccion` | Landsat, Sentinel-2 (o HLS) | `teledeteccion_anual.csv` |
| `validacion` | PRISM, CoCoRaHS | `validacion_mensual.csv` |
| `ecostress` | ECOSTRESS (pide Earthdata) | `ecostress_mensual.csv` |
| `nldas` | NLDAS-2 (pide Earthdata) | `nldas_mensual.csv` |
| `hidrologia` | USGS NWIS / Water Data APIs | `hidrologia_mensual.csv` |

Los temas de research `recursos_desafio` y `ag_data_commons` verifican cómo se baja cada
recurso y qué más conviene sumar. Los nombres de columna de estos paquetes son propuesta.

Las tablas unidas (`merge`) dependen de todos los paquetes: cuando una ronda de otra tarea
suma o cambia un archivo, `tabla_anual.csv` y `tabla_mensual.csv` quedan viejas y sus checks
bajan. Eso no se cuenta como regresión de esa ronda: `merge` vuelve a la cola y en los
últimos 45 minutos de la corrida pasa adelante, para que las tablas terminen al día.

## Qué cuida el orquestador

- Un hook (`loop/hooks/guard.py`, cargado solo durante la corrida) bloquea escribir fuera de
  las rutas de la tarea, tocar los checks, usar git para cambiar cosas, borrar o modificar
  `data/raw/` y leer credenciales.
- Después de cada ronda verifica los hashes de los archivos bloqueados contra su copia
  privada, revierte lo que quedó fuera de alcance y aparta los archivos de raw de las rondas
  descartadas en `data/interim/<paquete>/_descartados/`.
- Los archivos de `data/raw/` quedan de solo lectura después de cada ronda guardada.
- Mata todos los procesos de la ronda al terminar (las descargas tienen que ser reanudables).
- Si se agota el límite de uso de Claude, espera al reinicio y sigue.
- Evita que Windows se suspenda mientras corre.

## Cómo revisar lo que hizo

1. `loop/reports/<tag>.md`: puntaje inicial y final, rondas, decisiones pendientes para el
   humano (`loop/notes/decisiones.md`), hábitos que aprendió la reflexión.
2. `git log --oneline autoresearch/<tag>`: una ronda guardada por commit.
3. Los data cards (`docs/datasets/`), sobre todo "Supuestos" y "Problemas conocidos".
4. Si está bien, merge de la rama a `main`.

## Archivos

| Archivo | Qué es | ¿Lo toca el agente? |
|---|---|---|
| `loop/program.md` | instrucciones de cada ronda | no (la reflexión reescribe "Cómo trabajar") |
| `loop/spec/entregables.yaml` | checks de los paquetes de datos | no |
| `loop/spec/research.yaml` | checks de research y de `config/cultivos.csv` | no |
| `loop/spec/catalogo.csv` | IDs y prioridades del catálogo | no |
| `loop/checks/score.py` | el verificador | no |
| `loop/hooks/guard.py` | el hook que bloquea | no |
| `loop/run.py` | el orquestador | no |
| `loop/puntaje.py` | puntaje para el agente (solo lectura) | lo corre |
| `loop/registro.py` | arma `loop/runs/registro_rondas.xlsx` | no |
| `loop/notes/` | bitácoras y decisiones | sí |
| `docs/estructura_csv.md` | guía de los CSV para el equipo de ML (sale de los checks) | no |
