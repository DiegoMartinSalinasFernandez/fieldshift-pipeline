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
# Rendimientos por cultivo en bu/ac (formato largo, columna `cultivo`)
RENDIMIENTO_BU_AC = {"maiz": (20, 300), "soja": (5, 100)}
RELLENOS = {-9999, -999, -99.99, -999.9, -9999.9, -99999}
TEXTO = {"estado", "condado", "cultivo", "flag_nass", "ventana"}

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
        if num.isna().all():
            continue  # columna de texto
        if num.isna().any():
            errores.append(f"{c}: hay valores no numéricos {llenos[num.isna()].unique()[:3].tolist()}")
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
            r = rend[(df["cultivo"] == cult) & rend.notna()]
            n = int(((r < lo) | (r > hi)).sum())
            if n:
                errores.append(f"rend_bu_ac de {cult}: {n} valores fuera de {lo}-{hi} bu/ac")
    return errores
