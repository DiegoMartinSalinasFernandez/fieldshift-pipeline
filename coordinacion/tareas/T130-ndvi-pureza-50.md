---
id: T130
titulo: '`ndvi_maiz_p50` y `ndvi_soja_p50` con umbral de pureza de 50 % (código listo, espera OK)'
estado: hecha
plan_minimo: pro
maquina: pro-5
estados:
- OH
depende_de: []
rama: null
creada: 2026-11-15T09:24
actualizada: 2026-11-15 09:34
---

## Qué hacer

Fila 32 de `para_decidir.md` y el data card de `vegetacion` (T085): en OH, `ndvi_maiz` cubre solo 30–49 % de los
condados-año porque el umbral de pureza del píxel de 250 m es 75 %. Agregá, **además** de las columnas que ya
existen, `ndvi_maiz_p50` y `ndvi_soja_p50` (mismo cálculo con umbral 50 %) en `vegetacion_16d.csv` y
`vegetacion_mensual.csv`, y `ndvi_max_maiz_p50` / `ndvi_max_soja_p50` en `fenologia_anual.csv` si sale con la
misma función. El umbral, como constante con nombre en `src/vegetacion/`, no en `config/`.

Pruebas sin red: un píxel con 60 % de maíz entra en `_p50` y no en la columna de 75 %. Probalo con OH (los datos
del release alcanzan si tenés las máscaras; si no, con un recorte) y contá en el PR cuánto sube la cobertura.

**El PR no se une hasta que el humano diga que sí** a la fila 32 de `coordinacion/para_decidir.md` (esquema
nuevo). Escribí al principio del cuerpo del PR: "Espera el OK de para_decidir #32; no unir antes".
No cambies ninguna columna que ya existe; no toques `src/common/` ni `config/`.

## Terminada cuando

El código, las pruebas sin red y el data card en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 09:30 · pro-5: tomada
- 2026-11-15 09:34 · pro-5: terminada por el trabajador: PR #120, falta la revisión de max-1
