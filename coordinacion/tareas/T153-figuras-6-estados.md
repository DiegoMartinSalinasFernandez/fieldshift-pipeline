---
id: T153
titulo: Figuras 1 a 8 de la demo con los releases de OH/NE/MN y MO/WI/SD juntos
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15T14:14Z
actualizada: 2026-11-15T14:14Z
---

## Qué hacer

PR 144 dejó anotado que las figuras fig1 a fig8 y los números de las láminas 3 a 6 y de las tomas 2 a 5 del video
salen solo de OH/NE/MN. Rehacelas con `figuras.py --etiquetas datos-oh-ne-mn datos-mo-wi-sd`. Si el script no
acepta dos etiquetas, sumalo con una prueba sin red. Después recontá los números de esos textos con los 6 estados.

Mirá que los ejemplos de condado del user story (T091) sigan existiendo en los datos.

## Terminada cuando

PR con CI en verde y lo que se encontró en el cuerpo del PR.

## Notas
