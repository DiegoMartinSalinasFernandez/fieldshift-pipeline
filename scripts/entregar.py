"""Publica los CSV procesados de esta máquina en los Releases de GitHub (los datos no van en git).

Arma un zip por paquete con:
  data/processed/<paquete>/*        los CSV de los estados de esta máquina
  docs/datasets/<paquete>.md        el data card
  data/reference/condados.csv, anios.csv
  manifest.csv                      solo las filas del paquete; si alguna trae una clave
                                    (key=, api_key=, token=...) en la URL, corta sin subir nada
y lo sube al release `datos-<estados>` (por ejemplo `datos-ks` o `datos-oh-ne-mn`), reemplazando la versión
anterior del mismo paquete. Cada zip lleva al lado su .sha256.

Uso:
  python scripts/entregar.py                     # todos los paquetes de data/processed/
  python scripts/entregar.py cultivos clima      # solo esos
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
    (z.with_suffix(".zip.sha256")).write_text(f"{sha256(z)}  {z.name}\n", encoding="utf-8")
    print(f"{z.relative_to(REPO)}: {z.stat().st_size / 1e6:.1f} MB, {len(archivos)} archivos de datos")
    return z


def gh(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], cwd=REPO, capture_output=True, text=True, check=check)


def subir(etiqueta: str, zips: list[Path], estados: list[str]) -> None:
    if gh("release", "view", etiqueta, check=False).returncode != 0:
        gh("release", "create", etiqueta, "--title", f"Datos procesados: {', '.join(estados)}",
           "--notes", "CSV procesados por paquete, publicados con scripts/entregar.py. Ver MAQUINAS.md.")
    rutas = [str(p) for z in zips for p in (z, z.with_suffix(".zip.sha256"))]
    r = gh("release", "upload", etiqueta, *rutas, "--clobber", check=False)
    if r.returncode != 0:
        sys.exit(f"gh release upload falló:\n{r.stderr.strip()}")
    print(f"subido al release {etiqueta}: {', '.join(z.name for z in zips)}")


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
    zips = [armar_zip(p, etiqueta) for p in paquetes]
    if not a.solo_zip:
        subir(etiqueta, zips, estados)


if __name__ == "__main__":
    main()
