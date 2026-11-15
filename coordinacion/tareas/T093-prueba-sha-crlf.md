---
id: T093
titulo: 'Prueba: verificar_entrega.py acepta .sha256 con CRLF y LF'
estado: tomada
plan_minimo: pro
maquina: pro-2
estados: []
depende_de: []
rama: null
creada: 2026-11-15T06:44
actualizada: 2026-11-15 06:51
---

## Qué hacer

El release `datos-oh-ne-mn` tiene `.sha256` con CRLF (se arreglaron para los próximos en PR 74). Agregá a
`tests/` una prueba de `scripts/verificar_entrega.py` (o de la función que lee el `.sha256`) con un zip chico
inventado y dos `.sha256`, uno con LF y otro con CRLF, y otra para `scripts/entregar.py` que controle que el
`.sha256` nuevo sale con LF. Que pasen en Windows y en Linux. No cambies el código salvo que la prueba muestre
un error.

## Terminada cuando

Las pruebas en un PR.

## Notas
- 2026-11-15 06:51 · pro-2: tomada
