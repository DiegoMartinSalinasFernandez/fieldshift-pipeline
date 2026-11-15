# Cómo trabajan juntas las máquinas

Varias computadoras trabajan en este repo al mismo tiempo, cada una con la cuenta de Claude de su dueño: dos
con plan **Max** y cuatro con plan **Pro**. Las máquinas no se hablan entre ellas: **el repo es el punto de
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
`max-1`, `max-2` y `pro-1` a `pro-4`.

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
   Los scripts se corren con `.venv/bin/python -X utf8 ...` en Linux y con `.venv\Scripts\python -X utf8 ...`
   en Windows (ahí la consola no es UTF-8 y los mensajes en castellano se rompen sin `-X utf8`).
4. **Quién sos y qué estados tenés.** Dos variables de entorno.
   - En **Linux**, agregalas al final de `~/.bashrc` y abrí una terminal nueva:
     ```bash
     echo 'export FIELDSHIFT_MAQUINA=pro-1' >> ~/.bashrc
     ```
     ```bash
     echo 'export FIELDSHIFT_ESTADOS=OH,MN' >> ~/.bashrc
     ```
   - En **Windows**, con `setx` y una terminal nueva:
     ```bash
     setx FIELDSHIFT_MAQUINA max-2
     ```
     ```bash
     setx FIELDSHIFT_ESTADOS KS
     ```
   `FIELDSHIFT_ESTADOS` es la lista de `coordinacion/maquinas.yaml` (por ejemplo `OH,NE,MN`). Con ella todos los
   scripts bajan y procesan solo esos estados. No edites `config/config.yaml` para eso. En las **Max** los
   estados no se repiten entre máquinas (cada una procesa los suyos). En las **Pro**, que no procesan datos,
   solo deciden qué tareas toma primero. Para cambiarla, borrá la línea vieja antes de agregar la nueva:
   ```bash
   sed -i '/FIELDSHIFT_ESTADOS/d' ~/.bashrc
   ```
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
  condados y el `manifest.csv`, y lo sube al release `datos-<estados>` (reemplaza la versión anterior). Además
  sube `datos-<estados>_base.zip` con los polígonos de los condados (`condados.gpkg`, EPSG:4326),
  `condados.csv`, `anios.csv` y un README; `python scripts/entregar.py base` arma y sube solo ese. Para
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

## 6. Trabajador automático (en segundo plano)

En lugar de pedirle cada tarea a Claude a mano, cada máquina puede dejar corriendo un **trabajador** que toma
tareas del tablero y las hace solo durante horas, sin ventana. La máquina queda libre para usarla, y Claude
también.

Desde la carpeta del repo, con las variables de la sección 1 ya definidas, `git pull` y:

| | Linux | Windows |
|---|---|---|
| Iniciar por 7 h | `bash scripts/trabajador.sh iniciar` | `powershell -ExecutionPolicy Bypass -File scripts\trabajador.ps1 iniciar` |
| Solo una tarea, con más tiempo | `bash scripts/trabajador.sh iniciar T013 400` | `... trabajador.ps1 iniciar -Solo T013 -MinutosTarea 400` |
| Ver qué hace | `bash scripts/trabajador.sh estado` | `... trabajador.ps1 estado` |
| Pararlo | `bash scripts/trabajador.sh parar` (o `parar ya`) | `... trabajador.ps1 parar` (o `parar -Ya`) |

La primera vez crea una copia del repo solo para él, al lado de la tuya (`fieldshift-pipeline-trabajador`),
con su propio `.venv`. Nunca toca tu carpeta. Después de iniciarlo podés cerrar la terminal: sigue corriendo.
`parar` deja terminar la tarea en curso; `parar ya` la corta en el momento. Modelo y esfuerzo: Opus 5.5 y
medium por defecto (en Linux se cambian con `FIELDSHIFT_MODELO` y `FIELDSHIFT_EFFORT`).

**Qué hace en cada vuelta**
1. Toma la próxima tarea libre para su plan: en Max, primero las que solo puede hacer una Max; después, las
   de sus estados. No toma las que dicen `auto: false`.
2. Crea la rama `tarea/<id>-auto` y lanza Claude sin intervención (`claude -p`, Opus 5.5, esfuerzo medium) con
   las instrucciones de `coordinacion/prompt_trabajador.md`. Tope: 60 min por tarea en Pro, 150 en Max, salvo
   que la tarea diga otro en `minutos:` (por ejemplo T013, 400) o que se pase `--minutos-tarea`.
3. Sube la rama, abre el PR con el resultado del agente y marca la tarea como hecha. Si quedó a medias, la
   suelta con una nota y la rama queda para que otro siga.
4. Si se acaba el uso de Claude, espera a que se renueve y sigue con la misma tarea.
5. Si no hay tareas libres, vuelve a mirar cada 15 minutos. `max-1` agrega tareas cuando la cola se achica.

Los logs quedan en `fieldshift-pipeline-trabajador/.trabajador/`. El trabajador nunca une PRs ni hace push a
`main` salvo el tablero y la bitácora; los PRs los revisa `max-1`.

**Ojo con el uso en Pro:** el trabajador gasta el mismo límite de la cuenta que usa la persona cuando trabaja a
mano. Conviene dejarlo de noche o cuando no estés usando Claude.

**Que la máquina no se duerma:** en Windows el trabajador lo evita solo. En Linux lo evita con
`systemd-inhibit` si está instalado (Ubuntu y Fedora lo traen); en una notebook, dejala enchufada y
configurada para no suspenderse al cerrar la tapa. Si la máquina se duerme, el trabajador se pausa y sigue al
despertarse.
