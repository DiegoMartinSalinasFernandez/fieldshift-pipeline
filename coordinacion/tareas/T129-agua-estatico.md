---
id: T129
titulo: '`agua_estatico.csv` con la fracción del condado que saca el filtro de SMAP (código listo, espera OK)'
estado: libre
plan_minimo: pro
maquina: null
estados:
- MN
- OH
- WI
- MI
depende_de: []
rama: null
creada: 2026-11-15T09:24
actualizada: 2026-11-15T09:24
---

## Qué hacer

Fila 31 de `para_decidir.md`, con lo que midieron `docs/research/smap_costas.md` (T082) y el data card de `agua`
(T086): en `src/agua/process.py`, un archivo nuevo `agua_estatico.csv` (`fips, frac_celdas_excluidas`), la
fracción del área del condado cuyas celdas de SMAP se descartan por el filtro de 0,6 m³/m³ (lagos, turberas).
Reusá la misma lógica del filtro que ya aplica el paquete, sin cambiar `agua_mensual.csv` ni `agua_diario.csv`.
Pruebas sin red con una grilla chica armada en la prueba. Probalo con el release de OH/NE/MN (o lo que tengas) y
compará con los números del data card.

**El PR no se une hasta que el humano diga que sí** a la fila 31 de `coordinacion/para_decidir.md` (esquema
nuevo). Escribí al principio del cuerpo del PR: "Espera el OK de para_decidir #31; no unir antes".
No cambies ninguna columna que ya existe; no toques `src/common/` ni `config/`.

## Terminada cuando

El código, las pruebas sin red y el data card en un PR con CI en verde, retenido como dice arriba.

## Notas
