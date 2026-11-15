"""Registro del research agent en Excel: loop/runs/registro_rondas.xlsx.

Hojas:
  Resumen      cómo va cada corrida (puntaje, rondas, costo, ronda en curso, credenciales)
  Rondas       qué hizo cada ronda: tarea, resultado, puntaje, resumen del agente, aprendizajes
  Tareas       puntaje y estado de cada tarea y lo que le falta
  Fuentes      los NASA Data & Resources del desafío y en qué quedó cada uno
  Decisiones   lo que los agentes dejaron para el humano (loop/notes/decisiones.md)
  Datos        los CSV entregados y las descargas del manifest

run.py lo regenera después de cada ronda. A mano, o mirando una corrida en curso:
    uv run --no-project --with openpyxl==3.1.5 --with pyyaml==6.0.2 python loop/registro.py
    uv run --no-project --with openpyxl==3.1.5 --with pyyaml==6.0.2 python loop/registro.py --watch

Solo lee (loop/runs/, loop/notes/decisiones.md, loop/spec/, manifest.csv, data/) y escribe un
único archivo. Si el Excel está abierto, Windows no deja reemplazarlo: queda la versión anterior
y se reintenta en la próxima actualización (código de salida 3).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

REPO_DEF = Path(__file__).resolve().parents[1]
SALIDA_REL = "loop/runs/registro_rondas.xlsx"
CACHE_REL = "loop/runs/.registro_cache.json"
FUENTE = "Arial"

# --------------------------------------------------------------------------- recursos del desafío
# Pestaña "Resources" de https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/
# (consultada 2026-11-14), más GRACE, que el desafío nombra en sus objetivos.
# checks: subcadenas de los IDs de checks del scorer que miden ese recurso.
# tareas: tareas del loop que lo usan. manifest: regex sobre fuente + producto del manifest.
RECURSOS = [
    {"nombre": "SMAP (Soil Moisture Active Passive)", "org": "NASA",
     "url": "https://www.earthdata.nasa.gov/data/platforms/space-based-platforms/smap",
     "aporta": "Humedad del suelo superficial y de la zona radicular (9 km, diaria desde 2015-03).",
     "paquete": "agua", "checks": [":sm_surface_m3m3", ":sm_rootzone_m3m3", ":sm_rootzone_anom_z", ":dias_sm_saturado"],
     "tareas": ["agua"], "manifest": r"smap"},
    {"nombre": "GPM IMERG", "org": "NASA / JAXA", "url": "https://gpm.nasa.gov/data",
     "aporta": "Lluvia satelital diaria (0,1°): extremos, rachas secas, erosión.",
     "paquete": "clima", "checks": [":prec_imerg_mm"], "tareas": ["clima"], "manifest": r"imerg|gpm_3"},
    {"nombre": "Landsat", "org": "NASA / USGS", "url": "https://earthexplorer.usgs.gov/",
     "aporta": "Reflectancia y NDVI a 30 m: lotes desnudos y cobertura verde en invierno.",
     "paquete": "teledeteccion", "tareas": ["teledeteccion"], "manifest": r"landsat|hls"},
    {"nombre": "MODIS", "org": "NASA", "url": "https://lpdaac.usgs.gov/products/",
     "aporta": "NDVI y EVI (250 m), temperatura de superficie (1 km), ET y fenología.",
     "paquete": "vegetacion", "tareas": ["vegetacion"], "manifest": r"mod13|mod11|mod16|mcd12|modis"},
    {"nombre": "VIIRS", "org": "NASA / NOAA", "url": "https://search.earthdata.nasa.gov/search?q=VIIRS",
     "aporta": "Continuación de MODIS (índices de vegetación a 500 m desde 2012).",
     "no_uso": "Por ahora no: MODIS cubre 2000–2025 y su NDVI tiene más resolución (250 m). VIIRS es el "
               "reemplazo si MODIS deja de producir. Lo evalúa el research recursos_desafio."},
    {"nombre": "NASA POWER", "org": "NASA", "url": "https://power.larc.nasa.gov/",
     "aporta": "Clima diario por punto desde 1981: temperatura, lluvia, radiación, viento, humedad del suelo.",
     "paquete": "clima", "checks": [":prec_power_mm", ":tmax_c", ":tmin_c", ":rad_mj_m2", ":eto_pm_mm", ":gdd_10_30"],
     "tareas": ["clima"], "manifest": r"power"},
    {"nombre": "SRTM (NASADEM)", "org": "NASA / NGA", "url": "https://www.earthdata.nasa.gov/data/instruments/srtm",
     "aporta": "Elevación, pendiente e índice topográfico de humedad (30 m).",
     "paquete": "suelo_terreno", "checks": [":elevacion_", ":pendiente_", ":twi_"], "tareas": ["suelo_terreno"],
     "manifest": r"srtm|nasadem"},
    {"nombre": "ECOSTRESS", "org": "NASA / JPL", "url": "https://ecostress.jpl.nasa.gov/data",
     "aporta": "Temperatura de superficie y evapotranspiración a 70 m (desde 2018).",
     "paquete": "ecostress", "tareas": ["ecostress"], "manifest": r"ecostress|eco_?l[234]|eco[234]"},
    {"nombre": "USDA Ag Data Commons", "org": "USDA NAL", "url": "https://www.nal.usda.gov/services/agdatacommons",
     "aporta": "Portal de datasets agrícolas abiertos (manejo, suelos, fenología, ensayos).",
     "paquete": "research:ag_data_commons", "tareas": ["research:ag_data_commons"]},
    {"nombre": "Web Soil Survey", "org": "USDA NRCS", "url": "https://websoilsurvey.nrcs.usda.gov/app/",
     "aporta": "Visor oficial de los suelos SSURGO.",
     "paquete": "suelo_terreno", "checks": [":aws0_100_mm", ":clase_drenaje", ":grupo_hidrologico"],
     "tareas": ["suelo_terreno"], "nota": "Mismos datos que SSURGO (ver esa fila).",
     "manifest": r"soil data access|ssurgo"},
    {"nombre": "Cropland Data Layer (CropScape)", "org": "USDA NASS", "url": "https://nassgeodata.gmu.edu/CropScape/",
     "aporta": "Cultivo de cada píxel de 30 m por año: rotaciones, transiciones y máscaras.",
     "paquete": "cultivos", "checks": ["rotacion_anual.csv", "rotacion_secuencia.csv", "esp:cultivos:mascara",
                                       "esp:cultivos:clases_cdl"],
     "tareas": ["cultivos"], "manifest": r"cropland|cdl"},
    {"nombre": "PRISM", "org": "Oregon State University", "url": "https://prism.oregonstate.edu/",
     "aporta": "Clima mensual a 4 km: valida la lluvia y la temperatura de POWER e IMERG.",
     "paquete": "validacion", "checks": ["_prism_"], "tareas": ["validacion"], "manifest": r"prism"},
    {"nombre": "SSURGO / STATSGO2", "org": "USDA NRCS", "url": "https://www.nrcs.usda.gov/resources/data-and-reports/soils",
     "aporta": "Textura, materia orgánica, drenaje, agua disponible, NCCPI, factor K.",
     "paquete": "suelo_terreno", "checks": [":aws0_", ":soc0_", ":nccpi", ":arcilla_pct", ":materia_organica_pct",
                                            ":factor_k_rusle", ":clase_drenaje"],
     "tareas": ["suelo_terreno"], "manifest": r"ssurgo|statsgo|gnatsgo|soil data access"},
    {"nombre": "NAIP", "org": "USDA FPAC", "url": "https://naip-usdaonline.hub.arcgis.com/",
     "aporta": "Fotos aéreas de 1 m de la temporada de crecimiento.",
     "no_uso": "No entra en los CSV por condado: a 1 m sirve para el mapa de la app (ver los lotes), "
               "no como variable del modelo."},
    {"nombre": "NLCD (National Land Cover Database)", "org": "USGS",
     "url": "https://www.usgs.gov/centers/eros/science/national-land-cover-database",
     "aporta": "Cobertura del suelo a 30 m: cultivos, pasturas, bosque, humedales, urbano.",
     "paquete": "paisaje", "tareas": ["paisaje"], "manifest": r"nlcd|lcmap"},
    {"nombre": "NLDAS / GLDAS", "org": "NASA", "url": "https://www.earthdata.nasa.gov/",
     "aporta": "Humedad del suelo por capas, ET y escorrentía desde 1979 (cubre los años sin SMAP).",
     "paquete": "nldas", "tareas": ["nldas"], "manifest": r"nldas|gldas"},
    {"nombre": "FAO GAEZ", "org": "FAO", "url": "https://gaez.fao.org/",
     "aporta": "Aptitud y rendimiento alcanzable por cultivo, con clima actual y de 2041–2070.",
     "paquete": "aptitud", "tareas": ["aptitud"], "manifest": r"gaez"},
    {"nombre": "CoCoRaHS", "org": "CoCoRaHS", "url": "https://www.cocorahs.org/Maps",
     "aporta": "Lluvia de pluviómetros voluntarios: valida IMERG y detecta tormentas locales.",
     "paquete": "validacion", "checks": ["_cocorahs"], "tareas": ["validacion"], "manifest": r"cocorahs"},
    {"nombre": "USGS NWIS", "org": "USGS", "url": "https://waterdata.usgs.gov/nwis",
     "aporta": "Napa freática medida en pozos y caudales de ríos.",
     "paquete": "hidrologia", "tareas": ["hidrologia"], "manifest": r"nwis|waterdata|water data"},
    {"nombre": "USDA AMS Market News", "org": "USDA AMS", "url": "https://www.ams.usda.gov/market-news",
     "aporta": "Precios de mercado de granos y forrajes.", "opcional": True,
     "paquete": "economia", "tareas": ["economia"], "manifest": r"market news|\bams\b|mymarketnews",
     "nota": "economia arma precios y costos con NASS (precio recibido) y ERS; Market News es opcional."},
    {"nombre": "USDA NASS Quick Stats", "org": "USDA NASS", "url": "https://quickstats.nass.usda.gov/",
     "aporta": "Rendimiento, superficie y producción por condado; avance de siembra; Censo; precios.",
     "paquete": "cultivos", "checks": ["produccion_anual.csv", "fenologia_estado.csv", "practicas_censo.csv",
                                       "esp:cultivos:consistencia"],
     "tareas": ["cultivos"], "manifest": r"quick ?stats|crop progress"},
    {"nombre": "OpenET", "org": "OpenET (NASA, USGS y otros)", "url": "https://openetdata.org/",
     "aporta": "Evapotranspiración a escala de lote.",
     "no_uso": "Según el desafío cubre los estados del oeste de EE.UU.; el research recursos_desafio "
               "verifica si llega a IA, IL e IN."},
    {"nombre": "LANDFIRE", "org": "USFS / USGS", "url": "https://www.landfire.gov/",
     "aporta": "Vegetación natural, combustibles y paisaje.",
     "no_uso": "Pensado para vegetación natural e incendios; en lotes agrícolas lo cubren CDL y NLCD."},
    {"nombre": "GEDI", "org": "NASA / Univ. de Maryland", "url": "https://gedi.umd.edu/data",
     "aporta": "Altura del canopeo y biomasa con láser.",
     "no_uso": "Mide estructura de bosques; el propio desafío aclara que rinde mejor con vegetación alta. "
               "Poco aporte en lotes de maíz y soja."},
    {"nombre": "Copernicus Sentinel-2", "org": "ESA (socio)", "url": "https://dataspace.copernicus.eu/",
     "aporta": "Imágenes de 10–20 m: NDVI, suelo desnudo y estrés a escala de lote.",
     "paquete": "teledeteccion", "tareas": ["teledeteccion"], "manifest": r"sentinel|s2_l2a|hls"},
    {"nombre": "ERA5", "org": "ECMWF (socio)",
     "url": "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview",
     "aporta": "Reanálisis climático horario global.",
     "no_uso": "Pide cuenta en Copernicus; NASA POWER (desde 1981) y NLDAS cubren las mismas variables en la zona."},
    {"nombre": "GRACE / GRACE-FO (GRACE-DA-DM)", "org": "NASA", "url": "https://grace.jpl.nasa.gov/",
     "aporta": "Agua subterránea y humedad del suelo en percentiles semanales (objetivos del desafío).",
     "paquete": "agua", "checks": [":gws_pctl", ":rtzsm_pctl", ":sfsm_pctl"], "tareas": ["agua"],
     "manifest": r"grace"},
]

# --------------------------------------------------------------------------- estilos

COLOR = {
    "titulo": "1F3A4D", "encabezado": "1F3A4D", "texto_suave": "5F6B73", "borde": "C9D1D6",
    "verde": "D9EAD3", "amarillo": "FFF2CC", "rojo": "F4CCCC", "gris": "EDEDED", "lila": "E6E0F2",
    "celeste": "DDEBF7", "naranja": "FCE5CD", "barra": "6FA8DC",
}
RESULTADO_COLOR = {
    "guardada": "verde", "guardada_espera": "amarillo", "sin_cambios": "gris", "reflexion": "lila",
    "inicio": "celeste", "en curso": "celeste", "descartada": "rojo", "error_scorer": "rojo",
    "fuera_de_alcance": "rojo", "raw_modificado": "rojo", "tamper": "rojo", "limite_5gb": "naranja",
    "error_arranque": "rojo", "timeout": "rojo",
}
TEXTO_RESULTADO = {
    "guardada": "guardada", "guardada_espera": "guardada (esperando un pedido)", "sin_cambios": "sin cambios",
    "reflexion": "reflexión", "inicio": "inicio de la corrida", "descartada": "descartada",
    "error_scorer": "error del verificador", "fuera_de_alcance": "descartada (fuera de sus rutas)",
    "raw_modificado": "descartada (tocó data/raw)", "tamper": "descartada (tocó archivos bloqueados)",
    "limite_5gb": "frenada (más de 5 GB)", "error_arranque": "el agente no arrancó",
}


def _estilos():
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    lado = Side(style="thin", color=COLOR["borde"])
    return {
        "titulo": Font(name=FUENTE, size=16, bold=True, color=COLOR["titulo"]),
        "subtitulo": Font(name=FUENTE, size=10, color=COLOR["texto_suave"]),
        "seccion": Font(name=FUENTE, size=12, bold=True, color=COLOR["titulo"]),
        "normal": Font(name=FUENTE, size=10),
        "negrita": Font(name=FUENTE, size=10, bold=True),
        "enc_font": Font(name=FUENTE, size=10, bold=True, color="FFFFFF"),
        "enc_fill": PatternFill("solid", fgColor=COLOR["encabezado"]),
        "borde": Border(left=lado, right=lado, top=lado, bottom=lado),
        "arriba": Alignment(vertical="top", wrap_text=False),
        "envolver": Alignment(vertical="top", wrap_text=True),
        "centro": Alignment(horizontal="center", vertical="top"),
        "link": Font(name=FUENTE, size=10, color="1155CC", underline="single"),
    }


def relleno(nombre):
    from openpyxl.styles import PatternFill
    return PatternFill("solid", fgColor=COLOR[nombre])


# --------------------------------------------------------------------------- lectura

def leer_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def leer_tsv(p: Path):
    try:
        with open(p, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f, delimiter="\t"))
    except Exception:
        return []


def num(x, defecto=None):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return defecto
    return v


def texto(x, maximo=None) -> str:
    if x is None:
        return ""
    if isinstance(x, list):
        x = "\n".join(f"• {str(i).strip()}" for i in x if str(i).strip())
    s = str(x).replace("\r", "").strip()
    s = re.sub(r"\*\*|`", "", s)
    if maximo and len(s) > maximo:
        s = s[: maximo - 1].rstrip() + "…"
    return s


def resultado_final(m) -> str:
    """Texto del último mensaje 'result' de un log stream-json (reflexión)."""
    try:
        with open(m, "rb") as f:
            f.seek(0, os.SEEK_END)
            n = f.tell()
            f.seek(max(0, n - 200_000))
            cola = f.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return ""
    for linea in reversed(cola):
        linea = linea.strip()
        if '"type":"result"' not in linea.replace(" ", ""):
            continue
        try:
            d = json.loads(linea)
        except Exception:
            continue
        return str(d.get("result") or "")
    return ""


RE_TARJETA = re.compile(r"# Tarjeta de la ronda (\d+) — tarea `([^`]+)`")
RE_INICIO = re.compile(r"- Inicio: (\d{4}-\d{2}-\d{2} \d{2}:\d{2})\. Tenés hasta las \*\*(\d{2}:\d{2})\*\*")
RE_CRED = re.compile(r"- Credenciales: Earthdata (.+?); clave de NASS Quick Stats \(`NASS_API_KEY`\) (.+?)\.\s*$", re.M)
RE_CABECERA = re.compile(r"Research agent · corrida (\S+) · ([\d.]+) h · hasta (\d{4}-\d{2}-\d{2} \d{2}:\d{2})")
RE_FIN = re.compile(r"Fin \((.+?)\)\. Puntaje ([\d.]+) → ([\d.]+)")
RE_CDL_ANIO = re.compile(r"\(\d{4}_\d+m_cdls\)\s*")   # agrupa las teselas del CDL de todos los años


def cargar_corrida(d: Path) -> dict:
    filas = leer_tsv(d / "results.tsv")
    estado = leer_json(d / "state.json") or {}
    log = ""
    try:
        log = (d / "run.log").read_text(encoding="utf-8", errors="replace")
    except OSError:
        pass
    cabeceras = list(RE_CABECERA.finditer(log))
    fin_previsto = cabeceras[-1].group(3) if cabeceras else ""
    horas = cabeceras[-1].group(2) if cabeceras else ""
    desde_ultima = log[cabeceras[-1].start():] if cabeceras else log
    fines = list(RE_FIN.finditer(desde_ultima))
    terminada = fines[-1].group(1) if fines else ""
    # última actividad: el archivo más nuevo de la carpeta
    ultima = 0.0
    for p in d.iterdir():
        try:
            ultima = max(ultima, p.stat().st_mtime)
        except OSError:
            pass
    # ronda en curso: tarjeta sin fila en results.tsv
    hechas = {int(r["ronda"]) for r in filas if r.get("resultado") != "reflexion" and str(r.get("ronda", "")).isdigit()}
    en_curso = None
    if not terminada:
        tarjetas = sorted(d.glob("r[0-9][0-9][0-9].prompt.md"))
        for t in reversed(tarjetas):
            n = int(t.name[1:4])
            if n in hechas:
                break
            try:
                cab = t.read_text(encoding="utf-8", errors="replace")[:4000]
            except OSError:
                continue
            m, mi = RE_TARJETA.search(cab), RE_INICIO.search(cab)
            if m:
                en_curso = {"ronda": n, "tarea": m.group(2), "inicio": mi.group(1) if mi else "",
                            "hasta": mi.group(2) if mi else ""}
            break
    # credenciales según la última tarjeta (el orquestador las chequea sin leerlas)
    cred = {}
    tarjetas = sorted(d.glob("r[0-9][0-9][0-9].prompt.md"))
    if tarjetas:
        try:
            mc = RE_CRED.search(tarjetas[-1].read_text(encoding="utf-8", errors="replace")[:6000])
        except OSError:
            mc = None
        if mc:
            cred = {"Earthdata": texto(mc.group(1)), "NASS Quick Stats": texto(mc.group(2)).replace(
                " (en el entorno o en .env)", "")}
    # puntaje vigente: el de la última ronda aceptada
    actual = None
    for r in filas:
        res = r.get("resultado", "")
        if res not in ("inicio", "guardada", "guardada_espera") or not str(r.get("ronda", "")).isdigit():
            continue
        sc = leer_json(d / f"r{int(r['ronda']):03d}.score.json")
        if sc:
            actual = sc
    if actual is None:
        cand = sorted(d.glob("r[0-9][0-9][0-9].score.json"))
        actual = leer_json(cand[-1]) if cand else None
    inicio = estado.get("inicio") or (filas[0].get("inicio") if filas else "")
    return {"tag": d.name, "dir": d, "filas": filas, "estado": estado, "fin_previsto": fin_previsto,
            "horas": horas, "terminada": terminada, "ultima": ultima, "en_curso": en_curso, "cred": cred,
            "puntaje": actual, "inicio": str(inicio)[:16].replace("T", " ")}


def corridas(repo: Path):
    base = repo / "loop" / "runs"
    out = []
    if base.exists():
        for d in base.iterdir():
            if d.is_dir() and (d / "results.tsv").exists():
                out.append(cargar_corrida(d))
    out.sort(key=lambda c: c["inicio"] or "")
    return out


def cargar_spec(repo: Path):
    try:
        import yaml
    except ImportError:
        return {}, {}
    def y(p):
        try:
            return yaml.safe_load((repo / p).read_text(encoding="utf-8")) or {}
        except Exception:
            return {}
    return y("loop/spec/entregables.yaml"), y("loop/spec/research.yaml")


def tipo_tarea(t: str) -> str:
    if t == "-":
        return "inicio"
    if t == "reflexion":
        return "reflexión"
    if t.startswith("research:"):
        return "research"
    if t == "merge":
        return "unión"
    return "datos"


def titulo_tarea(t: str, ent: dict, res: dict) -> str:
    if t.startswith("research:"):
        tid = t.split(":", 1)[1]
        for tema in res.get("temas", []) or []:
            if tema.get("id") == tid:
                q = " ".join(str(tema.get("pregunta", "")).split())
                return texto(q, 220)
        return ""
    p = (ent.get("paquetes") or {}).get(t) or {}
    return texto(p.get("titulo", ""))


# --------------------------------------------------------------------------- hojas

def encabezado(ws, fila, columnas, E):
    for j, (nombre, ancho) in enumerate(columnas, start=1):
        c = ws.cell(row=fila, column=j, value=nombre)
        c.font, c.fill, c.border = E["enc_font"], E["enc_fill"], E["borde"]
        c.alignment = E["envolver"]
        ws.column_dimensions[c.column_letter].width = ancho


def celda(ws, fila, col, valor, E, fmt=None, envolver=False, negrita=False, fill=None):
    c = ws.cell(row=fila, column=col, value=valor)
    c.font = E["negrita"] if negrita else E["normal"]
    c.border = E["borde"]
    c.alignment = E["envolver"] if envolver else E["arriba"]
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = relleno(fill)
    return c


def hoja_rondas(wb, runs, E):
    ws = wb.create_sheet("Rondas")
    cols = [("Corrida", 16), ("Ronda", 7), ("Inicio", 16), ("Minutos", 9), ("Tarea", 26), ("Tipo", 10),
            ("Resultado", 20), ("Estado del agente", 13), ("Puntaje antes", 10), ("Puntaje después", 10),
            ("Δ puntaje", 9), ("Puntaje de la tarea", 13), ("Costo estimado (USD)", 11), ("Turnos", 8),
            ("Commit", 9), ("Qué hizo", 70), ("Motivo y notas del orquestador", 45), ("Intentos", 50),
            ("Aprendizajes", 50), ("Decisiones para el humano", 45)]
    encabezado(ws, 1, cols, E)
    f = 2
    for c in runs:
        for r in c["filas"]:
            n = r.get("ronda", "")
            tarea = r.get("tarea", "")
            res = r.get("resultado", "")
            rep = {}
            hizo = r.get("resumen", "")
            if res == "reflexion":
                hizo = resultado_final(c["dir"] / f"x{int(n):03d}.log.jsonl") if str(n).isdigit() else ""
                hizo = hizo or "Reescribió la sección 'Cómo trabajar' de loop/program.md."
            elif res != "inicio" and str(n).isdigit():
                rep = leer_json(c["dir"] / f"r{int(n):03d}.report.json") or {}
                hizo = rep.get("resumen") or hizo
            pt = ""
            if res in ("guardada", "guardada_espera") and str(n).isdigit():
                sc = leer_json(c["dir"] / f"r{int(n):03d}.score.json") or {}
                t = (sc.get("tareas") or {}).get(tarea)
                if t:
                    pt = f"{t['pts']:.2f} / {t['max']:.2f}"
            mot = "; ".join(x for x in (r.get("motivo", ""), r.get("notas", "")) if x)
            if res == "reflexion":
                mot = r.get("motivo", "")
            valores = [
                (c["tag"], None), (int(n) if str(n).isdigit() else n, "0"), (r.get("inicio", ""), None),
                (num(r.get("minutos")), "0.0"), (tarea if tarea != "-" else "", None), (tipo_tarea(tarea), None),
                (TEXTO_RESULTADO.get(res, res), None), (r.get("estado_agente", ""), None),
                (num(r.get("antes")), "0.00"), (num(r.get("despues")), "0.00"), (num(r.get("delta")), "+0.00;-0.00;0.00"),
                (pt, None), (num(r.get("costo_usd")), "#,##0.00"), (int(num(r.get("turnos"), 0)) if r.get("turnos") else None, "0"),
                (r.get("commit", ""), None), (texto(hizo, 3000), None), (texto(mot, 1500), None),
                (texto(rep.get("intentos"), 3000), None), (texto(rep.get("aprendizajes"), 3000), None),
                (texto(rep.get("decisiones_para_el_humano"), 3000), None),
            ]
            for j, (v, fmt) in enumerate(valores, start=1):
                celda(ws, f, j, v, E, fmt=fmt, envolver=j >= 16)
            ws.cell(row=f, column=7).fill = relleno(RESULTADO_COLOR.get(res, "gris"))
            ea = (r.get("estado_agente") or "").lower()
            if ea:
                ws.cell(row=f, column=8).fill = relleno(
                    "verde" if ea.startswith("termin") else "naranja" if ea.startswith("bloq") else
                    "amarillo" if ea.startswith("esper") else "celeste")
            f += 1
        e = c["en_curso"]
        if e:
            valores = [c["tag"], e["ronda"], e["inicio"], None, e["tarea"], tipo_tarea(e["tarea"]), "en curso",
                       "", None, None, None, "", None, None, "",
                       f"Trabajando (hasta las {e['hasta']}). El resultado aparece cuando termina la ronda.", "", "", "", ""]
            for j, v in enumerate(valores, start=1):
                celda(ws, f, j, v, E, envolver=j >= 16)
            ws.cell(row=f, column=7).fill = relleno("celeste")
            f += 1
    ws.freeze_panes = "F2"
    ws.auto_filter.ref = f"A1:T{max(1, f - 1)}"
    return ws


def estado_de_tarea(t, info, st, ronda_actual, terminada):
    if info.get("ok"):
        return "completa", "verde"
    cred = (st or {}).get("credencial") or []
    if cred:
        nombres = {"earthdata": "Earthdata", "nass": "clave de NASS"}
        return "bloqueada: falta " + " y ".join(nombres.get(x, x) for x in cred), "naranja"
    nad = (st or {}).get("no_antes_de") or ""
    if nad and not terminada:
        try:
            if dt.datetime.fromisoformat(nad) > dt.datetime.now():
                return f"esperando hasta {nad[11:16]}: {texto(st.get('motivo_espera'), 120)}".rstrip(": "), "amarillo"
        except ValueError:
            pass
    if (st or {}).get("enfriar_hasta", 0) > ronda_actual:
        return f"en pausa hasta la ronda {st['enfriar_hasta']} (se trabó)", "amarillo"
    if not (st or {}).get("rondas") and info.get("pts", 0) <= 0:
        return "pendiente", "gris"
    return "en progreso", "celeste"


def hoja_tareas(wb, runs, ent, res, E):
    from openpyxl.formatting.rule import DataBarRule
    ws = wb.create_sheet("Tareas")
    if not runs or not runs[-1]["puntaje"]:
        ws.cell(row=1, column=1, value="Todavía no hay puntaje.").font = E["normal"]
        return ws
    c = runs[-1]
    P = c["puntaje"]
    est_t = (c["estado"] or {}).get("tareas") or {}
    ronda_actual = int((c["estado"] or {}).get("ronda") or 0)
    ws.cell(row=1, column=1, value=f"Tareas de la corrida {c['tag']} (puntaje de la última ronda guardada)").font = E["seccion"]
    cols = [("Tarea", 26), ("Tipo", 10), ("Qué es", 55), ("Puntaje", 9), ("Máximo", 9), ("% hecho", 10),
            ("Estado", 30), ("Rondas (todas las corridas)", 12), ("Última ronda", 16), ("Último resultado", 20),
            ("Lo que falta (checks que no pasan, por lo que suman)", 80)]
    encabezado(ws, 3, cols, E)
    paquetes = list((ent.get("paquetes") or {}).keys())
    temas = ["research:" + t["id"] for t in (res.get("temas") or [])]
    orden = [t for t in paquetes if t != "merge"] + (["merge"] if "merge" in paquetes else []) + temas
    tareas = [t for t in orden if t in P["tareas"]] + [t for t in P["tareas"] if t not in orden]
    todas = [(rc["tag"], r) for rc in runs for r in rc["filas"]]
    f = 4
    for t in tareas:
        info = P["tareas"][t]
        rondas = [(tag, r) for tag, r in todas if r.get("tarea") == t]
        ult = rondas[-1] if rondas else None
        fallas = sorted(((ck["max"] - ck["pts"], ck.get("msg") or cid) for cid, ck in P["checks"].items()
                         if ck.get("tarea") == t and not ck.get("ok")), key=lambda x: -x[0])
        falta = "\n".join(f"+{g:.2f}  {texto(m, 220)}" for g, m in fallas[:5])
        if len(fallas) > 5:
            falta += f"\n… y {len(fallas) - 5} checks más"
        estado, color = estado_de_tarea(t, info, est_t.get(t), ronda_actual, bool(c["terminada"]))
        valores = [(t, None), (tipo_tarea(t), None), (titulo_tarea(t, ent, res), None), (round(info["pts"], 3), "0.00"),
                   (round(info["max"], 3), "0.00"), (f"=IFERROR(D{f}/E{f},0)", "0%"), (estado, None),
                   (len(rondas), "0"), (f"{ult[0]} · {ult[1].get('ronda')}" if ult else "", None),
                   (TEXTO_RESULTADO.get(ult[1].get("resultado", ""), ult[1].get("resultado", "")) if ult else "", None),
                   (falta, None)]
        for j, (v, fmt) in enumerate(valores, start=1):
            celda(ws, f, j, v, E, fmt=fmt, envolver=j in (3, 7, 11))
        ws.cell(row=f, column=7).fill = relleno(color)
        f += 1
    ult_fila = f - 1
    celda(ws, f, 1, "Total", E, negrita=True)
    for j in (2, 3, 7, 8, 9, 10, 11):
        celda(ws, f, j, None, E)
    celda(ws, f, 4, f"=SUM(D4:D{ult_fila})", E, fmt="0.00", negrita=True)
    celda(ws, f, 5, f"=SUM(E4:E{ult_fila})", E, fmt="0.00", negrita=True)
    celda(ws, f, 6, f"=IFERROR(D{f}/E{f},0)", E, fmt="0%", negrita=True)
    ws.conditional_formatting.add(f"F4:F{f}", DataBarRule(start_type="num", start_value=0, end_type="num",
                                                          end_value=1, color=COLOR["barra"]))
    ws.freeze_panes = "B4"
    ws.auto_filter.ref = f"A3:K{ult_fila}"
    return ws


def estado_recurso(rec, P, est_t):
    if rec.get("no_uso"):
        return "no se usa", "gris", "", rec["no_uso"]
    checks = (P or {}).get("checks") or {}
    tareas_p = (P or {}).get("tareas") or {}
    pts = mx = 0.0
    hay = False
    for cid, ck in checks.items():
        if any(s in cid for s in rec.get("checks", [])):
            pts, mx, hay = pts + ck["pts"], mx + ck["max"], True
    if not hay:
        for t in rec.get("tareas", []):
            if t in tareas_p:
                pts, mx, hay = pts + tareas_p[t]["pts"], mx + tareas_p[t]["max"], True
    if not hay:
        return "se suma en la próxima corrida", "amarillo", "", ""
    cred = sorted({x for t in rec.get("tareas", []) for x in ((est_t.get(t) or {}).get("credencial") or [])})
    pct = f"{pts:.1f} / {mx:.1f}"
    if mx and pts >= mx - 1e-6:
        return "en uso (completo)", "verde", pct, ""
    if pts > 0:
        extra = " · lo que falta espera " + ", ".join("Earthdata" if x == "earthdata" else x for x in cred) if cred else ""
        return "en uso (parcial)", "verde", pct, extra.strip(" ·")
    if cred:
        return "bloqueado: falta " + ", ".join("Earthdata" if x == "earthdata" else x for x in cred), "naranja", pct, ""
    return "en cola", "celeste", pct, ""


def resumen_manifest(repo: Path):
    filas = []
    try:
        with open(repo / "manifest.csv", encoding="utf-8", newline="") as f:
            filas = list(csv.DictReader(f))
    except OSError:
        pass
    return filas


def hoja_fuentes(wb, runs, repo, E):
    ws = wb.create_sheet("Fuentes")
    ws.cell(row=1, column=1, value="NASA Data & Resources del desafío Field Shift: qué usa el loop").font = E["seccion"]
    ws.cell(row=2, column=1, value="Lista de la pestaña Resources del desafío (consultada 2026-11-14) y GRACE, que "
                                   "nombran los objetivos. Estado según el puntaje de la última ronda guardada.").font = E["subtitulo"]
    cols = [("#", 5), ("Recurso", 30), ("Organismo", 18), ("Qué aporta", 50), ("Estado en el loop", 26),
            ("Paquete o tarea", 22), ("Puntaje de esos checks", 14), ("Archivos bajados (manifest)", 12),
            ("De dónde se bajó (manifest)", 50), ("Notas", 55), ("Link", 40)]
    encabezado(ws, 4, cols, E)
    P = runs[-1]["puntaje"] if runs else None
    est_t = ((runs[-1]["estado"] or {}).get("tareas") or {}) if runs else {}
    man = resumen_manifest(repo)
    f = 5
    for i, rec in enumerate(RECURSOS, start=1):
        estado, color, pct, extra = estado_recurso(rec, P, est_t)
        n_arch, origenes = 0, []
        if rec.get("manifest") and man:
            rx = re.compile(rec["manifest"], re.I)
            vistos = {}
            for m in man:
                clave = f"{m.get('fuente', '')} — {m.get('producto', '')}"
                if rx.search(clave):
                    n_arch += 1
                    k = (m.get("fuente", "").strip(), RE_CDL_ANIO.sub("", m.get("producto", "")).strip())
                    vistos[k] = vistos.get(k, 0) + 1
            origenes = [f"{a} — {b} ({n})" for (a, b), n in sorted(vistos.items(), key=lambda x: -x[1])[:4]]
        if rec.get("opcional") and not n_arch and estado.startswith("en uso"):
            # el paquete avanza con otras fuentes: esta todavía no se bajó
            estado, color, extra = "opcional: todavía no se usó", "celeste", ""
        notas = "; ".join(x for x in (rec.get("nota", ""), extra) if x)
        valores = [(i, "0"), (rec["nombre"], None), (rec["org"], None), (rec["aporta"], None), (estado, None),
                   (rec.get("paquete", "—"), None), (pct, None), (n_arch or None, "#,##0"),
                   ("\n".join(origenes), None), (notas, None), (rec["url"], None)]
        for j, (v, fmt) in enumerate(valores, start=1):
            celda(ws, f, j, v, E, fmt=fmt, envolver=j in (2, 4, 5, 9, 10))
        ws.cell(row=f, column=5).fill = relleno(color)
        link = ws.cell(row=f, column=11)
        link.hyperlink, link.font = rec["url"], E["link"]
        f += 1
    ws.freeze_panes = "C5"
    ws.auto_filter.ref = f"A4:K{f - 1}"
    return ws


def parsear_decisiones(p: Path):
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    secciones = re.split(r"^## ", txt, flags=re.M)[1:]
    out = []
    for s in secciones:
        lineas = s.splitlines()
        titulo = lineas[0].strip()
        campos, actual = {}, "Detalle"
        for ln in lineas[1:]:
            m = re.match(r"\s*[-*]\s+\*\*([^*:]+):?\*\*:?\s*(.*)", ln)
            if m:
                et = m.group(1).strip().lower()
                actual = ("Qué" if et.startswith("qué") else "Propuesta" if et.startswith("propuesta") else
                          "Alternativas" if et.startswith("alternativa") else "Detalle")
                campos.setdefault(actual, []).append((m.group(1).strip() + ": " if actual == "Detalle" else "") + m.group(2))
            elif ln.strip():
                campos.setdefault(actual, []).append(ln.strip().lstrip("-* ").strip())
        out.append({"titulo": titulo, **{k: texto(" ".join(v), 2500) for k, v in campos.items()}})
    return out


def hoja_decisiones(wb, repo, E):
    ws = wb.create_sheet("Decisiones")
    ws.cell(row=1, column=1, value="Decisiones que los agentes dejaron para el humano").font = E["seccion"]
    ws.cell(row=2, column=1, value="Sale de loop/notes/decisiones.md (lo escriben los agentes; nadie las aplica "
                                   "hasta que el humano decide).").font = E["subtitulo"]
    cols = [("#", 5), ("Tema", 40), ("Qué pasa", 70), ("Propuesta", 60), ("Alternativas", 50), ("Más detalle", 60)]
    encabezado(ws, 4, cols, E)
    f = 5
    for i, d in enumerate(parsear_decisiones(repo / "loop" / "notes" / "decisiones.md"), start=1):
        valores = [i, d["titulo"], d.get("Qué", ""), d.get("Propuesta", ""), d.get("Alternativas", ""), d.get("Detalle", "")]
        for j, v in enumerate(valores, start=1):
            celda(ws, f, j, v, E, fmt="0" if j == 1 else None, envolver=j > 1)
        f += 1
    if f == 5:
        celda(ws, f, 2, "(no hay decisiones pendientes)", E)
    ws.freeze_panes = "C5"
    return ws


def contar_filas(p: Path, cache: dict):
    st = p.stat()
    clave = str(p)
    c = cache.get(clave)
    if c and c.get("size") == st.st_size and c.get("mtime") == st.st_mtime_ns:
        return c["filas"], c["columnas"]
    n = 0
    with open(p, "rb") as f:
        primera = f.readline()
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            n += b.count(b"\n")
    with open(p, "rb") as f:
        f.seek(0, os.SEEK_END)
        if f.tell():
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n" and n >= 0 and st.st_size > len(primera):
                n += 1
    cols = len(next(csv.reader([primera.decode("utf-8", "replace")]))) if primera else 0
    cache[clave] = {"size": st.st_size, "mtime": st.st_mtime_ns, "filas": n, "columnas": cols}
    return n, cols


def tam_dir(p: Path) -> int:
    total = 0
    pila = [p]
    while pila:
        d = pila.pop()
        try:
            with os.scandir(d) as it:
                for e in it:
                    try:
                        if e.is_dir(follow_symlinks=False):
                            pila.append(Path(e.path))
                        elif e.is_file(follow_symlinks=False):
                            total += e.stat(follow_symlinks=False).st_size
                    except OSError:
                        pass
        except OSError:
            pass
    return total


def hoja_datos(wb, repo, ent, E, cache):
    ws = wb.create_sheet("Datos")
    ws.cell(row=1, column=1, value="CSV entregados en data/processed").font = E["seccion"]
    cols = [("Paquete", 16), ("Archivo", 52), ("Filas", 11), ("Columnas", 10), ("Tamaño (MB)", 11),
            ("¿En git?", 16), ("Actualizado", 17)]
    encabezado(ws, 3, cols, E)
    max_mb = float(((ent.get("contrato") or {}).get("max_mb_archivo_git")) or 50)
    f = 4
    proc = repo / "data" / "processed"
    archivos = sorted(proc.rglob("*.csv")) if proc.exists() else []
    for p in archivos:
        try:
            filas, ncols = contar_filas(p, cache)
            st = p.stat()
        except OSError:
            continue
        rel = p.relative_to(repo).as_posix()
        pkg = p.parent.name if p.parent != proc else "merge"
        mb = st.st_size / 1e6
        valores = [(pkg, None), (rel, None), (filas, "#,##0"), (ncols, "0"), (round(mb, 1), "#,##0.0"),
                   ("sí" if mb <= max_mb else f"no (más de {max_mb:.0f} MB)", None),
                   (dt.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"), None)]
        for j, (v, fmt) in enumerate(valores, start=1):
            celda(ws, f, j, v, E, fmt=fmt)
        f += 1
    if f == 4:
        celda(ws, f, 1, "(todavía no hay CSV procesados)", E)
        f += 1
    f += 2
    ws.cell(row=f, column=1, value="Descargas por paquete (manifest.csv y data/raw)").font = E["seccion"]
    f += 2
    cols2 = [("Paquete", 16), ("Fuentes y productos (cantidad de archivos)", 52), ("Archivos bajados", 11),
             ("data/raw (GB)", 10), ("% del límite de 5 GB", 16), ("Última descarga", 17)]
    for j, (nombre, _) in enumerate(cols2, start=1):
        c = ws.cell(row=f, column=j, value=nombre)
        c.font, c.fill, c.border, c.alignment = E["enc_font"], E["enc_fill"], E["borde"], E["envolver"]
    f0 = f + 1
    f += 1
    man = resumen_manifest(repo)
    por_pkg = {}
    for m in man:
        por_pkg.setdefault(m.get("paquete", ""), []).append(m)
    raw = repo / "data" / "raw"
    pkgs = sorted(set(por_pkg) | ({d.name for d in raw.iterdir() if d.is_dir()} if raw.exists() else set()))
    for pkg in pkgs:
        filas = por_pkg.get(pkg, [])
        orig = {}
        for m in filas:
            producto = RE_CDL_ANIO.sub("", m.get("producto", "")).strip()
            k = f"{m.get('fuente', '').strip()} — {producto}"
            orig[k] = orig.get(k, 0) + 1
        txt = "\n".join(f"{k} ({v:,})".replace(",", ".") for k, v in sorted(orig.items(), key=lambda x: -x[1])[:6])
        gb = tam_dir(raw / pkg) / 1e9 if (raw / pkg).exists() else 0.0
        fechas = sorted(m.get("fecha_descarga", "") for m in filas if m.get("fecha_descarga"))
        valores = [(pkg, None), (txt, None), (len(filas), "#,##0"), (round(gb, 2), "0.00"),
                   (f"=IFERROR(D{f}/5,0)", "0%"), (fechas[-1] if fechas else "", None)]
        for j, (v, fmt) in enumerate(valores, start=1):
            celda(ws, f, j, v, E, fmt=fmt, envolver=j == 2)
        f += 1
    if f > f0:
        from openpyxl.formatting.rule import DataBarRule
        ws.conditional_formatting.add(f"E{f0}:E{f - 1}", DataBarRule(start_type="num", start_value=0, end_type="num",
                                                                      end_value=1, color=COLOR["barra"]))
    ws.freeze_panes = "A4"
    return ws


def hoja_resumen(wb, runs, E, ahora):
    ws = wb.active
    ws.title = "Resumen"
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Field Shift · registro del research agent"
    ws["A1"].font = E["titulo"]
    ws["A2"] = (f"Actualizado {ahora:%Y-%m-%d %H:%M}. Se regenera solo después de cada ronda: no escribas acá "
                "(se pierde). Si lo tenés abierto, cerralo y se pone al día en la ronda siguiente.")
    ws["A2"].font = E["subtitulo"]
    f = 4
    if runs:
        c = runs[-1]
        P = c["puntaje"] or {}
        ws.cell(row=f, column=1, value="Ahora").font = E["seccion"]
        f += 1
        if c["terminada"]:
            estado = f"Corrida {c['tag']} terminada ({c['terminada']})."
        elif c["en_curso"]:
            e = c["en_curso"]
            estado = (f"Corrida {c['tag']} en curso: ronda {e['ronda']}, tarea {e['tarea']} "
                      f"(desde {e['inicio'][11:16]}, hasta las {e['hasta']}). Fin previsto {c['fin_previsto']}.")
        else:
            hace = (time.time() - c["ultima"]) / 60 if c["ultima"] else 0
            estado = (f"Corrida {c['tag']} en curso entre rondas (puntuando o esperando). Fin previsto "
                      f"{c['fin_previsto']}." + (f" Sin novedades hace {hace:.0f} min." if hace > 75 else ""))
        lineas = [estado]
        if P:
            lineas.append(f"Puntaje: {P.get('total', 0):.1f} de {P.get('max', 0):.1f} "
                          f"({(P.get('total', 0) / P['max'] * 100) if P.get('max') else 0:.0f} %). "
                          f"Tareas completas: {sum(1 for v in P.get('tareas', {}).values() if v.get('ok'))} de "
                          f"{len(P.get('tareas', {}))}.")
        if c["cred"]:
            lineas.append("Credenciales: " + "; ".join(f"{k} {v}" for k, v in c["cred"].items()) + ".")
        for ln in lineas:
            ws.cell(row=f, column=1, value=ln).font = E["normal"]
            f += 1
        f += 1
    ws.cell(row=f, column=1, value="Corridas").font = E["seccion"]
    f += 1
    cols = [("Corrida", 18), ("Inicio", 17), ("Fin previsto", 17), ("Estado", 34), ("Rondas", 9), ("Guardadas", 10),
            ("No guardadas", 11), ("Reflexiones", 11), ("Puntaje al empezar", 11), ("Puntaje actual", 11),
            ("Máximo", 9), ("% del máximo", 10), ("Costo estimado (USD)", 12)]
    encabezado(ws, f, cols, E)
    f += 1
    for c in runs:
        P = c["puntaje"] or {}
        pi = (c["estado"] or {}).get("puntaje_inicial") or {}
        if c["terminada"]:
            est = f"terminada: {c['terminada']}"
        elif c["en_curso"]:
            est = f"en curso (ronda {c['en_curso']['ronda']}: {c['en_curso']['tarea']})"
        else:
            est = "en curso"
        tag = c["tag"]
        valores = [
            (tag, None), (c["inicio"], None), (c["fin_previsto"], None), (est, None),
            (f'=COUNTIFS(Rondas!$A:$A,$A{f},Rondas!$F:$F,"<>reflexión",Rondas!$F:$F,"<>inicio",Rondas!$G:$G,"<>en curso")', "0"),
            (f'=COUNTIFS(Rondas!$A:$A,$A{f},Rondas!$G:$G,"guardada*")', "0"),
            (f"=E{f}-F{f}", "0"),
            (f'=COUNTIFS(Rondas!$A:$A,$A{f},Rondas!$F:$F,"reflexión")', "0"),
            (round(pi.get("total", 0.0), 2) if pi else None, "0.00"),
            (round(P.get("total", 0.0), 2) if P else None, "0.00"),
            (round(P.get("max", 0.0), 2) if P else None, "0.00"),
            (f"=IFERROR(J{f}/K{f},0)", "0%"),
            (f"=SUMIFS(Rondas!$M:$M,Rondas!$A:$A,$A{f})", "#,##0.00"),
        ]
        for j, (v, fmt) in enumerate(valores, start=1):
            celda(ws, f, j, v, E, fmt=fmt, envolver=j == 4)
        f += 1
    f += 1
    ws.cell(row=f, column=1, value="Cómo leer este Excel").font = E["seccion"]
    f += 1
    guia = [
        ("Rondas", "Una fila por ronda: la tarea, si se guardó (el puntaje subió sin romper nada) o se descartó, "
                   "qué hizo el agente, qué aprendió y qué dejó para decidir."),
        ("Tareas", "Puntaje y estado de cada paquete de datos y de cada research, con los checks que le faltan."),
        ("Fuentes", "Los NASA Data & Resources del desafío: cuáles usa el loop, cuáles esperan una credencial y "
                    "cuáles no se usan (y por qué)."),
        ("Decisiones", "Lo que los agentes proponen y necesita el visto bueno del humano."),
        ("Datos", "Los CSV entregados (filas, tamaño, si van a git) y lo bajado por paquete frente al límite de 5 GB."),
        ("Colores", "Verde: guardada o completa. Rojo: descartada. Amarillo: esperando o en pausa. Naranja: "
                    "bloqueada por una credencial. Lila: reflexión. Celeste: en curso."),
        ("Costo", "Lo estima Claude Code por ronda; con una suscripción se descuenta del límite de uso."),
    ]
    for k, v in guia:
        celda(ws, f, 1, k, E, negrita=True)
        ws.merge_cells(start_row=f, start_column=2, end_row=f, end_column=13)
        c = ws.cell(row=f, column=2, value=v)
        c.font, c.alignment = E["normal"], E["envolver"]
        ws.row_dimensions[f].height = 28
        f += 1
    return ws


# --------------------------------------------------------------------------- armado

def armar(repo: Path) -> Path:
    from openpyxl import Workbook
    E = _estilos()
    ahora = dt.datetime.now()
    runs = corridas(repo)
    ent, res = cargar_spec(repo)
    cache_p = repo / CACHE_REL
    cache = leer_json(cache_p) or {}
    wb = Workbook()
    hoja_resumen(wb, runs, E, ahora)
    hoja_rondas(wb, runs, E)
    hoja_tareas(wb, runs, ent, res, E)
    hoja_fuentes(wb, runs, repo, E)
    hoja_decisiones(wb, repo, E)
    hoja_datos(wb, repo, ent, E, cache)
    for ws in wb.worksheets:
        ws.sheet_properties.tabColor = COLOR["encabezado"]
    wb.calculation.fullCalcOnLoad = True
    wb.properties.title = "Field Shift · registro del research agent"
    salida = repo / SALIDA_REL
    salida.parent.mkdir(parents=True, exist_ok=True)
    tmp = salida.with_name(salida.stem + ".tmp.xlsx")
    wb.save(tmp)
    try:
        cache_p.write_text(json.dumps(cache), encoding="utf-8")
    except OSError:
        pass
    try:
        os.replace(tmp, salida)
    except PermissionError:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise
    return salida


def firma(repo: Path):
    """Lo que cambia cuando hay algo nuevo que mostrar."""
    partes = []
    for p in [repo / "loop" / "notes" / "decisiones.md", repo / "manifest.csv"]:
        try:
            st = p.stat()
            partes.append((str(p), st.st_mtime_ns, st.st_size))
        except OSError:
            pass
    base = repo / "loop" / "runs"
    if base.exists():
        for d in base.iterdir():
            if not d.is_dir():
                continue
            for nombre in ("results.tsv", "state.json", "run.log"):
                try:
                    st = (d / nombre).stat()
                    partes.append((str(d / nombre), st.st_mtime_ns, st.st_size))
                except OSError:
                    pass
            partes.append((str(d), len(list(d.glob("r*.prompt.md")))))
    return tuple(partes)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Excel de seguimiento del research agent (loop/runs/registro_rondas.xlsx).")
    ap.add_argument("--repo", default=str(REPO_DEF), help="raíz del repo (por defecto, la de este archivo)")
    ap.add_argument("--watch", action="store_true", help="quedarse mirando y actualizar cuando cambia algo")
    ap.add_argument("--cada", type=int, default=60, help="segundos entre revisiones con --watch (por defecto 60)")
    ap.add_argument("--hasta", default="", help="con --watch: hora de corte AAAA-MM-DD HH:MM (por defecto, nunca)")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    if not a.watch:
        try:
            p = armar(repo)
        except PermissionError:
            print("El Excel está abierto (o bloqueado): quedó la versión anterior. Cerralo y volvé a correr.",
                  file=sys.stderr)
            return 3
        print(f"Registro actualizado: {p}")
        return 0
    corte = dt.datetime.fromisoformat(a.hasta) if a.hasta else None
    ultima, pendiente = None, False
    while True:
        if corte and dt.datetime.now() >= corte:
            return 0
        f = firma(repo)
        if f != ultima or pendiente:
            try:
                p = armar(repo)
                print(f"[{dt.datetime.now():%H:%M}] actualizado: {p.name}", flush=True)
                ultima, pendiente = f, False
            except PermissionError:
                if not pendiente:
                    print(f"[{dt.datetime.now():%H:%M}] el Excel está abierto: reintento en {a.cada} s", flush=True)
                ultima, pendiente = f, True
            except Exception as e:  # que una lectura a medio escribir no corte el --watch
                print(f"[{dt.datetime.now():%H:%M}] no pude actualizar: {type(e).__name__}: {e}", flush=True)
                ultima, pendiente = f, True
        time.sleep(max(10, a.cada))


if __name__ == "__main__":
    sys.exit(main())
