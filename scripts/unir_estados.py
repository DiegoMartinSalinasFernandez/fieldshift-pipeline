"""Junta los releases de datos de cada máquina (uno por grupo de estados) en una sola copia por paquete.

Cada máquina publica con `scripts/entregar.py` un zip por paquete en el release `datos-<estados>`
(`datos-ia-il-in_clima.zip` + `.sha256`). Adentro vienen `data/processed/<paquete>/*.csv`, el data card
`docs/datasets/<paquete>.md`, `data/reference/condados.csv`, `anios.csv` y `manifest.csv`.

Este script:
  1. baja los zips de cada release con `gh release download` a `data/entregas/<release>/` (o usa los que ya
     están en `--dir/<release>/`) y verifica el `.sha256` de cada uno;
  2. por paquete, apila por filas los CSV del mismo nombre de todos los releases en `data/unido/<paquete>/`
     (mismo encabezado en todos; `fips` y `fips_estado` se leen como texto);
  3. chequea: sin claves duplicadas después de apilar (claves = primeras columnas, sección 4 del CLAUDE.md),
     cada `fips` en un solo release, y une `condados.csv`, `anios.csv` y `manifest.csv` sin repetir filas;
  4. imprime un resumen: filas por paquete y por estado.

No corre `src/merge.py` ni toca `src/common/`. Los data cards se copian como
`data/unido/<paquete>/<release>.md`.

Uso:
  python scripts/unir_estados.py --releases datos-ia-il-in,datos-oh-ne-mn,datos-ks
  python scripts/unir_estados.py --releases datos-ia-il-in,datos-ks --dir /ruta/con/zips_bajados
  python scripts/unir_estados.py --releases ... --paquetes clima,cultivos --salida data/unido

Con `--dir`, se esperan los zips en `<dir>/<release>/<release>_<paquete>.zip` (con su `.sha256` al lado) y no
se baja nada. Sale con código 1 y lista los problemas si algún chequeo falla.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]

# Columnas que pueden ser clave (sección 4 del CLAUDE.md y formatos largos de los paquetes). La clave de cada
# archivo es el prefijo de sus columnas que está en este conjunto.
COLUMNAS_CLAVE = ["fips", "fips_estado", "anio", "anio_censo", "fecha", "mes", "cultivo", "ventana",
                  "id_lote", "px_id", "mukey"]
TEXTO = {"fips": str, "fips_estado": str, "id_lote": str, "mukey": str}
REFERENCIAS = {"data/reference/condados.csv": "condados.csv", "data/reference/anios.csv": "anios.csv",
               "manifest.csv": "manifest.csv"}


class ErrorUnion(Exception):
    pass


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def bajar(release: str, destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["gh", "release", "download", release, "--dir", str(destino), "--clobber",
                        "--pattern", "*.zip", "--pattern", "*.sha256"],
                       cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        raise ErrorUnion(f"gh release download {release} falló: {r.stderr.strip()}")


def verificar(z: Path) -> None:
    s = z.with_suffix(".zip.sha256")
    if not s.exists():
        raise ErrorUnion(f"{z.name}: falta {s.name}")
    esperado = s.read_text(encoding="utf-8").split()[0].lower()
    if sha256(z) != esperado:
        raise ErrorUnion(f"{z.name}: el sha256 no coincide con {s.name} (zip corrupto o incompleto)")


def zips_de(release: str, carpeta: Path) -> dict[str, Path]:
    """paquete -> zip del release, sacando el paquete del nombre `<release>_<paquete>.zip`."""
    out = {}
    for z in sorted(carpeta.glob(f"{release}_*.zip")):
        out[z.name[len(release) + 1:-len(".zip")]] = z
    if not out:
        raise ErrorUnion(f"{release}: no hay zips {release}_*.zip en {carpeta}")
    return out


def leer_csv(zf: zipfile.ZipFile, nombre: str) -> pd.DataFrame:
    with zf.open(nombre) as f:
        return pd.read_csv(f, dtype=TEXTO, keep_default_na=False, na_values=[""])


def claves(columnas: list[str]) -> list[str]:
    out = []
    for c in columnas:
        if c not in COLUMNAS_CLAVE:
            break
        out.append(c)
    return out


def estado_de(df: pd.DataFrame) -> pd.Series | None:
    if "fips" in df.columns:
        return df["fips"].str[:2]
    if "fips_estado" in df.columns:
        return df["fips_estado"]
    return None


def unir(releases: list[str], base: Path, salida: Path, paquetes: list[str] | None = None,
         bajar_releases: bool = True) -> dict:
    """Une los releases. Devuelve el resumen; levanta ErrorUnion si algún chequeo falla."""
    problemas: list[str] = []
    zips: dict[str, dict[str, Path]] = {}
    for rel in releases:
        carpeta = base / rel
        if bajar_releases:
            bajar(rel, carpeta)
        zips[rel] = zips_de(rel, carpeta)
        for z in zips[rel].values():
            verificar(z)

    todos = sorted({p for d in zips.values() for p in d})
    if paquetes:
        faltan = [p for p in paquetes if p not in todos]
        if faltan:
            raise ErrorUnion(f"paquetes pedidos que no están en ningún release: {', '.join(faltan)}")
        todos = paquetes

    # partes[(paquete, archivo)] = [(release, df)]; refs[archivo_ref] = [(release, df)]
    partes: dict[tuple[str, str], list[tuple[str, pd.DataFrame]]] = defaultdict(list)
    refs: dict[str, list[tuple[str, pd.DataFrame]]] = defaultdict(list)
    for paquete in todos:
        for rel in releases:
            z = zips[rel].get(paquete)
            if z is None:
                print(f"aviso: {rel} no tiene el paquete {paquete}")
                continue
            prefijo = f"data/processed/{paquete}/"
            with zipfile.ZipFile(z) as zf:
                for nombre in zf.namelist():
                    if nombre.startswith(prefijo) and nombre.endswith(".csv"):
                        partes[(paquete, nombre[len(prefijo):])].append((rel, leer_csv(zf, nombre)))
                    elif nombre in REFERENCIAS:
                        refs[REFERENCIAS[nombre]].append((rel, leer_csv(zf, nombre)))
                    elif nombre == f"docs/datasets/{paquete}.md":
                        d = salida / paquete
                        d.mkdir(parents=True, exist_ok=True)
                        (d / f"{rel}.md").write_bytes(zf.read(nombre))

    resumen: dict[str, dict[str, int]] = {}
    for (paquete, archivo), lista in sorted(partes.items()):
        etiqueta = f"{paquete}/{archivo}"
        cols0 = list(lista[0][1].columns)
        distintas = False
        for rel, df in lista[1:]:
            if list(df.columns) != cols0:
                solo_a = [c for c in cols0 if c not in df.columns]
                solo_b = [c for c in df.columns if c not in cols0]
                detalle = (f"solo en {lista[0][0]}: {solo_a or '-'}; solo en {rel}: {solo_b or '-'}"
                           if solo_a or solo_b else "mismas columnas en distinto orden")
                problemas.append(f"{etiqueta}: el encabezado de {rel} difiere del de {lista[0][0]} ({detalle})")
                distintas = True
        if distintas:
            continue

        # cada fips (o fips_estado) en un solo release
        col_geo = "fips" if "fips" in cols0 else "fips_estado" if "fips_estado" in cols0 else None
        if col_geo:
            donde: dict[str, set[str]] = defaultdict(set)
            for rel, df in lista:
                for v in df[col_geo].dropna().unique():
                    donde[v].add(rel)
            repetidos = {v: sorted(r) for v, r in donde.items() if len(r) > 1}
            if repetidos:
                ej = ", ".join(f"{v} ({'/'.join(r)})" for v, r in sorted(repetidos.items())[:5])
                problemas.append(f"{etiqueta}: {len(repetidos)} valores de {col_geo} en más de un release: {ej}")

        unido = pd.concat([df for _, df in lista], ignore_index=True)
        k = claves(cols0)
        if not k:
            problemas.append(f"{etiqueta}: no se reconocen columnas clave al principio ({cols0[:3]})")
        else:
            dup = unido.duplicated(subset=k, keep=False)
            if dup.any():
                ej = unido.loc[dup, k].drop_duplicates().head(3).to_dict("records")
                problemas.append(f"{etiqueta}: {int(dup.sum())} filas con clave {k} duplicada, por ejemplo {ej}")

        destino = salida / paquete / archivo
        destino.parent.mkdir(parents=True, exist_ok=True)
        unido.to_csv(destino, index=False, encoding="utf-8")
        est = estado_de(unido)
        resumen[etiqueta] = (est.fillna("?").value_counts().sort_index().to_dict() if est is not None
                             else {"(sin fips)": len(unido)})

    # referencias: unión sin filas repetidas
    for archivo, lista in sorted(refs.items()):
        cols0 = list(lista[0][1].columns)
        malos = [rel for rel, df in lista if list(df.columns) != cols0]
        if malos:
            problemas.append(f"{archivo}: encabezado distinto en {', '.join(malos)}")
            continue
        unido = pd.concat([df for _, df in lista], ignore_index=True).drop_duplicates(ignore_index=True)
        clave_ref = {"condados.csv": ["fips"], "anios.csv": ["anio"]}.get(archivo)
        if clave_ref and unido.duplicated(subset=clave_ref).any():
            ej = unido.loc[unido.duplicated(subset=clave_ref, keep=False), clave_ref[0]].unique()[:5]
            problemas.append(f"{archivo}: el mismo {clave_ref[0]} viene con valores distintos en dos releases: "
                             f"{list(ej)}")
        if clave_ref:
            unido = unido.sort_values(clave_ref, ignore_index=True)
        salida.mkdir(parents=True, exist_ok=True)
        unido.to_csv(salida / archivo, index=False, encoding="utf-8")

    if problemas:
        raise ErrorUnion("\n".join(f"- {p}" for p in problemas))
    return resumen


def imprimir(resumen: dict[str, dict[str, int]]) -> None:
    for etiqueta, por_estado in resumen.items():
        total = sum(por_estado.values())
        detalle = ", ".join(f"{e}: {n}" for e, n in por_estado.items())
        print(f"{etiqueta}: {total} filas ({detalle})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--releases", required=True, help="releases separados por coma, ej. datos-ia-il-in,datos-ks")
    ap.add_argument("--dir", type=Path, help="carpeta con <release>/<zips> ya bajados (no baja nada)")
    ap.add_argument("--paquetes", help="solo estos paquetes, separados por coma")
    ap.add_argument("--salida", type=Path, default=REPO / "data" / "unido")
    a = ap.parse_args()
    releases = [r.strip() for r in a.releases.split(",") if r.strip()]
    paquetes = [p.strip() for p in a.paquetes.split(",")] if a.paquetes else None
    base = a.dir or REPO / "data" / "entregas"
    try:
        resumen = unir(releases, base, a.salida, paquetes, bajar_releases=a.dir is None)
    except ErrorUnion as e:
        sys.exit(f"La unión tiene problemas:\n{e}")
    imprimir(resumen)
    print(f"listo: {a.salida}")


if __name__ == "__main__":
    main()
