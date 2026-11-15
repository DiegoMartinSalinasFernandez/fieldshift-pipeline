---
name: escribir-checks
description: Agregar o cambiar los checks del research agent de Field Shift (loop/spec/entregables.yaml, loop/spec/research.yaml, loop/checks/score.py) y volver a aprobarlos. Usar cuando el humano quiere cambiar qué se mide, una columna, un rango o un tema de research.
disable-model-invocation: true
---

# Escribir o cambiar checks

Los checks se escriben ANTES de construir y el agente del loop no los puede tocar. Son la
única definición de "mejor" que tiene el loop: si un check es flojo, el loop lo explota.

## Dónde está cada cosa

- `loop/spec/entregables.yaml`: por paquete, las rutas que puede escribir (`escribe`), el
  `process.py`, las salidas y cada archivo con `temporal`, `claves`, columnas (`nombre` o
  `patron`, `catalogo`, `rango` o `tipo`, `desde`), `coherencia`, `estacionalidad` y
  `especiales` (funciones `esp_*` de `loop/checks/score.py`).
- `loop/spec/research.yaml`: temas de research (pregunta, archivo, rutas) y la tabla
  `config/cultivos.csv` (filas, atributos, rangos).
- `loop/spec/catalogo.csv`: IDs y prioridades (Alta 3, Media 2, Baja 1) de la planilla.
- `config/config.yaml`: estados, período, cultivos y conversiones (lo lee el scorer).

## Reglas

1. Cada check tiene que poder verificarse contra los datos o contra una fuente: nada que el
   agente pueda cumplir escribiendo texto.
2. Rangos físicos amplios (que no rechacen datos reales) pero que atrapen unidades
   equivocadas y valores de relleno.
3. Nombres de columna: los del CLAUDE.md tal cual; los demás, snake_case con la unidad al
   final y marcados como propuesta en una `nota`.
4. Probar antes de aprobar: `python loop/puntaje.py` (y un repo de prueba si se cambió
   `score.py`).
5. Volver a aprobar: `python loop/aprobar_checks.py --resumen` y después `--aprobar`. Sin
   eso, `loop/run.py` no arranca (compara los hashes con `loop/spec/LOCK.json`).
