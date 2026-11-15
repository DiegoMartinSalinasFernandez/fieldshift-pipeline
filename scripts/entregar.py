"""Publica los CSV procesados de esta máquina en los Releases de GitHub (los datos no van en git).

Arma un zip por paquete con:
  data/processed/<paquete>/*        los CSV de los estados de esta máquina
  docs/datasets/<paquete>.md        el data card
  data/reference/condados.csv, anios.csv
  manifest.csv                      solo las filas del paquete; si alguna trae una clave
                                    (key=, api_key=, token=...) en la URL, corta sin subir nada
y lo sube al release `datos-<estados>` (por ejemplo `datos-ks` o `datos-oh-ne-mn`), reemplazando la versión
anterior del mismo paquete. Cada zip lleva al lado su .sha256.

Además arma `<etiqueta>_base.zip` (también con su .sha256), con la referencia común a todos los paquetes:
  data/reference/condados.gpkg      polígonos de los condados (EPSG:4326, capa `condados`, de src/base/process.py),
                                    filtrado a los estados del release si trae más
  data/reference/condados.csv       las mismas filas, con centroides y área
  data/reference/anios.csv
  data/reference/cdl_precision.csv  precisión del CDL por estado, año y clase, solo los estados del release
                                    (si existe; la arma src/cultivos/precision_cdl.py)
  README.md                         qué trae el zip
Si falta data/reference/condados.gpkg, avisa y sigue sin el zip de base. Los zips de paquete no cambian.

Las notas del release se reescriben en cada entrega: la lista de paquetes que tiene el release y la declaración
de uso de IA en inglés y en castellano, leída del README.md en ese momento (secciones "## Use of AI" y
"## Uso de IA"), para que no se desincronice. Si algún paquete del release tiene una atribución obligatoria
(Copernicus en `lotes`, CC BY 4.0 de CoCoRaHS en `validacion`), las notas suman la sección "## Attribution /
Atribución" con el texto de `src/common/atribuciones.py`, el mismo que va en el data card.

Uso:
  python scripts/entregar.py                     # todos los paquetes de data/processed/
  python scripts/entregar.py cultivos clima      # solo esos (y el zip de base)
  python scripts/entregar.py base                # solo el zip de base
  python scripts/entregar.py --solo-zip          # arma los zips en data/entregas/ sin subir nada
Los estados salen de FIELDSHIFT_ESTADOS (obligatoria).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.common.atribuciones import seccion_release  # noqa: E402
from src.common.config import estados_elegidos  # noqa: E402

PROC = REPO / "data" / "processed"
SALIDA = REPO / "data" / "entregas"

# Parámetros de URL que suelen llevar credenciales (key=, api_key=, apikey=, token=, access_token=...).
CLAVE_EN_URL = re.compile(r"(?i)(?<![a-z0-9])(api[_-]?key|key|token|access[_-]?token)=")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def manifest_del_paquete(paquete: str) -> str | None:
    """Encabezado y filas de manifest.csv con `paquete == <paquete>`, en el mismo orden (UTF-8, `\\n`).

    Corta con error si alguna de esas filas tiene una clave en `consulta_o_url` (sin mostrar el valor).
    """
    man = REPO / "manifest.csv"
    if not man.exists():
        return None
    with open(man, encoding="utf-8", newline="") as f:
        filas = list(csv.reader(f))
    if not filas:
        return None
    encabezado, cuerpo = filas[0], filas[1:]
    for col in ("paquete", "consulta_o_url"):
        if col not in encabezado:
            sys.exit(f"manifest.csv: falta la columna {col}")
    i_paq, i_url = encabezado.index("paquete"), encabezado.index("consulta_o_url")
    i_arch = encabezado.index("archivo") if "archivo" in encabezado else None
    elegidas = [r for r in cuerpo if len(r) > i_paq and r[i_paq] == paquete]
    for n, r in enumerate(elegidas, 1):
        m = CLAVE_EN_URL.search(r[i_url]) if len(r) > i_url else None
        if m:
            donde = r[i_arch] if i_arch is not None and len(r) > i_arch else f"fila {n} del paquete"
            sys.exit(f"{paquete}: manifest.csv tiene una clave en consulta_o_url ({m.group(1)}=...) en "
                     f"{donde}. Sacala del manifest antes de entregar.")
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(encabezado)
    w.writerows(elegidas)
    return out.getvalue()


def armar_zip(paquete: str, etiqueta: str) -> Path:
    archivos = sorted(p for p in (PROC / paquete).rglob("*") if p.is_file())
    if not archivos:
        sys.exit(f"{paquete}: no hay archivos en data/processed/{paquete}/")
    extras = [REPO / "docs" / "datasets" / f"{paquete}.md", REPO / "data" / "reference" / "condados.csv",
              REPO / "data" / "reference" / "anios.csv"]
    manifest = manifest_del_paquete(paquete)
    SALIDA.mkdir(parents=True, exist_ok=True)
    z = SALIDA / f"{etiqueta}_{paquete}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in archivos + [e for e in extras if e.exists()]:
            zf.write(p, p.relative_to(REPO).as_posix())
        if manifest is not None:
            zf.writestr("manifest.csv", manifest.encode("utf-8"))
    _escribir_sha(z)  # LF: sha256sum -c de Linux rechaza el CR
    print(f"{z.relative_to(REPO)}: {z.stat().st_size / 1e6:.1f} MB, {len(archivos)} archivos de datos")
    return z


BASE = "base"   # nombre del asset de referencia: <etiqueta>_base.zip (no es un paquete de data/processed/)

README_BASE = """# {etiqueta}_base.zip

Reference files shared by every package of the release `{etiqueta}` ({estados}) / Referencia común a todos
los paquetes del release `{etiqueta}` ({estados}).

- `data/reference/condados.gpkg`: county polygons, layer `condados`, EPSG:4326 / polígonos de los condados,
  capa `condados`, EPSG:4326. Columns / columnas: fips, estado, condado, lat_centroide, lon_centroide,
  area_km2, geometry. Source / fuente: U.S. Census Bureau Cartographic Boundary Files 2024, 1:500k
  (`src/base/process.py`).
- `data/reference/condados.csv`: the same counties without geometry / los mismos condados sin geometría
  ({n} counties / condados).
- `data/reference/anios.csv`: season and previous-winter windows per year / ventanas de temporada e invierno
  previo por año.
{precision}
Published with `scripts/entregar.py` (see `MAQUINAS.md`) / publicado con `scripts/entregar.py`.
"""


def _escribir_sha(z: Path) -> None:
    (z.with_suffix(".zip.sha256")).write_text(f"{sha256(z)}  {z.name}\n", encoding="utf-8", newline="\n")


def armar_zip_base(etiqueta: str, estados: list[str]) -> Path | None:
    """`<etiqueta>_base.zip`: condados.gpkg y condados.csv de los estados del release, anios.csv y un README.

    None (con aviso) si falta condados.gpkg o condados.csv: los zips de paquete se entregan igual.
    """
    ref = REPO / "data" / "reference"
    gpkg, ccsv, anios = ref / "condados.gpkg", ref / "condados.csv", ref / "anios.csv"
    faltan = [p.name for p in (gpkg, ccsv) if not p.exists()]
    if faltan:
        print(f"aviso: falta data/reference/{', '.join(faltan)}; no se arma {etiqueta}_{BASE}.zip "
              "(correr src/base/process.py)", file=sys.stderr)
        return None
    import geopandas as gpd
    import pandas as pd

    pedidos = {e.upper() for e in estados}
    g = gpd.read_file(gpkg, layer="condados")
    if "estado" not in g.columns or "fips" not in g.columns:
        sys.exit("data/reference/condados.gpkg: faltan las columnas fips y estado (correr src/base/process.py)")
    if g.crs is None or g.crs.to_epsg() != 4326:
        sys.exit(f"data/reference/condados.gpkg: tiene que estar en EPSG:4326 (está en {g.crs})")
    sin = sorted(pedidos - set(g["estado"]))
    if sin:
        sys.exit(f"data/reference/condados.gpkg no tiene condados de {', '.join(sin)}")
    tabla = pd.read_csv(ccsv, dtype={"fips": str}, keep_default_na=False)
    if "estado" not in tabla.columns:
        sys.exit("data/reference/condados.csv: falta la columna estado")
    SALIDA.mkdir(parents=True, exist_ok=True)
    z = SALIDA / f"{etiqueta}_{BASE}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        if set(g["estado"]) <= pedidos:
            zf.write(gpkg, "data/reference/condados.gpkg")           # ya trae solo estos estados: tal cual
        else:
            tmp = SALIDA / f".{etiqueta}_condados.gpkg"
            tmp.unlink(missing_ok=True)
            g[g["estado"].isin(pedidos)].reset_index(drop=True).to_file(tmp, layer="condados", driver="GPKG")
            zf.write(tmp, "data/reference/condados.gpkg")
            tmp.unlink()
        if set(tabla["estado"]) <= pedidos:
            zf.write(ccsv, "data/reference/condados.csv")
            n = len(tabla)
        else:
            sub = tabla[tabla["estado"].isin(pedidos)]
            zf.writestr("data/reference/condados.csv", sub.to_csv(index=False, lineterminator="\n").encode("utf-8"))
            n = len(sub)
        if anios.exists():
            zf.write(anios, "data/reference/anios.csv")
        precision = ""
        prec = ref / "cdl_precision.csv"
        if prec.exists():                                            # T133: opcional, filtrada a los estados
            tp = pd.read_csv(prec, dtype=str, keep_default_na=False)
            if "estado" not in tp.columns:
                sys.exit("data/reference/cdl_precision.csv: falta la columna estado")
            tp = tp[tp["estado"].isin(pedidos)]
            zf.writestr("data/reference/cdl_precision.csv",
                        tp.to_csv(index=False, lineterminator="\n").encode("utf-8"))
            precision = README_PRECISION.format(n_prec=len(tp))
        zf.writestr("README.md", README_BASE.format(etiqueta=etiqueta, estados=", ".join(estados), n=n,
                                                    precision=precision).encode("utf-8"))
    _escribir_sha(z)
    print(f"{z.relative_to(REPO)}: {z.stat().st_size / 1e6:.1f} MB, {n} condados")
    return z


README_PRECISION = """- `data/reference/cdl_precision.csv`: Cropland Data Layer accuracy (producer's and user's, %) by state, year
  and CDL class, from the NASS accuracy assessments / precisión del CDL (del productor y del usuario, %) por
  estado, año y clase, de las evaluaciones de NASS ({n_prec} rows / filas; `src/cultivos/precision_cdl.py`,
  `docs/datasets/cultivos.md`).
"""


SECCIONES_IA = {"en": "## Use of AI", "es": "## Uso de IA"}
ENLACE_MD = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def seccion_readme(texto: str, titulo: str) -> str:
    """Cuerpo de la sección `titulo` (línea exacta) del README, hasta el siguiente encabezado o `---`.

    Los enlaces de markdown quedan como su texto: los relativos del README no andan en la página del release.
    """
    lineas = texto.splitlines()
    try:
        i = next(n for n, l in enumerate(lineas) if l.strip() == titulo)
    except StopIteration:
        sys.exit(f"README.md: falta la sección '{titulo}' (de ahí sale la declaración de IA del release)")
    cuerpo = []
    for l in lineas[i + 1:]:
        if l.startswith("#") or l.strip() == "---":
            break
        cuerpo.append(l)
    parrafo = " ".join(l.strip() for l in cuerpo if l.strip())
    if not parrafo:
        sys.exit(f"README.md: la sección '{titulo}' está vacía")
    return ENLACE_MD.sub(r"\1", parrafo)


def paquetes_de_assets(etiqueta: str, nombres: list[str]) -> list[str]:
    """Paquetes de un release a partir de los nombres de sus assets (`<etiqueta>_<paquete>.zip`).

    `<etiqueta>_base.zip` no es un paquete: queda afuera (ver `tiene_base`).
    """
    pre = f"{etiqueta}_"
    return sorted({n[len(pre):-len(".zip")] for n in nombres if n.startswith(pre) and n.endswith(".zip")}
                  - {BASE})


def tiene_base(etiqueta: str, nombres: list[str]) -> bool:
    return f"{etiqueta}_{BASE}.zip" in nombres


def notas_release(estados: list[str], paquetes: list[str], readme: str, base: str | None = None) -> str:
    """Notas del release en inglés y castellano: paquetes, atribuciones obligatorias y declaración de uso de IA.

    `base`: nombre del asset `<etiqueta>_base.zip` si el release lo tiene.
    """
    ia_en = seccion_readme(readme, SECCIONES_IA["en"])
    ia_es = seccion_readme(readme, SECCIONES_IA["es"])
    lista = "\n".join(f"- `{p}`" for p in sorted(paquetes)) or "- (none yet / ninguno todavía)"
    est = ", ".join(estados)
    return (f"Processed CSVs by package for {est}, published with `scripts/entregar.py` (see `MAQUINAS.md`).\n"
            f"CSV procesados por paquete de {est}, publicados con `scripts/entregar.py` (ver `MAQUINAS.md`).\n\n"
            f"## Packages / Paquetes\n\n{lista}\n\n"
            + (f"## Reference / Referencia\n\n`{base}`: county polygons (`condados.gpkg`, EPSG:4326), "
               f"`condados.csv` and `anios.csv` / polígonos de los condados, `condados.csv` y `anios.csv`.\n\n"
               if base else "") +
            seccion_release(paquetes) +
            f"## Use of AI\n\n{ia_en}\n\n"
            f"## Uso de IA\n\n{ia_es}\n")


def gh(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], cwd=REPO, capture_output=True, text=True, check=check)


def subir(etiqueta: str, zips: list[Path], estados: list[str]) -> None:
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    notas_release(estados, [], readme)  # corta antes de subir si al README le falta la declaración de IA
    nombres = [z.name for z in zips]
    nuevos = paquetes_de_assets(etiqueta, nombres)
    base = f"{etiqueta}_{BASE}.zip"
    if gh("release", "view", etiqueta, check=False).returncode != 0:
        gh("release", "create", etiqueta, "--title", f"Datos procesados: {', '.join(estados)}",
           "--notes", notas_release(estados, nuevos, readme, base if tiene_base(etiqueta, nombres) else None))
    rutas = [str(p) for z in zips for p in (z, z.with_suffix(".zip.sha256"))]
    r = gh("release", "upload", etiqueta, *rutas, "--clobber", check=False)
    if r.returncode != 0:
        sys.exit(f"gh release upload falló:\n{r.stderr.strip()}")
    print(f"subido al release {etiqueta}: {', '.join(z.name for z in zips)}")
    # Notas al día con todos los paquetes del release (también los de entregas anteriores).
    v = gh("release", "view", etiqueta, "--json", "assets", "--jq", ".assets[].name", check=False)
    assets = v.stdout.split() if v.returncode == 0 else []
    paquetes = paquetes_de_assets(etiqueta, assets)
    con_base = tiene_base(etiqueta, assets) or tiene_base(etiqueta, nombres)
    r = gh("release", "edit", etiqueta, "--notes",
           notas_release(estados, sorted(set(paquetes) | set(nuevos)), readme, base if con_base else None),
           check=False)
    if r.returncode != 0:
        print(f"aviso: no se pudieron actualizar las notas del release:\n{r.stderr.strip()}", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paquetes", nargs="*")
    ap.add_argument("--solo-zip", action="store_true")
    a = ap.parse_args()
    estados = estados_elegidos()
    if not estados:
        sys.exit("Definí FIELDSHIFT_ESTADOS con los estados de esta máquina (por ejemplo KS o OH,NE,MN).")
    etiqueta = "datos-" + "-".join(s.lower() for s in estados)
    paquetes = a.paquetes or sorted(p.name for p in PROC.iterdir() if p.is_dir())
    zips = [armar_zip(p, etiqueta) for p in paquetes if p != BASE]
    zb = armar_zip_base(etiqueta, estados)
    if zb is not None:
        zips.append(zb)
    if not zips:
        sys.exit("no hay nada para entregar")
    if not a.solo_zip:
        subir(etiqueta, zips, estados)


if __name__ == "__main__":
    main()
