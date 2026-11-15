import pandas as pd, sys
c=["com","cls","prac","util","short","st","fips","county","anio","val"]
d=pd.read_csv("/tmp/t145/rend.tsv",sep="\t",names=c,dtype=str)
d["v"]=pd.to_numeric(d.val.str.replace(",","").str.strip(),errors="coerce")
m={("CORN","ALL CLASSES","GRAIN"):"maiz",("SOYBEANS","ALL CLASSES","ALL UTILIZATION PRACTICES"):"soja",
   ("WHEAT","WINTER","ALL UTILIZATION PRACTICES"):"trigo_invierno",("OATS","ALL CLASSES","ALL UTILIZATION PRACTICES"):"avena"}
d["cultivo"]=[m.get(k) for k in zip(d.com,d.cls,d.util)]
d=d[d.cultivo.notna()&d.v.notna()]
ests=sys.argv[1].split(",")
d=d[d.st.isin(ests)]
pd.set_option("display.width",250); pd.set_option("display.max_rows",500)
for prac in ["ALL PRODUCTION PRACTICES","IRRIGATED","NON-IRRIGATED"]:
    x=d[d.prac==prac]
    print("==",prac, len(x))
    g=x.groupby("cultivo").v
    print(pd.DataFrame({"n":g.size(),"min":g.min(),"p001":g.quantile(.001),"max":g.max()}))
    for cul,(lo,hi) in {"maiz":(5,300),"soja":(2,100),"trigo_invierno":(5,130),"avena":(2,200)}.items():
        y=x[(x.cultivo==cul)]
        for _,r in y.nsmallest(3,"v").iterrows(): print(f"  min {cul} {r.st} {r.fips} {r.county} {r.anio} {r.v}")
        for _,r in y.nlargest(2,"v").iterrows(): print(f"  max {cul} {r.st} {r.fips} {r.county} {r.anio} {r.v}")
