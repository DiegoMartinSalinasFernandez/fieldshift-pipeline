#!/usr/bin/env bash
# T145: rendimientos de encuesta NASS por condado (bu/ac) de maíz, soja, trigo y avena, 2000-2025,
# desde la base completa de Quick Stats (solo lectura). Salida: /tmp/t145/rend.tsv.
# Después: python docs/research/rangos_rendimiento_10_estados_resumen.py IA,IL,IN,OH,NE,MN,KS,MO,WI,SD
set -euo pipefail
mkdir -p /tmp/t145
zcat data/raw/cultivos/nass/qs.crops_20261114.txt.gz | awk -F'\t' '$1=="SURVEY" && $13=="COUNTY" && $8=="YIELD" && $9=="BU / ACRE" && ($4=="CORN"||$4=="SOYBEANS"||$4=="WHEAT"||$4=="OATS") && $31>=2000 && $21!="998" {print $4"\t"$5"\t"$6"\t"$7"\t"$10"\t"$16"\t"$15$21"\t"$22"\t"$31"\t"$38}' > /tmp/t145/rend.tsv
