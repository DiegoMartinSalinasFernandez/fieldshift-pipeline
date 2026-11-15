---
id: T133
titulo: '`cdl_precision.csv` como tabla de referencia para ML (código listo, espera OK)'
estado: libre
plan_minimo: pro
maquina: null
estados: []
depende_de: []
rama: null
creada: 2026-11-15T09:33
actualizada: 2026-11-15T09:33
---

## Qué hacer

Fila 13 de `para_decidir.md`: la precisión del CDL por estado, año y clase ya está extraída en `docs/research/`
(`cdl_precision.md` y los `cdl_precision*_extraer.py` de los 10 estados más KY). Convertilo en una tabla de
referencia: `data/reference/cdl_precision.csv` con `fips_estado, anio, clase_cdl, nombre, exactitud_productor_pct,
exactitud_usuario_pct` (nombres según lo que traiga la fuente; documentalos), armada por un script en
`src/cultivos/` que reuse los extractores, y que `scripts/entregar.py` la sume al zip de base (T126) si existe.
Pruebas sin red con un pedacito de la fuente. Data card de `cultivos`: qué es, de dónde sale y cómo la usaría ML
(por ejemplo, para ponderar las transiciones de `rotacion_anual.csv` por la confiabilidad del año).

**El PR no se une hasta que el humano diga que sí** a la fila 13 de `coordinacion/para_decidir.md`. Escribí
al principio del cuerpo del PR: "Espera el OK de para_decidir #13; no unir antes". No cambies ninguna columna
que ya existe; no toques `src/common/` ni `config/`. Varias tareas retenidas tocan `src/cultivos/` y
`docs/datasets/cultivos.md` (T127 `riego.py`, T132 censo): trabajá en tu propio módulo o función y agregá tu
sección al final del data card, para que los conflictos sean fáciles.

## Terminada cuando

El código, las pruebas sin red y el data card en un PR con CI en verde, retenido como dice arriba.

## Notas
