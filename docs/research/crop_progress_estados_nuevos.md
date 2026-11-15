# NASS Crop Progress en los estados nuevos (OH, NE, MN, KS)

Pregunta: Para Ohio, Nebraska, Minnesota y Kansas, ¿qué etapas de Crop Progress (`source_desc=SURVEY`, `statisticcat_desc=PROGRESS`, nivel estado, semanal) hay para maíz, soja, trigo de invierno y avena, desde qué año y con qué huecos? ¿El trigo de invierno de Kansas y Nebraska tiene etapas distintas (siembra en otoño, año de cosecha)? ¿`src/cultivos/process.py` arma bien `doy_50_*` para esos estados y cultivos?

Respuesta corta: Los cuatro estados están en las tablas de maíz y soja de **todas** las etapas, todos los años de 2000 a 2026, sin años faltantes. El trigo de invierno se informa para **OH, NE y KS** (no para MN, que figura en trigo de primavera) y la avena para **OH, NE y MN** (no para KS). El único hueco grande es el de **2025: no salieron los reportes de las semanas que terminan entre el 5 de octubre y el 9 de noviembre** (cierre del gobierno federal). El reporte del 17 de noviembre de 2025 trae la semana anterior como `(NA)`. Ese hueco cae justo sobre la cosecha de maíz y soja y la siembra del trigo de invierno. El trigo de invierno tiene cuatro etapas: PLANTED y EMERGED en otoño (septiembre a noviembre, para la cosecha del año siguiente), HEADED en mayo y HARVESTED en junio y julio. `process.py` hoy arma `doy_50_*` **solo para maíz y soja**. Con esos dos cultivos funciona igual en los estados nuevos que en IA/IL/IN: no tiene nada específico de esos estados. No calcula trigo de invierno ni avena, y si se agregaran tal como está, el `anio` del trigo sembrado en otoño sería el de la siembra y no el de la cosecha.

Detalle:

**Cómo se midió.** No hay `qs.crops_*` en esta máquina, y el trabajador no tuvo acceso a `NASS_API_KEY` (no se leyó `.env`). Por eso no se consultó Quick Stats. Lo que se usó es la publicación semanal *Crop Progress* de NASS, que es la fuente de esos mismos datos de Quick Stats. Se bajaron a `/tmp` (fuera del repo, no se guardan) los 942 reportes en texto de 2000 a noviembre de 2026 del archivo de ESMIS. Un script tomó, de cada tabla "<Cultivo> <Etapa> - Selected States" (o "<Cultivo>: Percent <Etapa>" en el formato anterior a ~2010), la fila de cada estado con el valor de la semana actual. Los años con dato son aquellos en que el estado tiene al menos un valor numérico en esa tabla.

**Etapas por estado y cultivo** (2000–2026 = sin años faltantes; "—" = el estado no está en esa tabla ningún año). La columna "semanas" es la mediana de reportes por año con valor. En `UNIT_DESC` va el nombre que Quick Stats da a la etapa: `PCT <ETAPA>`.

| Estado | Maíz | Soja | Trigo de invierno | Avena |
|---|---|---|---|---|
| OH (39) | PLANTED, EMERGED, SILKING, DOUGH, DENTED, MATURE, HARVESTED: 2000–2026 | PLANTED, EMERGED, BLOOMING, SETTING PODS, DROPPING LEAVES, HARVESTED: 2000–2026 | PLANTED, EMERGED, HEADED, HARVESTED: 2000–2026 | PLANTED, EMERGED, HEADED, HARVESTED: 2000–2026 |
| NE (31) | ídem: 2000–2026 | ídem: 2000–2026 | PLANTED, EMERGED, HEADED, HARVESTED: 2000–2026 | PLANTED, EMERGED, HEADED, HARVESTED: 2000–2026 |
| MN (27) | ídem: 2000–2026 | ídem: 2000–2026 | — (MN figura en *Spring Wheat*: PLANTED, EMERGED, HEADED, HARVESTED) | PLANTED, EMERGED, HEADED, HARVESTED: 2000–2026 |
| KS (20) | ídem: 2000–2026 | ídem: 2000–2026 | PLANTED, EMERGED, HEADED, HARVESTED: 2000–2026 | — |

Semanas con valor por año (mediana): maíz y soja de 7 a 9 por etapa (HARVESTED de 9 a 11); trigo de invierno de 8 a 11; avena de 8 a 9. En 2026, a la fecha de consulta (reporte del 9 de noviembre de 2026), están las mismas tablas y estados.

**Día del año típico del 50 %** (mediana 2000–2018, interpolación lineal sobre la semana terminada el domingo anterior al reporte; n = años en que se cruzó el 50 % dentro de la serie). Sirve para validar `fenologia_estado.csv` después.

| Estado | Cultivo | Sembrado | Emergido | Floración (SILKING / BLOOMING) / espigado (HEADED) | Cosechado |
|---|---|---|---|---|---|
| OH | maíz | 129 | 140 | 201 | 301 (grano) |
| OH | soja | 141 | 152 | 199 | 285 |
| OH | trigo inv. | 284 (otoño previo) | 296 (otoño previo) | 143 | 190 |
| OH | avena | 114 | 128 | 166 | 213 |
| NE | maíz | 125 | 139 | 198 | 296 |
| NE | soja | 138 | 152 | 196 | 283 |
| NE | trigo inv. | 263 (otoño previo) | 276 (otoño previo) | 147 | 195 |
| NE | avena | 103 (n = 17/19) | 117 | 163 | 201 (n = 15/19) |
| MN | maíz | 123 | 140 | 202 | 296 |
| MN | soja | 138 | 152 | 197 | 280 |
| MN | avena | 120 | 130 | 177 | 220 |
| KS | maíz | 122 | 136 | 192 | 272 |
| KS | soja | 147 | 158 | 200 | 290 |
| KS | trigo inv. | 277 (otoño previo) | 289 (otoño previo) | 131 | 177 |

**Huecos y particularidades.**
- **2025, octubre–noviembre:** no hay reportes con semana terminada entre el 5 de octubre y el 9 de noviembre de 2025. El último antes del hueco es el de la semana al 28 de septiembre (publicado el 29 de septiembre) y el siguiente es el del 17 de noviembre de 2025, que trae la semana al 9 de noviembre como `(NA)`. Así quedan, por ejemplo, la cosecha de maíz y la emergencia del trigo en 2025:
  - maíz cosechado, de 28/9 a 16/11: OH 10 → 93 %, NE 11 → 74 %, MN 5 → 96 %, KS 29 → 92 %;
  - soja cosechada: OH 21 → 96 %, NE 11 → 84 %, MN 22 → 100 %, KS 5 → 91 %;
  - trigo de invierno emergido: OH 1 → 90 %, NE 32 → 75 %, KS 5 → 85 %.
  
  No verifiqué si Quick Stats cargó después esas semanas. Si no las cargó, el cruce del 50 % de 2025 se interpola sobre 7 semanas y el error puede ser de varias semanas.
- **Primera semana ya sobre 50 %:** en la avena de Nebraska la siembra arranca muy temprano (mediana día 103, mediados de abril). Algunos años el primer reporte de la temporada ya trae ≥ 50 %, y lo mismo pasa con la cosecha de avena de NE (n = 15/19). En esos años `doy_cruce_50` devuelve vacío, porque no hay dato anterior para interpolar.
- **Valores `-` en los reportes:** son "cero" (no "sin dato") y aparecen en las primeras semanas de cada etapa.
- **Trigo de invierno (KS, NE, OH):** la siembra y la emergencia se informan en septiembre–noviembre del año anterior a la cosecha. El espigado (HEADED, mayo) y la cosecha (HARVESTED, junio–julio) se informan en el año de la cosecha. En el reporte, las tablas de otoño hablan de "acreage" del año siguiente (por ejemplo, el reporte del 9/11/2026 informa la siembra para la cosecha 2027). **No pude verificar** qué valor de `YEAR` les pone Quick Stats a las filas PLANTED/EMERGED de otoño (año de la semana o año de comercialización/cosecha), porque no tuve acceso a la API ni a `qs.crops_*`. Hay que mirarlo en los datos antes de usarlo.

**Qué hace `src/cultivos/process.py` (función `fenologia`, líneas 140–172).**
1. Filtra `SOURCE_DESC=SURVEY`, `AGG_LEVEL_DESC=STATE`, `STATISTICCAT_DESC=PROGRESS` y `DOMAIN_DESC=TOTAL`, con `WEEK_ENDING` no vacío. No filtra por estado: toma todos los estados que vengan en el archivo crudo. Los estados nuevos entran sin cambios si el `qs.crops_*` es el nacional.
2. Solo tiene `maiz` y `soja`. Las etapas son PLANTED, EMERGED, SILKING/BLOOMING y HARVESTED, con `UTIL_PRACTICE_DESC=GRAIN` para el maíz cosechado y `ALL UTILIZATION PRACTICES` para el resto. Todas esas etapas existen en los cuatro estados nuevos, así que para maíz y soja la lógica sirve igual que para IA/IL/IN. Lo único que supone de esos estados es implícito: que la serie de cada etapa empieza por debajo del 50 % y lo cruza en el año calendario.
3. `anio` = año de `WEEK_ENDING`, y `doy` = día del año de esa fecha. Para maíz y soja coincide con el año de cosecha. **Para el trigo de invierno no:** si se agrega tal cual, el PLANTED/EMERGED de otoño quedaría en `anio − 1` respecto de HEADED/HARVESTED. Además, un `doy` de otoño no es comparable con uno de primavera (habría que usar días desde el 1 de enero del año de cosecha, que dan negativos, o fechas).
4. `doy_cruce_50` devuelve vacío si el primer dato ya es > 50 (caso avena NE) o si nunca se llega a 50. Si falta un tramo de semanas (2025), interpola linealmente sobre el hueco sin marcarlo.
5. No hay trigo de invierno ni avena en `fenologia_estado.csv`, ni en IA/IL/IN ni en los estados nuevos. Agregarlos cambia el esquema (filas de `cultivo` nuevas y, para el trigo, quizá una columna de espigado): lo decide el humano.

Fuentes:
- [Crop Progress – publicación semanal (USDA NASS, archivo ESMIS)](https://esmis.nal.usda.gov/publication/crop-progress), consultado 2026-11-15. Se leyeron los 942 reportes en texto de 2000 a 2026 enlazados ahí, por ejemplo:
  - [Crop Progress 10-07-2000](https://esmis.nal.usda.gov/sites/default/release-files/8336h188j/k930bz38z/vq27zp658/CropProg-07-10-2000.txt), formato viejo "Corn: Percent Silking";
  - [prog3925.txt, 29-09-2025](https://esmis.nal.usda.gov/sites/default/release-files/8336h188j/2514qk05k/br86d326b/prog3925.txt), último antes del hueco;
  - [prog4625_1.txt, 17-11-2025](https://esmis.nal.usda.gov/sites/default/release-files/795651/prog4625_1.txt), semana del 9/11/2025 en `(NA)`;
  - [prog4526.txt, 09-11-2026](https://esmis.nal.usda.gov/sites/default/release-files/796141/prog4526.txt).
- [Crop Progress 26-09-2005](https://esmis.nal.usda.gov/sites/default/release-files/8336h188j/h415pb976/b8515p821/CropProg-09-26-2005.txt), consultado 2026-11-15.
- `src/cultivos/process.py` (función `fenologia`) y `src/cultivos/data_card.py` de este repo, leídos 2026-11-15.

Confianza:
- **Alta** para qué estado está en qué tabla, los años y el hueco de 2025: sale de los reportes originales.
- **Media** para los días típicos: interpolación propia, 2000–2018.
- **Baja / sin verificar:** el `YEAR` que asigna Quick Stats al trigo de invierno de otoño, y si las semanas de octubre de 2025 se cargaron después en Quick Stats.

Impacto:
- **Paquete `cultivos`, archivo `fenologia_estado.csv`:** para los estados nuevos, maíz y soja salen sin cambiar código.
- **Propuestas para el humano (cambian el esquema):**
  - agregar avena (OH, NE, MN) y trigo de invierno (OH, NE, KS, y también IL/IN), con la etapa HEADED;
  - fijar la convención de año del trigo sembrado en otoño;
  - marcar con una columna de calidad los cruces interpolados sobre huecos de más de 2 semanas (2025).
- **Validación:** usar la tabla de días típicos de arriba para revisar `fenologia_estado.csv` de OH, NE, MN y KS cuando esté.
