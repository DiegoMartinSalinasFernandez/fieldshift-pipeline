---
id: T122
titulo: Declaración de IA en las notas de los releases (scripts/entregar.py)
estado: tomada
plan_minimo: pro
maquina: pro-5
estados: []
depende_de: []
rama: null
creada: 2026-11-15T08:55
actualizada: 2026-11-15 09:03
---

## Qué hacer

`docs/demo/pendientes_humano.md` #10: `project_page.md` dice que la declaración de uso de IA está en la metadata de
los releases, pero `scripts/entregar.py` (línea ~107) escribe solo "CSV procesados por paquete…". Hacé que las
notas del release incluyan, en inglés y en castellano, un párrafo corto sobre el uso de IA tomado de la sección
"Use of AI" del `README.md` (leelo del README al momento, no lo copies fijo en el script, para que no se
desincronice), más la lista de paquetes del release. Prueba sin red de la función que arma las notas.

No toques releases publicados: el coordinador actualiza las notas de `datos-oh-ne-mn` con `gh release edit` cuando
esto esté unido. Si hace falta, dejá en el PR el comando exacto.

## Terminada cuando

El cambio y la prueba en un PR, con CI en verde.

## Notas
- 2026-11-15 09:03 · pro-5: tomada
