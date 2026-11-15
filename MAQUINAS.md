# Cómo trabajan juntas las máquinas

Varias computadoras trabajan en este repo al mismo tiempo, cada una con la cuenta de Claude de su dueño: dos
con plan **Max** y dos con plan **Pro**. Las máquinas no se hablan entre ellas: **el repo es el punto de
encuentro**. Todo lo que una máquina necesita saber de otra está acá adentro.

| Qué | Dónde | Quién escribe |
|---|---|---|
| Qué hay que hacer y quién lo hace | `coordinacion/tareas/T00N-*.md` (el tablero) | cualquier máquina, con `scripts/tareas.py` |
| Qué hizo cada máquina en cada sesión | `coordinacion/bitacora/<maquina>.md` | cada máquina, solo en la suya |
| Cambios de código | una rama `tarea/<id>-<tema>` y un PR a `main` | la máquina que tomó la tarea |
| Datos procesados | Releases de GitHub, `datos-<estados>` | la máquina que tiene esos estados, con `scripts/entregar.py` |
| Qué máquina es cuál | `coordinacion/maquinas.yaml` | el humano o `max-1` |

`max-1` coordina: crea tareas, revisa y une los PRs, junta los datos de todos los estados y arma las entregas
para el equipo de ML. El humano decide lo que el CLAUDE.md le reserva: estados, período, descargas de más de
5 GB y cambios de esquema de los CSV.

**El repo es público.** No subas credenciales, `.env`, nombres, mails ni usuarios. Las máquinas se llaman
`max-1`, `max-2`, `pro-1` y `pro-2`.

---

## 1. Preparar una máquina (una sola vez)

1. **Acceso al repo.** El dueño del repo te agrega como colaborador. Instalá [Git](https://git-scm.com) y
   [GitHub CLI](https://cli.github.com), y entrá con `gh auth login`.
2. **Bajar el repo:**
   ```bash
   gh repo clone DiegoMartinSalinasFernandez/fieldshift-pipeline
   ```
3. **Python 3.11 con [uv](https://docs.astral.sh/uv/)**, dentro de la carpeta del repo:
   ```bash
   uv venv --python 3.11
   uv pip install -r requirements.txt
   ```
   En Windows corré los scripts con `.venv\Scripts\python -X utf8 ...`: la consola no es UTF-8 y los
   mensajes en castellano se rompen sin `-X utf8`.
4. **Quién sos y qué estados tenés.** Dos variables de entorno (en Windows, `setx` y abrir una terminal
   nueva):
   ```bash
   setx FIELDSHIFT_MAQUINA pro-1
   ```
   ```bash
   setx FIELDSHIFT_ESTADOS KS
   ```
   `FIELDSHIFT_ESTADOS` es la lista de `coordinacion/maquinas.yaml` (por ejemplo `OH,NE,MN`). Con ella todos los
   scripts bajan y procesan solo esos estados. No edites `config/config.yaml` para eso.
5. **Credenciales, solo si tu tarea las pide.** Casi todo se baja sin login. Earthdata (ECOSTRESS, LP DAAC) va
   en `~/.netrc` con tu propia cuenta; la clave de NASS Quick Stats, si la tenés, en `.env` como
   `NASS_API_KEY`. Las dos quedan fuera de git.
6. **Claude Code** (la app de escritorio o el CLI), con tu cuenta. Modelo **Opus 5.5**; en Pro, esfuerzo
   **medium**.
7. **Avisá** al coordinador que la máquina está lista, para que la anote en `coordinacion/maquinas.yaml`.

## 2. Cada sesión

Abrí Claude Code en la carpeta del repo y pedile: *"Leé MAQUINAS.md y tomá la próxima tarea libre para mi
plan"*. El agente hace esto:

1. `git pull` y `python scripts/tareas.py listar --libres --plan pro` (o `max`). Una tarea que dice
   `(espera T00N)` todavía no se puede tomar.
2. `python scripts/tareas.py tomar T004`. Si otra máquina la tomó un segundo antes, el push se rechaza y el
   script avisa: elegí otra.
3. Leer la tarea entera (`scripts/tareas.py ver T004`), y el CLAUDE.md si es la primera vez.
4. Trabajar en una rama: `git switch -c tarea/T004-riego`. Commits chicos y push seguido, así otra máquina
   puede seguir si esta se corta.
5. Anotar avances que le sirvan a otro: `python scripts/tareas.py nota T004 "texto"`.
6. Al terminar:
   - abrir el PR de la rama a `main` (`gh pr create`) con qué cambió y cómo se probó;
   - si hay datos, publicarlos con `python scripts/entregar.py <paquete>`;
   - `python scripts/tareas.py terminar T004 "PR #N y release datos-ks"`.
7. Dejar una línea en la bitácora de la máquina: `python scripts/tareas.py bitacora "qué hice, qué quedó a
   medias, qué le sirve a otro"`.

`scripts/tareas.py` lee y publica el tablero y las bitácoras desde `.tablero/`, una copia de `main` aparte
de tu carpeta de trabajo. Podés estar en cualquier rama, con cambios sin commit, y el tablero se actualiza
igual sin arrastrar tu código. Lo que ves en `coordinacion/` de tu rama puede estar viejo: mirá el tablero
siempre con el script.

Si el trabajo no se puede terminar: `scripts/tareas.py soltar T004 "por dónde quedó"` la devuelve al tablero
(con la rama empujada, para que la siga otra), y `bloquear T004 "motivo"` la frena hasta que el humano o el
coordinador decidan.

Para pedirle algo puntual a una máquina, el humano o `max-1` crean una tarea (`scripts/tareas.py nueva
"Título" --plan pro --estados KS`), completan "Qué hacer" y "Terminada cuando", y le dicen a esa máquina que
la tome.

## 3. Pro y Max

| | Pro | Max |
|---|---|---|
| Tareas | las marcadas `plan_minimo: pro` | todas |
| Sesiones | una tarea por sesión, acotada | tareas largas, varias seguidas |
| Corrida autónoma (`loop/`) | no | sí, cuando esté adaptada |
| Buen uso | research, control de calidad, un paquete o un estado, revisar un PR | descargar y procesar estados enteros, unir datos, coordinar |

**En Pro el límite de uso es lo que se acaba primero:**
- Las descargas y el procesamiento son scripts de Python y no gastan uso de Claude. Lanzalos en segundo plano
  y revisá solo el final del log, en lugar de mirar la salida entera.
- No cargues CSV grandes en la conversación: resumilos con pandas (filas, columnas, faltantes, rangos).
- Si el uso se está por terminar: commit y push de la rama, una nota en la tarea con por dónde quedó, y
  `soltar` si no vas a volver pronto. Así nada se pierde cuando se corta la sesión.

## 4. Datos entre máquinas

Los datos no van en git: son muchos GB y GitHub no acepta archivos de más de 100 MB.

- **Crudos (`data/raw/`):** se quedan en la máquina que los bajó. Si otra máquina los necesita, los baja
  ella con los mismos scripts. Los archivos nacionales (la base completa de NASS, GRACE-DA-DM de EE.UU.) se
  pueden copiar de una máquina que ya los tenga, con sus filas de `manifest.csv`.
- **Procesados:** `python scripts/entregar.py` arma un zip por paquete con los CSV, el data card, los
  condados y el `manifest.csv`, y lo sube al release `datos-<estados>` (reemplaza la versión anterior). Para
  usarlos en otra máquina:
  ```bash
  gh release download datos-ks --dir data/entregas
  ```
- **Unir los estados:** lo hace `max-1`. Los CSV de cada paquete se apilan por filas, porque las claves son
  por condado, y después corre `src/merge.py`.

## 5. Para no pisarse

- Solo se toca lo que la tarea pide. `src/common/` y `config/` se cambian con el OK del humano, en su propia
  tarea y con un PR.
- Nadie empuja código directo a `main`. A `main` van solo los cambios de tareas y bitácoras, y siempre con
  `scripts/tareas.py`.
- Dos tareas abiertas no tocan los mismos archivos. Si te pasa, anotalo en la tarea y avisá al coordinador.
- Antes de abrir un PR: `git pull origin main` y resolver los conflictos en tu rama.
- `data/raw/` no se modifica, y no se inventan datos (CLAUDE.md, sección 1).
