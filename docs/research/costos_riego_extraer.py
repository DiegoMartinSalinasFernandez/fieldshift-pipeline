"""Extrae costos por acre de maíz y soja de los presupuestos de UNL (Nebraska Crop Budgets) y K-State.

Tarea T142. Solo referencia: escribe docs/research/costos_riego.csv, no toca data/.

Uso (los PDF se bajan a mano o con curl a un directorio aparte, fuera del repo):

    pdftotext -layout <pdf> <txt>        # poppler-utils
    python -I docs/research/costos_riego_extraer.py unl <dir_txt_unl> > /tmp/unl.csv
    python -I docs/research/costos_riego_extraer.py ks <dir_txt_ks> > /tmp/ks.csv

UNL tiene dos formatos:
- 2009-2025 ("legacy"): título "YYYY Budget N-..." y líneas "Total Operating and Use Related Ownership Costs",
  "Total Cost per Acre Including Overhead", "Cash Cost per bushel" y "Cost of production per bushel".
- 2026 (Agricultural Budget Calculator): título "2026 UNL #NNN ..." y líneas "Total Operating Costs",
  "Total Ownership and Overhead Costs" y "Total Economic Cost".
"""
import csv
import re
import sys
from pathlib import Path

NUM = r"\$?\s*([\d,]+\.\d+)"


def num(s):
    return float(s.replace(",", ""))


def cultivo_de(titulo):
    t = titulo.lower().strip()
    if t.startswith("soybean"):
        return "soja"
    if (t.startswith("corn") or t.startswith("ecofallow corn")) and "silage" not in t:
        return "maiz"
    return None


def riego_de(titulo):
    t = titulo.lower()
    if "dryland" in t or "rainfed" in t or "non-irrigated" in t:
        return "secano"
    if "non-irrigated" in t:
        return "secano"
    if "pivot" in t or (t.startswith(("corn irrigated", "soybeans irrigated"))):
        return "pivote"
    if "gravity" in t or "furrow" in t:
        return "gravedad"
    if "irrigated" in t:
        return "riego_sin_detalle"
    return "sin_dato"


def rinde_de(titulo):
    m = re.search(r"(\d{2,3})\s*(?:bushels?|bu)\b", titulo, re.I)
    return int(m.group(1)) if m else None


def unl_legacy(lineas, anio, archivo):
    filas = []
    for i, l in enumerate(lineas):
        if "Total Cost per Acre Including Overhead" not in l:
            continue
        total = re.search(NUM + r"\s*$", l)
        # operativo: hacia atrás
        oper = None
        for j in range(i, max(i - 15, 0), -1):
            if "Total Operating and Use Related Ownership Costs" in lineas[j]:
                m = re.search(NUM + r"\s*$", lineas[j])
                oper = num(m.group(1)) if m else None
                break
        # título: la línea "Budget N" más cercana hacia atrás
        titulo, nro = None, None
        for j in range(i, max(i - 160, 0), -1):
            m = re.search(r"Budget\s+(\d+)\s*[-.:]\s*(.*)", lineas[j])
            if m:
                nro = int(m.group(1))
                titulo = (m.group(2).strip() + " " + lineas[j + 1].strip()).strip()
                break
        if titulo is None:
            continue
        cash = cop = None
        for j in range(i, min(i + 6, len(lineas))):
            m = re.search(r"Cash Cost per bushel.*?" + NUM + r"\s*$", lineas[j])
            if m:
                cash = num(m.group(1))
            m = re.search(r"Cost of production per bushel.*?" + NUM + r"\s*$", lineas[j])
            if m:
                cop = num(m.group(1))
        filas.append(dict(fuente="UNL", anio=anio, presupuesto=nro, titulo=titulo,
                          costo_operativo_usd_ac=oper, costo_total_usd_ac=num(total.group(1)) if total else None,
                          costo_efectivo_usd_bu=cash, costo_total_usd_bu=cop, archivo=archivo))
    return filas


def unl_abc(lineas, anio, archivo):
    filas, vistos = [], set()
    for i, l in enumerate(lineas):
        if not l.startswith("Total Economic Cost"):
            continue
        tot = re.findall(NUM, l)
        oper = over = None
        titulo, nro = None, None
        for j in range(i, max(i - 60, 0), -1):
            if lineas[j].startswith("Total Operating Costs") and oper is None:
                oper = num(re.findall(NUM, lineas[j])[-2])
            if lineas[j].startswith("Total Ownership and Overhead Costs") and over is None:
                over = num(re.findall(NUM, lineas[j])[-2])
            m = re.search(r"\d{4} UNL #(\d+)\s+(.*)", lineas[j])
            if m:
                nro = int(m.group(1))
                titulo = (m.group(2).strip() + " " + lineas[j + 1].strip()).strip()
                break
        if titulo is None or nro in vistos:
            continue
        vistos.add(nro)
        # el rinde del ABC está en "Yield per acre: N bushels"
        rinde = None
        for j in range(i, max(i - 60, 0), -1):
            m = re.search(r"Yield per acre:\s*([\d.]+)\s*bushels", lineas[j])
            if m:
                rinde = float(m.group(1))
                break
        filas.append(dict(fuente="UNL", anio=anio, presupuesto=nro, titulo=titulo,
                          costo_operativo_usd_ac=oper, costo_total_usd_ac=num(tot[-2]) if len(tot) >= 2 else None,
                          costo_efectivo_usd_bu=None, costo_total_usd_bu=num(tot[0]) if tot else None,
                          archivo=archivo, rinde_bu_ac=rinde))
    return filas


def main_unl(d):
    salida = []
    for p in sorted(Path(d).glob("*.txt")):
        m = re.search(r"(20\d{2})", p.name) or re.search(r"ec(\d{2})", p.name, re.I)
        if not m:
            continue
        anio = int(m.group(1)) if len(m.group(1)) == 4 else 2000 + int(m.group(1))
        lineas = p.read_text(errors="replace").splitlines()
        filas = unl_abc(lineas, anio, p.name) if any("Total Economic Cost" in l for l in lineas) else unl_legacy(lineas, anio, p.name)
        salida += filas
    return salida


def main_ks(d):
    """K-State, Farm Management Guides, Centro-Norte de Kansas, rendimiento medio (la primera hoja abstract)."""
    salida = []
    for p in sorted(Path(d).glob("*.txt")):
        lineas = p.read_text(errors="replace").splitlines()
        cab = " ".join(lineas[:6])
        m = re.search(r"\b(20\d{2})\b", cab)
        if not m:
            continue
        anio = int(m.group(1))
        texto = "\n".join(lineas)

        def primero(patron):
            mm = re.search(patron, texto)
            return num(mm.group(1)) if mm else None

        prod = re.search(r"(Corn|Soybeans?) - North Central KS\s+bu\s+\$([\d.]+)\s+([\d.]+)", texto)
        directos = primero(r"TOTAL DIRECT EXPENSES--\s+\$([\d,]+\.\d+)")
        fijos = primero(r"TOTAL FIXED EXPENSES--\s+\$([\d,]+\.\d+)")
        renta = primero(r"Cash rent[^\n$]*\$([\d,]+\.\d+)")
        titulo = "irrigated" if "irrigated" in p.name.lower() else "non-irrigated"
        titulo = f"{'Corn' if 'corn' in p.name.lower() else 'Soybeans'} {titulo} North Central Kansas"
        salida.append(dict(fuente="K-State", anio=anio, presupuesto=None, titulo=titulo,
                           rinde_bu_ac=float(prod.group(3)) if prod else None,
                           precio_usd_bu=float(prod.group(2)) if prod else None,
                           costo_operativo_usd_ac=directos, alquiler_usd_ac=renta, costo_fijo_usd_ac=fijos,
                           costo_total_usd_ac=round(directos + fijos, 2) if directos and fijos else None,
                           archivo=p.name))
    return salida


def main():
    modo, d = sys.argv[1], sys.argv[2]
    filas = main_unl(d) if modo == "unl" else main_ks(d)
    out = []
    for f in filas:
        c = cultivo_de(f["titulo"])
        if c is None:
            continue
        f["cultivo"] = c
        f["riego"] = riego_de(f["titulo"])
        f.setdefault("rinde_bu_ac", rinde_de(f["titulo"]))
        if f["rinde_bu_ac"] is None:
            f["rinde_bu_ac"] = rinde_de(f["titulo"])
        out.append(f)
    cols = ["fuente", "anio", "presupuesto", "cultivo", "riego", "rinde_bu_ac", "costo_operativo_usd_ac",
            "costo_fijo_usd_ac", "alquiler_usd_ac", "costo_total_usd_ac", "precio_usd_bu", "costo_efectivo_usd_bu", "costo_total_usd_bu", "titulo", "archivo"]
    w = csv.DictWriter(sys.stdout, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(out)


if __name__ == "__main__":
    main()
