"""T082: celdas SMAP (Crop-CASMA, capa SUB) > 0,6 m3/m3 por condado y su efecto en la media.

Uso: .venv/bin/python -I -X utf8 docs/research/smap_costas_celdas.py <dir_tifs> <cb_2023_us_county_500k.zip>
Los tifs se piden al WPS como src/agua/download.py (GetFileByFips) y van fuera del repo.
"""
import sys, numpy as np, geopandas as gpd, rasterio
from rasterio import features
from rasterio.transform import Affine
d, shp = sys.argv[1], sys.argv[2]
cty = gpd.read_file(shp).to_crs("EPSG:5070")
def rd(p):
    with rasterio.open(p) as s: a=s.read(1).astype(float); a[a==s.nodata]=np.nan; return a, s.transform, s.shape
for est in ("27","39"):
    A={k:rd(f"{d}/SMAP-9KM-DAILY-{k}_FIPS_{est}.tif") for k in ("SUB_2019.05.01_013000","SUB_2023.07.15_013000","TOP_2019.05.01_013000","TOP_2023.07.15_013000")}
    s1,s2=A["SUB_2019.05.01_013000"][0],A["SUB_2023.07.15_013000"][0]
    h1,h2=s1>0.6,s2>0.6
    print(f"\nFIPS {est}: SUB>0,6 2019-05-01 {h1.sum()}, 2023-07-15 {h2.sum()}, en ambos {(h1&h2).sum()}")
    print(f"  esas celdas: SUB mín {np.nanmin(np.fmin(s1,s2)[h1]):.3f}; TOP 2023-07-15 mediana {np.nanmedian(A['TOP_2023.07.15_013000'][0][h1]):.3f} (resto {np.nanmedian(A['TOP_2023.07.15_013000'][0][~h1&np.isfinite(s1)]):.3f})")
    # por condado: fracción del área con celdas excluidas y efecto en la media SUB 2023-07-15
    _,T,sh=A["SUB_2023.07.15_013000"]; F=10
    sub=cty[cty.STATEFP==est].sort_values("GEOID").reset_index(drop=True)
    fino=Affine(T.a/F,0,T.c,0,T.e/F,T.f)
    ids=features.rasterize(((g,i+1) for i,g in enumerate(sub.geometry)),out_shape=(sh[0]*F,sh[1]*F),transform=fino,fill=0,dtype="int32")
    W=np.zeros((len(sub),sh[0]*sh[1])); rr,cc=np.nonzero(ids); np.add.at(W,(ids[rr,cc]-1,(rr//F)*sh[1]+cc//F),1)
    for k in ("SUB_2019.05.01_013000","SUB_2023.07.15_013000"):
        a=A[k][0].ravel(); ok=np.isfinite(a); okr=ok&(a<=0.6)
        frac=(W@(ok&~okr))/(W@ok)
        m_ex=(W@np.where(okr,a,0))/(W@okr); m_all=(W@np.where(ok,a,0))/(W@ok)
        sub[f"exc_{k[:14]}"]=frac; sub[f"dif_{k[:14]}"]=m_all-m_ex; sub[f"mex_{k[:14]}"]=m_ex
        sub[f"nan_{k[:14]}"]=(W@ok)==0
    sub["nodata_frac"]=(W@(~np.isfinite(A["SUB_2023.07.15_013000"][0].ravel())))/W.sum(1)
    c=[x for x in sub.columns if x[:4] in("exc_","dif_","mex_")]+["nodata_frac"]
    import pandas as pd; pd.set_option("display.width",250)
    print("  condados con área excluida (orden por fracción):", (sub[c[0]]>0).sum(), "de", len(sub))
    print(sub.sort_values(c[0],ascending=False).head(12)[["GEOID","NAME"]+c].round(3).to_string(index=False))
    print("  condados costeros:"); cos={"27":["27137","27075","27031","27077"],"39":["39095","39123","39143","39043","39093","39035","39085","39007"]}[est]
    print(sub[sub.GEOID.isin(cos)][["GEOID","NAME"]+c].round(3).to_string(index=False))
    print("  algún condado sin celdas válidas:", sub[[x for x in sub.columns if x.startswith("nan_")]].any().to_dict())
