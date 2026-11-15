"""Cobertura de los datos publicados en los Releases, para `docs/demo/coverage.md` (página en inglés).

Lista los releases del repo con la API pública de GitHub (sin login), baja los zips que falten a
`data/coverage_zips/<release>/` (data/ no va en git), controla cada `.sha256` y cuenta, leyendo los zips sin
descomprimir a disco: estados, condados, años, paquetes, filas y columnas de cada CSV procesado y tamaño de
cada zip. El resultado reemplaza lo que está entre las marcas `<!-- coverage:start -->` y
`<!-- coverage:end -->` de `coverage.md`; el resto de la página se escribe a mano.

Dueño y repo salen de `git remote get-url origin`: no se escriben en ningún archivo.
Los releases esperados que todavía no existen se listan como "in progress", sin números.

Uso:
  .venv/bin/python -X utf8 docs/demo/coverage.py              # baja lo que falte y actualiza coverage.md
  .venv/bin/python -X utf8 docs/demo/coverage.py --sin-bajar  # solo usa los zips que ya están
  .venv/bin/python -X utf8 docs/demo/coverage.py --imprimir   # muestra la sección, sin tocar coverage.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
ZIPS = REPO / "data" / "coverage_zips"
PAGINA = Path(__file__).resolve().parent / "coverage.md"
INICIO, FIN = "<!-- coverage:start -->", "<!-- coverage:end -->"

# Releases que se esperan para la entrega (CLAUDE.md §2 y §6.6, coordinacion/maquinas.yaml).
ESPERADOS = {
    "datos-ia-il-in": "Iowa, Illinois, Indiana (first batch)",
    "datos-oh-ne-mn": "Ohio, Nebraska, Minnesota",
    "datos-ks": "Kansas",
    "datos-mo-wi-sd": "Missouri, Wisconsin, South Dakota",
    "fieldshift_lotes_v1": "10 demonstration fields, per 30 m pixel (CLAUDE.md §6.6)",
}
FIPS_ESTADO = {"19": "IA", "17": "IL", "18": "IN", "39": "OH", "31": "NE", "27": "MN", "20": "KS",
               "29": "MO", "55": "WI", "46": "SD"}


def repo_slug() -> str:
    url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=REPO, capture_output=True, text=True,
                         check=True).stdout.strip()
    m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    if not m:
        sys.exit("origin no es un repo de GitHub")
    return m.group(1)


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "fieldshift-coverage"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def bajar(slug: str, release: dict, sin_bajar: bool) -> list[Path]:
    """Zips del release en data/coverage_zips/<tag>/, con el .sha256 controlado."""
    tag = release["tag_name"]
    carpeta = ZIPS / tag
    carpeta.mkdir(parents=True, exist_ok=True)
    zips = []
    for a in release["assets"]:
        nombre = a["name"]
        if not nombre.endswith(".zip"):
            continue
        destino = carpeta / nombre
        base = f"https://github.com/{slug}/releases/download/{tag}/"
        if not destino.exists() or destino.stat().st_size != a["size"]:
            if sin_bajar:
                print(f"AVISO: falta {destino.relative_to(REPO)}; se saltea", file=sys.stderr)
                continue
            print(f"bajando {tag}/{nombre} ({a['size'] / 1e6:.1f} MB)", file=sys.stderr)
            destino.write_bytes(get(base + nombre))
        suma = carpeta / (nombre + ".sha256")
        if not suma.exists() and not sin_bajar:
            suma.write_bytes(get(base + nombre + ".sha256"))
        if not suma.exists():
            sys.exit(f"{nombre}: sin .sha256, no se usa")
        esperado = suma.read_text().split()[0].lower()
        if sha256(destino) != esperado:
            sys.exit(f"{nombre}: el sha256 no coincide")
        zips.append(destino)
    return zips


def contar_csv(z: zipfile.ZipFile, nombre: str) -> dict:
    with z.open(nombre) as f:
        cols = pd.read_csv(f, nrows=0).columns.tolist()
    col_geo = next((c for c in ("fips", "fips_estado") if c in cols), None)
    col_anio = next((c for c in ("anio", "anio_censo") if c in cols), None)
    col_ventana = "ventana" if "ventana" in cols else None   # rotacion_secuencia: "2008-2015"
    usar = [c for c in (col_geo, col_anio, col_ventana) if c]
    with z.open(nombre) as f:
        df = pd.read_csv(f, usecols=usar or [cols[0]], dtype=str, keep_default_na=False)
    anios = pd.to_numeric(df[col_anio], errors="coerce").dropna().astype(int) if col_anio else pd.Series([], dtype=int)
    geo = df[col_geo][df[col_geo] != ""] if col_geo else pd.Series([], dtype=str)
    return {
        "archivo": nombre.rsplit("/", 1)[-1],
        "filas": len(df),
        "columnas": len(cols),
        "unidad": col_geo or "",
        "n_geo": geo.nunique(),
        "anios": (anios.min(), anios.max(), anios.nunique()) if len(anios) else None,
        "fips": set(geo) if col_geo == "fips" else set(),
        "ventanas": sorted(set(df[col_ventana]) - {""}) if col_ventana else [],
    }


def resumir(zips: list[Path]) -> dict:
    paquetes, fips, anios, tam = {}, set(), set(), 0
    for p in sorted(zips):
        tam += p.stat().st_size
        with zipfile.ZipFile(p) as z:
            csvs = sorted(n for n in z.namelist() if n.startswith("data/processed/") and n.endswith(".csv"))
            filas = [contar_csv(z, n) for n in csvs]
        paquete = csvs[0].split("/")[2] if csvs else p.stem
        paquetes[paquete] = {"zip": p.name, "mb": p.stat().st_size / 1e6, "csv": filas}
        for f in filas:
            fips |= f["fips"]
            if f["anios"]:
                anios |= set(range(f["anios"][0], f["anios"][1] + 1)) if f["unidad"] == "fips" else set()
    por_estado = {}
    for f in fips:
        e = FIPS_ESTADO.get(f[:2], f[:2])
        por_estado[e] = por_estado.get(e, 0) + 1
    estados = [f"{e} ({n})" for e, n in sorted(por_estado.items())]
    return {"paquetes": paquetes, "fips": fips, "estados": estados, "anios": anios, "mb": tam / 1e6}


def rango(a) -> str:
    if not a:
        return ""
    return f"{a[0]}" if a[0] == a[1] else f"{a[0]}–{a[1]} ({a[2]} years)"


def años(f: dict) -> str:
    if f["ventanas"]:
        v = f["ventanas"]
        return f"{len(v)} 8-year windows, {v[0]} to {v[-1]}"
    return rango(f["anios"])


def seccion(slug: str, releases: list[dict], resumenes: dict) -> str:
    hoy = date.today().isoformat()
    lin = [INICIO, "",
           f"*Generated by `docs/demo/coverage.py` on {hoy} from the public GitHub Releases of this repository. "
           "Every number below is counted from the published zips (SHA-256 checked); none is typed by hand.*", "",
           "### Releases at a glance", "",
           "| Release | States (counties) | Counties | Years (county files) | Packages | Zips (MB) | Published | Status |",
           "|---|---|---|---|---|---|---|---|"]
    por_tag = {r["tag_name"]: r for r in releases}
    for tag in list(ESPERADOS) + sorted(t for t in por_tag if t not in ESPERADOS):
        if tag in resumenes:
            s = resumenes[tag]
            a = sorted(s["anios"])
            lin.append(f"| `{tag}` | {', '.join(s['estados'])} | {len(s['fips'])} | "
                       f"{f'{a[0]}–{a[-1]}' if a else ''} | {len(s['paquetes'])} | {s['mb']:.1f} | "
                       f"{por_tag[tag]['published_at'][:10]} | published |")
        else:
            lin.append(f"| `{tag}` | {ESPERADOS.get(tag, '')} | | | | | | in progress |")
    for tag, s in resumenes.items():
        lin += ["", f"### `{tag}`: rows per file", "",
                "| Package | File | Rows | Columns | Spatial unit | Units | Years |",
                "|---|---|---|---|---|---|---|"]
        for paquete, d in s["paquetes"].items():
            for f in d["csv"]:
                lin.append(f"| `{paquete}` ({d['mb']:.1f} MB zip) | `{f['archivo']}` | {f['filas']:,} | "
                           f"{f['columnas']} | {f['unidad'] or '—'} | {f['n_geo'] or ''} | {años(f)} |")
    lin += ["", FIN]
    return "\n".join(lin)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sin-bajar", action="store_true", help="no baja nada; usa los zips que ya están")
    ap.add_argument("--imprimir", action="store_true", help="muestra la sección sin tocar coverage.md")
    args = ap.parse_args()

    slug = repo_slug()
    releases = json.loads(get(f"https://api.github.com/repos/{slug}/releases?per_page=100"))
    releases = [r for r in releases if not r["draft"]]
    resumenes = {}
    for r in releases:
        zips = bajar(slug, r, args.sin_bajar)
        if zips:
            resumenes[r["tag_name"]] = resumir(zips)
    texto = seccion(slug, releases, resumenes)
    if args.imprimir:
        print(texto)
        return
    pagina = PAGINA.read_text(encoding="utf-8")
    if INICIO not in pagina or FIN not in pagina:
        sys.exit(f"{PAGINA.name}: faltan las marcas {INICIO} / {FIN}")
    antes, resto = pagina.split(INICIO, 1)
    despues = resto.split(FIN, 1)[1]
    PAGINA.write_text(antes + texto + despues, encoding="utf-8")
    print(f"actualizado {PAGINA.relative_to(REPO)}", file=sys.stderr)


if __name__ == "__main__":
    main()
