"""Numbers for the demo user stories (docs/demo/user_story.md), read straight from the release zips.

Lee los zips publicados en los Releases (sin descomprimir a disco) y reemplaza, en `user_story.md`, lo que
está entre los marcadores `<!-- tabla:<id> -->` y `<!-- /tabla:<id> -->` por una tabla con los números de
cada historia. El texto de la historia no lleva números escritos a mano: todos salen de estas tablas.

Antes, bajá los zips (y su .sha256) a data/demo_zips/<release>/ (data/ no va en git), por ejemplo:
  S=$(git remote get-url origin | sed -E 's#.*github.com[:/]##; s#\\.git$##')
  for p in clima cultivos vegetacion; do for e in zip zip.sha256; do
    curl -fL -o data/demo_zips/datos-oh-ne-mn/datos-oh-ne-mn_$p.$e \\
      https://github.com/$S/releases/download/datos-oh-ne-mn/datos-oh-ne-mn_$p.$e; done; done
El script controla el .sha256 de cada zip y corta si no coincide.

Uso:
  .venv/bin/python -I -X utf8 docs/demo/user_story.py                 # actualiza user_story.md
  .venv/bin/python -I -X utf8 docs/demo/user_story.py --imprimir      # solo muestra las tablas
  .venv/bin/python -I -X utf8 docs/demo/user_story.py --zips DIR
"""
from __future__ import annotations

import argparse
import hashlib
import io
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
ZIPS = REPO / "data" / "demo_zips"
HISTORIA = Path(__file__).resolve().parent / "user_story.md"

# Cada historia: un condado, el año del evento y los años con los que se compara.
HISTORIAS = [
    {"id": "boyd", "fips": "31015", "anios": [2011, 2012, 2013]},
    {"id": "defiance", "fips": "39039", "anios": [2018, 2019, 2020]},
    {"id": "butler", "fips": "39017", "anios": [2011, 2012, 2013]},
]

# (archivo, columna, etiqueta en inglés, decimales); en produccion_anual se filtra por cultivo.
FILAS = [
    ("produccion_anual", ("maiz", "rend_bu_ac"), "Corn yield (bu/ac) — NASS", 1),
    ("produccion_anual", ("soja", "rend_bu_ac"), "Soybean yield (bu/ac) — NASS", 1),
    ("produccion_anual", ("maiz", "sup_sembrada_ac"), "Corn planted (ac) — NASS", 0),
    ("produccion_anual", ("soja", "sup_sembrada_ac"), "Soybean planted (ac) — NASS", 0),
    ("produccion_anual", ("maiz", "ratio_cosechada"), "Corn harvested for grain / planted — NASS", 2),
    ("clima_anual", "prec_temporada_mm", "Growing-season rain, Apr–Sep (mm) — POWER", 0),
    ("clima_anual", "prec_jul_mm", "July rain (mm) — POWER", 0),
    ("clima_anual", "tmax_jul_c", "July mean Tmax (°C) — POWER", 1),
    ("clima_mensual", ("05", "spi3"), "SPI-3 ending May (Mar–May) — POWER", 2),
    ("clima_mensual", ("07", "spi3"), "SPI-3 ending July (May–Jul) — POWER", 2),
    ("fenologia_anual", "ndvi_max", "Peak NDVI, all cropland — MODIS", 3),
    ("fenologia_anual", "ndvi_max_maiz", "Peak NDVI, corn pixels — MODIS + CDL", 3),
    ("fenologia_anual", "ndvi_max_soja", "Peak NDVI, soybean pixels — MODIS + CDL", 3),
    ("rotacion_anual", "pct_maiz", "Cropland in corn (%) — CDL", 1),
    ("rotacion_anual", "pct_barbecho", "Cropland in fallow/idle (%) — CDL", 1),
    ("rotacion_anual", "pct_maiz_tras_soja", "Corn pixels that were soybean the year before (%) — CDL", 1),
    ("rotacion_anual", "pct_maiz_tras_maiz", "Corn pixels that were corn the year before (%) — CDL", 1),
]
PAQUETE = {"produccion_anual": "cultivos", "rotacion_anual": "cultivos", "practicas_censo": "cultivos",
           "fenologia_estado": "cultivos", "clima_anual": "clima", "clima_mensual": "clima",
           "fenologia_anual": "vegetacion"}
FIPS_ESTADO = {"19": "IA", "17": "IL", "18": "IN", "39": "OH", "31": "NE", "27": "MN", "20": "KS"}


def sha256_ok(z: Path) -> bool:
    f = z.with_name(z.name + ".sha256")
    if not f.exists():
        sys.exit(f"falta {f.name}: bajalo del release para controlar {z.name}")
    h = hashlib.sha256()
    with z.open("rb") as fh:
        for bloque in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest() == f.read_text().split()[0].strip().lower()


def cargar(zips: Path) -> tuple[dict[str, pd.DataFrame], pd.DataFrame, list[str]]:
    """Une cada CSV de todos los zips de todos los releases bajo `zips`."""
    tablas: dict[str, list[pd.DataFrame]] = {}
    condados, origen = [], []
    for z in sorted(zips.rglob("*.zip")):
        if not sha256_ok(z):
            sys.exit(f"{z.name}: el sha256 NO coincide; volvé a bajarlo")
        origen.append(z.name)
        with zipfile.ZipFile(z) as zf:
            for n in zf.namelist():
                nombre = Path(n).stem
                if n.startswith("data/processed/") and nombre in PAQUETE:
                    tablas.setdefault(nombre, []).append(
                        pd.read_csv(io.BytesIO(zf.read(n)), dtype={"fips": str, "fips_estado": str}))
                elif n == "data/reference/condados.csv":
                    condados.append(pd.read_csv(io.BytesIO(zf.read(n)), dtype={"fips": str}))
    if not origen:
        sys.exit(f"no hay zips bajo {zips}; ver el docstring para bajarlos")
    unidas = {k: pd.concat(v, ignore_index=True).drop_duplicates() for k, v in tablas.items()}
    return unidas, pd.concat(condados).drop_duplicates("fips"), origen


def valor(t: dict[str, pd.DataFrame], archivo: str, col, fips: str, anio: int):
    df = t.get(archivo)
    if df is None:
        return None
    df = df[(df["fips"] == fips) & (df["anio"] == anio)]
    if archivo == "produccion_anual":
        df, col = df[df["cultivo"] == col[0]], col[1]
    elif archivo == "clima_mensual":
        df, col = df[df["mes"] == f"{anio}-{col[0]}"], col[1]
    if df.empty or col not in df or pd.isna(df[col].iloc[0]):
        return None
    return float(df[col].iloc[0])


def fmt(v, dec: int) -> str:
    return "n/a" if v is None else f"{v:,.{dec}f}"


def tabla(t, cond, h) -> str:
    fips, anios = h["fips"], h["anios"]
    fila = cond[cond["fips"] == fips]
    nombre = f"{fila['condado'].iloc[0]} County, {fila['estado'].iloc[0]}" if not fila.empty else fips
    lineas = [f"**{nombre}** (FIPS {fips})", "",
              "| Variable — source | " + " | ".join(str(a) for a in anios) + " |",
              "|---|" + "---:|" * len(anios)]
    for archivo, col, etiqueta, dec in FILAS:
        lineas.append(f"| {etiqueta} | " + " | ".join(fmt(valor(t, archivo, col, fips, a), dec) for a in anios) + " |")

    # Contexto que no es por año del evento: riego del Censo y fechas de siembra del estado.
    extra = []
    censo = t.get("practicas_censo")
    if censo is not None:
        c = censo[censo["fips"] == fips].sort_values("anio_censo")
        if not c.empty:
            extra.append("Irrigated share of cropland, Census of Agriculture (`pct_riego`): "
                         + ", ".join(f"{int(r.anio_censo)}: {fmt(r.pct_riego, 1)} %" for r in c.itertuples()))
    fe = t.get("fenologia_estado")
    if fe is not None:
        e = fe[(fe["fips_estado"] == fips[:2]) & fe["anio"].isin(anios)]
        partes = []
        for cultivo, en in (("maiz", "corn"), ("soja", "soybean")):
            s = e[e["cultivo"] == cultivo].set_index("anio")["doy_50_sembrado"]
            partes.append(f"{en} " + ", ".join(f"{a}: {fmt(s.get(a), 0)}" for a in anios))
        extra.append(f"Day of year when 50 % of the crop was planted, statewide ({FIPS_ESTADO.get(fips[:2], fips[:2])},"
                     " NASS Crop Progress): " + "; ".join(partes))
    if extra:
        lineas += [""] + [f"- {x}" for x in extra]
    return "\n".join(lineas)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zips", type=Path, default=ZIPS)
    ap.add_argument("--imprimir", action="store_true", help="solo imprime las tablas, no toca user_story.md")
    a = ap.parse_args()

    t, cond, origen = cargar(a.zips)
    print("zips leídos (sha256 ok): " + ", ".join(origen))
    tablas = {h["id"]: tabla(t, cond, h) for h in HISTORIAS}
    if a.imprimir:
        print("\n\n".join(tablas.values()))
        return
    texto = HISTORIA.read_text(encoding="utf-8")
    for k, v in tablas.items():
        patron = re.compile(rf"(<!-- tabla:{k} -->\n).*?(\n<!-- /tabla:{k} -->)", re.S)
        if not patron.search(texto):
            sys.exit(f"user_story.md no tiene los marcadores de la tabla {k}")
        texto = patron.sub(lambda m: m.group(1) + v + m.group(2), texto)
    texto = re.sub(r"(<!-- zips -->).*?(<!-- /zips -->)",
                   lambda m: m.group(1) + ", ".join(f"`{z}`" for z in origen) + m.group(2), texto, flags=re.S)
    HISTORIA.write_text(texto, encoding="utf-8")
    print(f"actualizado {HISTORIA.relative_to(REPO)}")


if __name__ == "__main__":
    main()
