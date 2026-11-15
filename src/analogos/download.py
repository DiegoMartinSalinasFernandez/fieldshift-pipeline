"""Análogos climáticos Argentina ↔ Corn Belt: descarga.

- Departamentos de Argentina con su código INDEC y centroide, de la API Georef del Estado argentino
  (apis.datos.gob.ar). Quedan en data/raw/analogos/georef_departamentos.json.
- NASA POWER mensual (comunidad AG) en el centroide de cada departamento y de cada condado del Corn Belt
  (data/reference/condados_cornbelt_10.csv). Es la misma fuente y el mismo período en los dos lados.
  Va un JSON por punto en data/raw/analogos/power/<id>.json. Si el archivo ya está, no se vuelve a bajar.

- `diario`: NASA POWER diario (AG, los mismos 10 parámetros que el paquete clima, 1981 a 2025) en el centroide de
  los departamentos de Buenos Aires: data/raw/analogos/power_diario/ar_<id>.csv.
- `suelo`: SoilGrids v2.0 (ISRIC), versión agregada a 1 km (data_aggregated/1000m, proyección Homolosine
  ESRI:54052). Arcilla, arena, carbono orgánico y pH en agua de 0-5, 5-15 y 15-30 cm. Se lee solo la ventana
  de cada región (pampa y Corn Belt) del GeoTIFF oficial, sin cambiar valores, y se guarda como GeoTIFF en
  data/raw/analogos/soilgrids/. Además, los polígonos: departamentos de Georef (departamentos.geojson) y
  condados del Census (Cartographic Boundary 1:500k, 2023).
- `rendimiento`: estimaciones agrícolas por departamento del MAGyP (datos.magyp.gob.ar), el CSV consolidado.

Cada archivo bajado suma una fila a manifest.csv.

Uso: python src/analogos/download.py [mensual|diario|suelo|rendimiento|todo]   (sin argumento: mensual)
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw" / "analogos"
POWER_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"
GEOREF_URL = "https://apis.datos.gob.ar/georef/api/departamentos"
PARAMS = "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,ALLSKY_SFC_SW_DWN,RH2M"
INICIO, FIN = 2001, 2024  # años completos en POWER mensual
MANIFEST = RAIZ / "manifest.csv"
CAMPOS = ["paquete", "archivo", "fuente", "producto", "version", "fecha_descarga", "consulta_o_url"]


def manifest(filas: list[list[str]]) -> None:
    nuevo = not MANIFEST.exists()
    with open(MANIFEST, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if nuevo:
            w.writerow(CAMPOS)
        w.writerows(filas)


def georef() -> list[dict]:
    p = RAW / "georef_departamentos.json"
    if not p.exists():
        q = {"max": 5000, "campos": "id,nombre,provincia.id,provincia.nombre,centroide"}
        r = requests.get(GEOREF_URL, params=q, timeout=120)
        r.raise_for_status()
        RAW.mkdir(parents=True, exist_ok=True)
        p.write_text(r.text, encoding="utf-8")
        manifest([["analogos", p.relative_to(RAIZ).as_posix(), "Georef (datos.gob.ar)", "departamentos", "API v2",
                    dt.date.today().isoformat(), r.url]])
    return json.loads(p.read_text(encoding="utf-8"))["departamentos"]


def bajar_punto(pid: str, lat: float, lon: float) -> list[str] | None:
    p = RAW / "power" / f"{pid}.json"
    if p.exists():
        return None
    q = {"parameters": PARAMS, "community": "AG", "latitude": round(lat, 4), "longitude": round(lon, 4),
         "start": INICIO, "end": FIN, "format": "JSON"}
    for intento in range(5):
        try:
            r = requests.get(POWER_URL, params=q, timeout=180)
            if r.status_code == 200:
                j = r.json()
                p.write_text(json.dumps(j), encoding="utf-8")
                version = j.get("header", {}).get("api", {}).get("version", "")
                return ["analogos", p.relative_to(RAIZ).as_posix(), "NASA POWER", "monthly point (AG)", version,
                        dt.date.today().isoformat(), r.url]
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(10 * (intento + 1))
                continue
            print(f"{pid}: HTTP {r.status_code}", file=sys.stderr)
            return None
        except requests.RequestException as e:
            print(f"{pid}: {e}", file=sys.stderr)
            time.sleep(10 * (intento + 1))
    print(f"{pid}: falló después de 5 intentos", file=sys.stderr)
    return None


def mensual() -> int:
    (RAW / "power").mkdir(parents=True, exist_ok=True)
    puntos = [(f"ar_{d['id']}", d["centroide"]["lat"], d["centroide"]["lon"]) for d in georef()]
    with open(RAIZ / "data" / "reference" / "condados_cornbelt_10.csv", encoding="utf-8", newline="") as f:
        puntos += [(f"us_{r['fips']}", float(r["lat_centroide"]), float(r["lon_centroide"])) for r in csv.DictReader(f)]
    print(f"{len(puntos)} puntos")
    filas, hechos = [], 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for fila in ex.map(lambda t: bajar_punto(*t), puntos):
            hechos += 1
            if fila:
                filas.append(fila)
            if len(filas) >= 50:
                manifest(filas)
                filas = []
            if hechos % 100 == 0:
                print(f"  {hechos}/{len(puntos)}", flush=True)
    manifest(filas)
    faltan = [pid for pid, _, _ in puntos if not (RAW / "power" / f"{pid}.json").exists()]
    print(f"listo; faltan {len(faltan)}: {faltan[:10]}")
    return 1 if faltan else 0


# --------------------------------------------------------------------------- POWER diario (Buenos Aires)

POWER_DIARIO_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS_DIARIO = "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN,GWETTOP,GWETROOT,GWETPROF"
DIARIO_INI, DIARIO_FIN = "19810101", "20251231"
PROVINCIAS_DIARIO = ("06",)  # Buenos Aires


def bajar_diario(pid: str, lat: float, lon: float) -> list[str] | None:
    p = RAW / "power_diario" / f"{pid}.csv"
    if p.exists():
        return None
    q = {"parameters": PARAMS_DIARIO, "community": "AG", "latitude": f"{lat:.5f}", "longitude": f"{lon:.5f}",
         "start": DIARIO_INI, "end": DIARIO_FIN, "format": "CSV"}
    ultimo = f"{DIARIO_FIN[:4]},365,"
    for intento in range(5):
        try:
            r = requests.get(POWER_DIARIO_URL, params=q, timeout=300)
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(15 * (intento + 1))
                continue
            r.raise_for_status()
            if "-END HEADER-" not in r.text or ultimo not in r.text:
                raise ValueError("respuesta incompleta")
            part = p.with_suffix(".part")
            part.write_text(r.text, encoding="utf-8")
            part.replace(p)
            v = (r.headers.get("x-app-version") or "").strip()
            return ["analogos", p.relative_to(RAIZ).as_posix(), "NASA POWER", "daily point (AG)",
                    f"POWER API {v}" if v else "", dt.date.today().isoformat(), r.url]
        except (requests.RequestException, ValueError) as e:
            print(f"{pid}: {e}", file=sys.stderr)
            time.sleep(15 * (intento + 1))
    print(f"{pid}: falló después de 5 intentos", file=sys.stderr)
    return None


def diario() -> int:
    (RAW / "power_diario").mkdir(parents=True, exist_ok=True)
    puntos = [(f"ar_{d['id']}", d["centroide"]["lat"], d["centroide"]["lon"]) for d in georef()
              if d["provincia"]["id"] in PROVINCIAS_DIARIO]
    print(f"{len(puntos)} departamentos")
    filas = []
    with ThreadPoolExecutor(max_workers=3) as ex:
        for i, fila in enumerate(ex.map(lambda t: bajar_diario(*t), puntos), 1):
            if fila:
                filas.append(fila)
            if i % 20 == 0:
                manifest(filas)
                filas = []
                print(f"  {i}/{len(puntos)}", flush=True)
    manifest(filas)
    faltan = [pid for pid, _, _ in puntos if not (RAW / "power_diario" / f"{pid}.csv").exists()]
    print(f"listo; faltan {len(faltan)}: {faltan[:10]}")
    return 1 if faltan else 0


# --------------------------------------------------------------------------- SoilGrids y polígonos

SG_URL = "https://files.isric.org/soilgrids/latest/data_aggregated/1000m/{p}/{p}_{d}_mean_1000.tif"
SG_PROPS = ("clay", "sand", "soc", "phh2o")
SG_PROF = ("0-5cm", "5-15cm", "15-30cm")
# ventanas en grados (lon_min, lat_min, lon_max, lat_max), con margen
SG_REGIONES = {"pampa": (-68.5, -42.5, -56.0, -26.0), "cornbelt": (-105.5, 35.5, -79.5, 50.0)}
GEOREF_GEOJSON = "https://infra.datos.gob.ar/georef/departamentos.geojson"
CENSUS_ZIP = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip"


def bajar_archivo(url: str, p: Path, producto: str, fuente: str, version: str = "") -> None:
    if p.exists():
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=600, headers={"User-Agent": "Mozilla/5.0 (fieldshift-research)"})
    r.raise_for_status()
    part = p.with_suffix(p.suffix + ".part")
    part.write_bytes(r.content)
    part.replace(p)
    manifest([["analogos", p.relative_to(RAIZ).as_posix(), fuente, producto, version, dt.date.today().isoformat(), url]])


def suelo() -> int:
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    bajar_archivo(GEOREF_GEOJSON, RAW / "poligonos" / "departamentos.geojson", "departamentos (geojson)",
                  "Georef (datos.gob.ar)")
    bajar_archivo(CENSUS_ZIP, RAW / "poligonos" / "cb_2023_us_county_500k.zip", "Cartographic Boundary counties 1:500k",
                  "US Census Bureau", "2023")
    d = RAW / "soilgrids"
    d.mkdir(parents=True, exist_ok=True)
    env = {"GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR", "GDAL_HTTP_MAX_RETRY": "5", "GDAL_HTTP_RETRY_DELAY": "5"}
    filas = []
    with rasterio.Env(**env):
        for prop in SG_PROPS:
            for prof in SG_PROF:
                url = SG_URL.format(p=prop, d=prof)
                for reg, bb in SG_REGIONES.items():
                    p = d / f"{prop}_{prof}_mean_1000_{reg}.tif"
                    if p.exists():
                        continue
                    with rasterio.open("/vsicurl/" + url) as src:
                        b = transform_bounds("EPSG:4326", src.crs, *bb, densify_pts=100)
                        w = from_bounds(*b, transform=src.transform).round_offsets().round_lengths()
                        a = src.read(1, window=w)
                        perfil = src.profile.copy()
                        perfil.update(width=a.shape[1], height=a.shape[0], transform=src.window_transform(w),
                                      compress="deflate", tiled=True, blockxsize=256, blockysize=256)
                    part = p.with_name(p.stem + "_part.tif")
                    with rasterio.open(part, "w", **perfil) as dst:
                        dst.write(a, 1)
                    part.replace(p)
                    filas.append(["analogos", p.relative_to(RAIZ).as_posix(), "ISRIC SoilGrids",
                                  f"{prop} {prof} mean 1000 m", "v2.0 (data_aggregated)", dt.date.today().isoformat(),
                                  f"{url} ventana {reg} {bb}"])
                    print(p.name, a.shape, flush=True)
    manifest(filas)
    return 0


# --------------------------------------------------------------------------- MAGyP

MAGYP_URL = ("https://datos.magyp.gob.ar/dataset/9e1e77ba-267e-4eaa-a59f-3296e86b5f36/resource/"
             "95d066e6-8a0f-4a80-b59d-6f28f88eacd5/download/estimaciones-agricolas-2026-03.csv")


def rendimiento() -> int:
    bajar_archivo(MAGYP_URL, RAW / "magyp" / "estimaciones-agricolas-2026-03.csv",
                  "Estimaciones agrícolas (consolidado)", "MAGyP (datos.magyp.gob.ar)", "2026-03")
    return 0


def main() -> int:
    que = sys.argv[1] if len(sys.argv) > 1 else "mensual"
    pasos = {"mensual": mensual, "diario": diario, "suelo": suelo, "rendimiento": rendimiento}
    if que == "todo":
        return max(f() for f in pasos.values())
    return pasos[que]()


if __name__ == "__main__":
    sys.exit(main())
