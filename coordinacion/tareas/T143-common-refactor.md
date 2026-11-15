---
id: T143
titulo: Mover `zona_texto.py` y `asegurar_manifest()` a `src/common/` (código listo, espera OK)
estado: tomada
plan_minimo: pro
maquina: pro-2
estados: []
depende_de: []
rama: null
creada: 2026-11-15T10:17
actualizada: 2026-11-15 10:29
---

## Qué hacer

Filas 4 y 10 de `para_decidir.md`: mover `src/zona_texto.py` a `src/common/` y pasar `asegurar_manifest()`, hoy
repetida en unos 12 `download.py`, a una sola función en `src/common/`, y que todos los paquetes la importen.
**Sin efecto en los datos**: comprobalo con una prueba que compare el `manifest.csv` que escribe la función vieja
y la nueva (mismo encabezado, mismas filas) y corriendo la suite entera. Dejá un alias en `src/zona_texto.py` que
importe de `src/common/` para no romper scripts viejos, o explicá en el PR por qué no hace falta.

**El PR no se une hasta que el humano diga que sí** a la fila #4 y #10 de `coordinacion/para_decidir.md`. Escribí al
principio del cuerpo del PR: "Espera el OK de para_decidir #4 y #10; no unir antes". Este PR **sí** puede tocar
`src/common/` (o `config/`, si se indica abajo) porque es justamente la propuesta que el humano tiene que aprobar:
dejá en el cuerpo del PR la lista exacta de lo que cambia en esos directorios.

## Terminada cuando

El cambio, las pruebas sin red y la documentación en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 10:29 · pro-2: tomada
