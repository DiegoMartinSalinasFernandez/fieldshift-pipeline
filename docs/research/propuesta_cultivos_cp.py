"""Crop Progress por estado en Quick Stats (PROGRESS, STATE, 2000–2025) para los cultivos propuestos en T103.

Cuenta años con dato por estado, cultivo y etapa (sin trigo de invierno). Sin clave: interfaz web pública.
Uso: .venv/bin/python -I docs/research/propuesta_cultivos_cp.py > docs/research/propuesta_cultivos_cp.csv
"""
import requests,csv,io,sys
from collections import defaultdict
QS="https://quickstats.nass.usda.gov"; UA={"User-Agent":"Mozilla/5.0 (fieldshift-research)"}
EST={"ND":"NORTH DAKOTA","SD":"SOUTH DAKOTA","MN":"MINNESOTA","KS":"KANSAS","NE":"NEBRASKA","WI":"WISCONSIN"}
res=defaultdict(set)
for e,nom in EST.items():
  for com in ["WHEAT","BARLEY","SUNFLOWER","CANOLA","BEANS"]:
    form=[("source_desc","SURVEY"),("sector_desc","CROPS"),("commodity_desc",com),("statisticcat_desc","PROGRESS"),("agg_level_desc","STATE"),("state_name",nom)]+[("year",str(a)) for a in range(2000,2026)]
    n=requests.post(QS+"/row_counts",data=form,headers=UA,timeout=120).json()["rowcnt"]
    if n==0: continue
    if n>50000: print("#grande",e,com); continue
    u=requests.post(QS+"/uuid/encode",data=form,headers=UA,timeout=120).json()
    r=requests.get(f"{QS}/data/spreadsheet/{u}.csv",headers=UA,timeout=300)
    for f in csv.DictReader(io.StringIO(r.text)):
      it=f["Data Item"]
      if "WINTER" in it: continue
      if it.endswith(("PCT PLANTED","PCT HARVESTED","PCT HEADED","PCT BLOOMING","PCT EMERGED")):
        res[(e,it.split(" - ")[0],it.rsplit(" ",1)[1])].add(int(f["Year"]))
w=csv.writer(sys.stdout); w.writerow(["estado","cultivo","etapa","n_anios","desde","hasta"])
for k in sorted(res): a=sorted(res[k]); w.writerow([*k,len(a),a[0],a[-1]])
