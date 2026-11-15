# fieldshift-pipeline

Pipeline de datos de **Field Shift** para NASA Space Apps Challenge 2026, desafío *"Field Shift: Adapting
Farms with NASA Data"*. Baja, limpia y estructura en CSV datos de la NASA y del USDA por condado y año para el
Corn Belt de EE.UU. (Iowa, Illinois, Indiana, Ohio, Nebraska, Minnesota y Kansas, 2000–2025), listos para que
el equipo de machine learning compare rotaciones de cultivos. Este repo no entrena modelos.

Viene del repo ResearchAgent, donde se armó la primera tanda (Iowa, Illinois e Indiana). Acá trabajan varias
máquinas a la vez, cada una con sus estados y sus tareas.

- **Para sumarte o trabajar:** [MAQUINAS.md](MAQUINAS.md).
- **Reglas, contrato de los CSV y paquetes:** [CLAUDE.md](CLAUDE.md).
- **Qué hay que hacer:** `python scripts/tareas.py listar`, o la carpeta [coordinacion/tareas](coordinacion/tareas).
- **Datos procesados:** en los [Releases](../../releases), uno por grupo de estados.

Las fuentes son de dominio público (NASA POWER, GPM IMERG, MODIS, SMAP, GRACE-DA-DM, NLDAS, ECOSTRESS, USDA
NASS, Cropland Data Layer, gSSURGO, NASADEM, Annual NLCD, ERS). Cada data card en `docs/datasets/` dice de
dónde sale cada columna.
