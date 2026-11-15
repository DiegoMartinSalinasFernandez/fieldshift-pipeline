"""T038: ventanas de floración del maíz y llenado de la soja por estado, desde Crop Progress (NASS).

Baja de ESMIS los reportes semanales de junio a octubre de 2008-2025 a una carpeta de trabajo (fuera del
repo), toma el % de la semana actual de cada estado en las tablas de maíz (silking, dough, dented) y soja
(blooming, setting pods, dropping leaves), e interpola el día del año en que se cruza el 25, 50 y 75 %.

Uso: python -I docs/research/ventanas_por_estado.py <carpeta_trabajo> <salida.csv>
Escribe <carpeta_trabajo>/prog.csv (semanal) y <salida.csv> (cruces por estado, etapa y año).
"""
import re, sys, os, datetime as dt, csv, subprocess
import numpy as np, pandas as pd

TRABAJO, SALIDA = sys.argv[1], sys.argv[2]
REP = os.path.join(TRABAJO, 'rep'); os.makedirs(REP, exist_ok=True)
BASE = 'https://esmis.nal.usda.gov'

# 1. lista de reportes (paginado de ESMIS) y descarga de los de junio a octubre
urls = set()
for p in range(0, 200):
    html = subprocess.run(['curl', '-sL', '-m', '60', f'{BASE}/publication/crop-progress?page={p}'],
                          capture_output=True, text=True).stdout
    nuevos = set(re.findall(r'href="([^"]*\.txt)"', html))
    if not nuevos: break
    urls |= nuevos
for u in sorted(urls):
    f = u.rsplit('/', 1)[1]
    m = re.match(r'CropProg-(\d\d)-(\d\d)-(\d{4})', f)
    if m: ok = 2008 <= int(m[3]) <= 2025 and 6 <= int(m[1]) <= 10
    else:
        m = re.match(r'prog(\d\d)(\d\d)', f)
        ok = bool(m) and 2008 <= 2000 + int(m[2]) <= 2025 and 23 <= int(m[1]) <= 42
    destino = os.path.join(REP, u.replace('/', '_'))
    if ok and not os.path.exists(destino):
        subprocess.run(['curl', '-sL', '-m', '60', BASE + u, '-o', destino])

# 2. parseo
ST={'Iowa':'IA','Illinois':'IL','Indiana':'IN','Ohio':'OH','Nebraska':'NE','Minnesota':'MN','Kansas':'KS'}
CODES=set(ST.values())
MON={m:i+1 for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'])}
TABS={('corn','silking'):'maiz_silking',('corn','dough'):'maiz_dough',('corn','dented'):'maiz_dented',
      ('soybeans','blooming'):'soja_blooming',('soybeans','setting pods'):'soja_setting_pods',('soybeans','dropping leaves'):'soja_dropping_leaves'}
rows={}
for f in sorted(os.listdir(REP)):
    t=open(os.path.join(REP,f),encoding='latin-1').read()
    m=re.search(r'Released\s+([A-Z][a-z]+)\s+(\d+),\s+(\d{4})',t)
    if m: rel=dt.date(int(m[3]),MON[m[1]],int(m[2]))
    else:
        mf=re.search(r'CropProg-(\d\d)-(\d\d)-(\d{4})',f)
        if not mf: print('sin fecha',f); continue
        rel=dt.date(int(mf[3]),int(mf[1]),int(mf[2]))
    we=rel-dt.timedelta(days=1)
    while we.weekday()!=6: we-=dt.timedelta(days=1)
    lines=t.splitlines()
    for i,l in enumerate(lines):
        ll=l.lower()
        for (c,s),name in TABS.items():
            new = re.match(rf'\s*{c} {s} - selected states',ll)
            old = re.match(rf'\s*{c}:\s+percent {s},?\s*$',ll)
            if not (new or old): continue
            # bloque hasta línea en blanco tras datos
            yrs=None; seen=False
            for j in range(i+1,min(i+60,len(lines))):
                L=lines[j]
                ys=re.findall(r'\b(20\d\d)\b',L)
                if yrs is None and len(ys)>=3 and 'average' not in L.lower() or (yrs is None and len(ys)>=4):
                    yrs=[int(y) for y in ys]
                if seen and re.match(r'\s*(\d+ States|[A-Z]\w* States|Total|\d+ Sts)',L): break
                if new:
                    mm=re.match(r'\s*([A-Z][a-z]+(?: [A-Z][a-z]+)?)\s*\.+:\s*(.*)',L)
                    if mm and mm[1] in ST:
                        vals=mm[2].split(); col=2; code=ST[mm[1]]
                    else: continue
                else:
                    mm=re.match(r'\s*([A-Z]{2})\s*:\s*(.*)',L)
                    if mm and mm[1] in CODES:
                        vals=mm[2].split(); col=0; code=mm[1]
                    else: continue
                # verificación del año de la columna "esta semana"
                if yrs and yrs[col]!=we.year: print('ojo año',f,name,yrs); break
                v=vals[col] if len(vals)>col else 'NA'
                v=0 if v=='-' else (int(v) if v.isdigit() else None)
                seen=True
                if v is not None: rows[(code,name,we)]=v
with open(os.path.join(TRABAJO, 'prog.csv'),'w',newline='') as fo:
    w=csv.writer(fo); w.writerow(['estado','etapa','semana','pct'])
    for (c,n,we),v in sorted(rows.items()): w.writerow([c,n,we.isoformat(),v])
print(len(rows))

# 3. cruces del 25, 50 y 75 % (interpolación lineal entre semanas)
d=pd.read_csv(os.path.join(TRABAJO, 'prog.csv'),parse_dates=['semana']); d['anio']=d.semana.dt.year
def cruce(g,p):
    g=g.sort_values('semana'); x=g.semana.dt.day_of_year.values; y=g.pct.values
    for i in range(1,len(y)):
        if y[i-1]<p<=y[i]:
            return x[i-1]+(p-y[i-1])*(x[i]-x[i-1])/(y[i]-y[i-1]), x[i]-x[i-1]
    return np.nan, np.nan
out=[]
for (e,et,a),g in d.groupby(['estado','etapa','anio']):
    r={'estado':e,'etapa':et,'anio':a}
    for p in (25,50,75):
        r[f'doy{p}'],r[f'gap{p}']=cruce(g,p)
    out.append(r)
o=pd.DataFrame(out); o.to_csv(SALIDA,index=False)
print(o[[c for c in o if c.startswith('gap')]].stack().value_counts())
print(o.isna().sum())
