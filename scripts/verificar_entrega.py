"""Controla zips de entrega (de `scripts/entregar.py`) o carpetas unidas (de `scripts/unir_estados.py`) contra el
contrato de los CSV (sección 4 del CLAUDE.md), sin bajar nada.

Por cada paquete controla:
  - formato: UTF-8 sin BOM, separador `,`, encabezado en la primera fila, nombres en `snake_case`;
  - claves primero y con su formato (`fips` de 5 dígitos, `anio` entero, `fecha` YYYY-MM-DD, `mes` YYYY-MM),
    rangos físicos, decimales con punto y rellenos numéricos: lo hace `validar_csv()` de `src/common/`, con los
    `fips` del `condados.csv` que viene en el zip (no el de esta máquina);
  - faltantes escritos como texto: `-999`, `-9999`, `NaN`, `nan`, `None`, `(D)`, `(Z)` (van como celda vacía;
    el código de NASS va en `flag_nass`);
  - claves sin duplicados (las primeras columnas clave, más `cultivo` y `ventana` si están);
  - que el data card tenga una fila (`| archivo | columna | ...`) por cada columna no clave de cada CSV;
  - si el zip trae su `.sha256` al lado, que coincida.

El zip de base (`<release>_base.zip`, sin `data/processed/`) se controla aparte: que `condados.gpkg` se pueda
leer (capa `condados`, EPSG:4326, `fips` de 5 dígitos sin repetir, geometrías no vacías), que `condados.csv`
tenga los mismos `fips`, que venga `anios.csv` y que coincida el `.sha256`.

Salida: un informe en Markdown por paquete (APTO / NO APTO con la lista de problemas). Sale con código 1 si
algún paquete es NO APTO.

Uso:
  python scripts/verificar_entrega.py data/entregas/datos-ks_clima.zip data/entregas/datos-ks_cultivos.zip
  python scripts/verificar_entrega.py data/entregas/datos-ks/*.zip --salida data/entregas/informes
  python scripts/verificar_entrega.py data/unido/clima          # carpeta de scripts/unir_estados.py
  python scripts/verificar_entrega.py data/entregas/datos-ks_base.zip   # zip de base (polígonos)

En una carpeta unida, los CSV y los data cards (`<release>.md`) están en `data/unido/<paquete>/` y el
`condados.csv` en `data/unido/`.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import os
import re
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from unittest import mock

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.common import config as _config  # noqa: E402
from src.common import validacion as _validacion  # noqa: E402
from src.common.validacion import validar_csv  # noqa: E402

# Mismas columnas clave que scripts/unir_estados.py: la clave de un archivo es el prefijo de sus columnas que
# está en esta lista, más `cultivo` y `ventana` donde estén (formatos largos).
COLUMNAS_CLAVE = ["fips", "fips_estado", "anio", "anio_censo", "fecha", "mes", "cultivo", "ventana",
                  "id_lote", "px_id", "mukey"]
FALTANTES_TEXTO = {"-999", "-9999", "-999.0", "-9999.0", "NaN", "nan", "NAN", "None", "none", "(D)", "(Z)"}
# Columnas que pueden guardar el código original de NASS: ahí `(D)` y `(Z)` son válidos.
COLUMNAS_FLAG = re.compile(r"^flag_")
SNAKE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
FILA_CARD = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")


@dataclass
class Informe:
    nombre: str                       # zip o carpeta
    paquete: str
    problemas: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    archivos: list[tuple[str, int, int]] = field(default_factory=list)  # (csv, filas, columnas)

    @property
    def apto(self) -> bool:
        return not self.problemas

    def markdown(self) -> str:
        r = [f"# {self.nombre} — {'APTO' if self.apto else 'NO APTO'}", "", f"Paquete: `{self.paquete}`", ""]
        if self.archivos:
            r += ["| archivo | filas | columnas |", "|---|---|---|"]
            r += [f"| {a} | {f} | {c} |" for a, f, c in self.archivos]
            r.append("")
        r.append(f"## Problemas ({len(self.problemas)})")
        r += [f"- {p}" for p in self.problemas] or ["- ninguno"]
        if self.avisos:
            r += ["", f"## Avisos ({len(self.avisos)})"] + [f"- {a}" for a in self.avisos]
        return "\n".join(r) + "\n"


# ---------------------------------------------------------------------------------------------------------
# Lectura de la entrega: zip o carpeta unida → {csv: bytes}, data cards, condados

@dataclass
class Entrega:
    nombre: str
    paquete: str
    csvs: dict[str, bytes]
    cards: dict[str, str]
    condados: bytes | None
    otros: set[str]                   # referencias presentes (anios.csv, manifest.csv)
    avisos: list[str] = field(default_factory=list)
    problemas: list[str] = field(default_factory=list)


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def es_zip_base(z: Path) -> bool:
    """Zip de base de entregar.py: `<release>_base.zip`, o un zip sin `data/processed/` que trae condados.gpkg."""
    if z.name.endswith("_base.zip"):
        return True
    try:
        with zipfile.ZipFile(z) as zf:
            nombres = zf.namelist()
    except zipfile.BadZipFile:
        return False
    return GPKG in nombres and not any(n.startswith("data/processed/") for n in nombres)


GPKG = "data/reference/condados.gpkg"
FIPS5 = re.compile(r"^\d{5}$")


def verificar_base(z: Path) -> Informe:
    """Controles del zip de base: condados.gpkg, condados.csv, anios.csv y .sha256."""
    inf = Informe(z.name, "base")
    sha = z.with_suffix(".zip.sha256")
    if sha.exists():
        if _sha256(z) != sha.read_text(encoding="utf-8").split()[0].lower():
            inf.problemas.append(f"el sha256 no coincide con {sha.name} (zip corrupto o incompleto)")
    else:
        inf.avisos.append(f"no viene {sha.name}")
    try:
        zf = zipfile.ZipFile(z)
    except zipfile.BadZipFile as e:
        inf.problemas.append(f"no es un zip válido: {e}")
        return inf
    with zf, tempfile.TemporaryDirectory() as tmp:
        nombres = zf.namelist()
        for ref in ("data/reference/anios.csv", "README.md"):
            if ref not in nombres:
                inf.avisos.append(f"no viene {ref}")
        fips_gpkg: set[str] | None = None
        if GPKG not in nombres:
            inf.problemas.append(f"falta {GPKG}")
        else:
            try:
                import geopandas as gpd
            except ImportError:
                inf.avisos.append("falta geopandas: no se controla condados.gpkg por dentro")
                gpd = None
            if gpd is not None:
                ruta = Path(tmp) / "condados.gpkg"
                ruta.write_bytes(zf.read(GPKG))
                try:
                    g = gpd.read_file(ruta, layer="condados")
                except Exception as e:  # noqa: BLE001
                    inf.problemas.append(f"condados.gpkg: no se pudo leer la capa `condados`: {e}")
                    g = None
                if g is not None:
                    inf.archivos.append(("condados.gpkg", len(g), len(g.columns)))
                    if g.crs is None or g.crs.to_epsg() != 4326:
                        inf.problemas.append(f"condados.gpkg: tiene que estar en EPSG:4326 (está en {g.crs})")
                    if "fips" not in g.columns:
                        inf.problemas.append("condados.gpkg: falta la columna fips")
                    else:
                        f = g["fips"].astype(str)
                        malos = sorted(set(f[~f.str.match(FIPS5)]))
                        if malos:
                            inf.problemas.append(f"condados.gpkg: fips que no son de 5 dígitos: {malos[:5]}")
                        if f.duplicated().any():
                            inf.problemas.append(f"condados.gpkg: fips repetidos: {sorted(set(f[f.duplicated()]))[:5]}")
                        fips_gpkg = set(f)
                    vacias = int((g.geometry.isna() | g.geometry.is_empty).sum())
                    if vacias:
                        inf.problemas.append(f"condados.gpkg: {vacias} condados sin geometría")
                    if len(g) == 0:
                        inf.problemas.append("condados.gpkg: no tiene condados")
        if "data/reference/condados.csv" not in nombres:
            inf.problemas.append("falta data/reference/condados.csv")
        else:
            crudo = zf.read("data/reference/condados.csv")
            fips_csv = _fips_de_condados(crudo)
            inf.archivos.append(("condados.csv", len(fips_csv), 0))
            if not fips_csv:
                inf.problemas.append("condados.csv no tiene la columna fips")
            elif fips_gpkg is not None and fips_csv != fips_gpkg:
                solo_g, solo_c = sorted(fips_gpkg - fips_csv), sorted(fips_csv - fips_gpkg)
                inf.problemas.append(f"condados.gpkg y condados.csv no tienen los mismos fips (solo en el gpkg: "
                                     f"{solo_g[:5] or '-'}; solo en el csv: {solo_c[:5] or '-'})")
    return inf


def leer_zip(z: Path) -> list[Entrega]:
    """Una Entrega por paquete del zip (entregar.py arma uno por paquete, pero no se asume)."""
    problemas: list[str] = []
    sha = z.with_suffix(".zip.sha256")
    if sha.exists():
        esperado = sha.read_text(encoding="utf-8").split()[0].lower()
        if _sha256(z) != esperado:
            problemas.append(f"el sha256 no coincide con {sha.name} (zip corrupto o incompleto)")
    try:
        zf = zipfile.ZipFile(z)
    except zipfile.BadZipFile as e:
        return [Entrega(z.name, "?", {}, {}, None, set(), problemas=problemas + [f"no es un zip válido: {e}"])]
    with zf:
        nombres = zf.namelist()
        paquetes = sorted({n.split("/")[2] for n in nombres
                           if n.startswith("data/processed/") and n.count("/") >= 3 and n.endswith(".csv")})
        condados = zf.read("data/reference/condados.csv") if "data/reference/condados.csv" in nombres else None
        otros = {Path(n).name for n in ("data/reference/anios.csv", "manifest.csv") if n in nombres}
        if not paquetes:
            return [Entrega(z.name, "?", {}, {}, condados, otros,
                            problemas=problemas + ["no hay CSV en data/processed/<paquete>/"])]
        out = []
        for p in paquetes:
            pre = f"data/processed/{p}/"
            csvs = {n[len(pre):]: zf.read(n) for n in nombres if n.startswith(pre) and n.endswith(".csv")}
            card = f"docs/datasets/{p}.md"
            cards = {card: zf.read(card).decode("utf-8", errors="replace")} if card in nombres else {}
            out.append(Entrega(z.name, p, csvs, cards, condados, otros, problemas=list(problemas)))
        return out


def leer_carpeta(d: Path) -> list[Entrega]:
    """Carpeta `data/unido/<paquete>/` de unir_estados.py."""
    csvs = {p.relative_to(d).as_posix(): p.read_bytes() for p in sorted(d.rglob("*.csv"))}
    cards = {p.name: p.read_text(encoding="utf-8", errors="replace") for p in sorted(d.glob("*.md"))}
    cond = d.parent / "condados.csv"
    otros = {n for n in ("anios.csv", "manifest.csv") if (d.parent / n).exists()}
    e = Entrega(d.as_posix(), d.name, csvs, cards, cond.read_bytes() if cond.exists() else None, otros)
    if not csvs:
        e.problemas.append(f"no hay CSV en {d}")
    return [e]


# ---------------------------------------------------------------------------------------------------------
# Controles

def claves(columnas: list[str]) -> list[str]:
    out = []
    for c in columnas:
        if c not in COLUMNAS_CLAVE:
            break
        out.append(c)
    return out


def columnas_card(texto: str) -> set[tuple[str, str]]:
    """(archivo, columna) de las tablas `| archivo | columna | ... |` del data card."""
    filas = set()
    en_tabla = False
    for linea in texto.splitlines():
        m = FILA_CARD.match(linea.strip())
        if not m:
            en_tabla = False
            continue
        a, c = m.group(1).strip("` "), m.group(2).strip("` ")
        if a.lower() == "archivo" and c.lower() == "columna":
            en_tabla = True
            continue
        if en_tabla and not set(a) <= {"-", ":"}:
            filas.add((Path(a).name, c))
    return filas


def controlar_formato(nombre: str, crudo: bytes) -> tuple[list[str], pd.DataFrame | None]:
    """Formato del archivo; devuelve (problemas, df como texto) o df None si no se puede leer."""
    probs: list[str] = []
    if crudo.startswith(b"\xef\xbb\xbf"):
        probs.append(f"{nombre}: empieza con BOM; tiene que ser UTF-8 sin BOM")
        crudo = crudo[3:]
    try:
        texto = crudo.decode("utf-8")
    except UnicodeDecodeError as e:
        return [f"{nombre}: no es UTF-8 ({e})"], None
    if not texto.strip():
        return [f"{nombre}: está vacío"], None
    encabezado = texto.splitlines()[0]
    if "," not in encabezado and (";" in encabezado or "\t" in encabezado):
        return probs + [f"{nombre}: el separador no es `,` (encabezado: {encabezado[:60]!r})"], None
    try:
        df = pd.read_csv(io.StringIO(texto), dtype=str, keep_default_na=False)
    except Exception as e:  # noqa: BLE001
        return probs + [f"{nombre}: no se pudo leer como CSV: {e}"], None
    cols = list(df.columns)
    numericas = [c for c in cols if re.fullmatch(r"-?\d+([.,]\d+)?", c.strip())]
    if numericas:
        probs.append(f"{nombre}: la primera fila parece datos, no encabezado ({numericas[:3]})")
    no_snake = [c for c in cols if not SNAKE.match(c) and c not in numericas]
    if no_snake:
        probs.append(f"{nombre}: columnas que no están en snake_case: {no_snake[:5]}")
    return probs, df


def controlar_faltantes(nombre: str, df: pd.DataFrame) -> list[str]:
    probs = []
    for c in df.columns:
        valores = df[c].str.strip()
        malos = valores[valores.isin(FALTANTES_TEXTO)]
        if COLUMNAS_FLAG.match(c):
            malos = malos[~malos.isin({"(D)", "(Z)"})]
        if len(malos):
            probs.append(f"{nombre}: {c} tiene faltantes escritos como texto {sorted(malos.unique())[:4]} "
                         f"en {len(malos)} filas; van como celda vacía")
    return probs


def controlar_duplicados(nombre: str, df: pd.DataFrame) -> list[str]:
    cols = list(df.columns)
    k = claves(cols)
    k += [c for c in ("cultivo", "ventana") if c in cols and c not in k]
    if not k:
        return []  # validar_csv ya reporta que falta la clave
    dup = df.duplicated(subset=k, keep=False)
    if not dup.any():
        return []
    ej = df.loc[dup, k].drop_duplicates().head(3).to_dict("records")
    return [f"{nombre}: {int(dup.sum())} filas con clave {k} duplicada, por ejemplo {ej}"]


@contextlib.contextmanager
def _contexto_validar(fips: set[str]):
    """validar_csv() con los fips del zip y con los siete estados de config.yaml.

    validar_csv() lee los fips de data/reference/condados.csv de esta máquina y los estados de
    FIELDSHIFT_ESTADOS; una entrega se controla contra su propio condados.csv y puede ser de otros estados.
    No se cambia src/common/: se reemplaza su lector de fips solo mientras dura el control.
    """
    previo = os.environ.pop(_config.VAR_ESTADOS, None)
    _config.cargar_config.cache_clear()
    try:
        with mock.patch.object(_validacion, "_fips_validos", lambda: set(fips)):
            yield
    finally:
        if previo is not None:
            os.environ[_config.VAR_ESTADOS] = previo
        _config.cargar_config.cache_clear()


def _fips_de_condados(crudo: bytes) -> set[str]:
    df = pd.read_csv(io.BytesIO(crudo), dtype=str, keep_default_na=False)
    if "fips" not in df.columns:
        return set()
    return set(df["fips"].str.zfill(5))


def verificar_entrega(e: Entrega) -> Informe:
    inf = Informe(e.nombre, e.paquete, list(e.problemas), list(e.avisos))
    if not e.csvs:
        return inf

    fips: set[str] = set()
    if e.condados is None:
        inf.problemas.append("falta condados.csv: no se pueden controlar los fips")
    else:
        fips = _fips_de_condados(e.condados)
        if not fips:
            inf.problemas.append("condados.csv no tiene la columna fips")
    for ref in ("anios.csv", "manifest.csv"):
        if ref not in e.otros:
            inf.avisos.append(f"no viene {ref}")

    card: set[tuple[str, str]] = set()
    if not e.cards:
        inf.problemas.append(f"falta el data card (docs/datasets/{e.paquete}.md)")
    else:
        for texto in e.cards.values():
            card |= columnas_card(texto)
        if not card:
            inf.problemas.append("el data card no tiene la tabla `| archivo | columna | ... |`")

    with tempfile.TemporaryDirectory() as tmp, _contexto_validar(fips):
        for nombre, crudo in sorted(e.csvs.items()):
            probs, df = controlar_formato(nombre, crudo)
            inf.problemas += probs
            if df is None:
                continue
            inf.archivos.append((nombre, len(df), len(df.columns)))
            inf.problemas += controlar_faltantes(nombre, df)
            inf.problemas += controlar_duplicados(nombre, df)

            ruta = Path(tmp) / Path(nombre).name
            ruta.write_bytes(crudo)
            for err in validar_csv(ruta):
                if "claves duplicadas" in err:
                    continue  # controlar_duplicados() lo hace con la clave completa (id_lote, px_id, mukey)
                if not fips and "condados.csv" in err:
                    continue  # ya reportado arriba
                inf.problemas.append(f"{nombre}: {err}")

            if card:
                base = Path(nombre).name
                k = set(claves(list(df.columns)))
                faltan = [c for c in df.columns if c not in k and (base, c) not in card]
                if faltan:
                    inf.problemas.append(f"{nombre}: columnas sin fila en el data card: {faltan[:8]}"
                                         + (f" y {len(faltan) - 8} más" if len(faltan) > 8 else ""))
                sobran = sorted(c for a, c in card if a == base and c not in df.columns)
                if sobran:
                    inf.avisos.append(f"{nombre}: el data card describe columnas que no están: {sobran[:8]}")
    return inf


def verificar(rutas: list[Path]) -> list[Informe]:
    informes = []
    for r in rutas:
        if r.is_dir():
            entregas = leer_carpeta(r)
        elif r.suffix == ".zip" and r.exists() and es_zip_base(r):
            informes.append(verificar_base(r))
            continue
        elif r.suffix == ".zip" and r.exists():
            entregas = leer_zip(r)
        else:
            informes.append(Informe(r.as_posix(), "?", [f"no existe o no es un zip ni una carpeta: {r}"]))
            continue
        informes += [verificar_entrega(e) for e in entregas]
    return informes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rutas", nargs="+", type=Path, help="zips de entregar.py o carpetas data/unido/<paquete>/")
    ap.add_argument("--salida", type=Path, help="carpeta donde guardar un informe <nombre>.md por paquete")
    a = ap.parse_args(argv)
    informes = verificar(a.rutas)
    for inf in informes:
        md = inf.markdown()
        print(md)
        if a.salida:
            a.salida.mkdir(parents=True, exist_ok=True)
            base = Path(inf.nombre).name.removesuffix(".zip")
            nombre = base if base.endswith(inf.paquete) else f"{base}_{inf.paquete}"
            (a.salida / f"{nombre}.md").write_text(md, encoding="utf-8")
    malos = [i for i in informes if not i.apto]
    print(f"{len(informes) - len(malos)} APTO, {len(malos)} NO APTO")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
