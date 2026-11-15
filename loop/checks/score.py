#!/usr/bin/env python
"""Puntaje del research agent de Field Shift (checks bloqueados).

Lo corre el orquestador después de cada ronda, con su copia bloqueada de este archivo, y el
agente lo puede correr para ver qué falla (es de solo lectura):

    python loop/puntaje.py --tarea clima

Uso directo:
    python score.py --repo <raiz> [--json salida.json] [--tarea clima] [--resumen]
                    [--reproducir clima,base] [--python <python del proyecto>]
                    [--cache <carpeta>] [--sin-red]

Cómo se puntúa (resumen; el detalle está en loop/spec/*.yaml):
  - Cada columna de loop/spec/entregables.yaml vale el peso de su ID del catálogo
    (Alta 3, Media 2, Baja 1), repartido entre las columnas que comparten ese ID.
  - 75 % del peso: datos. El archivo tiene que cumplir el contrato del CLAUDE.md §4, los
    valores tienen que estar en rango y la cobertura (celdas llenas / esperadas en la ventana
    de la fuente) llega al 100 % del puntaje al alcanzar el umbral (0,95).
  - 25 % del peso: documentación en docs/datasets/<paquete>.md, verificada contra los datos
    (desde, hasta y % de faltantes tienen que coincidir con lo real).
  - Compuertas por paquete: sin datos crudos registrados en manifest.csv, o si process.py no
    reproduce los mismos CSV, los datos del paquete valen 0.
  - Research: formato del CLAUDE.md §8, fuentes que responden y citas textuales que el
    verificador encuentra en la fuente. Cada celda de config/cultivos.csv vale si su
    evidencia se verifica.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import functools
import hashlib
import html as htmllib
import io
import json
import math
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

csv.field_size_limit(2**31 - 1)

AQUI = Path(__file__).resolve().parent


# --------------------------------------------------------------------------- utilidades

def sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def norm(s) -> str:
    return re.sub(r"\s+", " ", sin_tildes(str(s)).lower()).strip()


SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")
RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_MES = re.compile(r"^\d{4}-\d{2}$")
RE_FIPS = re.compile(r"^\d{5}$")
RE_FIPS_ESTADO = re.compile(r"^\d{2}$")
RE_ANIO = re.compile(r"^\d{4}$")
RE_VENTANA = re.compile(r"^(\d{4})-(\d{4})$")
RE_MMDD = re.compile(r"^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
RE_COMA_DECIMAL = re.compile(r"^-?\d+,\d+$")
RE_ID_LOTE = re.compile(r"^(\d{5})_[0-9A-Za-z]+$")
RE_ENTERO_NN = re.compile(r"^(0|[1-9]\d*)$")
RE_MUKEY = re.compile(r"^[1-9]\d*$")
# Archivos con grande: true en el spec (millones de filas): se leen por partes de este tamaño.
FILAS_POR_PARTE = 250_000
# comparar_csv lee por partes los CSV de más de estos MB (en el orden en que están escritos).
MB_COMPARAR_POR_PARTES = 150


def parse_fecha(s):
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except Exception:
        return None


def sha256_archivo(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def hash_arbol(repo: Path, rutas, contenido=True) -> str:
    """Hash de un conjunto de archivos y carpetas (contenido, o nombre+tamaño+fecha)."""
    h = hashlib.sha256()
    for r in rutas:
        p = repo / r
        if p.is_file():
            archivos = [p]
        elif p.is_dir():
            archivos = sorted(x for x in p.rglob("*") if x.is_file() and "__pycache__" not in x.parts)
        else:
            h.update(f"falta:{r}".encode())
            continue
        for a in archivos:
            rel = a.relative_to(repo).as_posix()
            h.update(rel.encode())
            st = a.stat()
            if contenido and st.st_size < 50 * 1024 * 1024:
                h.update(sha256_archivo(a).encode())
            else:
                h.update(f"{st.st_size}:{int(st.st_mtime)}".encode())
    return h.hexdigest()


# --------------------------------------------------------------------------- período

class Periodo:
    """Período en años calendario (anio = año de la cosecha, CLAUDE.md §2 y §4)."""

    def __init__(self, cfg: dict):
        p = cfg.get("periodo") or {}
        self.y0 = int(p.get("anio_inicio", 2000))
        self.y1 = int(p.get("anio_fin", 2025))
        self.c0, self.c1 = str(self.y0), str(self.y1)
        self.inicio = dt.date(self.y0, 1, 1)
        self.fin = dt.date(self.y1, 12, 31)
        self.censos = [int(x) for x in (p.get("censos") or [2012, 2017, 2022])]

    def anios(self):
        return [str(y) for y in range(self.y0, self.y1 + 1)]

    def ventana(self, desde=None):
        w0 = self.inicio
        if desde:
            d = parse_fecha(desde)
            if d and d > w0:
                w0 = d
        return w0, self.fin

    def esperados(self, temporal: str, desde=None) -> int:
        w0, w1 = self.ventana(desde)
        if w0 > w1:
            return 0
        dias = (w1 - w0).days + 1
        if temporal == "diario":
            return dias
        if temporal == "16d":
            return math.ceil(dias / 16)
        if temporal == "8d":
            return math.ceil(dias / 8)
        if temporal == "semanal":
            return math.ceil(dias / 7)
        if temporal == "mensual":
            return (w1.year - w0.year) * 12 + (w1.month - w0.month) + 1
        if temporal in ("anual", "lista_anios"):
            return sum(1 for y in range(self.y0, self.y1 + 1) if w0 <= dt.date(y, 1, 1) <= w1)
        if temporal == "censo":
            return sum(1 for y in self.censos if w0 <= dt.date(y, 1, 1) <= w1)
        return 1


# --------------------------------------------------------------------------- contexto

class Ctx:
    def __init__(self, repo: Path, spec_dir: Path, cache: Path, python: str | None, red: bool):
        self.repo = repo
        self.spec_dir = spec_dir
        self.cache = cache
        self.cache.mkdir(parents=True, exist_ok=True)
        self.python = python
        self.red = red
        self.cfg = yaml.safe_load((repo / "config" / "config.yaml").read_text(encoding="utf-8"))
        self.ent = yaml.safe_load((spec_dir / "entregables.yaml").read_text(encoding="utf-8"))
        self.res = yaml.safe_load((spec_dir / "research.yaml").read_text(encoding="utf-8"))
        self.periodo = Periodo(self.cfg)
        self.cultivos = list((self.cfg.get("cultivos") or {}).keys())
        # Estados de la zona: {"IA": {"fips": "19", "nombre": "Iowa", "condados": 99}, ...}
        self.estados = {}
        for alfa, e in ((self.cfg.get("zona") or {}).get("estados") or {}).items():
            e = e or {}
            self.estados[str(alfa)] = {"fips": str(e.get("fips", "")).zfill(2), "nombre": str(e.get("nombre", alfa)),
                                       "condados": e.get("condados")}
        self.fips_estados = {e["fips"] for e in self.estados.values()}
        self.conversiones = self.cfg.get("conversiones") or {}
        self.catalogo = {}
        with open(spec_dir / "catalogo.csv", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                self.catalogo[r["id"]] = r
        self.fips = None            # set de fips válidos (de condados.csv)
        self.fips_msg = "falta data/reference/condados.csv válido (tarea base)"
        self.avisos = []
        self.manifest = None
        self.manifest_err = None
        # Unidades que no son condados (lotes, píxeles): {unidad: {"n", "claves", "archivo", "set"}}
        self.unidades = {}
        self.unidades_msg = {}

    def peso_prioridad(self, cat_id):
        pesos = self.ent["puntaje"]["pesos_prioridad"]
        if cat_id and cat_id in self.catalogo:
            return float(pesos.get(self.catalogo[cat_id]["prioridad"], self.ent["puntaje"]["peso_sin_catalogo"]))
        return float(self.ent["puntaje"]["peso_sin_catalogo"])

    @property
    def n_fips(self):
        if self.fips:
            return len(self.fips)
        esperados = sum(int(e["condados"]) for e in self.estados.values() if str(e.get("condados") or "").isdigit())
        return max(1, esperados)

    @property
    def n_estados(self):
        return max(1, len(self.estados))


class Checks:
    """Acumula checks con id único: puntos, máximo, ok y mensaje."""

    def __init__(self):
        self.items = {}

    def add(self, cid, tarea, pts, mx, msg="", catalogo=None):
        pts = max(0.0, min(float(pts), float(mx)))
        self.items[cid] = {
            "tarea": tarea,
            "pts": round(pts, 4),
            "max": round(float(mx), 4),
            "ok": pts >= mx - 1e-9,
            "msg": msg,
        }
        if catalogo:
            self.items[cid]["catalogo"] = catalogo


# --------------------------------------------------------------------------- CSV

def leer_csv(path: Path):
    try:
        raw = path.read_bytes()
    except Exception as e:
        return None, [f"no se pudo leer: {e}"]
    if raw.startswith(b"\xef\xbb\xbf"):
        return None, ["el archivo tiene BOM: guardalo como UTF-8 sin BOM"]
    try:
        texto = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None, ["no está en UTF-8"]
    if not texto.strip():
        return None, ["el archivo está vacío"]
    try:
        df = pd.read_csv(io.StringIO(texto), dtype=str, keep_default_na=False, na_filter=False)
    except Exception as e:
        return None, [f"no se pudo parsear como CSV con separador ',': {e}"]
    df.columns = [str(c) for c in df.columns]
    for c in df.columns:
        df[c] = df[c].astype(str).str.strip()
    return df, []


def tiempos_de(df: pd.DataFrame, temporal: str):
    """Serie de fechas (date) que ubica cada fila en el tiempo, o None si no aplica."""
    if temporal in ("diario", "16d", "8d", "semanal") and "fecha" in df.columns:
        return df["fecha"].map(parse_fecha)
    if temporal == "mensual" and "mes" in df.columns:
        return df["mes"].map(lambda s: parse_fecha(f"{s}-01") if RE_MES.match(s or "") else None)
    if temporal in ("anual", "lista_anios") and "anio" in df.columns:
        return df["anio"].map(lambda s: dt.date(int(s), 1, 1) if RE_ANIO.match(s or "") else None)
    if temporal == "censo" and "anio_censo" in df.columns:
        return df["anio_censo"].map(lambda s: dt.date(int(s), 1, 1) if RE_ANIO.match(s or "") else None)
    return None


def contrato(df: pd.DataFrame, af: dict, ctx: Ctx, duplicados=True):
    """Valida el contrato del CLAUDE.md §4. Devuelve (errores, avisos)."""
    errores, avisos = [], []
    cols = list(df.columns)
    malas = [c for c in cols if not SNAKE.match(c)]
    if malas:
        errores.append(f"columnas que no son snake_case: {malas[:5]}")
    if len(set(cols)) != len(cols):
        errores.append("hay columnas repetidas")
    claves = af.get("claves", [])
    if cols[: len(claves)] != claves:
        errores.append(f"las primeras columnas tienen que ser {claves} (hay {cols[:len(claves)]})")
        return errores, avisos
    for k in claves:
        vac = (df[k] == "").sum()
        if vac:
            errores.append(f"{vac} filas con la clave '{k}' vacía")
    if "fips" in claves:
        if ctx.fips is None and af["ruta"] != "data/reference/condados.csv":
            errores.append(ctx.fips_msg)
        else:
            mal = ~df["fips"].str.match(RE_FIPS)
            if mal.any():
                errores.append(f"{mal.sum()} fips que no son 5 dígitos con ceros a la izquierda (ej. {df['fips'][mal].iloc[0]!r})")
            elif ctx.fips is not None:
                fuera = ~df["fips"].isin(ctx.fips)
                if fuera.any():
                    errores.append(f"{fuera.sum()} filas con fips que no está en condados.csv (ej. {df['fips'][fuera].iloc[0]})")
    if "fips_estado" in claves:
        mal = ~df["fips_estado"].str.match(RE_FIPS_ESTADO)
        if mal.any():
            errores.append(f"{mal.sum()} fips_estado que no son 2 dígitos (ej. {df['fips_estado'][mal].iloc[0]!r})")
        else:
            fuera = ~df["fips_estado"].isin(ctx.fips_estados)
            if fuera.any():
                errores.append(f"fips_estado que no son estados de config.yaml: {sorted(df['fips_estado'][fuera].unique())[:5]} (usar {sorted(ctx.fips_estados)})")
    if "id_lote" in claves:
        m = df["id_lote"].str.extract(RE_ID_LOTE)
        mal = m[0].isna()
        if mal.any():
            errores.append(f"{mal.sum()} id_lote que no son <fips>_<id del CSB> con letras y números (ej. {df['id_lote'][mal].iloc[0]!r})")
        elif "fips" in claves:
            otro = m[0] != df["fips"]
            if otro.any():
                errores.append(f"{otro.sum()} filas donde id_lote no empieza con su fips (ej. {df['id_lote'][otro].iloc[0]} con fips {df['fips'][otro].iloc[0]})")
    for k, rx, txt in (("px_id", RE_ENTERO_NN, "enteros sin ceros a la izquierda"), ("mukey", RE_MUKEY, "enteros positivos")):
        if k in claves:
            mal = ~df[k].str.match(rx)
            if mal.any():
                errores.append(f"{mal.sum()} valores de '{k}' que no son {txt} (ej. {df[k][mal].iloc[0]!r})")
    for k in ("anio", "anio_censo"):
        if k in claves:
            bad = ~df[k].str.match(RE_ANIO)
            if bad.any():
                errores.append(f"{bad.sum()} valores de '{k}' que no son un año de 4 dígitos (ej. {df[k][bad].iloc[0]!r})")
            else:
                anios = df[k].astype(int)
                fuera = (anios < ctx.periodo.y0) | (anios > ctx.periodo.y1)
                if fuera.any():
                    avisos.append(f"{fuera.sum()} filas con {k} fuera del período {ctx.periodo.y0}–{ctx.periodo.y1} (no suman)")
    if "ventana" in claves:
        m = df["ventana"].str.extract(RE_VENTANA)
        bad = m[0].isna()
        if not bad.all():
            y0 = pd.to_numeric(m[0], errors="coerce")
            y1 = pd.to_numeric(m[1], errors="coerce")
            bad = bad | ((y1 - y0) != 7)
        if bad.any():
            errores.append(f"{bad.sum()} ventanas mal escritas (AAAA-AAAA de 8 años, ej. 2018-2025; hay {df['ventana'][bad].iloc[0]!r})")
    if "fecha" in claves:
        fechas = df["fecha"].map(lambda s: parse_fecha(s) if RE_FECHA.match(s or "") else None)
        if fechas.isna().any():
            errores.append(f"{fechas.isna().sum()} fechas que no son AAAA-MM-DD válidas (ej. {df['fecha'][fechas.isna()].iloc[0]!r})")
        elif "anio" in claves and not errores:
            anio_f = fechas.map(lambda d: f"{d.year:04d}")
            mal = anio_f != df["anio"]
            if mal.any():
                errores.append(f"{mal.sum()} filas donde anio no es el año calendario de la fecha (ej. {df['fecha'][mal].iloc[0]} con anio {df['anio'][mal].iloc[0]})")
    if "mes" in claves:
        ok = df["mes"].str.match(RE_MES)
        fechas = df["mes"].map(lambda s: parse_fecha(f"{s}-01") if RE_MES.match(s or "") else None)
        if (~ok).any() or fechas.isna().any():
            errores.append("hay valores de 'mes' que no son AAAA-MM")
        elif "anio" in claves and not errores:
            mal = df["mes"].str[:4] != df["anio"]
            if mal.any():
                errores.append(f"{mal.sum()} filas donde anio no es el año calendario del mes (ej. {df['mes'][mal].iloc[0]} con anio {df['anio'][mal].iloc[0]})")
    if "cultivo" in claves:
        fuera = ~df["cultivo"].isin(ctx.cultivos)
        if fuera.any():
            errores.append(f"cultivos que no están en config.yaml: {sorted(df['cultivo'][fuera].unique())[:5]} (usar {ctx.cultivos})")
    if not errores:
        for u, d in (ctx.ent.get("unidades") or {}).items():
            cu = list(d.get("claves") or [])
            if not cu or not set(cu) <= set(claves) or af["ruta"] == d.get("archivo"):
                continue
            info = ctx.unidades.get(u)
            if info is None:
                errores.append(ctx.unidades_msg.get(u, f"falta el archivo que define la unidad '{u}'"))
                continue
            fuera = ~_clave_texto(df, cu).isin(info["set"])
            if fuera.any():
                ej = df[cu][fuera].iloc[0].tolist()
                errores.append(f"{fuera.sum()} filas con {' + '.join(cu)} que no están en {info['archivo']} (ej. {ej})")
    if claves and not errores and duplicados:
        dup = df.duplicated(subset=claves, keep=False)
        if dup.any():
            errores.append(f"{dup.sum()} filas con claves duplicadas ({claves})")
    prohibidos = set(ctx.ent["contrato"]["valores_relleno_prohibidos"])
    no_clave = [c for c in cols if c not in claves]
    if no_clave:
        sub = df[no_clave]
        # flag_* guarda a propósito los códigos originales de la fuente, ej. (D) de NASS
        con_relleno = [c for c in no_clave if not c.startswith("flag_") and sub[c].isin(prohibidos).any()]
        if con_relleno:
            errores.append(f"valores de relleno (-9999, NaN, NA, (D), (Z)...) en {con_relleno[:5]}: los faltantes van como celda vacía (el código va en flag_*)")
        con_coma = [c for c in no_clave if sub[c].str.match(RE_COMA_DECIMAL).any()]
        if con_coma:
            errores.append(f"decimales con coma en {con_coma[:5]}: usar punto")
    for sub in af.get("columnas_prohibidas", []):
        malas = [c for c in cols if sub in c]
        if malas:
            motivo = af.get("motivo_prohibidas") or "no sacar tendencias ni anomalías acá (CLAUDE.md §6.2)"
            errores.append(f"columnas prohibidas en este archivo ({malas}): {motivo}")
    return errores, avisos


def columnas_de_spec(af: dict, df_cols):
    """Expande la lista de columnas del spec (incluye patrones verano_*_pct)."""
    out = []
    for c in af.get("columnas", []):
        if "patron" in c:
            rx = re.compile("^" + re.escape(c["patron"]).replace(r"\*", "[a-z0-9_]+") + "$")
            nombres = [x for x in df_cols if rx.match(x)] if df_cols is not None else []
            out.append((c, nombres))
        else:
            out.append((c, [c["nombre"]]))
    return out


def evaluar_valores(df, nombre, cspec, af, ctx, tiempos):
    """Devuelve (fraccion_datos 0..1, mensaje, stats)."""
    if nombre not in df.columns:
        return 0.0, f"falta la columna '{nombre}'", None
    s = df[nombre]
    vacio = s == ""
    tipo = cspec.get("tipo", "numero")
    temporal = af["temporal"]
    stats = {"faltantes_pct": round(100.0 * vacio.mean(), 3) if len(s) else 100.0}
    if tipo == "numero":
        vals = pd.to_numeric(s.where(~vacio), errors="coerce")
        no_num = (~vacio) & vals.isna()
        if no_num.any():
            return 0.0, f"'{nombre}': {no_num.sum()} valores no numéricos (ej. {s[no_num].iloc[0]!r})", stats
        rango = cspec.get("rango")
        if rango:
            lo, hi = float(rango[0]), float(rango[1])
            fuera = (~vacio) & ((vals < lo) | (vals > hi))
            n_llenos = max(1, int((~vacio).sum()))
            if fuera.sum() / n_llenos > ctx.ent["puntaje"]["tolerancia_fuera_de_rango"]:
                return 0.0, f"'{nombre}': {fuera.sum()} valores fuera del rango físico [{lo}, {hi}] (ej. {vals[fuera].iloc[0]})", stats
        if (~vacio).sum() >= 20 and vals[~vacio].nunique() <= 1:
            return 0.0, f"'{nombre}': el mismo valor en todas las filas (¿relleno?)", stats
    elif tipo == "categoria":
        validos = set(cspec.get("valores", []))
        malos = (~vacio) & ~s.isin(validos)
        if malos.any():
            return 0.0, f"'{nombre}': valores fuera de la lista {sorted(validos)[:6]}… (ej. {s[malos].iloc[0]!r})", stats
    elif tipo == "fecha":
        malos = (~vacio) & s.map(lambda x: parse_fecha(x) is None if x else False)
        if malos.any():
            return 0.0, f"'{nombre}': fechas inválidas (ej. {s[malos].iloc[0]!r})", stats
    if cspec.get("sin_cobertura"):
        # Columna obligatoria pero mayormente vacía por diseño (ej. flag_nass)
        return 1.0, "", stats
    # cobertura en la ventana de la fuente
    desde = cspec.get("desde") or af.get("desde")
    w0, w1 = ctx.periodo.ventana(desde)
    if tiempos is not None:
        en_ventana = tiempos.map(lambda d: d is not None and w0 <= d <= w1)
    else:
        en_ventana = pd.Series(True, index=df.index)
    llenos = int(((~vacio) & en_ventana).sum())
    esperados, msg_u = esperados_de(af, ctx, temporal, desde, int(en_ventana.sum()))
    if msg_u:
        return 0.0, f"'{nombre}': {msg_u}", stats
    umbral = float(af.get("umbral_cobertura", ctx.ent["puntaje"]["umbral_cobertura"]))
    cov = llenos / esperados if esperados else 0.0
    frac = min(1.0, cov / umbral) if umbral > 0 else 1.0
    no_vacio = s[~vacio]
    if tiempos is not None and len(no_vacio):
        t = tiempos[~vacio].dropna()
        if len(t):
            stats["desde"], stats["hasta"] = min(t), max(t)
    msg = "" if frac >= 1 else f"'{nombre}': cobertura {cov:.1%} ({llenos}/{esperados} celdas desde {w0}); con {umbral:.0%} suma completo"
    return frac, msg, stats


def esperados_de(af, ctx, temporal, desde, filas_en_ventana):
    """Celdas esperadas de una columna en su ventana. Devuelve (esperados, mensaje si la unidad no está definida)."""
    unidad = af.get("unidad") or "condado"
    if temporal == "lista_anios":
        esperados = ctx.periodo.esperados(temporal, desde)
    elif unidad == "fila":
        esperados = filas_en_ventana
    else:
        if unidad == "estado":
            n = ctx.n_estados
        elif unidad in (ctx.ent.get("unidades") or {}):
            info = ctx.unidades.get(unidad)
            if info is None:
                return 0, ctx.unidades_msg.get(unidad, f"falta el archivo que define la unidad '{unidad}'")
            n = info["n"]
        else:
            n = ctx.n_fips
        esperados = n * ctx.periodo.esperados(temporal, desde)
    mult = af.get("multiplica_por")
    if mult == "cultivos":
        esperados *= max(1, len(ctx.cultivos))
    elif isinstance(mult, int) and mult > 0:
        esperados *= mult
    return esperados, ""


def _clave_texto(df, claves):
    """Une las columnas clave de cada fila en un texto (para comparar contra un set)."""
    s = df[claves[0]].astype(str)
    for c in claves[1:]:
        s = s + "\x1f" + df[c].astype(str)
    return s


def cargar_unidades(ctx: Ctx):
    """Lee los archivos que definen las unidades del spec (por ejemplo lotes.csv y pixeles.csv)."""
    for u, d in (ctx.ent.get("unidades") or {}).items():
        ruta, claves = d.get("archivo"), list(d.get("claves") or [])
        ctx.unidades_msg[u] = f"falta {ruta} válido (define la unidad '{u}')"
        p = ctx.repo / ruta
        if not ruta or not claves or not p.exists():
            continue
        df, _ = leer_csv(p)
        if df is None or not len(df) or any(c not in df.columns for c in claves):
            continue
        if (df[claves] == "").any().any() or df.duplicated(subset=claves).any():
            ctx.unidades_msg[u] = f"{ruta} tiene claves vacías o repetidas ({claves})"
            continue
        ctx.unidades[u] = {"n": len(df), "claves": claves, "archivo": ruta, "set": set(_clave_texto(df, claves))}


def leer_csv_partes(path: Path, filas=None, usecols=None):
    """Lee un CSV grande por partes, con las mismas reglas que leer_csv. Si no se puede, levanta ValueError."""
    filas = filas or FILAS_POR_PARTE
    with open(path, "rb") as f:
        cab = f.read(3)
    if cab.startswith(b"\xef\xbb\xbf"):
        raise ValueError("el archivo tiene BOM: guardalo como UTF-8 sin BOM")
    if path.stat().st_size == 0:
        raise ValueError("el archivo está vacío")
    try:
        lector = pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False, encoding="utf-8",
                             chunksize=filas, usecols=usecols)
        for parte in lector:
            parte.columns = [str(c) for c in parte.columns]
            for c in parte.columns:
                parte[c] = parte[c].astype(str).str.strip()
            yield parte
    except UnicodeDecodeError:
        raise ValueError("no está en UTF-8") from None
    except pd.errors.EmptyDataError:
        raise ValueError("el archivo está vacío") from None
    except Exception as e:
        raise ValueError(f"no se pudo parsear como CSV con separador ',': {e}") from None


class ArchivoGrande:
    """Archivo grande que pasó el contrato: los especiales lo leen por partes (no se guarda en memoria)."""

    def __init__(self, path: Path, columns):
        self.path = path
        self.columns = list(columns)

    def partes(self, usecols=None, filas=None):
        return leer_csv_partes(self.path, filas=filas, usecols=usecols)


def _partes_de(obj, usecols):
    """Partes de un archivo leído (DataFrame) o grande (ArchivoGrande), solo con esas columnas."""
    if isinstance(obj, ArchivoGrande):
        return obj.partes(usecols=usecols)
    return [obj[usecols]]


class AcumValores:
    """Lo mismo que evaluar_valores, acumulado parte por parte (archivos grandes)."""

    def __init__(self, nombre, cspec, af, ctx):
        self.nombre, self.cspec, self.af, self.ctx = nombre, cspec, af, ctx
        self.tipo = cspec.get("tipo", "numero")
        self.desde = cspec.get("desde") or af.get("desde")
        self.w0, self.w1 = ctx.periodo.ventana(self.desde)
        self.n = self.vacios = self.fuera = self.llenos_ventana = self.filas_ventana = 0
        self.error = None
        self.ej_fuera = None
        self.unicos = set()
        self.tmin = self.tmax = None
        self.validos = set(cspec.get("valores", [])) if self.tipo == "categoria" else None

    def agregar(self, df, tiempos, en_ventana):
        if self.error:
            return
        nombre = self.nombre
        if nombre not in df.columns:
            self.error = f"falta la columna '{nombre}'"
            return
        s = df[nombre]
        vacio = s == ""
        self.n += len(s)
        self.vacios += int(vacio.sum())
        if self.tipo == "numero":
            vals = pd.to_numeric(s.where(~vacio), errors="coerce")
            no_num = (~vacio) & vals.isna()
            if no_num.any():
                self.error = f"'{nombre}': valores no numéricos (ej. {s[no_num].iloc[0]!r})"
                return
            rango = self.cspec.get("rango")
            if rango:
                lo, hi = float(rango[0]), float(rango[1])
                fuera = (~vacio) & ((vals < lo) | (vals > hi))
                k = int(fuera.sum())
                if k:
                    self.fuera += k
                    if self.ej_fuera is None:
                        self.ej_fuera = vals[fuera].iloc[0]
            if len(self.unicos) < 2:
                self.unicos.update(vals[~vacio].drop_duplicates().head(2).tolist())
        elif self.tipo == "categoria":
            malos = (~vacio) & ~s.isin(self.validos)
            if malos.any():
                self.error = f"'{nombre}': valores fuera de la lista {sorted(self.validos)[:6]}… (ej. {s[malos].iloc[0]!r})"
                return
        elif self.tipo == "fecha":
            malos = (~vacio) & s.map(lambda x: parse_fecha(x) is None if x else False)
            if malos.any():
                self.error = f"'{nombre}': fechas inválidas (ej. {s[malos].iloc[0]!r})"
                return
        if en_ventana is not None:
            self.filas_ventana += int(en_ventana.sum())
            self.llenos_ventana += int(((~vacio) & en_ventana).sum())
        else:
            self.filas_ventana += len(s)
            self.llenos_ventana += int((~vacio).sum())
        if tiempos is not None:
            tt = tiempos[~vacio].dropna()
            if len(tt):
                a, b = min(tt), max(tt)
                self.tmin = a if self.tmin is None else min(self.tmin, a)
                self.tmax = b if self.tmax is None else max(self.tmax, b)

    def resultado(self):
        nombre = self.nombre
        stats = {"faltantes_pct": round(100.0 * self.vacios / self.n, 3) if self.n else 100.0}
        if self.error:
            return 0.0, self.error, (None if self.error.startswith("falta la columna") else stats)
        if self.tipo == "numero":
            llenos = self.n - self.vacios
            rango = self.cspec.get("rango")
            if rango and self.fuera / max(1, llenos) > self.ctx.ent["puntaje"]["tolerancia_fuera_de_rango"]:
                lo, hi = float(rango[0]), float(rango[1])
                return 0.0, f"'{nombre}': {self.fuera} valores fuera del rango físico [{lo}, {hi}] (ej. {self.ej_fuera})", stats
            if llenos >= 20 and len(self.unicos) <= 1:
                return 0.0, f"'{nombre}': el mismo valor en todas las filas (¿relleno?)", stats
        if self.cspec.get("sin_cobertura"):
            return 1.0, "", stats
        esperados, msg_u = esperados_de(self.af, self.ctx, self.af["temporal"], self.desde, self.filas_ventana)
        if msg_u:
            return 0.0, f"'{nombre}': {msg_u}", stats
        umbral = float(self.af.get("umbral_cobertura", self.ctx.ent["puntaje"]["umbral_cobertura"]))
        cov = self.llenos_ventana / esperados if esperados else 0.0
        frac = min(1.0, cov / umbral) if umbral > 0 else 1.0
        if self.tmin is not None:
            stats["desde"], stats["hasta"] = self.tmin, self.tmax
        msg = "" if frac >= 1 else (f"'{nombre}': cobertura {cov:.1%} ({self.llenos_ventana}/{esperados} celdas desde "
                                    f"{self.w0}); con {umbral:.0%} suma completo")
        return frac, msg, stats


def evaluar_grande(ctx, af, p: Path):
    """Contrato y valores de un archivo grande, leído por partes.

    Devuelve (errores, avisos, coherencia, resultados por columna, columnas)."""
    errores, avisos, coh = [], [], []
    claves = af.get("claves", [])
    acum, cols, hashes, n = {}, None, [], 0
    try:
        for parte in leer_csv_partes(p):
            if cols is None:
                cols = list(parte.columns)
                for cspec, nombres in columnas_de_spec(af, cols):
                    for nm in nombres:
                        acum[nm] = AcumValores(nm, cspec, af, ctx)
            e, a = contrato(parte, af, ctx, duplicados=False)
            if e:
                errores = [f"filas {n + 1}–{n + len(parte)}: {x}" for x in e]
                break
            avisos.extend(a)
            c = evaluar_coherencia(parte, af)
            if c:
                coh = c
                break
            if claves:
                hashes.append(pd.util.hash_pandas_object(parte[claves], index=False).to_numpy())
            tiempos = tiempos_de(parte, af["temporal"])
            en_v = {}
            for ac in acum.values():
                k = (ac.w0, ac.w1)
                if tiempos is not None and k not in en_v:
                    en_v[k] = tiempos.map(lambda d, a0=ac.w0, a1=ac.w1: d is not None and a0 <= d <= a1)
                ac.agregar(parte, tiempos, en_v.get(k) if tiempos is not None else None)
            n += len(parte)
    except ValueError as e:
        errores = [str(e)]
    if not errores and not n:
        errores = ["el archivo está vacío"]
    if not errores and hashes:
        h = np.concatenate(hashes)
        rep = len(h) - len(np.unique(h))
        if rep:
            errores.append(f"{rep} filas con claves duplicadas ({claves})")
    avisos = list(dict.fromkeys(avisos))[:10]
    if errores or coh:
        return errores, avisos, coh, None, cols
    return errores, avisos, coh, {nm: ac.resultado() for nm, ac in acum.items()}, cols


def evaluar_coherencia(df, af):
    """Reglas 'a <= b' o 'a <= b <= c'. Devuelve lista de errores."""
    errores = []
    for regla in af.get("coherencia", []) or []:
        partes = [p.strip() for p in regla.split("<=")]
        if any(p not in df.columns for p in partes):
            continue
        vals = [pd.to_numeric(df[p], errors="coerce") for p in partes]
        mask = pd.Series(True, index=df.index)
        for v in vals:
            mask &= v.notna()
        if mask.sum() < 5:
            continue
        ok = pd.Series(True, index=df.index)
        for a, b in zip(vals, vals[1:]):
            ok &= (a <= b + 1e-6)
        frac = ok[mask].mean()
        if frac < 0.99:
            errores.append(f"incoherencia: '{regla}' no se cumple en {1 - frac:.1%} de las filas")
    for est in af.get("estacionalidad", []) or []:
        col = est["columna"]
        if col not in df.columns or "mes" not in df.columns:
            continue
        v = pd.to_numeric(df[col], errors="coerce")
        mes = pd.to_numeric(df["mes"].str[5:7], errors="coerce")
        alto = v[mes.isin(est["mayor"])].mean()
        bajo = v[mes.isin(est["menor"])].mean()
        if pd.notna(alto) and pd.notna(bajo) and not alto > bajo:
            errores.append(f"incoherencia: '{col}' no es mayor en los meses {est['mayor']} que en {est['menor']} (hemisferio norte)")
    return errores


# --------------------------------------------------------------------------- data card

def leer_data_card(path: Path, ctx: Ctx):
    """Devuelve (filas de la tabla, errores de estructura)."""
    if not path.exists():
        return [], [f"falta {path.as_posix()}"]
    txt = path.read_text(encoding="utf-8", errors="replace")
    errores = []
    pedidas = ctx.ent["data_card"]["columnas_tabla"]
    filas = []
    lineas = txt.splitlines()
    i = 0
    encontrada = False
    while i < len(lineas):
        l = lineas[i].strip()
        if l.startswith("|") and i + 1 < len(lineas) and re.match(r"^\|?\s*:?-{2,}", lineas[i + 1].strip()):
            enc = [norm(x).replace(" ", "_") for x in l.strip("|").split("|")]
            if all(p in enc for p in pedidas):
                encontrada = True
                j = i + 2
                while j < len(lineas) and lineas[j].strip().startswith("|"):
                    celdas = [x.strip() for x in lineas[j].strip().strip("|").split("|")]
                    if len(celdas) >= len(enc):
                        filas.append({enc[k]: celdas[k].strip("` ") for k in range(len(enc))})
                    j += 1
                i = j
                continue
        i += 1
    if not encontrada:
        errores.append(f"no tiene la tabla de columnas con encabezados {pedidas}")
    for sec in ctx.ent["data_card"]["secciones"]:
        m = re.search(r"^#{2,4}\s*" + re.escape(sec) + r"\s*$", txt, re.M | re.I)
        if not m:
            errores.append(f"falta la sección '## {sec}'")
            continue
        resto = txt[m.end():]
        sig = re.search(r"^#{1,4}\s", resto, re.M)
        cuerpo = resto[: sig.start()] if sig else resto
        if not cuerpo.strip():
            errores.append(f"la sección '{sec}' está vacía")
    return filas, errores


def fmt_tiempo(d: dt.date, temporal: str):
    if d is None:
        return None
    if temporal in ("anual", "lista_anios", "censo"):
        return f"{d.year:04d}"
    if temporal == "mensual":
        return d.strftime("%Y-%m")
    return d.isoformat()


def doc_ok(filas, ruta_archivo, nombre, cat_id, stats, af, ctx):
    """¿La columna está documentada y lo documentado coincide con los datos?"""
    base = Path(ruta_archivo).name
    cand = [f for f in filas if norm(f.get("columna", "")) == norm(nombre)
            and (norm(f.get("archivo", "")) in (norm(base), norm(ruta_archivo), norm(Path(base).stem)))]
    if not cand:
        return False, f"'{nombre}' ({base}) no está en la tabla del data card"
    f = cand[0]
    if cat_id and norm(f.get("id_catalogo", "")).upper() != cat_id.upper() and cat_id.upper() not in f.get("id_catalogo", "").upper():
        return False, f"'{nombre}': id_catalogo debería ser {cat_id}"
    if not f.get("unidad", "").strip():
        return False, f"'{nombre}': falta la unidad en el data card"
    if not f.get("fuente", "").strip():
        return False, f"'{nombre}': falta la fuente en el data card"
    if stats is None:
        return False, f"'{nombre}': sin datos para comparar"
    try:
        doc = float(f.get("faltantes_pct", "").replace("%", "").replace(",", ".").strip())
    except ValueError:
        return False, f"'{nombre}': faltantes_pct no es un número"
    real = stats.get("faltantes_pct", 100.0)
    if abs(doc - real) > ctx.ent["data_card"]["tolerancia_faltantes_pct"]:
        return False, f"'{nombre}': el data card dice {doc}% de faltantes y en los datos hay {real:.1f}%"
    temporal = af["temporal"]
    if temporal not in ("estatico", "ventana") and stats.get("desde"):
        for campo in ("desde", "hasta"):
            real_t = fmt_tiempo(stats[campo], temporal)
            doc_t = f.get(campo, "").strip()
            if temporal in ("diario", "16d", "8d", "semanal"):
                ok = doc_t[:7] == real_t[:7]
            else:
                ok = doc_t == real_t
            if not ok:
                return False, f"'{nombre}': {campo} documentado '{doc_t}' y en los datos es '{real_t}'"
    return True, ""


# --------------------------------------------------------------------------- manifest y raw

def leer_manifest(ctx: Ctx):
    p = ctx.repo / "manifest.csv"
    esperado = ["paquete", "archivo", "fuente", "producto", "version", "fecha_descarga", "consulta_o_url"]
    if not p.exists():
        return [], "falta manifest.csv"
    try:
        with open(p, encoding="utf-8", newline="") as f:
            r = csv.reader(f)
            enc = next(r, [])
            if [x.strip() for x in enc] != esperado:
                return [], f"el encabezado de manifest.csv tiene que ser {','.join(esperado)}"
            filas = [dict(zip(esperado, [x.strip() for x in fila])) for fila in r if any(x.strip() for x in fila)]
        return filas, None
    except Exception as e:
        return [], f"no se pudo leer manifest.csv: {e}"


def ruta_manifest(archivo: str, pkg: str) -> str:
    a = archivo.replace("\\", "/").strip().lstrip("./")
    if a.startswith("data/raw/"):
        return a
    if a.startswith(f"{pkg}/"):
        return f"data/raw/{a}"
    return f"data/raw/{pkg}/{a}"


def archivos_raw(ctx: Ctx, pkg: str):
    d = ctx.repo / "data" / "raw" / pkg
    if not d.exists():
        return []
    out = []
    for p in d.rglob("*"):
        if p.is_file() and not p.name.startswith("_") and not p.name.startswith(".") and not any(x.startswith("_") for x in p.relative_to(d).parts[:-1]):
            out.append(p.relative_to(ctx.repo).as_posix())
    return sorted(out)


def check_manifest(ctx: Ctx, pkg: str):
    """Devuelve (ok_manifest, mensaje, hay_raw_registrado)."""
    filas, err = ctx.manifest, ctx.manifest_err
    if err:
        return False, err, False
    propias = [f for f in filas if f["paquete"] == pkg]
    en_manifest = {ruta_manifest(f["archivo"], pkg): f for f in propias}
    en_disco = set(archivos_raw(ctx, pkg))
    registrados_existentes = [r for r in en_manifest if r in en_disco]
    hay_raw = len(registrados_existentes) > 0
    problemas = []
    sin_fila = sorted(en_disco - set(en_manifest))
    if sin_fila:
        problemas.append(f"{len(sin_fila)} archivos de data/raw/{pkg}/ sin fila en manifest.csv (ej. {sin_fila[0]})")
    sin_archivo = sorted(set(en_manifest) - en_disco)
    if sin_archivo:
        problemas.append(f"{len(sin_archivo)} filas del manifest sin archivo (ej. {sin_archivo[0]})")
    for r, f in en_manifest.items():
        faltan = [k for k in ("fuente", "producto", "fecha_descarga", "consulta_o_url") if not f.get(k)]
        if faltan:
            problemas.append(f"fila de {r} sin {faltan}")
            break
        if not RE_FECHA.match(f.get("fecha_descarga", "")):
            problemas.append(f"fecha_descarga de {r} no es AAAA-MM-DD")
            break
    if not en_disco:
        problemas.append(f"no hay archivos en data/raw/{pkg}/")
    return (not problemas), "; ".join(problemas), hay_raw


# --------------------------------------------------------------------------- reproducibilidad

def archivos_salida(ctx: Ctx, pspec: dict):
    out = []
    for s in pspec.get("salidas", []):
        p = ctx.repo / s
        if p.is_file() and p.suffix.lower() == ".csv":
            out.append(p)
        elif p.is_dir():
            out.extend(sorted(x for x in p.rglob("*.csv") if x.is_file()))
    return out


def clave_repro(ctx: Ctx, pkg: str, pspec: dict) -> str:
    rutas_codigo = [f"src/{pkg}", "src/common", "config", "data/reference"]
    if pkg == "merge":
        rutas_codigo = ["src/merge.py", "src/common", "config", "data/processed"]
    h = hashlib.sha256()
    h.update(hash_arbol(ctx.repo, rutas_codigo, contenido=True).encode())
    h.update(hash_arbol(ctx.repo, [f"data/raw/{pkg}", f"data/interim/{pkg}"], contenido=False).encode())
    for a in archivos_salida(ctx, pspec):
        h.update(a.relative_to(ctx.repo).as_posix().encode())
        h.update(sha256_archivo(a).encode())
    return h.hexdigest()


def comparar_csv_partes(a: Path, b: Path):
    """Compara dos CSV grandes fila a fila, en el orden en que están escritos."""
    try:
        pa, pb = leer_csv_partes(a), leer_csv_partes(b)
        fila = 0
        while True:
            da, db = next(pa, None), next(pb, None)
            if da is None and db is None:
                return True, ""
            if da is None or db is None or len(da) != len(db):
                return False, f"{a.name}: cambia la cantidad de filas"
            if list(da.columns) != list(db.columns):
                return False, f"{a.name}: cambian las columnas"
            da, db = da.reset_index(drop=True), db.reset_index(drop=True)
            for c in da.columns:
                if (da[c] == db[c]).all():
                    continue
                na = pd.to_numeric(da[c].replace("", None), errors="coerce")
                nb = pd.to_numeric(db[c].replace("", None), errors="coerce")
                if na.notna().sum() == (da[c] != "").sum() and nb.notna().sum() == (db[c] != "").sum():
                    iguales = ((na - nb).abs() <= 1e-6 * (1 + nb.abs())) | (na.isna() & nb.isna())
                    if iguales.all():
                        continue
                return False, (f"{a.name}: cambian los valores de '{c}' cerca de la fila {fila + 1} (los archivos "
                               "grandes se comparan fila a fila: escribilos ordenados por las claves)")
            fila += len(da)
    except ValueError as e:
        return False, f"no se pudo leer {a.name}: {e}"


def comparar_csv(a: Path, b: Path):
    try:
        if a.stat().st_size == b.stat().st_size and sha256_archivo(a) == sha256_archivo(b):
            return True, ""
        if max(a.stat().st_size, b.stat().st_size) > MB_COMPARAR_POR_PARTES * 1e6:
            return comparar_csv_partes(a, b)
    except OSError:
        pass
    da, ea = leer_csv(a)
    db, eb = leer_csv(b)
    if da is None or db is None:
        return False, f"no se pudo leer {a.name}: {ea or eb}"
    if list(da.columns) != list(db.columns):
        return False, f"{a.name}: cambian las columnas"
    if len(da) != len(db):
        return False, f"{a.name}: cambia la cantidad de filas ({len(db)} → {len(da)})"
    claves = [c for c in ("fips", "fips_estado", "id_lote", "px_id", "mukey", "anio", "anio_censo", "ventana", "cultivo",
                          "fecha", "mes", "producto", "sensor") if c in da.columns]
    if claves:
        da = da.sort_values(claves).reset_index(drop=True)
        db = db.sort_values(claves).reset_index(drop=True)
    for c in da.columns:
        if (da[c] == db[c]).all():
            continue
        na = pd.to_numeric(da[c].replace("", None), errors="coerce")
        nb = pd.to_numeric(db[c].replace("", None), errors="coerce")
        if na.notna().sum() == (da[c] != "").sum() and nb.notna().sum() == (db[c] != "").sum():
            iguales = ((na - nb).abs() <= 1e-6 * (1 + nb.abs())) | (na.isna() & nb.isna())
            if iguales.all():
                continue
        return False, f"{a.name}: cambian los valores de '{c}'"
    return True, ""


def reproducir(ctx: Ctx, pkg: str, pspec: dict, timeout_s: int):
    """Corre process.py del paquete y verifica que regenera los mismos CSV."""
    script = ctx.repo / pspec.get("process", f"src/{pkg}/process.py")
    salidas = archivos_salida(ctx, pspec)
    if not salidas:
        return None, "sin salidas para verificar"
    if not script.exists():
        return False, f"falta {script.relative_to(ctx.repo).as_posix()}"
    python = ctx.python or sys.executable
    respaldo = Path(tempfile.mkdtemp(prefix=f"repro_{pkg}_"))
    rels = [s.relative_to(ctx.repo) for s in salidas]
    try:
        for r in rels:
            (respaldo / r).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ctx.repo / r, respaldo / r)
            (ctx.repo / r).unlink()
        env = dict(os.environ, PYTHONPATH=str(ctx.repo), PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        try:
            pr = subprocess.run([python, str(script)], cwd=ctx.repo, env=env, capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=timeout_s)
        except subprocess.TimeoutExpired:
            return False, f"process.py tardó más de {timeout_s // 60} min"
        if pr.returncode != 0:
            cola = (pr.stderr or pr.stdout or "").strip().splitlines()[-6:]
            return False, "process.py falló: " + " | ".join(cola)
        for r in rels:
            nuevo = ctx.repo / r
            if not nuevo.exists():
                return False, f"process.py no volvió a generar {r.as_posix()}"
            ok, msg = comparar_csv(nuevo, respaldo / r)
            if not ok:
                return False, "process.py no reproduce los CSV: " + msg
        return True, "reproduce"
    finally:
        # Siempre se dejan las salidas como estaban antes del check.
        for r in rels:
            destino = ctx.repo / r
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(respaldo / r, destino)
        shutil.rmtree(respaldo, ignore_errors=True)


# --------------------------------------------------------------------------- fuentes (research)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/130.0 Safari/537.36 FieldShiftVerifier/1.0")


def norm_busqueda(t: str) -> str:
    t = t.replace("­", "")
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)
    t = sin_tildes(t).lower()
    t = (t.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
          .replace("–", "-").replace("—", "-").replace(" ", " "))
    t = re.sub(r"[ \t\r\n]+", " ", t)
    return t.strip()


def html_a_texto(h: str) -> str:
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?s)<!--.*?-->", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d|td|th)>", "\n", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    return htmllib.unescape(h)


class Fuentes:
    def __init__(self, ctx: Ctx, max_nuevas=60):
        self.dir = ctx.cache / "fuentes"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.red = ctx.red
        self.restantes = max_nuevas
        self.mem = {}

    def texto(self, url: str):
        if url in self.mem:
            return self.mem[url]
        f = self.dir / (hashlib.sha1(url.encode()).hexdigest() + ".json")
        if f.exists():
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                if d.get("ok") or (time.time() - d.get("cuando", 0) < 3600):
                    self.mem[url] = (d["ok"], d.get("texto") if d["ok"] else d.get("error"))
                    return self.mem[url]
            except Exception:
                pass
        if not self.red or self.restantes <= 0:
            return False, "sin verificar todavía (se verifica en la próxima pasada)"
        self.restantes -= 1
        ok, contenido = self._bajar(url)
        d = {"url": url, "ok": ok, "cuando": time.time()}
        if ok:
            d["texto"] = contenido
        else:
            d["error"] = contenido
        try:
            f.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        self.mem[url] = (ok, contenido)
        return ok, contenido

    def _bajar(self, url: str):
        try:
            import requests
        except ImportError:
            return False, "falta requests en el entorno del verificador"
        try:
            r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "es,en;q=0.8"},
                             timeout=(15, 60), stream=True, allow_redirects=True)
            if r.status_code >= 400:
                return False, f"HTTP {r.status_code}"
            buf = bytearray()
            for chunk in r.iter_content(1 << 16):
                buf.extend(chunk)
                if len(buf) > 40 * 1024 * 1024:
                    break
            datos = bytes(buf)
            ctype = r.headers.get("content-type", "").lower()
            if datos[:5] == b"%PDF-" or "pdf" in ctype:
                try:
                    from pypdf import PdfReader
                    lector = PdfReader(io.BytesIO(datos))
                    paginas = []
                    for i, pg in enumerate(lector.pages):
                        if i >= 400:
                            break
                        try:
                            paginas.append(pg.extract_text() or "")
                        except Exception:
                            pass
                    texto = "\n".join(paginas)
                except Exception as e:
                    return False, f"no se pudo leer el PDF: {e}"
            else:
                enc = r.encoding or "utf-8"
                try:
                    texto = datos.decode(enc, errors="replace")
                except LookupError:
                    texto = datos.decode("utf-8", errors="replace")
                if "html" in ctype or texto.lstrip()[:200].lower().find("<html") >= 0 or "<body" in texto[:5000].lower():
                    texto = html_a_texto(texto)
            texto = norm_busqueda(texto)
            if len(texto) < 50:
                return False, "la página no tiene texto legible (¿PDF escaneado o página con JavaScript?)"
            return True, texto[:5_000_000]
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"[:200]


@functools.lru_cache(maxsize=32)
def _plano(texto: str) -> str:
    return " " + " ".join(re.findall(r"[a-z0-9]+(?:[.,][0-9]+)?", texto)) + " "


def cita_en_texto(cita: str, texto: str) -> bool:
    c = norm_busqueda(cita).strip(" \"'.,;:")
    if len(c) < 15:
        return False
    if c in texto:
        return True
    palabras = re.findall(r"[a-z0-9]+(?:[.,][0-9]+)?", c)
    if len(palabras) < 4:
        return False
    tri = [" " + " ".join(palabras[i:i + 3]) + " " for i in range(len(palabras) - 2)]
    plano = _plano(texto)
    presentes = sum(1 for t in tri if t in plano)
    return presentes / len(tri) >= 0.85


def numero_en_cita(valor: str, cita: str) -> bool:
    nums = re.findall(r"-?\d+(?:[.,]\d+)?", str(valor))
    if not nums:
        return True
    c = norm_busqueda(cita)
    for n in nums:
        variantes = {n, n.replace(".", ","), n.replace(",", ".")}
        try:
            f = float(n.replace(",", "."))
            if f.is_integer():
                variantes.add(str(int(f)))
            variantes.add(("%g" % f))
            variantes.add(("%g" % f).replace(".", ","))
        except ValueError:
            pass
        if any(re.search(r"(?<![\d.,])" + re.escape(v.lstrip("-")) + r"(?![\d])", c) for v in variantes):
            return True
    return False


# --------------------------------------------------------------------------- especiales

def _norm_estado(s) -> str:
    return norm(s).replace(" ", "")


def _es_geotiff(p: Path):
    if not p.exists():
        return False, f"falta {p.name}"
    with open(p, "rb") as f:
        cab = f.read(4)
    if cab not in (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"):
        return False, f"{p.name} no es un GeoTIFF"
    if p.stat().st_size < 1024:
        return False, f"{p.name} es demasiado chico"
    return True, ""


def esp_zona_config(ctx, pkg, esp, archivos):
    df = archivos.get("data/reference/condados.csv")
    if df is None:
        return 0, "falta data/reference/condados.csv válido"
    if not ctx.estados:
        return 0, "config.yaml no tiene zona.estados"
    msgs = []
    por_prefijo = {e["fips"]: (alfa, e) for alfa, e in ctx.estados.items()}
    pref = df["fips"].str[:2]
    ajenos = sorted(set(pref) - set(por_prefijo))
    if ajenos:
        msgs.append(f"hay condados de estados que no están en config.yaml (fips {ajenos[:4]}): filtrar a la zona")
    for fp, (alfa, e) in por_prefijo.items():
        n = int((pref == fp).sum())
        esperado = e.get("condados")
        if str(esperado or "").isdigit() and n != int(esperado):
            msgs.append(f"{alfa}: hay {n} condados y se esperan {esperado}")
        elif n == 0:
            msgs.append(f"{alfa}: no hay condados")
    if "estado" in df.columns:
        validos = {e["fips"]: {_norm_estado(alfa), _norm_estado(e["nombre"]), e["fips"]} for alfa, e in ctx.estados.items()}
        malos = [f"{r['fips']}={r['estado']}" for _, r in df.iterrows()
                 if r["fips"][:2] in validos and _norm_estado(r["estado"]) not in validos[r["fips"][:2]]]
        if malos:
            msgs.append(f"la columna estado no coincide con los 2 primeros dígitos del fips: {malos[:4]}")
    return (0 if msgs else 1), "; ".join(msgs)


def esp_gpkg_condados(ctx, pkg, esp, archivos):
    p = ctx.repo / "data" / "reference" / "condados.gpkg"
    if not p.exists():
        return 0, "falta data/reference/condados.gpkg"
    with open(p, "rb") as f:
        if f.read(16) != b"SQLite format 3\x00":
            return 0, "condados.gpkg no es un GeoPackage (SQLite)"
    try:
        con = sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True)
        tablas = [r[0] for r in con.execute("SELECT table_name FROM gpkg_contents WHERE data_type='features'")]
        if not tablas:
            con.close()
            return 0, "condados.gpkg no tiene capas de features"
        n = con.execute(f'SELECT COUNT(*) FROM "{tablas[0]}"').fetchone()[0]
        con.close()
    except Exception as e:
        return 0, f"no se pudo leer condados.gpkg: {e}"
    df = archivos.get("data/reference/condados.csv")
    if df is not None and n != len(df):
        return 0, f"condados.gpkg tiene {n} polígonos y condados.csv {len(df)} filas"
    return 1, ""


def esp_anios_exactos(ctx, pkg, esp, archivos):
    df = archivos.get("data/reference/anios.csv")
    if df is None:
        return 0, "falta data/reference/anios.csv válido"
    need = ["inicio_temporada", "fin_temporada", "inicio_invierno_previo", "fin_invierno_previo"]
    if any(c not in df.columns for c in need):
        return 0, f"anios.csv tiene que tener las columnas {need}"
    v = ctx.cfg.get("ventanas") or {}
    t = v.get("temporada") or {"desde": "04-01", "hasta": "09-30"}
    inv = v.get("invierno_previo") or {"desde": "11-01", "hasta": "03-31"}
    esperado = {str(y): (f"{y}-{t['desde']}", f"{y}-{t['hasta']}", f"{y - 1}-{inv['desde']}", f"{y}-{inv['hasta']}")
                for y in range(ctx.periodo.y0, ctx.periodo.y1 + 1)}
    hay = {r["anio"]: tuple(r[c] for c in need) for _, r in df.iterrows()}
    malos = [a for a, val in esperado.items() if hay.get(a) != val]
    if malos:
        return 0, (f"años faltantes o con ventanas incorrectas: {malos[:4]} (temporada AAAA-{t['desde']} a "
                   f"AAAA-{t['hasta']}, invierno previo (AAAA-1)-{inv['desde']} a AAAA-{inv['hasta']})")
    return 1, ""


TEST_COMUNES = r'''
import csv, json, os, sys, tempfile
repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}
def cerca(a, b, tol):
    try:
        return abs(float(a) - float(b)) <= tol * abs(float(b))
    except Exception:
        return False
try:
    from src.common import fecha_a_anio
    casos = {"2023-07-15": 2023, "2000-01-01": 2000, "2025-09-30": 2025, "2010-04-01": 2010, "2016-02-29": 2016}
    malos = []
    for k, v in casos.items():
        r = fecha_a_anio(k)
        try:
            ok = int(r) == v
        except Exception:
            ok = False
        if not ok:
            malos.append((k, v, repr(r)))
    out["fecha_a_anio"] = "ok" if not malos else "da mal: " + str(malos[:3])
except Exception as e:
    out["fecha_a_anio"] = "error: %s: %s" % (type(e).__name__, e)
try:
    from src.common import bu_ac_a_kgha
    esperado = {"maiz": 62.77, "soja": 67.25, "trigo_invierno": 67.25, "avena": 35.87}
    malos = []
    for c, f in esperado.items():
        r = None
        for intento in (lambda: bu_ac_a_kgha(c), lambda: bu_ac_a_kgha(1.0, c), lambda: bu_ac_a_kgha(valor=1.0, cultivo=c)):
            try:
                r = intento()
                if callable(r):
                    r = r(1.0)
                break
            except TypeError:
                continue
        if not cerca(r, f, 0.005):
            malos.append((c, f, repr(r)))
    out["bu_ac_a_kgha"] = "ok" if not malos else "da mal (1 bu/ac en kg/ha): " + str(malos[:3])
except Exception as e:
    out["bu_ac_a_kgha"] = "error: %s: %s" % (type(e).__name__, e)
try:
    from src.common import acres_a_ha
    r = None
    for intento in (lambda: acres_a_ha(10.0), lambda: acres_a_ha() * 10.0):
        try:
            r = intento()
            break
        except TypeError:
            continue
    out["acres_a_ha"] = "ok" if cerca(r, 4.047, 0.002) else "acres_a_ha(10) da %r y tiene que dar 4.047" % (r,)
except Exception as e:
    out["acres_a_ha"] = "error: %s: %s" % (type(e).__name__, e)
try:
    from src.common import validar_csv
    with open(os.path.join(repo, "data", "reference", "condados.csv"), encoding="utf-8") as f:
        f0 = next(csv.DictReader(f))["fips"]
    tmp = tempfile.mkdtemp()
    def escribir(nombre, filas):
        p = os.path.join(tmp, nombre)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write("fips,anio,mes,prec_power_mm\n")
            for fila in filas:
                f.write(fila + "\n")
        return p
    bueno = escribir("prueba_mensual.csv", [f0 + ",2023,2023-07,85.2", f0 + ",2023,2023-08,40.0"])
    dup = escribir("prueba_dup_mensual.csv", [f0 + ",2023,2023-07,85.2", f0 + ",2023,2023-07,85.2"])
    inex = escribir("prueba_inex_mensual.csv", ["99999,2023,2023-07,85.2"])
    def rechaza(p):
        try:
            r = validar_csv(p)
        except Exception:
            return True
        return r is False or (isinstance(r, (list, tuple, set, dict)) and len(r) > 0)
    problemas = []
    try:
        r = validar_csv(bueno)
        if not (r is None or r is True or (isinstance(r, (list, tuple, set, dict)) and len(r) == 0)):
            problemas.append("rechaza un CSV correcto: " + str(r)[:120])
    except Exception as e:
        problemas.append("falla con un CSV correcto: %s: %s" % (type(e).__name__, e))
    if not rechaza(dup):
        problemas.append("acepta claves duplicadas")
    if not rechaza(inex):
        problemas.append("acepta un fips que no existe")
    out["validar_csv"] = "ok" if not problemas else "; ".join(problemas)
except Exception as e:
    out["validar_csv"] = "error: %s: %s" % (type(e).__name__, e)
try:
    from src.common import zonal_mean
    out["zonal_mean"] = "ok" if callable(zonal_mean) else "no es una función"
except Exception as e:
    out["zonal_mean"] = "error: %s: %s" % (type(e).__name__, e)
print("@@RESULTADO@@" + json.dumps(out, ensure_ascii=False))
'''


def esp_funciones_comunes(ctx, pkg, esp, archivos):
    if not (ctx.repo / "src" / "common").exists():
        return 0, "falta src/common/"
    if archivos.get("data/reference/condados.csv") is None:
        return 0, "primero hace falta condados.csv válido"
    python = ctx.python or sys.executable
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(TEST_COMUNES)
        prueba = f.name
    try:
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        pr = subprocess.run([python, prueba, str(ctx.repo)], cwd=ctx.repo, env=env, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=180)
    except subprocess.TimeoutExpired:
        return 0, "las pruebas de src/common tardaron más de 3 min"
    finally:
        os.unlink(prueba)
    m = re.search(r"@@RESULTADO@@(\{.*\})", pr.stdout or "")
    if not m:
        return 0, "no se pudo probar src/common: " + " | ".join((pr.stderr or "").strip().splitlines()[-4:])
    res = json.loads(m.group(1))
    oks = [k for k, v in res.items() if v == "ok"]
    malos = [f"{k}: {v}" for k, v in res.items() if v != "ok"]
    return len(oks) / 5.0, "; ".join(malos)


# Códigos del CDL que pide el CLAUDE.md §6.2, con palabras que tiene que tener su nombre
CLASES_CDL = {"1": ["corn", "maiz"], "5": ["soy", "soja"], "24": ["winter wheat", "trigo"],
              "26": ["dbl", "double", "doble"], "28": ["oats", "avena"], "36": ["alfalfa"],
              "37": ["hay", "heno"], "61": ["fallow", "barbecho"], "176": ["grass", "pasti", "pasture"]}


def esp_clases_cdl(ctx, pkg, esp, archivos):
    p = ctx.repo / "data" / "reference" / "clases_cdl.csv"
    if not p.exists():
        return 0, "falta data/reference/clases_cdl.csv"
    df, err = leer_csv(p)
    if df is None:
        return 0, "; ".join(err)
    need = ["codigo", "nombre", "grupo"]
    if any(c not in df.columns for c in need):
        return 0, f"clases_cdl.csv tiene que tener las columnas {need}"
    nombres = {(str(r["codigo"]).strip().lstrip("0") or "0"): norm(r["nombre"]) for _, r in df.iterrows()}
    malos = []
    for cod, palabras in CLASES_CDL.items():
        n = nombres.get(cod)
        if n is None:
            malos.append(f"falta el código {cod}")
        elif not any(k in n for k in palabras):
            malos.append(f"el código {cod} dice '{n}'")
    return (0 if malos else 1), "; ".join(malos[:5])


RINDES_BU = {"maiz": (20, 300), "soja": (5, 100), "trigo_invierno": (10, 150), "avena": (20, 200)}


def esp_consistencia_rendimiento(ctx, pkg, esp, archivos):
    df = archivos.get("data/processed/cultivos/produccion_anual.csv")
    if df is None:
        return 0, "falta produccion_anual.csv válido"
    need = ["produccion_bu", "sup_cosechada_ac", "rend_bu_ac", "cultivo"]
    if any(c not in df.columns for c in need):
        return 0, "faltan columnas para verificar el rendimiento"

    def num(c):
        return pd.to_numeric(df[c], errors="coerce")

    prod, sup, ren = num("produccion_bu"), num("sup_cosechada_ac"), num("rend_bu_ac")
    m = prod.notna() & sup.notna() & ren.notna() & (sup > 0) & (ren > 0)
    if m.sum() < 10:
        return 0, "menos de 10 filas completas para verificar"
    msgs = []
    rel = ((prod[m] / sup[m]) - ren[m]).abs() / ren[m]
    if (rel <= 0.10).mean() < 0.90:
        msgs.append(f"rend_bu_ac ≠ produccion_bu / sup_cosechada_ac en {(rel > 0.10).mean():.0%} de las filas")
    fuera = 0
    for cult, (lo, hi) in RINDES_BU.items():
        mm = m & (df["cultivo"] == cult)
        fuera += int(((ren[mm] < lo) | (ren[mm] > hi)).sum())
    if fuera / m.sum() > 0.05:
        msgs.append(f"{fuera} rendimientos fuera de rangos plausibles por cultivo (bu/ac)")
    factores = ctx.conversiones.get("bu_ac_a_kgha") or {}
    if "rend_kgha" in df.columns:
        kg = num("rend_kgha")
        malos, total = 0, 0
        for cult, f in factores.items():
            mm = (df["cultivo"] == cult) & ren.notna() & kg.notna() & (ren > 0)
            total += int(mm.sum())
            malos += int(((kg[mm] - ren[mm] * float(f)).abs() > 0.01 * ren[mm] * float(f)).sum())
        if total and malos / total > 0.01:
            msgs.append(f"rend_kgha ≠ rend_bu_ac × factor de config.yaml en {malos} filas")
    if "sup_sembrada_ha" in df.columns and "sup_sembrada_ac" in df.columns:
        ac, ha = num("sup_sembrada_ac"), num("sup_sembrada_ha")
        f = float(ctx.conversiones.get("acre_a_ha", 0.4047))
        mm = ac.notna() & ha.notna() & (ac > 0)
        if mm.sum() and ((ha[mm] - ac[mm] * f).abs() > 0.01 * ac[mm] * f).mean() > 0.01:
            msgs.append(f"sup_sembrada_ha ≠ sup_sembrada_ac × {f}")
    return (0 if msgs else 1), "; ".join(msgs)


def esp_mascara_agricola(ctx, pkg, esp, archivos):
    ok, msg = _es_geotiff(ctx.repo / "data" / "reference" / "mascara_agricola.tif")
    return (1 if ok else 0), msg


def esp_mascaras_cultivo(ctx, pkg, esp, archivos):
    d = ctx.repo / "data" / "reference"
    desde = int((ctx.cfg.get("periodo") or {}).get("rotaciones_desde", 2008))
    anios = list(range(max(desde, ctx.periodo.y0), ctx.periodo.y1 + 1))
    if not anios:
        return 0, "sin años para verificar"
    faltan = [y for y in anios if not all(_es_geotiff(d / f"mascara_{c}_{y}.tif")[0] for c in ("maiz", "soja"))]
    frac = (len(anios) - len(faltan)) / len(anios)
    return frac, ("" if not faltan else f"faltan máscaras de maíz o soja (GeoTIFF) de {len(faltan)} años, ej. {faltan[:4]}")


def esp_textura_suma_100(ctx, pkg, esp, archivos):
    df = archivos.get("data/processed/suelo_terreno/suelo_terreno_estatico.csv")
    if df is None:
        return 0, "falta suelo_terreno_estatico.csv válido"
    cols = ["arcilla_pct", "arena_pct", "limo_pct"]
    if any(c not in df.columns for c in cols):
        return 0, "faltan arcilla_pct, arena_pct o limo_pct"
    s = sum(pd.to_numeric(df[c], errors="coerce") for c in cols)
    if s.isna().all():
        return 0, "sin valores de textura"
    malos = ((s - 100).abs() > 3) & s.notna()
    if malos.any():
        return 0, f"arcilla + arena + limo no da 100 ± 3 en {malos.sum()} condados"
    return 1, ""


def _componentes(ctx, temporales, frames=None):
    """Columnas no clave de los CSV procesados con esos temporales: {columna: paquete}.

    Si se pasa la lista `frames`, le agrega (paquete, spec del archivo, DataFrame) de cada archivo leído."""
    columnas, n = {}, 0
    for pkg, pspec in ctx.ent["paquetes"].items():
        if pspec.get("fuera_de_tablas"):
            continue
        for af in pspec.get("archivos", []):
            if af["temporal"] in temporales and af["ruta"].startswith("data/processed/") and (ctx.repo / af["ruta"]).exists():
                d, _ = leer_csv(ctx.repo / af["ruta"])
                if d is not None:
                    n += 1
                    if frames is not None:
                        frames.append((pkg, af, d))
                    for c in d.columns:
                        if c not in af.get("claves", []):
                            columnas.setdefault(c, pkg)
    return columnas, n


def _iguales(a: str, b: str) -> bool:
    """Mismo valor de celda: texto idéntico, o números iguales con tolerancia (redondeo al escribir)."""
    if a == b:
        return True
    if a == "" or b == "":
        return False
    try:
        x, y = float(a), float(b)
    except ValueError:
        return False
    if math.isnan(x) or math.isnan(y):
        return False
    return math.isclose(x, y, rel_tol=1e-3, abs_tol=1e-4)


def _desactualizadas(tabla, frames, n_muestra=300, tolerancia=0.01):
    """Columnas de la tabla unida cuyos valores no coinciden con los del archivo de su paquete (muestra fija).

    Solo compara columnas que se pueden ubicar sin ambigüedad: <paquete>_<columna> en la tabla, o el nombre
    tal cual si ese nombre aparece en un solo archivo de los que se unen. Los archivos por estado se cruzan
    por los dos primeros dígitos de fips."""
    usos = {}
    for pkg, af, d in frames:
        for c in d.columns:
            if c not in af.get("claves", []):
                usos[c] = usos.get(c, 0) + 1
    t = tabla
    if "fips" in t.columns and "fips_estado" not in t.columns:
        t = t.assign(fips_estado=t["fips"].str[:2])
    malas = []
    for pkg, af, d in frames:
        claves = list(af.get("claves", []))
        if not claves or not all(k in d.columns for k in claves) or not all(k in t.columns for k in claves):
            continue
        pares = []
        for c in d.columns:
            if c in claves:
                continue
            if f"{pkg}_{c}" in t.columns:
                pares.append((c, f"{pkg}_{c}"))
            elif c in t.columns and usos.get(c, 0) == 1:
                pares.append((c, c))
        if not pares:
            continue
        m = d.drop_duplicates(subset=claves)
        if len(m) > n_muestra:
            m = m.sample(n=n_muestra, random_state=0)
        m = m[claves + [c for c, _ in pares]]
        sub = t[claves + [ct for _, ct in pares]].drop_duplicates(subset=claves)
        sub.columns = claves + [f"__tabla__{i}" for i in range(len(pares))]
        j = m.merge(sub, on=claves, how="inner")
        if j.empty:
            continue
        for i, (c, ct) in enumerate(pares):
            dif = sum(1 for x, y in zip(j[c].tolist(), j[f"__tabla__{i}"].tolist()) if not _iguales(x, y))
            if dif > max(2, tolerancia * len(j)):
                malas.append(f"{pkg}/{c} ({dif} de {len(j)} filas)")
    return malas


def _tabla_unida(ctx, nombre, temporales, claves_tabla, base=None):
    p = ctx.repo / "data" / "processed" / nombre
    if not p.exists():
        return 0, f"falta data/processed/{nombre}"
    df, err = leer_csv(p)
    if df is None:
        return 0, "; ".join(err)
    frames = []
    columnas, n_comp = _componentes(ctx, temporales, frames)
    if n_comp == 0:
        return 0, "todavía no hay archivos para unir"
    msgs = []
    if list(df.columns[: len(claves_tabla)]) != claves_tabla:
        msgs.append(f"las primeras columnas tienen que ser {claves_tabla}")
    faltan = sorted(c for c, pkg in columnas.items() if c not in df.columns and f"{pkg}_{c}" not in df.columns)
    if faltan:
        msgs.append(f"faltan columnas de los paquetes: {faltan[:6]}")
    tiene_claves = all(k in df.columns for k in claves_tabla)
    if tiene_claves and df.duplicated(subset=claves_tabla).any():
        msgs.append(f"claves duplicadas en {nombre} ({claves_tabla})")
    if base and tiene_claves and (ctx.repo / base).exists():
        db, _ = leer_csv(ctx.repo / base)
        if db is not None and all(k in db.columns for k in claves_tabla):
            kb = set(map(tuple, db[claves_tabla].values.tolist()))
            kt = set(map(tuple, df[claves_tabla].values.tolist()))
            if kb - kt:
                msgs.append(f"faltan {len(kb - kt)} filas de {Path(base).name} en {nombre}")
    if not msgs:
        viejas = _desactualizadas(df, frames)
        if viejas:
            msgs.append(f"{nombre} está desactualizada: {len(viejas)} columnas no coinciden con los archivos de sus "
                        f"paquetes (ej. {'; '.join(viejas[:4])}). Volvé a correr src/merge.py")
    return (0 if msgs else 1), "; ".join(msgs)


def esp_tabla_anual(ctx, pkg, esp, archivos):
    return _tabla_unida(ctx, "tabla_anual.csv", ("anual", "estatico"), ["fips", "anio", "cultivo"],
                        base="data/processed/cultivos/produccion_anual.csv")


def esp_tabla_mensual(ctx, pkg, esp, archivos):
    return _tabla_unida(ctx, "tabla_mensual.csv", ("mensual",), ["fips", "anio", "mes"])


# --------------------------------------------------------------------------- especiales del paquete lotes

LOTES_DIR = "data/processed/lotes/"
SENSORES_PRODUCTO = {"landsat_c2_l2": {"L5", "L7", "L8", "L9"}, "hls_l30": {"L8", "L9"}, "hls_s30": {"S2A", "S2B", "S2C"}}
# Desde el lanzamiento (o la primera imagen) hasta el fin de la misión; las fechas finales son holgadas.
MISION_SENSOR = {"L5": ("1984-03-01", "2013-06-05"), "L7": ("1999-04-15", "2025-12-31"),
                 "L8": ("2013-03-18", "2099-12-31"), "L9": ("2021-10-31", "2099-12-31"),
                 "S2A": ("2015-06-23", "2099-12-31"), "S2B": ("2017-03-07", "2099-12-31"),
                 "S2C": ("2024-09-05", "2099-12-31")}
SLC_OFF_DESDE = "2003-05-31"
CONTROLES_LOTES = {"píxeles por lote": ["por lote"], "pureza": ["pureza"], "observaciones despejadas": ["despejad"],
                   "2012 y SLC-off": ["2012", "slc"], "Landsat–Sentinel-2": ["sentinel"],
                   "alineación CSB–CDL": ["alineaci"], "relieve": ["relieve"], "SSURGO": ["ssurgo"]}


def _num(s):
    return pd.to_numeric(s, errors="coerce")


def esp_lotes_seleccion(ctx, pkg, esp, archivos):
    df = archivos.get(LOTES_DIR + "lotes.csv")
    if df is None:
        return 0, "falta lotes.csv válido"
    need = ["paisaje", "area_ha", "n_px_interior", "n_anios_maiz_soja", "relieve_m", "motivo", "n_candidatos"]
    faltan = [c for c in need if c not in df.columns]
    if faltan:
        return 0, f"a lotes.csv le faltan columnas: {faltan}"
    paisajes = esp.get("paisajes") or {}
    pedidos = sum(int(v.get("lotes", 0)) for v in paisajes.values())
    if not pedidos:
        return 0, "el spec no define paisajes"
    msgs, bien = [], 0
    for nombre, v in paisajes.items():
        sub = df[df["paisaje"] == nombre]
        if "condados" in v:
            en_zona = sub["fips"].isin([str(x) for x in v["condados"]])
            donde = "los condados " + ", ".join(str(x) for x in v["condados"])
        else:
            en_zona = sub["fips"].str.startswith(str(v.get("prefijo", "")))
            donde = f"los fips {v.get('prefijo', '')}xxx"
        if (~en_zona).any():
            msgs.append(f"{nombre}: {int((~en_zona).sum())} lotes fuera de {donde}")
        s = sub[en_zona]
        area = _num(s["area_ha"])
        ok = (area >= 30) & (area <= 120) & (_num(s["n_px_interior"]) >= 300) & (_num(s["n_anios_maiz_soja"]) >= 6)
        ok &= (s["motivo"].str.len() >= 10) & (_num(s["n_candidatos"]) >= 1)
        if v.get("relieve_min_m") is not None:
            ok &= _num(s["relieve_m"]) > float(v["relieve_min_m"])
        n_ok, pedido = int(ok.sum()), int(v.get("lotes", 0))
        if n_ok < pedido:
            msgs.append(f"{nombre}: {n_ok} lotes cumplen los criterios y se piden {pedido}")
        elif len(sub) > pedido:
            msgs.append(f"{nombre}: hay {len(sub)} lotes y se piden {pedido}")
        bien += min(n_ok, pedido)
    frac = bien / pedidos
    if len(df) != pedidos:
        frac = min(frac, 0.9)
        msgs.append(f"lotes.csv tiene {len(df)} lotes y se piden {pedidos}")
    return frac, "; ".join(msgs)


def esp_lotes_claves(ctx, pkg, esp, archivos):
    lotes, px = archivos.get(LOTES_DIR + "lotes.csv"), archivos.get(LOTES_DIR + "pixeles.csv")
    if lotes is None or px is None:
        return 0, "faltan lotes.csv o pixeles.csv válidos"
    msgs, ok = [], 0
    kl = set(_clave_texto(lotes, ["fips", "id_lote"]))
    kp = set(_clave_texto(px, ["fips", "id_lote"]))
    if kl == kp:
        ok += 1
    else:
        msgs.append(f"{len(kl - kp)} lotes sin píxeles en pixeles.csv y {len(kp - kl)} lotes de pixeles.csv que no están en lotes.csv")
    if all(c in lotes.columns for c in ("n_px", "n_px_interior")) and "interior" in px.columns:
        cnt = px.groupby("id_lote").size()
        cint = px[px["interior"] == "1"].groupby("id_lote").size()
        mal = [i for i, a, b in zip(lotes["id_lote"], _num(lotes["n_px"]), _num(lotes["n_px_interior"]))
               if a != cnt.get(i, 0) or b != cint.get(i, 0)]
        if mal:
            msgs.append(f"n_px o n_px_interior no coinciden con pixeles.csv en {len(mal)} lotes (ej. {mal[0]})")
        else:
            ok += 1
    else:
        msgs.append("faltan n_px y n_px_interior en lotes.csv o interior en pixeles.csv")
    if "x_m" in px.columns and "y_m" in px.columns:
        paso = float(esp.get("grilla_paso_m", 30))
        x, y = _num(px["x_m"]), _num(px["y_m"])
        fuera = (x.isna() | y.isna() | ((x / paso - (x / paso).round()).abs() > 1e-4)
                 | ((y / paso - (y / paso).round()).abs() > 1e-4))
        if fuera.any():
            msgs.append(f"{int(fuera.sum())} píxeles cuyo centro no cae en la grilla de {paso:g} m de mascara_agricola.tif "
                        f"(x_m e y_m tienen que ser múltiplos de {paso:g})")
        else:
            ok += 1
        rep = pd.DataFrame({"l": px["id_lote"], "x": x, "y": y}).duplicated()
        if rep.any():
            msgs.append(f"{int(rep.sum())} píxeles repetidos (mismo centro) dentro de un lote")
        else:
            ok += 1
    else:
        msgs.append("faltan x_m e y_m en pixeles.csv")
    return ok / 4, "; ".join(msgs)


def esp_lotes_gpkg(ctx, pkg, esp, archivos):
    p = ctx.repo / "data" / "processed" / "lotes" / "lotes.gpkg"
    if not p.exists():
        return 0, "falta data/processed/lotes/lotes.gpkg"
    with open(p, "rb") as f:
        if f.read(16) != b"SQLite format 3\x00":
            return 0, "lotes.gpkg no es un GeoPackage (SQLite)"
    pedidas = ["lote", "lote_interior", "suelo_poligonos"]
    lotes = archivos.get(LOTES_DIR + "lotes.csv")
    msgs, ok = [], 0
    try:
        con = sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True)
        try:
            capas = {str(r[0]): str(r[1]) for r in con.execute("SELECT table_name, srs_id FROM gpkg_geometry_columns")}
            faltan = [c for c in pedidas if c not in capas]
            if faltan:
                msgs.append(f"faltan las capas {faltan} (hay {sorted(capas)[:6]})")
            else:
                ok += 1
            otras = [c for c in pedidas if c in capas and capas[c] != "4326"]
            if otras:
                msgs.append(f"capas que no están en EPSG:4326: {otras}")
            elif not faltan:
                ok += 1
            if lotes is None:
                msgs.append("falta lotes.csv válido para comparar los polígonos")
            else:
                ids = set(lotes["id_lote"])
                for capa in ("lote", "lote_interior"):
                    if capa not in capas:
                        continue
                    cols = [r[1] for r in con.execute(f'PRAGMA table_info("{capa}")')]
                    if "id_lote" not in cols:
                        msgs.append(f"la capa {capa} no tiene la columna id_lote")
                        continue
                    vals = [str(r[0]) for r in con.execute(f'SELECT id_lote FROM "{capa}"')]
                    if len(vals) != len(set(vals)) or set(vals) != ids:
                        msgs.append(f"la capa {capa} tiene {len(vals)} polígonos que no coinciden uno a uno con los "
                                    f"{len(ids)} lotes de lotes.csv")
                    else:
                        ok += 1
        finally:
            con.close()
    except Exception as e:
        return 0, f"no se pudo leer lotes.gpkg: {e}"
    return ok / 4, "; ".join(msgs)


def esp_lotes_pureza(ctx, pkg, esp, archivos):
    la = archivos.get(LOTES_DIR + "lotes_anual.csv")
    if la is None:
        return 0, "falta lotes_anual.csv válido"
    if any(c not in la.columns for c in ("pct_px_cultivo_principal", "lote_partido")):
        return 0, "faltan pct_px_cultivo_principal o lote_partido en lotes_anual.csv"
    pct = _num(la["pct_px_cultivo_principal"])
    m = pct.notna() & (la["lote_partido"] != "")
    if not m.any():
        return 0, "lotes_anual.csv no tiene pct_px_cultivo_principal ni lote_partido"
    msgs, ok = [], 0
    incoh = m & ((pct < 90) != (la["lote_partido"] == "1"))
    if incoh.any():
        msgs.append(f"lote_partido no es 1 justo cuando pct_px_cultivo_principal < 90 en {int(incoh.sum())} lotes-año")
    else:
        ok += 1
    cp, px = archivos.get(LOTES_DIR + "cultivo_px_anual.csv"), archivos.get(LOTES_DIR + "pixeles.csv")
    if cp is None or px is None or "cultivo" not in cp.columns or "interior" not in px.columns:
        msgs.append("faltan cultivo_px_anual.csv o pixeles.csv válidos para recalcular la pureza")
    else:
        inter = px.loc[px["interior"] == "1", ["id_lote", "px_id"]]
        c = cp.loc[cp["cultivo"] != "", ["id_lote", "px_id", "anio", "cultivo"]].merge(inter, on=["id_lote", "px_id"])
        if not len(c):
            msgs.append("cultivo_px_anual.csv no tiene el cultivo de los píxeles interiores")
        else:
            g = c.groupby(["id_lote", "anio", "cultivo"]).size().unstack(fill_value=0)
            rec = (100.0 * g.max(axis=1) / g.sum(axis=1)).rename("rec")
            ref = pd.Series(pct.values, index=pd.MultiIndex.from_arrays([la["id_lote"], la["anio"]])).rename("ref")
            j = pd.concat([rec, ref], axis=1, join="inner").dropna()
            if not len(j):
                msgs.append("no hay lotes-año en común entre lotes_anual.csv y cultivo_px_anual.csv")
            else:
                dif = (j["rec"] - j["ref"]).abs() > 0.5
                if dif.any():
                    msgs.append(f"pct_px_cultivo_principal no coincide (± 0,5) con los píxeles interiores de "
                                f"cultivo_px_anual.csv en {int(dif.sum())} de {len(j)} lotes-año")
                else:
                    ok += 1
    return ok / 2, "; ".join(msgs)


def esp_lotes_obs_cobertura(ctx, pkg, esp, archivos):
    obs, px = archivos.get(LOTES_DIR + "vegetacion_px_obs.csv"), archivos.get(LOTES_DIR + "pixeles.csv")
    if obs is None or px is None:
        return 0, "faltan vegetacion_px_obs.csv o pixeles.csv válidos"
    cols = ["id_lote", "px_id", "anio", "fecha", "producto"]
    if any(c not in obs.columns for c in cols):
        return 0, f"a vegetacion_px_obs.csv le faltan columnas: {[c for c in cols if c not in obs.columns]}"
    conteos, presentes, fuera_temp, n = [], [], 0, 0
    try:
        for parte in _partes_de(obs, cols):
            mmdd = parte["fecha"].str[5:10]
            fuera = (mmdd < "03-01") | (mmdd > "11-30")
            fuera_temp += int(fuera.sum())
            n += len(parte)
            presentes.append(parte[["id_lote", "px_id"]].drop_duplicates())
            ls = parte[(parte["producto"] == "landsat_c2_l2") & ~fuera]
            if len(ls):
                conteos.append(ls.groupby(["id_lote", "px_id", "anio"]).size())
    except ValueError as e:
        return 0, f"no se pudo leer vegetacion_px_obs.csv: {e}"
    if not n:
        return 0, "vegetacion_px_obs.csv no tiene filas"
    msgs, pts = [], 0.0
    if fuera_temp:
        msgs.append(f"{fuera_temp} observaciones fuera del 1 de marzo al 30 de noviembre")
    else:
        pts += 1
    pres = set(_clave_texto(pd.concat(presentes).drop_duplicates(), ["id_lote", "px_id"]))
    todos = set(_clave_texto(px, ["id_lote", "px_id"]))
    sin_obs = len(todos - pres)
    if sin_obs:
        msgs.append(f"{sin_obs} de {len(todos)} píxeles de pixeles.csv sin ninguna observación")
    else:
        pts += 1
    cnt = pd.concat(conteos).groupby(level=[0, 1, 2]).sum() if conteos else pd.Series(dtype="int64")
    anios = [str(y) for y in range(ctx.periodo.y0, ctx.periodo.y1 + 1) if y != 2012]
    idx = pd.MultiIndex.from_tuples([(lo, pi, a) for lo, pi in zip(px["id_lote"], px["px_id"]) for a in anios])
    med = cnt.reindex(idx, fill_value=0).groupby(level=[0, 2]).median()
    share = float((med >= 5).mean()) if len(med) else 0.0
    if share < 0.9:
        msgs.append(f"solo {share:.0%} de los lotes-año ({ctx.periodo.y0}–{ctx.periodo.y1} sin 2012) tienen una mediana de "
                    "5 o más observaciones despejadas de Landsat por píxel (se pide 90 %)")
    pts += 2 * min(1.0, share / 0.9)
    va = archivos.get(LOTES_DIR + "vegetacion_px_anual.csv")
    if va is None or "n_obs_mar_nov" not in va.columns:
        msgs.append("falta vegetacion_px_anual.csv válido con n_obs_mar_nov para comparar")
    else:
        ref = pd.Series(_num(va["n_obs_mar_nov"]).values,
                        index=pd.MultiIndex.from_arrays([va["id_lote"], va["px_id"], va["anio"]]))
        m = ref.notna()
        if not m.any():
            msgs.append("vegetacion_px_anual.csv no tiene n_obs_mar_nov")
        else:
            obs_n = cnt.reindex(ref.index, fill_value=0)
            igual = float((obs_n[m].values == ref[m].values).mean())
            if igual < 0.99:
                msgs.append(f"n_obs_mar_nov de vegetacion_px_anual.csv no coincide con las observaciones de Landsat de "
                            f"vegetacion_px_obs.csv en {1 - igual:.1%} de los píxeles-año")
            else:
                pts += 1
    return pts / 5, "; ".join(msgs)


def esp_lotes_sensores(ctx, pkg, esp, archivos):
    obs = archivos.get(LOTES_DIR + "vegetacion_px_obs.csv")
    if obs is None:
        return 0, "falta vegetacion_px_obs.csv válido"
    cols = ["fecha", "producto", "sensor", "slc_off"]
    if any(c not in obs.columns for c in cols):
        return 0, f"a vegetacion_px_obs.csv le faltan columnas: {[c for c in cols if c not in obs.columns]}"
    mal_par = mal_fecha = mal_slc = l7_2012 = 0
    try:
        for parte in _partes_de(obs, cols):
            f, sen = parte["fecha"], parte["sensor"]
            par_ok = pd.Series(False, index=parte.index)
            for prod, sens in SENSORES_PRODUCTO.items():
                par_ok |= (parte["producto"] == prod) & sen.isin(sens)
            mal_par += int((~par_ok).sum())
            fecha_ok = pd.Series(False, index=parte.index)
            for s, (a, b) in MISION_SENSOR.items():
                fecha_ok |= (sen == s) & (f >= a) & (f <= b)
            mal_fecha += int((~fecha_ok).sum())
            debe = (sen == "L7") & (f >= SLC_OFF_DESDE)
            mal_slc += int(((parte["slc_off"] == "1") != debe).sum())
            l7_2012 += int(((sen == "L7") & (f.str[:4] == "2012")).sum())
    except ValueError as e:
        return 0, f"no se pudo leer vegetacion_px_obs.csv: {e}"
    msgs, ok = [], 0
    if mal_par:
        msgs.append(f"{mal_par} observaciones con un sensor que no es de su producto (landsat_c2_l2: L5, L7, L8, L9; "
                    "hls_l30: L8, L9; hls_s30: S2A, S2B, S2C)")
    else:
        ok += 1
    if mal_fecha:
        msgs.append(f"{mal_fecha} observaciones fuera de los años de misión de su sensor")
    else:
        ok += 1
    if mal_slc:
        msgs.append(f"slc_off mal marcado en {mal_slc} observaciones (1 solo en L7 desde el {SLC_OFF_DESDE})")
    else:
        ok += 1
    if l7_2012:
        ok += 1
    else:
        msgs.append("2012 no tiene observaciones de Landsat 7 (es el único Landsat de ese año)")
    return ok / 4, "; ".join(msgs)


def esp_lotes_cdl_10m(ctx, pkg, esp, archivos):
    cp, px = archivos.get(LOTES_DIR + "cultivo_px_anual.csv"), archivos.get(LOTES_DIR + "pixeles.csv")
    if cp is None or px is None:
        return 0, "faltan cultivo_px_anual.csv o pixeles.csv válidos"
    if "frac_clase" not in cp.columns:
        return 0, "falta frac_clase en cultivo_px_anual.csv"
    anios = [str(y) for y in (2024, 2025) if ctx.periodo.y0 <= y <= ctx.periodo.y1]
    fr = _num(cp.loc[cp["anio"].isin(anios), "frac_clase"]).dropna()
    esperados = len(px) * len(anios)
    cov = len(fr) / esperados if esperados else 0.0
    msgs, pts = [], min(1.0, cov / 0.99)
    if cov < 0.99:
        msgs.append(f"frac_clase solo en {len(fr)} de {esperados} píxeles-año de {', '.join(anios)}")
    if len(fr) and float((fr < 1 - 1e-9).mean()) >= 0.01:
        pts += 1
    else:
        msgs.append("ningún píxel (o menos de 1 %) tiene frac_clase < 1 en 2024–2025: parece la exportación a 30 m y "
                    "no el CDL de 10 m")
    return pts / 2, "; ".join(msgs)


def esp_lotes_suelo_fracciones(ctx, pkg, esp, archivos):
    sp, sm, px = (archivos.get(LOTES_DIR + x) for x in ("suelo_px.csv", "suelo_mukey.csv", "pixeles.csv"))
    if sp is None or sm is None or px is None:
        return 0, "faltan suelo_px.csv, suelo_mukey.csv o pixeles.csv válidos"
    if "frac_mukey" not in sp.columns:
        return 0, "falta frac_mukey en suelo_px.csv"
    msgs, ok = [], 0
    suma = _num(sp["frac_mukey"]).groupby([sp["id_lote"], sp["px_id"]]).sum()
    suma = suma.reindex(pd.MultiIndex.from_arrays([px["id_lote"], px["px_id"]]), fill_value=0)
    pasan = int((suma > 1.01).sum())
    bajos = float((suma < 0.5).mean()) if len(suma) else 1.0
    if pasan:
        msgs.append(f"{pasan} píxeles con la suma de frac_mukey mayor a 1")
    elif bajos > 0.05:
        msgs.append(f"{bajos:.1%} de los píxeles tienen menos de la mitad de su área con mukey (se pide al menos 95 % "
                    "de los píxeles con 0,5 o más)")
    else:
        ok += 1
    usados, tabla = set(sp["mukey"]), set(sm["mukey"])
    if usados - tabla:
        msgs.append(f"{len(usados - tabla)} mukey de suelo_px.csv que no están en suelo_mukey.csv")
    else:
        ok += 1
    if tabla - usados:
        msgs.append(f"{len(tabla - usados)} mukey de suelo_mukey.csv que no se usan en suelo_px.csv")
    else:
        ok += 1
    return ok / 3, "; ".join(msgs)


def esp_lotes_controles_data_card(ctx, pkg, esp, archivos):
    p = ctx.repo / "docs" / "datasets" / f"{pkg}.md"
    if not p.exists():
        return 0, f"falta docs/datasets/{pkg}.md"
    txt = p.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^(#{2,4})\s*Controles de calidad\s*$", txt, re.M | re.I)
    if not m:
        return 0, "falta la sección '## Controles de calidad' en la data card"
    resto = txt[m.end():]
    sig = re.search(r"^#{1,%d}\s" % len(m.group(1)), resto, re.M)
    cuerpo = sin_tildes(resto[: sig.start()] if sig else resto).lower()
    faltan = [k for k, claves in CONTROLES_LOTES.items() if not all(sin_tildes(c).lower() in cuerpo for c in claves)]
    frac = 1 - len(faltan) / len(CONTROLES_LOTES)
    return frac, ("" if not faltan else "la sección 'Controles de calidad' no reporta: " + ", ".join(faltan))


ESPECIALES = {
    "zona_config": esp_zona_config,
    "gpkg_condados": esp_gpkg_condados,
    "anios_exactos": esp_anios_exactos,
    "funciones_comunes": esp_funciones_comunes,
    "clases_cdl": esp_clases_cdl,
    "consistencia_rendimiento": esp_consistencia_rendimiento,
    "mascara_agricola": esp_mascara_agricola,
    "mascaras_cultivo": esp_mascaras_cultivo,
    "textura_suma_100": esp_textura_suma_100,
    "tabla_anual": esp_tabla_anual,
    "tabla_mensual": esp_tabla_mensual,
    "lotes_seleccion": esp_lotes_seleccion,
    "lotes_claves": esp_lotes_claves,
    "lotes_gpkg": esp_lotes_gpkg,
    "lotes_pureza": esp_lotes_pureza,
    "lotes_obs_cobertura": esp_lotes_obs_cobertura,
    "lotes_sensores": esp_lotes_sensores,
    "lotes_cdl_10m": esp_lotes_cdl_10m,
    "lotes_suelo_fracciones": esp_lotes_suelo_fracciones,
    "lotes_controles_data_card": esp_lotes_controles_data_card,
}


# --------------------------------------------------------------------------- puntaje de datos

def pesos_columnas(ctx: Ctx):
    """Peso de cada (archivo, columna): el del ID del catálogo repartido entre sus columnas."""
    conteo = {}
    for pspec in ctx.ent["paquetes"].values():
        for af in pspec.get("archivos", []):
            for c in af.get("columnas", []):
                cid = c.get("catalogo")
                if cid:
                    conteo[cid] = conteo.get(cid, 0) + 1
    pesos = {}
    for pspec in ctx.ent["paquetes"].values():
        for af in pspec.get("archivos", []):
            for c in af.get("columnas", []):
                key = (af["ruta"], c.get("nombre") or c.get("patron"))
                cid = c.get("catalogo")
                if c.get("peso") is not None:
                    pesos[key] = float(c["peso"])
                else:
                    pesos[key] = ctx.peso_prioridad(cid) / conteo[cid] if cid else ctx.peso_prioridad(None)
    return pesos


def puntuar_datos(ctx: Ctx, checks: Checks, repro_pedidos, repro_timeout, variables):
    p_datos = ctx.ent["puntaje"]["parte_datos"]
    p_doc = ctx.ent["puntaje"]["parte_documentacion"]
    pesos = pesos_columnas(ctx)

    # Base primero: define los fips válidos.
    dep = ctx.repo / "data" / "reference" / "condados.csv"
    if dep.exists():
        df, err = leer_csv(dep)
        if df is not None and "fips" in df.columns and df["fips"].str.match(RE_FIPS).all() and not df["fips"].duplicated().any() and len(df):
            ctx.fips = set(df["fips"])
        elif df is not None:
            ctx.fips_msg = "data/reference/condados.csv tiene fips inválidos o repetidos (tarea base)"

    ctx.manifest, ctx.manifest_err = leer_manifest(ctx)
    cargar_unidades(ctx)
    repro = {}
    for pkg, pspec in ctx.ent["paquetes"].items():
        tarea = pkg
        archivos_ok = {}
        # Compuertas del paquete
        es_merge = pkg == "merge"
        if not es_merge:
            ok_man, msg_man, hay_raw = check_manifest(ctx, pkg)
            checks.add(f"manifest:{pkg}", tarea, ctx.ent["puntaje"]["peso_manifest"] if ok_man else 0,
                       ctx.ent["puntaje"]["peso_manifest"], msg_man)
        else:
            hay_raw = True
        # Reproducibilidad (con caché por contenido)
        cache_f = ctx.cache / f"repro_{pkg}.json"
        clave = clave_repro(ctx, pkg, pspec) if archivos_salida(ctx, pspec) else None
        r_ok, r_msg = None, "sin verificar"
        if clave:
            if cache_f.exists():
                try:
                    d = json.loads(cache_f.read_text(encoding="utf-8"))
                    if d.get("clave") == clave:
                        r_ok, r_msg = d["ok"], d["msg"]
                except Exception:
                    pass
            if r_ok is None and pkg in repro_pedidos:
                r_ok, r_msg = reproducir(ctx, pkg, pspec, repro_timeout)
                if r_ok is not None:
                    cache_f.write_text(json.dumps({"clave": clave, "ok": r_ok, "msg": r_msg, "cuando": time.time()}, ensure_ascii=False), encoding="utf-8")
        repro[pkg] = {"ok": r_ok, "msg": r_msg}
        compuerta = 1.0
        bloqueos = []
        if not hay_raw:
            compuerta = 0.0
            bloqueos.append(f"sin datos crudos registrados: ningún archivo de data/raw/{pkg}/ figura en manifest.csv (¿de dónde salen los valores?)")
        if r_ok is False:
            compuerta = 0.0
            bloqueos.append(f"no reproducible: {r_msg}")

        filas_doc, err_doc = ([], [])
        if not pspec.get("sin_data_card"):
            filas_doc, err_doc = leer_data_card(ctx.repo / "docs" / "datasets" / f"{pkg}.md", ctx)
            peso_dc = ctx.ent["puntaje"]["peso_data_card"]
            checks.add(f"datacard:{pkg}", tarea, 0 if err_doc else peso_dc, peso_dc, "; ".join(err_doc))

        for af in pspec.get("archivos", []):
            ruta = af["ruta"]
            p = ctx.repo / ruta
            resultados = None
            if af.get("grande") and p.exists():
                # millones de filas: contrato y valores por partes; los especiales lo leen por partes
                err, avisos, coh, resultados, cols_g = evaluar_grande(ctx, af, p)
                df_valido = None if err else ArchivoGrande(p, cols_g or [])
                if df_valido is not None:
                    archivos_ok[ruta] = df_valido
                tiempos = None
            else:
                df, err = (None, [f"falta {ruta}"]) if not p.exists() else leer_csv(p)
                avisos = []
                if df is not None:
                    err, avisos = contrato(df, af, ctx)
                if err:
                    df_valido = None
                else:
                    df_valido = df
                    archivos_ok[ruta] = df
                coh = evaluar_coherencia(df_valido, af) if df_valido is not None else []
                tiempos = tiempos_de(df_valido, af["temporal"]) if df_valido is not None else None
            for a in avisos:
                ctx.avisos.append(f"{ruta}: {a}")
            msg_archivo = "; ".join(err) if err else ("; ".join(coh) if coh else "")

            def valores(nm, cs, df_valido=df_valido, tiempos=tiempos, resultados=resultados, af=af):
                if resultados is not None:
                    return resultados.get(nm, (0.0, f"falta la columna '{nm}'", None))
                return evaluar_valores(df_valido, nm, cs, af, ctx, tiempos)

            for cspec, nombres in columnas_de_spec(af, list(df_valido.columns) if df_valido is not None else None):
                etiqueta = cspec.get("nombre") or cspec.get("patron")
                cid = cspec.get("catalogo")
                peso = pesos[(ruta, etiqueta)]
                frac_d, frac_doc, msgs = 0.0, 0.0, []
                if df_valido is None:
                    msgs.append(msg_archivo or f"falta {ruta}")
                elif coh:
                    msgs.append(msg_archivo)
                else:
                    if "patron" in cspec:
                        minimo = int(cspec.get("min_columnas", 1))
                        if not nombres:
                            msgs.append(f"no hay columnas con el patrón '{etiqueta}' (mínimo {minimo})")
                        fr, dc = [], []
                        for n in nombres:
                            f_, m_, st = valores(n, cspec)
                            fr.append(f_)
                            if m_:
                                msgs.append(m_)
                            ok_d, m_d = doc_ok(filas_doc, ruta, n, cid, st, af, ctx) if f_ > 0 else (False, "")
                            dc.append(1.0 if ok_d else 0.0)
                            if m_d and f_ > 0:
                                msgs.append(m_d)
                        if nombres:
                            factor = min(1.0, len(nombres) / minimo)
                            frac_d = factor * sum(fr) / len(fr)
                            frac_doc = factor * sum(dc) / len(dc)
                            if len(nombres) < minimo:
                                msgs.append(f"hay {len(nombres)} columnas '{etiqueta}' y se esperan al menos {minimo}")
                    else:
                        nombre = cspec["nombre"]
                        frac_d, m_, st = valores(nombre, cspec)
                        if m_:
                            msgs.append(m_)
                        if frac_d > 0 and not pspec.get("sin_data_card"):
                            ok_d, m_d = doc_ok(filas_doc, ruta, nombre, cid, st, af, ctx)
                            frac_doc = 1.0 if ok_d else 0.0
                            if m_d:
                                msgs.append(m_d)
                frac_d *= compuerta
                frac_doc = frac_doc if frac_d > 0 else 0.0
                if compuerta == 0 and bloqueos and df_valido is not None:
                    msgs = bloqueos + msgs
                pts = peso * (p_datos * frac_d + p_doc * frac_doc)
                cid_txt = f" [{cid}]" if cid else ""
                checks.add(f"col:{ruta}:{etiqueta}", tarea, pts, peso, f"{Path(ruta).name}:{etiqueta}{cid_txt} — " + "; ".join(dict.fromkeys(m for m in msgs if m)) if msgs else "", catalogo=cid)
                if cid:
                    v = variables.setdefault(cid, {"pts": 0.0, "max": 0.0, "paquete": pkg})
                    v["pts"] += pts
                    v["max"] += peso
                for extra in cspec.get("catalogo_extra", []) or []:
                    variables.setdefault(extra, {"pts": 0.0, "max": 0.0, "paquete": pkg})

        for esp in pspec.get("especiales", []) or []:
            fn = ESPECIALES.get(esp["id"])
            if fn is None:
                continue
            try:
                frac, msg = fn(ctx, pkg, esp, archivos_ok)
            except Exception as e:
                frac, msg = 0, f"error al verificar: {type(e).__name__}: {e}"
            if esp["id"] in ("tabla_anual", "tabla_mensual"):
                pass
            elif compuerta == 0 and bloqueos and esp["id"] not in ("anios_exactos", "funciones_comunes"):
                frac, msg = 0, "; ".join(bloqueos)
            checks.add(f"esp:{pkg}:{esp['id']}", tarea, esp["peso"] * frac, esp["peso"],
                       (esp["id"] + " — " + msg) if msg else "", catalogo=esp.get("catalogo"))
            if esp.get("catalogo"):
                v = variables.setdefault(esp["catalogo"], {"pts": 0.0, "max": 0.0, "paquete": pkg})
                v["pts"] += esp["peso"] * frac
                v["max"] += esp["peso"]
    return repro


# --------------------------------------------------------------------------- puntaje de research

RE_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
RE_CITA = re.compile(r'^\s*>\s*["“](.+?)["”]\s*[—–-]+\s*\[[^\]]*\]\((https?://[^)\s]+)\)', re.M)


def campo(txt, nombre, siguientes):
    m = re.search(r"^\s*(?:\*\*)?" + re.escape(nombre.rstrip(":")) + r"(?:\*\*)?\s*:(?:\*\*)?(.*)$", txt, re.M)
    if not m:
        return None
    resto = txt[m.start(1):]
    corte = len(resto)
    for s in siguientes:
        mm = re.search(r"^\s*(?:\*\*)?" + re.escape(s.rstrip(":")) + r"(?:\*\*)?\s*:", resto, re.M)
        if mm and mm.start() > 0:
            corte = min(corte, mm.start())
    return resto[:corte].strip()


def puntuar_research(ctx: Ctx, checks: Checks, fuentes: Fuentes, variables):
    R = ctx.res
    pts_cfg = R["puntaje"]
    campos = R["formato"]["campos"]
    for tema in R["temas"]:
        tarea = f"research:{tema['id']}"
        p = ctx.repo / tema["archivo"]
        if not p.exists():
            checks.add(f"research:{tema['id']}:formato", tarea, 0, pts_cfg["formato"], f"falta {tema['archivo']}")
            checks.add(f"research:{tema['id']}:fuente", tarea, 0, pts_cfg["fuente_accesible"], "")
            checks.add(f"research:{tema['id']}:citas", tarea, 0, pts_cfg["por_cita_verificada"] * pts_cfg["max_citas"], "")
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        problemas = []
        valores = {}
        for i, c in enumerate(campos):
            v = campo(txt, c, campos[i + 1:] + [R["formato"]["seccion_citas"]])
            if not v:
                problemas.append(f"falta '{c}' o está vacío")
            valores[c] = v or ""
        conf = norm(valores.get("Confianza:", ""))
        if conf and not any(conf.startswith(x) for x in R["formato"]["confianza"]):
            problemas.append("Confianza tiene que ser alta, media o baja")
        fuentes_txt = valores.get("Fuentes:", "")
        links = RE_LINK.findall(fuentes_txt)
        if not links:
            problemas.append("Fuentes sin links [título](URL)")
        if not re.search(R["formato"]["fecha_consulta"], fuentes_txt):
            problemas.append("Fuentes sin 'consultado AAAA-MM-DD'")
        if not txt.lstrip().startswith("#"):
            problemas.append("falta el título '# <Tema>'")
        checks.add(f"research:{tema['id']}:formato", tarea, 0 if problemas else pts_cfg["formato"], pts_cfg["formato"],
                   f"{tema['archivo']} — " + "; ".join(problemas) if problemas else "")
        # Fuentes accesibles
        acc = 0
        msg_f = ""
        for _, url in links[:6]:
            ok, _ = fuentes.texto(url)
            if ok:
                acc = 1
                break
        if links and not acc:
            msg_f = f"{tema['archivo']} — ninguna URL de Fuentes respondió con texto legible"
        checks.add(f"research:{tema['id']}:fuente", tarea, pts_cfg["fuente_accesible"] * acc, pts_cfg["fuente_accesible"], msg_f)
        # Citas verificadas
        citas = RE_CITA.findall(txt)
        verif, fallas, vistas = 0, [], set()
        for cita, url in citas:
            if verif >= pts_cfg["max_citas"]:
                break
            if norm_busqueda(cita) in vistas:
                continue
            vistas.add(norm_busqueda(cita))
            if not (R["formato"]["cita_min_caracteres"] <= len(cita) <= R["formato"]["cita_max_caracteres"]):
                fallas.append(f"cita de largo inválido ({len(cita)} caracteres)")
                continue
            ok, contenido = fuentes.texto(url)
            if not ok:
                fallas.append(f"{url}: {contenido}")
            elif cita_en_texto(cita, contenido):
                verif += 1
            else:
                fallas.append(f"la cita '{cita[:60]}…' no aparece en {url}")
        mx = pts_cfg["por_cita_verificada"] * pts_cfg["max_citas"]
        if not citas:
            fallas.append(f"sin sección 'Citas:' con líneas > \"cita textual\" — [título](URL)")
        checks.add(f"research:{tema['id']}:citas", tarea, min(mx, verif * pts_cfg["por_cita_verificada"]), mx,
                   f"{tema['archivo']} — " + "; ".join(fallas[:3]) if verif < pts_cfg["max_citas"] else "")

    # Tabla de cultivos
    C = R["cultivos"]
    tarea = "research:cultivos_zona"
    p = ctx.repo / C["archivo"]
    pe = ctx.repo / C["evidencia"]
    df, err = leer_csv(p) if p.exists() else (None, [f"falta {C['archivo']}"])
    ev_df, ev_err = leer_csv(pe) if pe.exists() else (None, [f"falta {C['evidencia']}"])
    if ev_df is not None and list(ev_df.columns)[: len(C["columnas_evidencia"])] != C["columnas_evidencia"]:
        ev_err = [f"{C['evidencia']} tiene que tener las columnas {C['columnas_evidencia']}"]
        ev_df = None
    evid = {}
    if ev_df is not None:
        for _, r in ev_df.iterrows():
            evid.setdefault((r["cultivo"], r["atributo"]), []).append(r)
    por_celda = pts_cfg["por_celda_verificada"]
    filas_df = {}
    if df is not None and "cultivo" in df.columns:
        for _, r in df.iterrows():
            filas_df[r["cultivo"]] = r
    for cult in C["filas"]:
        for at in C["atributos"]:
            cid = f"cultivo:{cult}:{at['nombre']}"
            msg = ""
            pts = 0.0
            if df is None:
                msg = "; ".join(err)
            elif at["nombre"] not in df.columns:
                msg = f"config/cultivos.csv no tiene la columna {at['nombre']}"
            elif cult not in filas_df:
                msg = f"falta la fila '{cult}' en config/cultivos.csv"
            else:
                val = str(filas_df[cult][at["nombre"]]).strip()
                if not val:
                    msg = f"{cult}.{at['nombre']} vacío"
                else:
                    tipo = at.get("tipo", "numero")
                    valido = True
                    if tipo == "numero":
                        try:
                            x = float(val)
                            lo, hi = at.get("rango", [-1e18, 1e18])
                            if not (lo <= x <= hi):
                                valido, msg = False, f"{cult}.{at['nombre']}={val} fuera de rango {at.get('rango')}"
                        except ValueError:
                            valido, msg = False, f"{cult}.{at['nombre']}={val!r} no es un número (usar punto decimal)"
                    elif tipo == "mmdd" and not RE_MMDD.match(val):
                        valido, msg = False, f"{cult}.{at['nombre']}={val!r} tiene que ser MM-DD"
                    elif tipo == "categoria" and val not in at.get("valores", []):
                        valido, msg = False, f"{cult}.{at['nombre']}={val!r} tiene que ser uno de {at.get('valores')}"
                    if valido:
                        if ev_df is None:
                            msg = "; ".join(ev_err)
                        else:
                            cand = [e for e in evid.get((cult, at["nombre"]), []) if norm(e["valor"]) == norm(val)]
                            if not cand:
                                msg = f"{cult}.{at['nombre']}={val}: sin fila de evidencia con ese valor"
                            for e in cand:
                                ok, contenido = fuentes.texto(e["fuente_url"])
                                if not ok:
                                    msg = f"{cult}.{at['nombre']}: {e['fuente_url']} → {contenido}"
                                    continue
                                if not cita_en_texto(e["cita"], contenido):
                                    msg = f"{cult}.{at['nombre']}: la cita no aparece en {e['fuente_url']}"
                                    continue
                                if tipo == "numero" and not numero_en_cita(val, e["cita"]):
                                    msg = f"{cult}.{at['nombre']}: el número {val} no aparece en la cita"
                                    continue
                                pts, msg = por_celda, ""
                                break
            checks.add(cid, tarea, pts, por_celda, msg, catalogo=at.get("catalogo"))
            v = variables.setdefault(at["catalogo"], {"pts": 0.0, "max": 0.0, "paquete": "research"})
            v["pts"] += pts
            v["max"] += por_celda


# --------------------------------------------------------------------------- principal

def tareas_de(ctx: Ctx):
    t = list(ctx.ent["paquetes"].keys())
    t += [f"research:{x['id']}" for x in ctx.res["temas"]]
    return t


def calcular(ctx: Ctx, repro_pedidos=(), repro_timeout=1800):
    checks = Checks()
    variables = {}
    fuentes = Fuentes(ctx)
    repro = puntuar_datos(ctx, checks, set(repro_pedidos), repro_timeout, variables)
    puntuar_research(ctx, checks, fuentes, variables)
    tareas = {t: {"pts": 0.0, "max": 0.0} for t in tareas_de(ctx)}
    for c in checks.items.values():
        t = tareas.setdefault(c["tarea"], {"pts": 0.0, "max": 0.0})
        t["pts"] += c["pts"]
        t["max"] += c["max"]
    for t in tareas.values():
        t["pts"] = round(t["pts"], 3)
        t["max"] = round(t["max"], 3)
        t["ok"] = t["pts"] >= t["max"] - 1e-6
    umbral = 0.999
    estados = {}
    for cid, row in ctx.catalogo.items():
        v = variables.get(cid)
        if v is None:
            estados[cid] = {"estado": "Fuera de v1", "pts": 0, "max": 0}
            continue
        frac = v["pts"] / v["max"] if v["max"] else 0
        estado = "Procesado" if frac >= umbral else ("En curso" if frac > 0 else "Pendiente")
        estados[cid] = {"estado": estado, "pts": round(v["pts"], 3), "max": round(v["max"], 3), "paquete": v.get("paquete")}
    total = round(sum(c["pts"] for c in checks.items.values()), 3)
    mx = round(sum(c["max"] for c in checks.items.values()), 3)
    return {
        "version": 1,
        "fecha": dt.datetime.now().isoformat(timespec="seconds"),
        "total": total,
        "max": mx,
        "tareas": tareas,
        "reproducible": repro,
        "checks": checks.items,
        "variables": estados,
        "avisos": ctx.avisos[:50],
    }


def resumen(res: dict, tarea: str | None, n=40) -> str:
    L = [f"PUNTAJE TOTAL: {res['total']:.2f} / {res['max']:.2f}"]
    L.append("")
    L.append("Por tarea:")
    for t, v in res["tareas"].items():
        marca = "OK " if v["ok"] else "   "
        L.append(f"  {marca}{t:<32} {v['pts']:8.2f} / {v['max']:.2f}")
    sel = [(cid, c) for cid, c in res["checks"].items() if not c["ok"] and (tarea is None or c["tarea"] == tarea or (tarea == "research" and c["tarea"].startswith("research")))]
    sel.sort(key=lambda x: -(x[1]["max"] - x[1]["pts"]))
    L.append("")
    L.append(f"Checks que fallan{' en ' + tarea if tarea else ''} (ordenados por lo que suman si se arreglan; {len(sel)} en total):")
    for cid, c in sel[:n]:
        L.append(f"  +{c['max'] - c['pts']:.2f}  {c['msg'] or cid}")
    if tarea and tarea in res.get("reproducible", {}):
        r = res["reproducible"][tarea]
        L.append("")
        L.append(f"Reproducibilidad de {tarea}: {r['ok']} ({r['msg']})")
    if res.get("avisos"):
        L.append("")
        L.append("Avisos:")
        for a in res["avisos"][:10]:
            L.append(f"  - {a}")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--spec", default=None, help="carpeta con entregables.yaml, research.yaml y catalogo.csv")
    ap.add_argument("--cache", default=None)
    ap.add_argument("--json", default=None)
    ap.add_argument("--tarea", default=None)
    ap.add_argument("--resumen", action="store_true")
    ap.add_argument("--reproducir", default="", help="paquetes separados por coma")
    ap.add_argument("--repro-timeout", type=int, default=1800)
    ap.add_argument("--python", default=None, help="python del proyecto (.venv) para correr process.py")
    ap.add_argument("--sin-red", action="store_true")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    repo = Path(a.repo).resolve()
    spec = Path(a.spec).resolve() if a.spec else repo / "loop" / "spec"
    cache = Path(a.cache).resolve() if a.cache else repo / "loop" / "state" / "cache_agente"
    python = a.python
    if not python:
        cand = repo / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        python = str(cand) if cand.exists() else None
    ctx = Ctx(repo, spec, cache, python, red=not a.sin_red)
    pedidos = [x.strip() for x in a.reproducir.split(",") if x.strip()]
    res = calcular(ctx, pedidos, a.repro_timeout)
    if a.json:
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    if a.resumen or not a.json:
        sys.stdout.write(resumen(res, a.tarea) + "\n")


if __name__ == "__main__":
    main()
