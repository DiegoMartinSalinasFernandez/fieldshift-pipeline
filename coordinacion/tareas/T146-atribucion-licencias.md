---
id: T146
titulo: Texto de atribución de Copernicus (lotes) y CC BY 4.0 de CoCoRaHS (validación) en los data cards (espera
  OK)
estado: tomada
plan_minimo: pro
maquina: pro-1
estados: []
depende_de: []
rama: null
creada: 2026-11-15T10:17
actualizada: 2026-11-15 10:34
---

## Qué hacer

Fila 30 de `para_decidir.md` y `docs/research/licencias_fuentes.md` (T060): agregá la línea de atribución de
Copernicus/Sentinel-2 (vía HLS) al data card de `lotes` y a las notas del release de lotes (si `scripts/entregar.py`
arma esas notas, que la tome de un lugar único), y la de CC BY 4.0 de CoCoRaHS al data card de `validacion`. Usá
exactamente el texto que recomiende el research. Si algún data card se genera con `data_card.py`, cambialo ahí.

**El PR no se une hasta que el humano diga que sí** a la fila #30 de `coordinacion/para_decidir.md`. Escribí al
principio del cuerpo del PR: "Espera el OK de para_decidir #30; no unir antes". Este PR **sí** puede tocar
`src/common/` (o `config/`, si se indica abajo) porque es justamente la propuesta que el humano tiene que aprobar:
dejá en el cuerpo del PR la lista exacta de lo que cambia en esos directorios.

## Terminada cuando

El cambio, las pruebas sin red y la documentación en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 10:34 · pro-1: tomada
