# Hábitos detectados por la reflexión

# Hábitos detectados — corridas noche-20261114 (rondas 1–20) y noche2-20261114 (rondas 1–15)

Las evidencias de la corrida anterior se marcan "n1"; las de esta, "n2".

## 1. Comandos de Bash bloqueados por mencionar archivos protegidos
- **Problema:** el hook bloquea cualquier comando de Bash cuyo texto nombre un archivo protegido
  o una ruta de raw, aunque sea dentro de un heredoc o de un script que reescribe otro archivo.
- **Evidencia:** n1 rondas 1, 2, 3, 9, 10 y 11; n2 ronda 2. n2 rondas 6–15 sin bloqueos: sostenido.
- **Regla:** crear o modificar cualquier archivo va con Write o Edit, nunca con heredoc, `echo >>`,
  `cat >>` ni scripts de reemplazo lanzados desde Bash. Para leer los protegidos, Read.

## 2. Subcomandos de git no permitidos encadenados con trabajo útil
- **Evidencia:** n1 ronda 12; n2 sin bloqueos: sostenido.
- **Regla:** solo `git status`, `git diff`, `git log` y `git show`, en comandos aparte.

## 3. Descargas en segundo plano que rompen la reproducibilidad
- **Evidencia:** n1 rondas 3, 4 y 9; n2 rondas 1–15 reprodujeron (md5 igual): sostenido.
- **Regla:** cortá todas las descargas y confirmá que no quedan procesos tuyos antes de la corrida
  final de `process.py`. `process.py` usa solo unidades completas.

## 4. Manifest reescrito entero (duplicados o cambio de fin de línea)
- **Evidencia:** n1 rondas 9 y 12; n2 rondas 1 y 5. n2 rondas 6–15 solo sumaron filas (r013 y r014
  con dos procesos: un paso final reconcilió sin duplicados): sostenido.
- **Regla:** upsert por `archivo` que conserva el orden y el fin de línea de las filas existentes
  y agrega las nuevas al final; con varios procesos, lo escribe un solo paso final. Al cierre,
  `git diff --stat` del manifest solo muestra inserciones.

## 5. `process.py` que crece hacia el límite de 30 minutos
- **Evidencia:** n1 rondas 4 y 5; n2: todos en segundos o pocos minutos (paisaje 3,6 min con 150
  archivos, validacion 35 s rasterizando una sola vez + bincount): sostenido.
- **Regla:** cronometrá cada etapa; si pasa los 15 min, cacheá intermedios en interim.

## 6. Paquetes que pasan o rozan el límite de 5 GB
- **Problema:** raw es de solo lectura, así que lo que se baja de más (archivos nacionales cuando solo
  hacen falta 3 estados) no se puede recortar después y deja al paquete sin margen.
- **Evidencia:** n1 rondas 3–5, 9, 11 y 12; n2 ronda 4; n2 ronda 14 (paisaje 3,88 GB) y ronda 15
  (validacion 4,00 GB: zips nacionales de PRISM, 3,2 GB; la ronda dice que no queda margen). Bien:
  n2 rondas 8 y 12 (recorte por bbox y variable o lectura por ventana en origen).
- **Regla:** medí raw en bytes, proyectá con 10 % de margen, bajá solo el período del contrato y,
  si la fuente solo da archivos nacionales, buscá antes un acceso que recorte en origen.

## 7. Volver a probar callejones ya cerrados
- **Evidencia:** n1 rondas 3–5, 7–8 y 20. n2 rondas 8 y 11 reusaron callejones sin reintentarlos:
  sostenido.
- **Regla:** grep del dominio en "Callejones cerrados" de todas las bitácoras antes de probarlo.

## 8. Puntos que dependen de un check o de una decisión, no de los datos
- **Evidencia:** n1 rondas 3–8 y 20; n2 ronda 3 (`napa_min_cm`), 9 (manifest entre paquetes), 10 y 11
  (`fija_n_kgha = 0`, proxy del centeno), 14 (Annual NLCD 2025 no existe), 15 (conteo 0 de CoCoRaHS).
- **Regla:** escribilo una vez en `decisiones.md`, dejalo en "Problemas conocidos" y seguí.

## 9. Valores reales que coinciden con códigos de relleno o con "0 = faltante"
- **Problema:** el contrato pide vacío para faltantes; un conteo real en 0 o un valor real igual a
  -9999 se confunde con relleno.
- **Evidencia:** n1 ronda 2; n2 ronda 8 (relleno -9999 convertido a vacío); n2 ronda 15
  (`n_estaciones_cocorahs` = 0 como conteo real, documentado y llevado a `decisiones.md`: bien).
- **Regla:** floats con decimales fijos, búsqueda de celdas iguales a códigos de relleno; sin consulta
  o sin dato, vacío; un 0 real (conteo) se deja y se explica en Supuestos.

## 10. Data card generada desde los datos (hábito bueno)
- **Evidencia:** n1 rondas 2–5 y 9–12; n2 rondas 1–15 (paisaje y validacion: data card con md5 igual
  en dos corridas).
- **Regla:** script del paquete que genera la tabla desde los CSV, al final de `process.py`.

## 11. Tareas que siguen en `progreso` con rendimiento muy bajo
- **Evidencia:** n1 rondas 6–8 y 20; n2 rondas 6 y 7 (ecostress +0,27 y +0,16), ronda 10 (`progreso`
  con 35 checks que dependían de callejones). Aplicada bien después de la regla con números: n2 rondas
  11 (+1,25, `terminada`), 14 (`terminada` al completar) y 15. Sigue habiendo ~33 pts en tareas que
  nunca se empezaron (aptitud, hidrologia, merge, dos research): lo decide el orquestador (anotado en
  `decisiones.md`).
- **Regla:** al cierre, poné puntos sumados, unidades por minuto y rondas que faltan. Si la ronda sumó
  menos de 1 punto, faltan más de 5 rondas o lo que queda depende de callejones o del humano,
  `terminada` con esos números y la ruta en "Pendiente".

## 12. Tarea reportada `bloqueada` con huecos públicos sin completar
- **Evidencia:** n1 rondas 3, 4 y 9. n2 sin casos: sostenido.
- **Regla:** `bloqueada` solo si no queda nada sin el humano; con huecos públicos, `progreso`.

## 13. Sustituciones de fuente, acceso o método documentadas (hábito bueno)
- **Evidencia:** n1 rondas 4, 9, 10 y 11; n2 rondas 3, 4, 5, 8, 10, 12 (mirror de Annual NLCD) y 15
  (directorio HTTP de PRISM), todas en Supuestos y en `decisiones.md`.
- **Regla:** antes de sustituir, buscá la fuente nueva en `loop/spec/entregables.yaml`; si otro
  paquete ya la usa, decilo en Supuestos y en `decisiones.md` con la ruta fiel.

## 14. Librerías que rompen con versiones nuevas de sus dependencias
- **Evidencia:** n1 rondas 9 y 10; n2 ronda 2.
- **Regla:** probá cada librería o lector con un caso chico y anotá el arreglo en la bitácora.

## 15. Research: lo que más suma primero y verificado localmente (hábito bueno)
- **Evidencia:** n1 rondas 13–20; n2 rondas 10 y 11 (194 evidencias, 0 malas, `build.py` reproducible).
- **Regla:** formato completo, una fuente y dos citas verificadas primero; reusá los ayudantes.

## 16. Fuentes en PDF sin lector en el entorno
- **Evidencia:** n1 rondas 13, 15, 17 y 18; n2 rondas 10 y 11 (PDF de UK AGR-33 y de mssoy.org leídos
  con el lector en interim).
- **Regla:** preferí HTML o texto plano; si no, el lector en `data/interim/_tmp/`.

## 17. Sitios con anti-bots, 403 o timeouts que consumen la ronda
- **Evidencia:** n1 rondas 16, 17, 18 y 20; n2 rondas 3, 4, 8, 10 (seis dominios) y 11 (403,
  Incapsula, Anubis, redirect a portada: cinco dominios, 83 turnos para +1,25).
- **Regla:** un intento por dominio (un reintento solo para 5xx); si falla, a "Callejones cerrados"
  y a otra fuente.

## 18. Responder con datos que ya están bajados (hábito bueno)
- **Evidencia:** n1 rondas 17–19; n2 rondas 1, 2, 9, 10 y 11 (tabla de CSBE ya en caché).
- **Regla:** antes de buscar en la web, buscá en `data/raw/`, `data/reference/` y las bitácoras.

## 19. Bitácoras fragmentadas por ronda
- **Evidencia:** n1 research_cultivos_zona; n2 ecostress acumula un "Resumen rNNN" por ronda, con una
  sola "Pendiente" y una sola "Callejones": sostenido.
- **Regla:** una sola "Callejones cerrados" y una sola "Pendiente", reescrita cada ronda.

## 20. Tablas unidas viejas y merge corrido fuera de alcance
- **Evidencia:** n1 ronda 19 (merge 6/6); n2 ronda 4 (revertido), rondas 5, 8, 9 y 14 (avisaron sin
  correrlo: bien). merge sigue en 0/6 desde n2 ronda 4: cada paquete nuevo agrega columnas.
- **Regla:** corré `src/merge.py` solo si las tablas unidas están en tu tarjeta; si no, anotá en el
  reporte que el merge quedó viejo.

## 21. Credenciales nombradas de forma indirecta
- **Evidencia:** n2 rondas 3 y 5; n2 rondas 6–15 sin bloqueos: sostenido.
- **Regla:** no nombres el archivo de credenciales de ninguna forma; si una librería no autentica
  sola, token o cookies de requests guardados en interim.

## 22. Paralelismo: frena sin medir, rinde con rangos disjuntos (actualizado)
- **Problema:** sumar hilos o procesos sin medir frenó (n2 rondas 2 y 5); en cambio, dos procesos con
  rangos de años que no se pisan aceleraron un servidor de latencia variable. La regla anterior ("un
  solo lanzador por paquete") no se cumplió y no hizo daño.
- **Evidencia:** n2 rondas 2, 5 y 6 (sacar lecturas inútiles rindió más que sumar procesos); rondas 13
  y 14 (dos procesos de 16 hilos con rangos disjuntos: de 17–266 s a ~18 s por archivo, sin errores,
  manifest reconciliado al final).
- **Regla:** medí 1–2 min con una configuración chica antes de escalar; un segundo proceso solo con
  unidades que no se pisen y si mediste que acelera; el manifest lo escribe un paso final. Siempre con
  `run_in_background`, nunca `nohup` ni `&`; procesos con `Get-CimInstance`.

## 23. Alcance de la bajada que no puede llegar al umbral de cobertura
- **Evidencia:** n2 ronda 5 (abril–octubre llega como máximo a 57 % contra 60 %); teledeteccion en ~38 %
  contra 80 % desde n1; ecostress en 7,1 % tras tres rondas.
- **Regla:** antes de diseñar la bajada, sacá del puntaje celdas esperadas y umbral, y verificá que el
  alcance y la velocidad medida los cubren.

## 24. Cobertura espacial de la consulta sin verificar
- **Evidencia:** n2 rondas 5–7 (bbox a mano dejó afuera 83 condados). n2 rondas 12 y 15 usaron los
  polígonos de condados: sostenido.
- **Regla:** bbox o teselas desde `data/reference/condados.gpkg`; con la primera muestra, contá
  condados con dato contra `condados.csv` antes de escalar.

## 25. Descargas largas cortadas por el timeout del lanzador
- **Evidencia:** n2 ronda 7; rondas 12–15 lanzadas temprano con timeout explícito: sostenido.
- **Regla:** si la bitácora deja una descarga para retomar, lanzala en los primeros minutos con un
  timeout mayor que su duración planeada.

## 26. Fila de manifest que apunta al raw de otro paquete
- **Evidencia:** n2 ronda 9.
- **Regla:** el archivo ajeno queda registrado solo por su paquete; en el tuyo, citalo en Supuestos.

## 27. Servicio oficial con límite, cuenta o 403, pero los mismos archivos en otro acceso (nuevo, bueno)
- **Problema:** el acceso del plan falla (bucket requester-pays o 403, servicio web con límite de 2
  bajadas por archivo y día) y sería fácil cerrar el producto como callejón.
- **Evidencia:** n2 ronda 2 (Planetary Computer), ronda 12 (mirror público de Annual NLCD: paquete de 0
  a 10/10 en tres rondas) y ronda 15 (directorio HTTP público de PRISM: 1248 zips sin errores; tarea
  0 → 9/9 en una ronda).
- **Regla:** antes de cerrar un producto, buscá un directorio HTTP público o un mirror documentado de
  los mismos archivos; si lo usás, va a Supuestos y a `decisiones.md` como cambio de acceso.

## 28. Proyecciones de tiempo optimistas (nuevo)
- **Problema:** las rondas estiman lo que falta con el ritmo típico y sin contar el cierre; con
  servidores de latencia muy variable, la estimación se queda corta y la cola recibe una ronda más.
- **Evidencia:** n2 ronda 12 ("una ronda de 45 min" para completar: hicieron falta dos), ronda 13
  ("~10–15 min" para el resto: la ronda 14 tardó 31 min, con 17–340 s por archivo y 3,6 min por cada
  corrida de `process.py`); ecostress rondas 5–7.
- **Regla:** proyectá con el ritmo más lento medido, más dos corridas de `process.py` y el cierre, y
  anotá un rango, no un número.

## 29. Escritura atómica que hace seguro cortar una descarga (nuevo, bueno)
- **Problema:** matar un proceso a mitad de una escritura deja archivos truncados (n1: manifest truncado
  en teledeteccion); escribir a `.part` y renombrar evita el problema.
- **Evidencia:** n1 teledeteccion (manifest truncado al matar `download.py`); n2 ronda 13 (cortado a mitad
  de lectura sin dejar archivos a medias, porque solo se escribe la ventana completa); merge n1 r019.
- **Regla:** cada archivo de una descarga se escribe a `.part` (o en memoria) y se renombra al completar;
  el manifest, solo en el paso final.
