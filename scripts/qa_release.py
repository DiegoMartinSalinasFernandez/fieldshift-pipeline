"""Control de calidad de los CSV publicados en un release, para cualquier tanda de estados (tarea T097).

Generaliza `docs/qa/oh_ne_mn_qa.py` (T073): los estados salen de `data/reference/condados.csv` de los zips y
los eventos a revisar, de un archivo YAML que se pasa por argumento. Solo lee los CSV; no escribe en
`data/processed/`.

Entrada, una de dos:
- el nombre de un release (`datos-oh-ne-mn`): baja sus zips y `.sha256` con `curl -L` a
  `data/entregas/<release>/`, controla las sumas y los descomprime en `data/entregas/<release>-ext/`, un zip
  por subcarpeta (si ya están, no los vuelve a bajar);
- una carpeta con los zips ya descomprimidos, uno por subcarpeta
  (`<carpeta>/<zip>/data/processed/<paquete>/*.csv`).

Opcional: la base completa de Quick Stats (`qs.crops_<fecha>.txt.gz`) para comparar la superficie sembrada de
condado con la de estado.

Uso:
  .venv/bin/python -X utf8 scripts/qa_release.py datos-oh-ne-mn --eventos docs/qa/eventos_oh_ne_mn.yaml \
      [--qs qs.crops_<fecha>.txt.gz] > informe.md

Salida en Markdown por stdout, con secciones: faltantes por estado contra el data card de `main` (IA/IL/IN),
eventos, rangos, outliers por vecinos y totales de NASS. Las secciones cuyo paquete no está en el release se
saltean con un aviso.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO = Path(__file__).resolve().parents[1]
CLAVES = {"fips", "fips_estado", "anio", "anio_censo", "fecha", "mes", "cultivo", "ventana"}
REFERENCIA = "IA/IL/IN"  # los data cards de docs/datasets/ en main son los de la primera tanda


# ---------------------------------------------------------------- entrada

def repo_github() -> str:
    """`dueño/repo` del remoto origin (no se escribe en ningún archivo)."""
    url = subprocess.run(["git", "-C", str(REPO), "remote", "get-url", "origin"], capture_output=True,
                         text=True, check=True).stdout.strip()
    return re.sub(r"\.git$", "", re.sub(r"^.*github\.com[:/]", "", url))


def bajar_release(release: str, destino: Path) -> Path:
    """Baja los zips del release (si faltan), controla los `.sha256` y descomprime. Devuelve la carpeta."""
    rep = repo_github()
    with urllib.request.urlopen(f"https://api.github.com/repos/{rep}/releases/tags/{release}") as r:
        nombres = [a["name"] for a in json.load(r)["assets"]]
    zips = destino / release
    ext = destino / f"{release}-ext"
    zips.mkdir(parents=True, exist_ok=True)
    for n in nombres:
        if not (zips / n).exists():
            url = f"https://github.com/{rep}/releases/download/{release}/{n}"
            subprocess.run(["curl", "-sfL", "-o", str(zips / n), url], check=True)
    for z in sorted(zips.glob("*.zip")):
        sha = zips / f"{z.name}.sha256"
        if not sha.exists():
            sys.exit(f"falta {sha.name} en el release")
        esperado = sha.read_text(encoding="utf-8").split()[0].lower()
        if hashlib.sha256(z.read_bytes()).hexdigest() != esperado:
            sys.exit(f"{z.name}: la suma sha256 no coincide")
        d = ext / z.stem
        if not d.exists():
            with zipfile.ZipFile(z) as zf:
                zf.extractall(d)
    return ext


class Release:
    """Los CSV de un release descomprimido, con la columna `estado` agregada a partir del fips."""

    def __init__(self, base: Path):
        self.base = base
        self.paquetes: dict[str, Path] = {}
        for d in sorted(p for p in base.iterdir() if p.is_dir()):
            for proc in sorted((d / "data" / "processed").glob("*")):
                if proc.is_dir():
                    self.paquetes[proc.name] = proc
        conds = sorted(base.glob("*/data/reference/condados.csv"))
        if not conds:
            sys.exit(f"no hay data/reference/condados.csv en {base}")
        self.condados = pd.read_csv(conds[0], dtype={"fips": str})
        self.est = dict(zip(self.condados.fips.str[:2], self.condados.estado))
        self.estados = sorted(set(self.est.values()))

    def tiene(self, paquete: str, archivo: str) -> bool:
        return paquete in self.paquetes and (self.paquetes[paquete] / archivo).exists()

    def leer(self, paquete: str, archivo: str, **kw) -> pd.DataFrame:
        df = pd.read_csv(self.paquetes[paquete] / archivo, dtype={"fips": str, "fips_estado": str}, **kw)
        if "fips" in df:
            df["estado"] = df["fips"].str[:2].map(self.est)
        elif "fips_estado" in df:
            df["estado"] = df["fips_estado"].map(self.est)
        if "mes" in df:
            df["m"] = df["mes"].str[5:7].astype(int)
        return df


def falta(rel: Release, paquete: str, archivo: str) -> bool:
    if rel.tiene(paquete, archivo):
        return False
    print(f"_No está `{paquete}/{archivo}` en el release: se saltea._\n")
    return True


# ---------------------------------------------------------------- faltantes

def faltantes_card(card: Path) -> dict[tuple[str, str], float]:
    """(archivo, columna) -> faltantes_pct del data card (el de main es el de IA/IL/IN)."""
    r = {}
    for linea in card.read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in linea.strip().strip("|").split("|")]
        if len(c) >= 9 and c[0].endswith(".csv"):
            try:
                r[(c[0], c[1])] = float(c[8].replace(",", ".").rstrip("%"))
            except ValueError:
                pass
    return r


def seccion_faltantes(rel: Release, umbral: float = 15) -> None:
    print(f"## Faltantes por columna y estado contra {REFERENCIA}\n")
    print(f"Solo las columnas donde algún estado supera en más de {umbral:g} puntos al data card de "
          f"{REFERENCIA} (`docs/datasets/<paquete>.md` de `main`).\n")
    print(f"| paquete | archivo | columna | {REFERENCIA} % | " + " | ".join(f"{e} %" for e in rel.estados) + " |")
    print("|---|---|---|---|" + "---|" * len(rel.estados))
    for paq, carpeta in rel.paquetes.items():
        card = REPO / "docs" / "datasets" / f"{paq}.md"
        ref = faltantes_card(card) if card.exists() else {}
        for p in sorted(carpeta.glob("*.csv")):
            cols_ref = {c for a, c in ref if a == p.name}
            if not cols_ref:
                continue
            df = rel.leer(paq, p.name)
            for col in df.columns:
                if col in CLAVES or col in ("estado", "m") or col.startswith("flag_") or col not in cols_ref:
                    continue
                por = df.groupby("estado")[col].apply(lambda s: s.isna().mean() * 100)
                r = ref[(p.name, col)]
                if (por - r).max() > umbral:
                    print(f"| {paq} | {p.name} | {col} | {r:.1f} | "
                          + " | ".join(f"{por.get(e, np.nan):.1f}" for e in rel.estados) + " |")
    print()


# ---------------------------------------------------------------- eventos

def tabla(nombre: str, serie: pd.DataFrame, anios: list[int]) -> None:
    s = serie.reindex(anios)
    print(f"**{nombre}**\n")
    print("| anio | " + " | ".join(s.columns) + " |")
    print("|---|" + "---|" * len(s.columns))
    for a, f in s.iterrows():
        print(f"| {a} | " + " | ".join("" if pd.isna(v) else f"{v:.2f}" for v in f) + " |")
    print()


def rend_implicito(pa: pd.DataFrame, cultivo: str) -> pd.DataFrame:
    """Rendimiento de estado implícito: suma de producción / suma de cosechada (condados con ambos)."""
    d = pa[(pa.cultivo == cultivo) & pa.produccion_bu.notna() & pa.sup_cosechada_ac.notna()]
    g = d.groupby(["estado", "anio"])[["produccion_bu", "sup_cosechada_ac"]].sum()
    return (g.produccion_bu / g.sup_cosechada_ac).unstack("estado")


def serie_evento(rel: Release, ev: dict) -> pd.DataFrame:
    """Tipos (campo `tipo`, por defecto `media`):
    - media: media de condados por estado y año de `columna`, opcionalmente solo en `meses`;
    - suma_meses: suma de `columna` en `meses` por condado y año, y después media de condados;
    - suma_condados: suma de `columna` sobre condados (con `min_count=1`), dividida por `escala`;
    - rend_implicito: suma de producción / suma de cosechada de `cultivo` (paquete cultivos);
    - rend_dif5: diferencia % del rendimiento implícito contra la media de los 5 años previos.
    `cultivo` filtra filas de un archivo largo en media / suma_condados."""
    tipo = ev.get("tipo", "media")
    if tipo in ("rend_implicito", "rend_dif5"):
        rend = rend_implicito(rel.leer("cultivos", "produccion_anual.csv"), ev["cultivo"])
        if tipo == "rend_implicito":
            return rend
        return (rend / rend.shift(1).rolling(5).mean() - 1) * 100
    df = rel.leer(ev["paquete"], ev["archivo"])
    if "cultivo" in ev:
        df = df[df.cultivo == ev["cultivo"]]
    if "meses" in ev:
        df = df[df.m.isin(ev["meses"])]
    col = ev["columna"]
    if tipo == "media":
        return df.groupby(["estado", "anio"])[col].mean().unstack("estado")
    if tipo == "suma_meses":
        return (df.groupby(["estado", "anio", "fips"])[col].sum().groupby(["estado", "anio"]).mean()
                .unstack("estado"))
    if tipo == "suma_condados":
        return df.groupby(["estado", "anio"])[col].sum(min_count=1).unstack("estado") / ev.get("escala", 1)
    raise ValueError(f"tipo de evento desconocido: {tipo}")


def seccion_eventos(rel: Release, eventos: list[dict]) -> None:
    """Campos opcionales de cada evento, además de los de serie_evento():
    - estados: lista de estados del evento; la tabla muestra solo esos, y si ninguno está en el release el
      evento se saltea con un aviso (así una lista de KS o de MO/WI/SD corre sobre cualquier release);
    - esperado: texto con la dirección esperada de la señal; fuente: sección del research que la respalda."""
    print("## Eventos extremos (medias de condado por estado)\n")
    for ev in eventos:
        paq, arch = ((ev["paquete"], ev["archivo"]) if "paquete" in ev
                     else ("cultivos", "produccion_anual.csv"))
        estados = ev.get("estados")
        if estados:
            estan = [e for e in estados if e in rel.estados]
            if not estan:
                print(f"_{ev['titulo']}: {', '.join(estados)} no están en el release "
                      f"({', '.join(rel.estados)}): se saltea._\n")
                continue
        if not rel.tiene(paq, arch):
            print(f"_{ev['titulo']}: no está `{paq}/{arch}` en el release._\n")
            continue
        col = ev.get("columna")
        if col and col not in pd.read_csv(rel.paquetes[paq] / arch, nrows=0).columns:
            print(f"_{ev['titulo']}: no está la columna `{col}` en `{paq}/{arch}`: se saltea._\n")
            continue
        serie = serie_evento(rel, ev)
        if estados:
            serie = serie.reindex(columns=estan)
        tabla(ev["titulo"], serie, ev["anios"])
        if ev.get("esperado"):
            print(f"Esperado: {ev['esperado']}" + (f" ({ev['fuente']})" if ev.get("fuente") else "") + "\n")


# ---------------------------------------------------------------- rangos

def seccion_rangos(rel: Release) -> None:
    print("## Rangos\n")
    if not falta(rel, "cultivos", "produccion_anual.csv"):
        pa = rel.leer("cultivos", "produccion_anual.csv")
        print("| cultivo | estado | rend mín | rend máx | n |")
        print("|---|---|---|---|---|")
        for (c, e), d in pa.dropna(subset=["rend_bu_ac"]).groupby(["cultivo", "estado"]):
            print(f"| {c} | {e} | {d.rend_bu_ac.min():.1f} | {d.rend_bu_ac.max():.1f} | {len(d)} |")
        print()
    if not falta(rel, "clima", "clima_diario.csv"):
        cd = rel.leer("clima", "clima_diario.csv",
                      usecols=["fips", "fecha", "tmin_c", "tmax_c", "prec_power_mm", "prec_imerg_mm"])
        for col in ["tmin_c", "tmax_c", "prec_power_mm", "prec_imerg_mm"]:
            i_min, i_max = cd[col].idxmin(), cd[col].idxmax()
            print(f"- `{col}` diario: mín {cd.at[i_min, col]} ({cd.at[i_min, 'fips']}, {cd.at[i_min, 'fecha']}), "
                  f"máx {cd.at[i_max, col]} ({cd.at[i_max, 'fips']}, {cd.at[i_max, 'fecha']})")
    if not falta(rel, "clima", "clima_mensual.csv"):
        cm = rel.leer("clima", "clima_mensual.csv")
        for col in ["prec_imerg_mm", "prec_power_mm", "tmax_c", "tmin_c", "gdd_10_30"]:
            if col in cm:
                print(f"- `{col}` mensual: {cm[col].min()} a {cm[col].max()}")
    if rel.tiene("clima", "clima_mensual.csv") and {"prec_imerg_mm", "prec_power_mm"} <= set(cm.columns):
        tot = cm.groupby(["estado", "fips", "anio"])[["prec_imerg_mm", "prec_power_mm"]].sum(min_count=1)
        r = (tot.prec_imerg_mm / tot.prec_power_mm).groupby("estado").median()
        print("- Cociente lluvia anual IMERG / POWER (mediana): "
              + ", ".join(f"{k} {v:.2f}" for k, v in r.items()))
    print()


# ---------------------------------------------------------------- outliers

def vecinos(cond: pd.DataFrame, k: int = 6) -> dict[str, list[str]]:
    lat = np.radians(cond.lat_centroide.values)
    lon = np.radians(cond.lon_centroide.values)
    x = np.c_[np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)]
    d = ((x[:, None, :] - x[None, :, :]) ** 2).sum(-1)
    f = cond.fips.values
    return {f[i]: list(f[np.argsort(d[i])[1:k + 1]]) for i in range(len(f))}


def outliers(df: pd.DataFrame, col: str, vec: dict, umbral: float) -> pd.DataFrame:
    """Diferencia robusta de cada condado-año contra la mediana de sus 6 vecinos más cercanos."""
    piv = df.pivot_table(index="anio", columns="fips", values=col)
    filas = []
    for f, vs in vec.items():
        if f not in piv:
            continue
        vs = [v for v in vs if v in piv]
        if len(vs) < 3:
            continue
        med = piv[vs].median(axis=1)
        mad = (piv[vs].sub(med, axis=0)).abs().median(axis=1) * 1.4826
        esc = np.maximum(mad, 0.1 * med.abs())
        z = (piv[f] - med) / esc
        for a in z.index[z.abs() > umbral]:
            filas.append((f, a, piv.at[a, f], med[a], z[a]))
    return pd.DataFrame(filas, columns=["fips", "anio", "valor", "mediana_vecinos", "z"])


def seccion_outliers(rel: Release) -> None:
    print("## Outliers por condado contra sus 6 vecinos más cercanos\n")
    cond = rel.condados
    vec = vecinos(cond)
    nombre = dict(zip(cond.fips, cond.condado))
    casos = []
    ca = None
    if rel.tiene("clima", "clima_anual.csv"):
        ca = rel.leer("clima", "clima_anual.csv")
        casos += [("clima_anual", "prec_temporada_mm", ca, 4), ("clima_anual", "gdd_temporada", ca, 4)]
    else:
        falta(rel, "clima", "clima_anual.csv")
    if not falta(rel, "cultivos", "produccion_anual.csv"):
        pa = rel.leer("cultivos", "produccion_anual.csv")
        for c in ["maiz", "soja"]:
            casos.append((f"produccion_anual ({c})", "rend_bu_ac", pa[pa.cultivo == c], 5))
    for arch, col, df, u in casos:
        o = outliers(df, col, vec, u).sort_values("z", key=abs, ascending=False)
        print(f"**{arch} `{col}`** (|z| > {u}): {len(o)} condado-años\n")
        if len(o):
            print("| fips | condado | anio | valor | mediana vecinos | z |")
            print("|---|---|---|---|---|---|")
            for r in o.head(12).itertuples():
                print(f"| {r.fips} | {nombre.get(r.fips, '')} | {r.anio} | {r.valor:.1f} | "
                      f"{r.mediana_vecinos:.1f} | {r.z:.1f} |")
            print()
    if ca is not None:
        # media de largo plazo de la lluvia: condados con media muy distinta de sus vecinos
        m = ca.groupby("fips")["prec_temporada_mm"].mean()
        a0, a1 = ca.anio.min(), ca.anio.max()
        fil = [(f, m[f], m[[v for v in vs if v in m]].median()) for f, vs in vec.items() if f in m]
        fil = [(f, a, b) for f, a, b in fil if abs(a / b - 1) > 0.25]
        print(f"Condados con `prec_temporada_mm` media {a0}–{a1} a más de 25 % de la mediana de sus vecinos: "
              f"{len(fil)}" + "".join(f"\n- {f} {nombre.get(f, '')}: {a:.0f} contra {b:.0f}" for f, a, b in fil))
        print()


# ---------------------------------------------------------------- NASS

def leer_qs(qs: Path, estados: set[str]):
    """Superficie sembrada de maíz y soja de la base de Quick Stats: (estado, otros 998, condados NASS)."""
    est, otros, n_cond = {}, {}, {}
    comm = {"CORN": "maiz", "SOYBEANS": "soja"}
    with gzip.open(qs, "rt", encoding="utf-8", errors="replace") as fh:
        lec = csv.reader(fh, delimiter="\t")
        cab = next(lec)
        i = {c: k for k, c in enumerate(cab)}
        for f in lec:
            if (f[i["SOURCE_DESC"]] != "SURVEY" or f[i["STATE_ALPHA"]] not in estados
                    or f[i["COMMODITY_DESC"]] not in comm
                    or f[i["STATISTICCAT_DESC"]] != "AREA PLANTED" or f[i["UNIT_DESC"]] != "ACRES"
                    or f[i["REFERENCE_PERIOD_DESC"]] != "YEAR" or f[i["CLASS_DESC"]] != "ALL CLASSES"
                    or f[i["PRODN_PRACTICE_DESC"]] != "ALL PRODUCTION PRACTICES"
                    or f[i["UTIL_PRACTICE_DESC"]] != "ALL UTILIZATION PRACTICES"):
                continue
            nivel = f[i["AGG_LEVEL_DESC"]]
            k = (f[i["STATE_ALPHA"]], comm[f[i["COMMODITY_DESC"]]], int(f[i["YEAR"]]))
            v = re.sub(r"[,\s]", "", f[i["VALUE"]])
            numero = v.replace(".", "").isdigit()
            if nivel == "COUNTY":
                if f[i["COUNTY_CODE"]] == "998":
                    if numero:
                        otros[k] = otros.get(k, 0) + float(v)
                else:
                    n_cond[k] = n_cond.get(k, 0) + 1
            elif nivel == "STATE" and numero:
                est[k] = float(v)
    return est, otros, n_cond


def seccion_nass(rel: Release, qs: Path) -> None:
    print("## Superficie sembrada: suma de condados contra NASS a nivel estado\n")
    if falta(rel, "cultivos", "produccion_anual.csv"):
        return
    pa = rel.leer("cultivos", "produccion_anual.csv")
    est, otros, n_cond = leer_qs(qs, set(rel.estados))
    suma = pa.groupby(["estado", "cultivo", "anio"])["sup_sembrada_ac"].sum(min_count=1)
    a0, a1 = pa.anio.min(), pa.anio.max()
    filas = [(e, c, a, v, suma[(e, c, a)]) for (e, c, a), v in est.items()
             if a0 <= a <= a1 and (e, c, a) in suma.index]
    df = pd.DataFrame(filas, columns=["estado", "cultivo", "anio", "nass_estado", "suma_condados"])
    if df.empty:
        print("_Sin años en común entre el release y Quick Stats._\n")
        return
    df["pct"] = df.suma_condados / df.nass_estado * 100
    df["otros_998"] = [otros.get(k, 0.0) for k in zip(df.estado, df.cultivo, df.anio)]
    df["n_cond_nass"] = [n_cond.get(k, 0) for k in zip(df.estado, df.cultivo, df.anio)]
    df["pct_con_998"] = (df.suma_condados + df.otros_998) / df.nass_estado * 100
    print("| estado | cultivo | n años | % mín (año) | % mediana | % máx (año) |")
    print("|---|---|---|---|---|---|")
    for (e, c), d in df.groupby(["estado", "cultivo"]):
        lo, hi = d.loc[d.pct.idxmin()], d.loc[d.pct.idxmax()]
        print(f"| {e} | {c} | {len(d)} | {lo.pct:.1f} ({lo.anio}) | {d.pct.median():.1f} | "
              f"{hi.pct:.1f} ({hi.anio}) |")
    print()
    malos = df[(df.pct < 85) | (df.pct > 101)].sort_values(["estado", "cultivo", "anio"])
    print(f"Años con la suma de condados fuera de 85–101 % del total de estado: {len(malos)}\n")
    for r in malos.itertuples():
        print(f"- {r.estado} {r.cultivo} {r.anio}: {r.suma_condados:,.0f} de {r.nass_estado:,.0f} ac "
              f"({r.pct:.1f} %); con OTHER (COMBINED) {r.pct_con_998:.1f} %; condados en NASS {r.n_cond_nass}")
    print()
    print("Suma de condados + OTHER (COMBINED) COUNTIES contra el total de estado (% mín–máx): "
          + "; ".join(f"{e} {c} {d.pct_con_998.min():.1f}–{d.pct_con_998.max():.1f}"
                      for (e, c), d in df.groupby(["estado", "cultivo"])))
    print()


# ---------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("release", help="nombre del release o carpeta con los zips descomprimidos")
    ap.add_argument("--eventos", type=Path, help="YAML con la lista `eventos` (ver serie_evento)")
    ap.add_argument("--qs", type=Path, help="base de Quick Stats qs.crops_<fecha>.txt.gz")
    ap.add_argument("--destino", type=Path, default=REPO / "data" / "entregas",
                    help="dónde bajar y descomprimir el release (por defecto data/entregas)")
    a = ap.parse_args(argv)
    base = Path(a.release)
    if not base.is_dir():
        base = bajar_release(a.release, a.destino)
    rel = Release(base)
    print(f"# QA de `{Path(a.release).name}`: {', '.join(rel.estados)}\n")
    print(f"Paquetes: {', '.join(rel.paquetes)}. Condados: {len(rel.condados)} ("
          + ", ".join(f"{e} {n}" for e, n in rel.condados.estado.value_counts().sort_index().items()) + ").\n")
    seccion_faltantes(rel)
    if a.eventos:
        eventos = yaml.safe_load(a.eventos.read_text(encoding="utf-8"))["eventos"]
        seccion_eventos(rel, eventos)
    seccion_rangos(rel)
    seccion_outliers(rel)
    if a.qs:
        seccion_nass(rel, a.qs)


if __name__ == "__main__":
    main()
