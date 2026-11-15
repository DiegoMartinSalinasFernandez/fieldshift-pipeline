"""validar_csv(): chequea que un CSV procesado cumpla el contrato de los CSV (§4 y §7 del plan)."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from src.common.config import REPO, estados_config

# Rangos físicos por nombre exacto de columna o por prefijo (§7 del plan).
RANGOS_EXACTOS = {
    "ndvi": (-1, 1), "evi": (-1, 1), "ndvi_maiz": (-1, 1), "ndvi_soja": (-1, 1),
    "sm_surface_m3m3": (0, 0.6), "sm_rootzone_m3m3": (0, 0.6),
    "hr_pct": (0, 100), "gwettop": (0, 1), "gwetroot": (0, 1), "gwetprof": (0, 1),
    "frac_pixeles_validos": (0, 1), "lat_centroide": (-90, 90), "lon_centroide": (-180, 180),
}
RANGOS_PREFIJO = [  # (regex, (min, max))
    (r"^prec_.*_mm$", (0, None)), (r"^dias_", (0, 366)), (r"^pct_", (0, 100)),
    (r"^sup_", (0, None)), (r"^produccion_", (0, None)), (r"^area_", (0, None)),
]
# Rendimientos por cultivo en bu/ac (formato largo, columna `cultivo`). Rangos de los 10 estados
# (para_decidir #24, docs/research/rangos_estados_nuevos.md y T145): encuesta NASS por condado
# 2000-2025, todas las prácticas, riego y secano. Mínimos reales: maíz 4,5 (Pennington SD 2002),
# soja 2,9 (Pennington SD 2003), trigo de invierno 7,2 (secano, Morton KS 2013), avena 5,0
# (Dundy NE 2000). Máximos: maíz 253,6, soja 80,4, trigo 117,8, avena 133,6.
RENDIMIENTO_BU_AC = {"maiz": (2, 300), "soja": (2, 100), "trigo_invierno": (5, 130), "avena": (2, 200)}
# NASS publica rendimiento 0 en condados sin cosecha de grano (maíz y avena de SD 2000-2006: todo a
# silo o a forraje). Un 0 se acepta solo si la fila no tiene superficie cosechada ni producción.
SIN_COSECHA = ("sup_cosechada_ac", "produccion_bu")
RELLENOS = {-9999, -999, -99.99, -999.9, -9999.9, -99999}
TEXTO = {"estado", "condado", "cultivo", "flag_nass", "ventana"}
# Columnas numéricas por nombre (prefijo o unidad al final, CLAUDE.md §4). Aunque todos sus valores
# sean texto (por ejemplo "(D)" o "(Z)" de NASS sin pasar a vacío), no se toman por columna de texto:
# se avisa. Las columnas en TEXTO o que empiezan con "clase" no se revisan.
NUMERICAS_PATRON = re.compile(
    r"^(rend|sup|produccion|prec|dias|pct|doy|gdd)_"
    r"|_(mm|c|ac|ha|bu|kgha|m3m3|pct|km2|m)$"
    r"|_usd_"
)

_RE_FIPS = re.compile(r"^\d{5}$")
_RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_RE_MES = re.compile(r"^\d{4}-\d{2}$")


def _fips_validos() -> set[str]:
    p = REPO / "data" / "reference" / "condados.csv"
    if not p.exists():
        return set()
    return set(pd.read_csv(p, dtype={"fips": str}, usecols=["fips"])["fips"].str.zfill(5))


def validar_csv(ruta) -> list[str]:
    """Devuelve la lista de errores del CSV (vacía si está bien)."""
    ruta = Path(ruta)
    errores: list[str] = []
    try:
        df = pd.read_csv(ruta, dtype=str, keep_default_na=False, encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return [f"no se pudo leer {ruta.name}: {e}"]
    cols = list(df.columns)
    if not cols:
        return ["el CSV no tiene columnas"]

    # Claves y su orden
    claves = []
    if "fips" in cols:
        claves.append("fips")
    elif "fips_estado" in cols:
        claves.append("fips_estado")
    for c in ("anio", "anio_censo"):
        if c in cols:
            claves.append(c)
            break
    for c in ("fecha", "mes"):
        if c in cols:
            claves.append(c)
            break
    if not claves or claves[0] not in ("fips", "fips_estado"):
        errores.append("falta la columna clave fips (o fips_estado)")
    if cols[:len(claves)] != claves:
        errores.append(f"las claves {claves} tienen que ser las primeras columnas (hay {cols[:len(claves)]})")
    claves_dup = claves + [c for c in ("cultivo", "ventana") if c in cols]

    # Formato de claves
    if "fips" in cols:
        malos = df.loc[~df["fips"].str.match(_RE_FIPS), "fips"]
        if len(malos):
            errores.append(f"fips sin formato de 5 dígitos: {malos.unique()[:5].tolist()}")
        validos = _fips_validos()
        if not validos:
            errores.append("no existe data/reference/condados.csv para validar los fips")
        else:
            inex = sorted(set(df["fips"]) - validos)
            if inex:
                errores.append(f"fips que no están en condados.csv: {inex[:5]}")
    if "fips_estado" in cols:
        est = {e["fips"] for e in estados_config().values()}
        malos = sorted(set(df["fips_estado"]) - est)
        if malos:
            errores.append(f"fips_estado fuera de los estados de config.yaml: {malos[:5]}")
    for c in ("anio", "anio_censo"):
        if c in cols and not df[c].str.fullmatch(r"\d{4}").all():
            errores.append(f"{c} tiene valores que no son años enteros")
    if "fecha" in cols:
        if not df["fecha"].str.match(_RE_FECHA).all() or pd.to_datetime(df["fecha"], errors="coerce").isna().any():
            errores.append("fecha tiene valores que no son YYYY-MM-DD")
        elif "anio" in cols and (df["fecha"].str[:4] != df["anio"]).any():
            errores.append("anio no coincide con el año de fecha")
    if "mes" in cols:
        if not df["mes"].str.match(_RE_MES).all():
            errores.append("mes tiene valores que no son YYYY-MM")
        elif "anio" in cols and (df["mes"].str[:4] != df["anio"]).any():
            errores.append("anio no coincide con el año de mes")

    # Duplicados
    if claves_dup:
        n = int(df.duplicated(subset=claves_dup).sum())
        if n:
            errores.append(f"{n} filas con claves duplicadas ({claves_dup})")

    # Valores: decimales con punto, sin rellenos, rangos físicos
    for c in cols:
        if c in claves or c in TEXTO or c.startswith("clase"):
            continue
        llenos = df.loc[df[c] != "", c]
        if llenos.empty:
            continue
        if llenos.str.contains(r"^-?\d+,\d+$", regex=True).any():
            errores.append(f"{c}: hay decimales con coma")
        num = pd.to_numeric(llenos, errors="coerce")
        numerica = bool(NUMERICAS_PATRON.search(c))
        if num.isna().all() and not numerica:
            continue  # columna de texto
        if num.isna().any():
            por_nombre = " (es numérica por su nombre)" if numerica and num.isna().all() else ""
            errores.append(f"{c}: hay valores no numéricos{por_nombre} "
                           f"{llenos[num.isna()].unique()[:3].tolist()}")
        if num.isin(RELLENOS).any():
            errores.append(f"{c}: hay valores de relleno (-999/-9999); van vacíos")
        rango = RANGOS_EXACTOS.get(c)
        if rango is None:
            for patron, r in RANGOS_PREFIJO:
                if re.search(patron, c):
                    rango = r
                    break
        if rango is not None:
            lo, hi = rango
            fuera = pd.Series(False, index=num.index)
            if lo is not None:
                fuera |= num < lo
            if hi is not None:
                fuera |= num > hi
            if fuera.any():
                errores.append(f"{c}: {int(fuera.sum())} valores fuera del rango físico {rango}")
    if "rend_bu_ac" in cols and "cultivo" in cols:
        rend = pd.to_numeric(df["rend_bu_ac"], errors="coerce")
        for cult, (lo, hi) in RENDIMIENTO_BU_AC.items():
            fila = (df["cultivo"] == cult) & rend.notna()
            fuera = fila & ((rend < lo) | (rend > hi))
            # sin columnas de cosecha no hay cómo saberlo: el 0 se rechaza
            sin_cosecha = (rend == 0) & any(c in cols for c in SIN_COSECHA)
            for c in SIN_COSECHA:
                if c in cols:
                    sin_cosecha &= pd.to_numeric(df[c], errors="coerce").fillna(0) == 0
            n = int((fuera & ~sin_cosecha).sum())
            if n:
                errores.append(f"rend_bu_ac de {cult}: {n} valores fuera de {lo}-{hi} bu/ac")
    return errores
