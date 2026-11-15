"""Sorgo granífero como clase de rotación en Kansas (T137, `para_decidir.md` fila 11).

Suma columnas nuevas a dos salidas que ya arma `process.py`, sin cambiar las que existen:

- `rotacion_anual.csv` (fips, anio): `pct_sorgo`, `pct_doble_trigo_sorgo` y las transiciones por píxel
  entre el CDL del año anterior y el actual que propone `docs/research/sorgo.md`:
  `pct_sorgo_tras_trigo`, `pct_sorgo_tras_sorgo`, `pct_barbecho_tras_sorgo`, `pct_trigo_tras_barbecho`.
- `rotacion_secuencia.csv` (fips, ventana): `pct_trigo_sorgo_barbecho` (la secuencia trigo–sorgo–barbecho
  en tres años seguidos, al menos una vez en la ventana de 8 años) y `pct_rotacion_sorgo` (sorgo en algún año).

El sorgo **no** entra en `produccion_anual.csv` (no es cultivo con rendimiento).

Solo los condados de Kansas (FIPS de estado 20): en Nebraska la precisión del sorgo en el CDL es mala
(productor 41–57 %) y en los demás estados casi no hay sorgo. En las filas de otros estados las columnas
nuevas quedan vacías; si la máquina no tiene Kansas, el script no hace nada.

Clases del CDL (metadatos oficiales): 4 Sorghum, 236 Dbl Crop WinWht/Sorghum, 24 Winter Wheat,
26 Dbl Crop WinWht/Soybeans, 61 Fallow/Idle Cropland.

Correr después de `process.py`:  .venv/bin/python -X utf8 src/cultivos/sorgo.py
Idempotente: si las columnas de sorgo ya están en los CSV, se reemplazan.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.cultivos.process import (AGRICOLA, OUT, VENTANA, teselas_esperadas,  # noqa: E402
                                  teselas_por_anio)

ESTADOS_SORGO = ("20",)  # Kansas
SORGO = [4, 236]          # sorgo solo y doble cultivo trigo de invierno/sorgo
DOBLE_TRIGO_SORGO = [236]
TRIGO = [24, 26]          # igual que pct_trigo de process.py
BARBECHO = [61]

# columna -> (clases del año anterior, clases del año actual)
TRANS_SORGO = {
    "pct_sorgo_tras_trigo": (TRIGO, SORGO),
    "pct_sorgo_tras_sorgo": (SORGO, SORGO),
    "pct_barbecho_tras_sorgo": (SORGO, BARBECHO),
    "pct_trigo_tras_barbecho": (BARBECHO, TRIGO),
}
COLS_ANUAL = ["pct_sorgo", "pct_doble_trigo_sorgo", *TRANS_SORGO]
COLS_SECUENCIA = ["pct_trigo_sorgo_barbecho", "pct_rotacion_sorgo"]


def _lut(clases) -> np.ndarray:
    t = np.zeros(256, bool)
    t[list(clases)] = True
    return t


ES_AGRICOLA = _lut(AGRICOLA)
ES_SORGO, ES_TRIGO, ES_BARBECHO = _lut(SORGO), _lut(TRIGO), _lut(BARBECHO)
ES_DOBLE = _lut(DOBLE_TRIGO_SORGO)
# para cada transición: (lut del año anterior, lut del año actual)
LUT_TRANS = {c: (_lut(a), _lut(b)) for c, (a, b) in TRANS_SORGO.items()}


# ---------------------------------------------------------------- núcleo sin rasters (se prueba sin red)

def acumular_anio(ids: np.ndarray, x: np.ndarray, previo: np.ndarray | None, n: int,
                  acc: dict[str, np.ndarray]) -> None:
    """Suma a `acc` las cuentas por condado (ids 1..n; 0 = fuera) de un año del CDL.

    Claves de `acc`: `agricola`, `sorgo`, `doble` (año actual) y, si hay `previo`,
    `<col>_num` (píxeles con la transición) y `<col>_den` (píxeles de la clase actual que el año
    anterior eran agrícolas: el mismo denominador que las transiciones maíz–soja de process.py).
    """
    x = x.ravel()
    ids = ids.ravel()

    def suma(sel, clave):
        acc[clave] = acc.get(clave, np.zeros(n + 1, np.int64)) + np.bincount(ids[sel], minlength=n + 1)

    suma(ES_AGRICOLA[x], "agricola")
    suma(ES_SORGO[x], "sorgo")
    suma(ES_DOBLE[x], "doble")
    if previo is None:
        return
    previo = previo.ravel()
    agr_prev = ES_AGRICOLA[previo]
    for col, (antes, ahora) in LUT_TRANS.items():
        den = ahora[x] & agr_prev
        suma(den, f"{col}_den")
        suma(den & antes[previo], f"{col}_num")


def porcentajes_anio(acc: dict[str, np.ndarray], hay_previo: bool) -> dict[str, np.ndarray]:
    """Columnas de un año (sin la fila 0 de 'fuera de condado'). Vacío (NaN) si el denominador es 0."""
    def pct(num, den):
        num, den = num[1:], den[1:]
        return np.where(den > 0, 100 * num / np.maximum(den, 1), np.nan)

    out = {"pct_sorgo": pct(acc["sorgo"], acc["agricola"]),
           "pct_doble_trigo_sorgo": pct(acc["doble"], acc["agricola"])}
    for col in TRANS_SORGO:
        if hay_previo:
            cero = np.zeros_like(acc["agricola"])
            out[col] = pct(acc.get(f"{col}_num", cero), acc.get(f"{col}_den", cero))
        else:
            out[col] = np.full(len(acc["agricola"]) - 1, np.nan)
    return out


def indicadores_secuencia(s: np.ndarray) -> dict[str, np.ndarray]:
    """Indicadores por píxel de una pila (años × píxeles) de códigos CDL de una ventana.

    `trigo_sorgo_barbecho`: en algún año t, trigo en t, sorgo en t+1 y barbecho en t+2.
    `sorgo`: sorgo (4 o 236) en algún año. `base`: los 8 años son agrícolas (denominador).
    """
    t, so, b = ES_TRIGO[s], ES_SORGO[s], ES_BARBECHO[s]
    wsf = (t[:-2] & so[1:-1] & b[2:]).any(axis=0)
    return {"base": ES_AGRICOLA[s].all(axis=0), "trigo_sorgo_barbecho": wsf, "sorgo": so.any(axis=0)}


def sumar_columnas(base: pd.DataFrame, nuevas: pd.DataFrame, claves: list[str]) -> pd.DataFrame:
    """Une `nuevas` a `base` por `claves`, reemplazando las columnas que ya estuvieran (idempotente).

    Mantiene las filas y el orden de `base`; las columnas nuevas van al final.
    """
    extra = [c for c in nuevas.columns if c not in claves]
    b = base.drop(columns=[c for c in extra if c in base.columns])
    n = nuevas.copy()
    for c in claves:
        n[c] = n[c].astype(b[c].dtype)
    out = b.merge(n, on=claves, how="left", validate="one_to_one")
    assert len(out) == len(b)
    return out


# ---------------------------------------------------------------- rasters del CDL

def _condados_sorgo():
    import geopandas as gpd
    cond = gpd.read_file(REPO / "data" / "reference" / "condados.gpkg").to_crs(5070)
    cond["fips"] = cond["fips"].astype(str).str.zfill(5)
    return cond[cond["fips"].str[:2].isin(ESTADOS_SORGO)].reset_index(drop=True)


def _ids_tesela(src, formas):
    from rasterio.features import rasterize
    return rasterize(formas, out_shape=(src.height, src.width), transform=src.transform,
                     fill=0, dtype="int32").ravel()


def rotacion_sorgo_anual(cond=None, tes=None) -> pd.DataFrame | None:
    """Columnas de sorgo por condado de Kansas y año (mismos años completos que `rotacion_anual`)."""
    import rasterio

    cond = _condados_sorgo() if cond is None else cond
    tes = teselas_por_anio() if tes is None else tes
    if cond.empty or not tes:
        return None
    claves = teselas_esperadas(cond, set().union(*[set(t) for t in tes.values()]))
    completos = sorted(a for a, t in tes.items() if claves <= set(t))
    if not completos:
        return None
    fips = cond["fips"].tolist()
    n = len(fips)
    formas = [(g, i + 1) for i, g in enumerate(cond.geometry)]
    acc = {a: {} for a in completos}
    for clave in sorted(claves):
        ids, previo = None, None
        for a in range(completos[0], completos[-1] + 1):
            if a not in completos:
                previo = None
                continue
            with rasterio.open(tes[a][clave]) as src:
                x = src.read(1)
                if ids is None:
                    ids = _ids_tesela(src, formas)
            x = x.ravel()
            ok = previo is not None and previo.shape == x.shape
            acumular_anio(ids, x, previo if ok else None, n, acc[a])
            previo = x
    filas = []
    for a in completos:
        cols = porcentajes_anio(acc[a], hay_previo=(a - 1) in completos)
        filas.append(pd.DataFrame({"fips": fips, "anio": a, **cols}))
    df = pd.concat(filas, ignore_index=True)
    df[COLS_ANUAL] = df[COLS_ANUAL].round(3)
    return df.sort_values(["fips", "anio"]).reset_index(drop=True)


def rotacion_sorgo_secuencia(cond=None, tes=None) -> pd.DataFrame | None:
    """Columnas de sorgo por condado de Kansas y ventana de 8 años (mismas ventanas que process.py)."""
    import rasterio

    cond = _condados_sorgo() if cond is None else cond
    tes = teselas_por_anio() if tes is None else tes
    if cond.empty or not tes:
        return None
    claves = teselas_esperadas(cond, set().union(*[set(t) for t in tes.values()]))
    completos = sorted(a for a, t in tes.items() if claves <= set(t))
    ventanas = [a for a in completos if all(a + k in completos for k in range(VENTANA))]
    if not ventanas:
        return None
    anios = sorted({a + k for a in ventanas for k in range(VENTANA)})
    fips = cond["fips"].tolist()
    n = len(fips)
    formas = [(g, i + 1) for i, g in enumerate(cond.geometry)]
    ind = ["base", "trigo_sorgo_barbecho", "sorgo"]
    acc = {v: {k: np.zeros(n + 1) for k in ind} for v in ventanas}
    for clave in sorted(claves):
        pila, ids = [], None
        for a in anios:
            with rasterio.open(tes[a][clave]) as src:
                pila.append(src.read(1).ravel())
                if ids is None:
                    ids = _ids_tesela(src, formas)
        dentro = ids > 0
        pila = np.stack([p[dentro] for p in pila])
        i = ids[dentro]
        for v in ventanas:
            s = pila[anios.index(v):anios.index(v) + VENTANA]
            vals = indicadores_secuencia(s)
            ok = vals["base"]
            for k in ind:
                acc[v][k] += np.bincount(i[ok], weights=vals[k][ok].astype(float), minlength=n + 1)
    filas = []
    for v in ventanas:
        b = acc[v]["base"][1:]

        def media(k):
            return np.where(b > 0, 100 * acc[v][k][1:] / np.maximum(b, 1), np.nan)

        filas.append(pd.DataFrame({"fips": fips, "ventana": f"{v}-{v + VENTANA - 1}",
                                   "pct_trigo_sorgo_barbecho": media("trigo_sorgo_barbecho"),
                                   "pct_rotacion_sorgo": media("sorgo")}))
    df = pd.concat(filas, ignore_index=True)
    df[COLS_SECUENCIA] = df[COLS_SECUENCIA].round(4)
    return df.sort_values(["fips", "ventana"]).reset_index(drop=True)


def _agregar(nombre: str, claves: list[str], nuevas: pd.DataFrame | None) -> None:
    ruta = OUT / nombre
    if nuevas is None:
        print(f"{nombre}: sin teselas completas de Kansas; no se agrega nada")
        return
    if not ruta.exists():
        print(f"{nombre}: no existe (correr antes src/cultivos/process.py); no se agrega nada")
        return
    base = pd.read_csv(ruta, dtype={"fips": str})
    out = sumar_columnas(base, nuevas, claves)
    out.to_csv(ruta, index=False, encoding="utf-8")
    print(f"{nombre}: columnas de sorgo agregadas ({nuevas['fips'].nunique()} condados de KS)")


def main() -> None:
    cond = _condados_sorgo()
    if cond.empty:
        print("Los estados de esta máquina no incluyen Kansas: no se agregan columnas de sorgo")
        return
    tes = teselas_por_anio()
    _agregar("rotacion_anual.csv", ["fips", "anio"], rotacion_sorgo_anual(cond, tes))
    _agregar("rotacion_secuencia.csv", ["fips", "ventana"], rotacion_sorgo_secuencia(cond, tes))


if __name__ == "__main__":
    main()
