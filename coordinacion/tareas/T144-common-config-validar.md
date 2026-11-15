---
id: T144
titulo: '`cargar_config()` con `FIELDSHIFT_ESTADOS` en la clave del caché y `validar_csv()` con columnas numéricas
  por nombre (código listo, espera OK)'
estado: tomada
plan_minimo: pro
maquina: pro-1
estados: []
depende_de: []
rama: null
creada: 2026-11-15T10:17
actualizada: 2026-11-15 10:30
---

## Qué hacer

Filas 14 y 25 de `para_decidir.md`:

- 14: que `cargar_config()` de `src/common/` incluya `FIELDSHIFT_ESTADOS` en la clave del caché, para que cambiar
  la variable dentro de un mismo proceso (un notebook) recargue la configuración. Prueba sin red.
- 25: que `validar_csv()` trate como numéricas las columnas con prefijo o sufijo de unidad conocido (`rend_`,
  `sup_`, `produccion_`, `_mm`, `_c`, y los que proponga `tests/` o el research de T046) aunque vengan enteras
  vacías por `(D)`/`(Z)`, y que avise si una de esas columnas trae texto. Sacá el `xfail` de la prueba que lo
  documenta.

Corré `validar_csv()` sobre los CSV de un release publicado (`datos-oh-ne-mn`) antes y después: no puede aparecer
ningún error nuevo en datos que hoy pasan (si aparece, es un hallazgo: anotalo en el PR, no lo escondas).

**El PR no se une hasta que el humano diga que sí** a la fila #14 y #25 de `coordinacion/para_decidir.md`. Escribí al
principio del cuerpo del PR: "Espera el OK de para_decidir #14 y #25; no unir antes". Este PR **sí** puede tocar
`src/common/` (o `config/`, si se indica abajo) porque es justamente la propuesta que el humano tiene que aprobar:
dejá en el cuerpo del PR la lista exacta de lo que cambia en esos directorios.

## Terminada cuando

El cambio, las pruebas sin red y la documentación en un PR con CI en verde, retenido como dice arriba.

## Notas
- 2026-11-15 10:30 · pro-1: tomada
