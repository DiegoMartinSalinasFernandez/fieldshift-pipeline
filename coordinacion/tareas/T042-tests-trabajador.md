---
id: T042
titulo: Pruebas de scripts/trabajador.py (orden de tareas y tiempo)
estado: tomada
plan_minimo: pro
maquina: pro-2
estados: []
depende_de: []
rama: null
creada: 2026-11-15 04:00
actualizada: 2026-11-15 03:30
---

## Qué hacer

Escribí `tests/test_trabajador.py` para las partes de `scripts/trabajador.py` que no lanzan a Claude:

- el orden de candidatas: una Max prefiere las tareas con `plan_minimo: max`, después las de sus estados
  (`FIELDSHIFT_ESTADOS`), después el número de tarea; una Pro no toma tareas `max`;
- las tareas en `espera`, `tomada`, `hecha` o con `depende_de` sin terminar no se toman;
- el tope de minutos: el `minutos:` de la tarea manda, salvo que se pase `--minutos-tarea` por línea de comandos;
  nunca menos de 10 ni más que lo que queda hasta el fin menos 5.

Armá un tablero inventado en una carpeta temporal (como `tests/test_tareas.py`). Si para probar algo hay que
separar una función, hacelo con el cambio mínimo y explicalo en el PR; si encontrás un error, marcá la prueba
`expectedFailure` y explicalo en "Para decidir". Las pruebas tienen que pasar en Windows y en Linux (ojo con
las barras de las rutas y con `\r\n`).

## Terminada cuando

Las pruebas en un PR.

## Notas
- 2026-11-15 03:29 · pro-2: tomada
- 2026-11-15 03:30 · pro-2: intento sin cambios (You've hit your weekly limit · resets Nov 16, 9am (America/Argentina/Buenos_Aires)); reintento
