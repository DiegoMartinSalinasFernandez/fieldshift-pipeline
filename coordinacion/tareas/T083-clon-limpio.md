---
id: T083
titulo: Probar el repo desde un clon limpio, como lo haría un juez de Space Apps
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15T06:18
actualizada: 2026-11-15T06:18
---

## Qué hacer

En una carpeta nueva, cloná el repo y seguí solo el `README.md` (y la versión en inglés, si está): crear el
entorno, instalar `requirements.txt`, correr las pruebas (`pytest`) y el paquete 0 (`src/base`) para un estado
chico. Anotá cada paso que falle, que no esté escrito o que pida algo que el README no dice (credenciales,
versión de Python, GDAL en Windows, etc.). Arreglá en el README lo que sea solo documentación; para lo que sea
código, abrí una tarea nueva con `scripts/tareas.py nueva`. Decí en qué sistema lo probaste.

No bajes más que el paquete 0, y no subas nada de `data/`.

## Terminada cuando

El arreglo del README y la lista de problemas en un PR.

## Notas
