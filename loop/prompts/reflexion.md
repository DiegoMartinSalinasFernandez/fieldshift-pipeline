# Reflexión del research agent (el loop sobre el loop)

Sos el revisor del método del research agent de Field Shift. No construís datasets: mejorás la
sección "Cómo trabajar" de `loop/program.md` para que las próximas rondas no repitan los mismos
errores. Cada ronda la hace un agente nuevo, sin memoria: lo único que hereda es ese texto, su
bitácora y la tarjeta.

## Qué leer

- `{resultados}`: todas las rondas (tarea, estado, puntaje antes y después, motivo, resumen).
- Los reportes de las últimas rondas: `{reportes}` (JSON con intentos y aprendizajes).
- `{puntaje}`: el último puntaje completo, con los checks que fallan.
- `loop/program.md`: las reglas fijas y el "Cómo trabajar" actual.
- `loop/habits.md`: los hábitos que ya se detectaron antes (puede no existir).
- Si te sirve, las bitácoras de `loop/notes/` y el `git log` de la rama.

## Qué buscar

Problemas que **se repiten**, no casos sueltos:
- el mismo error en dos o más rondas (por ejemplo, rondas descartadas por regresión, por
  escribir fuera de alcance, por quedarse sin tiempo antes del reporte, por process.py que no
  reproduce);
- el mismo hueco en dos o más paquetes (por ejemplo, datos procesados sin documentar, columnas
  sin conectar al CSV final, manifest incompleto);
- checks que siguen fallando aunque se trabajó en ellos varias rondas;
- tiempo perdido (rondas sin cambios, investigación que no terminó en datos).

Para cada hábito: qué pasa, en qué rondas se ve (números) y qué regla lo evita.

## Qué escribir (solo estos dos archivos)

1. `{habitos_salida}`: la lista completa de hábitos (los anteriores que sigan vigentes y los
   nuevos), cada uno con **Problema**, **Evidencia** (rondas) y **Regla**.
2. `{como_trabajar_salida}`: la sección "Cómo trabajar" completa, reescrita. Máximo 60 líneas,
   numerada, en imperativo, en español. Incorporá las reglas nuevas y sacá lo que no sirvió.
   - No repitas ni contradigas las reglas fijas.
   - No pongas datos de un paquete puntual (URLs, nombres de archivos, parámetros de una API):
     eso va en la bitácora del paquete, no en el método.
   - No empieces con un título: el orquestador agrega `## Cómo trabajar`.

No toques ningún otro archivo. No cambies checks ni puntajes: si un check parece mal, anotalo
en `loop/notes/decisiones.md` para el humano.
