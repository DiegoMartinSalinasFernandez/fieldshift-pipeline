"""Fechas habituales de Dakota del Norte desde Crop Progress (tarea T108).

Baja de ESMIS los reportes semanales de texto de un año (por defecto 2026) a la carpeta que se le pasa, fuera
del repo, sin volver a bajar lo que ya está. De cada tabla "<Cultivo> <Etapa> - Selected States" toma la fila
de North Dakota y la columna del promedio de 5 años (en los reportes de 2026: "2021-2025 Average"), junto con
la fecha de cierre de la semana actual. Con esa serie interpola linealmente el día del año (y la fecha MM-DD)
en que el promedio cruza el 10, 25, 50, 75 y 90 %.

Imprime un CSV: cultivo, etapa, umbral, doy, fecha, n_semanas, primera_semana, ultima_semana, pct_primera,
pct_ultima. Si el umbral queda antes de la primera semana publicada o después de la última, doy queda vacío.

Uso:
  .venv/bin/python -X utf8 docs/research/fechas_nd_cp.py /tmp/t108/cp [2026] > docs/research/fechas_nd_cp.csv
"""
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

import requests

BASE = "https://esmis.nal.usda.gov"
UA = {"User-Agent": "Mozilla/5.0 (fieldshift-research)"}
ESTADO = "North Dakota"
UMBRALES = (10, 25, 50, 75, 90)
CULTIVOS = ("Corn", "Soybeans", "Spring Wheat", "Winter Wheat", "Oats", "Barley")
TABLA = re.compile(r"^(" + "|".join(CULTIVOS) + r") ([A-Za-z ]+?) - Selected States\s*$")
FECHA = re.compile(r"([A-Z][a-z]{2})[a-z]*\.? (\d{1,2}),")


def bajar(carpeta: Path, anio: int) -> None:
    yy = f"{anio % 100:02d}"
    patron = re.compile(r'href="(/sites/default/release-files/\d+/prog\d{2}' + yy + r'\.txt)"')
    pagina, vistos_viejos, vistos = 0, 0, set()
    while vistos_viejos < 2:
        html = requests.get(f"{BASE}/publication/crop-progress", params={"page": pagina}, headers=UA,
                            timeout=120).text
        if "release-files" not in html:
            break
        # cada página repite el último reporte en un recuadro lateral: solo cuentan los enlaces nuevos
        enlaces = [e for e in patron.findall(html) if e not in vistos]
        vistos.update(enlaces)
        # las páginas van de lo más nuevo a lo más viejo: se corta dos páginas después de la última del año
        vistos_viejos = vistos_viejos + 1 if not enlaces else 0
        for e in enlaces:
            destino = carpeta / Path(e).name
            if not destino.exists():
                r = requests.get(BASE + e, headers=UA, timeout=120)
                if r.ok:
                    destino.write_bytes(r.content)
                else:
                    print(f"{r.status_code} {e}", file=sys.stderr)
        pagina += 1
        time.sleep(0.3)


def leer(archivo: Path, anio: int):
    """Devuelve [(cultivo, etapa, fecha_semana, pct_promedio)] de North Dakota en un reporte."""
    lineas = archivo.read_text(encoding="latin-1").splitlines()
    filas = []
    i = 0
    while i < len(lineas):
        m = TABLA.match(lineas[i].strip())
        if not m:
            i += 1
            continue
        cultivo, etapa = m.group(1), m.group(2).strip()
        fecha_semana = None
        j = i + 1
        while j < len(lineas) and not TABLA.match(lineas[j].strip()) and j < i + 60:
            ln = lineas[j]
            if "State" in ln and fecha_semana is None:
                fechas = FECHA.findall(ln)
                if len(fechas) >= 3:
                    mes, dia = fechas[2]
                    fecha_semana = datetime.strptime(f"{mes} {dia} {anio}", "%b %d %Y").date()
            if ln.startswith(ESTADO):
                valores = ln.split(":", 1)[1].split()
                if len(valores) >= 4 and fecha_semana is not None:
                    v = valores[3]
                    filas.append((cultivo, etapa, fecha_semana, None if v == "-" else float(v)))
                break
            j += 1
        i = j
    return filas


def cruce(serie, umbral):
    for (d0, p0), (d1, p1) in zip(serie, serie[1:]):
        if p0 < umbral <= p1:
            doy0, doy1 = d0.timetuple().tm_yday, d1.timetuple().tm_yday
            return doy0 + (umbral - p0) * (doy1 - doy0) / (p1 - p0)
    return None


def main() -> None:
    carpeta = Path(sys.argv[1])
    anio = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    carpeta.mkdir(parents=True, exist_ok=True)
    bajar(carpeta, anio)
    datos = {}
    for archivo in sorted(carpeta.glob(f"prog??{anio % 100:02d}.txt")):
        for cultivo, etapa, f, p in leer(archivo, anio):
            if p is not None:
                datos.setdefault((cultivo, etapa), {})[f] = p
    print("cultivo,etapa,umbral,doy,fecha,n_semanas,primera_semana,ultima_semana,pct_primera,pct_ultima")
    for (cultivo, etapa), por_fecha in sorted(datos.items()):
        serie = sorted(por_fecha.items())
        for u in UMBRALES:
            doy = cruce(serie, u)
            fecha = "" if doy is None else date.fromordinal(date(anio, 1, 1).toordinal() + round(doy) - 1
                                                            ).strftime("%m-%d")
            print(f"{cultivo},{etapa},{u},{'' if doy is None else round(doy, 1)},{fecha},{len(serie)},"
                  f"{serie[0][0]},{serie[-1][0]},{serie[0][1]:g},{serie[-1][1]:g}")


if __name__ == "__main__":
    main()
