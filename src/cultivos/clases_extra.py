"""Clases 0, 27 y 58 del CDL en `data/reference/clases_cdl.csv` (T139, para_decidir #19).

`docs/research/cdl_csb.md` propone darles grupo propio a tres clases que hoy caen en `otro`:

- 0  Background          → `sin_dato` (fondo / sin dato; no es una cobertura)
- 27 Rye                 → `centeno`
- 58 Clover/Wildflowers  → `trebol`

Este módulo:

1. `aplicar_grupos(df)`: pone esos grupos en la tabla de clases (idempotente). Verifica que el
   nombre oficial sea el esperado y no inventa filas: si falta un código, falla.
2. `efecto(...)`: con un recorte del CDL y los ids de condado por píxel, calcula `pct_*` y
   `frac_pixeles_validos` antes y después, en los escenarios que se discuten en la fila 19.
3. CLI:
   - `python -m src.cultivos.clases_extra --escribir` reescribe `clases_cdl.csv` con los grupos.
   - `python -m src.cultivos.clases_extra --efecto <cdl1.tif> [<cdl2.tif> ...]` mide el efecto
     en recortes del CDL (EPSG:5070) usando `data/reference/condados.gpkg`. Con `--sumar` junta
     los conteos de todas las teselas (condados completos).

No cambia `rotacion_anual()` ni las máscaras: las clases 27 y 58 ya cuentan como área agrícola
(`AGRICOLA` de `process.py`, códigos 1–61) y el 0 ya queda fuera del denominador. Sí cambia la
columna `cultivo` de `src/lotes/process.py`, que sale de `grupo`. Lo que cambia
cada escenario se documenta en `docs/datasets/cultivos.md` (sección T139).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
CLASES = REPO / "data" / "reference" / "clases_cdl.csv"

# código → (palabra que tiene que estar en el nombre oficial, grupo propuesto por el research)
GRUPOS_EXTRA = {0: ("background", "sin_dato"), 27: ("rye", "centeno"),
                58: ("clover", "trebol")}

# Copia de las listas de src/cultivos/process.py (no se importan para no depender de geopandas
# ni de los cambios de las tareas retenidas que tocan ese archivo).
AGRICOLA = list(range(1, 62)) + list(range(66, 78)) + list(range(204, 255))
PCT_CLASES = {"pct_maiz": [1], "pct_soja": [5], "pct_trigo": [24, 26], "pct_alfalfa": [36],
              "pct_heno": [37], "pct_doble_trigo_soja": [26], "pct_barbecho": [61]}
# columnas nuevas que harían falta si el humano quiere ver centeno y trébol en rotacion_anual.csv
PCT_NUEVAS = {"pct_centeno": [27], "pct_trebol": [58]}

ESCENARIOS = {
    "actual": "hoy: 27 y 58 dentro del área agrícola; el 0 no cuenta",
    "A_grupos": "propuesta: solo cambia el grupo en clases_cdl.csv (pct_* iguales) "
                "y se agregan pct_centeno, pct_trebol y frac_pixeles_validos",
    "B_cobertura": "alternativa: 27 y 58 salen del área agrícola (como 'cobertura/forraje')",
}


def aplicar_grupos(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve la tabla de clases con los grupos de 0, 27 y 58 (idempotente)."""
    out = df.copy()
    cod = out["codigo"].astype(int)
    for c, (palabra, grupo) in GRUPOS_EXTRA.items():
        fila = cod == c
        if not fila.any():
            raise ValueError(f"falta el código {c} en clases_cdl.csv; no se agrega a mano")
        nombre = str(out.loc[fila, "nombre"].iloc[0])
        if palabra not in nombre.lower():
            raise ValueError(f"el código {c} se llama '{nombre}', se esperaba '{palabra}'")
        out.loc[fila, "grupo"] = grupo
    return out


def escribir_clases(ruta: Path) -> None:
    """Reescribe la tabla con los grupos nuevos y conserva el fin de línea del archivo.

    El `.gitattributes` del repo no convierte finales de línea: pasar de CRLF a LF ensuciaría el
    diff de todas las filas.
    """
    fin = "\r\n" if b"\r\n" in ruta.read_bytes()[:200] else "\n"
    df = aplicar_grupos(pd.read_csv(ruta))
    df.to_csv(ruta, index=False, encoding="utf-8", lineterminator=fin)


def conteo_por_condado(cdl: np.ndarray, ids: np.ndarray, n: int) -> np.ndarray:
    """Matriz (n + 1, 256) de píxeles por id de condado (0 = fuera) y código CDL."""
    x = cdl.ravel().astype(np.int64)
    i = ids.ravel().astype(np.int64)
    return np.bincount(i * 256 + x, minlength=(n + 1) * 256).reshape(n + 1, 256)


def efecto(cuenta: np.ndarray) -> pd.DataFrame:
    """pct_* y frac_pixeles_validos por condado (filas 1..n de `cuenta`) y escenario.

    `frac_pixeles_validos` = píxeles con código distinto de 0 / píxeles del condado. En el
    escenario `actual` no existe la columna en rotacion_anual.csv: se informa igual (sería 1,
    porque hoy no se distingue el fondo) para comparar.
    """
    c = cuenta[1:]
    total = c.sum(axis=1)
    validos = total - c[:, 0]
    filas = []
    for esc in ESCENARIOS:
        agr_cls = AGRICOLA if esc != "B_cobertura" else [k for k in AGRICOLA if k not in (27, 58)]
        agr = c[:, agr_cls].sum(axis=1)
        d = {"id": np.arange(1, len(c) + 1), "escenario": esc, "px_condado": total,
             "px_agricolas": agr}
        for col, cls in {**PCT_CLASES, **PCT_NUEVAS}.items():
            d[col] = np.where(agr > 0, 100 * c[:, cls].sum(axis=1) / np.maximum(agr, 1), np.nan)
        d["frac_pixeles_validos"] = (np.ones(len(c)) if esc == "actual"
                                     else np.where(total > 0, validos / np.maximum(total, 1), np.nan))
        filas.append(pd.DataFrame(d))
    df = pd.concat(filas, ignore_index=True)
    df = df[df["px_condado"] > 0]
    num = [k for k in df.columns if k.startswith(("pct_", "frac_"))]
    df[num] = df[num].round(4)
    return df.reset_index(drop=True)


def _tabla(cuenta: np.ndarray, fips: np.ndarray, archivo: str) -> pd.DataFrame:
    d = efecto(cuenta)
    ids = d["id"].to_numpy()
    d.insert(0, "archivo", archivo)
    d.insert(1, "fips", fips[ids - 1])
    # px de cada clase extra, para leer la tabla sin abrir el raster
    for k in GRUPOS_EXTRA:
        d[f"px_clase_{k}"] = cuenta[ids, k]
    return d.drop(columns="id")


def efecto_tifs(rutas: list[Path], sumar: bool = False) -> pd.DataFrame:
    """Efecto en recortes del CDL (GeoTIFF EPSG:5070) con los condados de condados.gpkg.

    Con `sumar=True` junta los conteos de todos los recortes (por ejemplo, las teselas de un
    año) antes de calcular, así los condados que corta una tesela quedan completos.
    """
    import geopandas as gpd
    import rasterio
    from rasterio.features import rasterize

    cond = gpd.read_file(REPO / "data" / "reference" / "condados.gpkg").to_crs(5070)
    fips = cond["fips"].astype(str).str.zfill(5).to_numpy()
    formas = [(g, i + 1) for i, g in enumerate(cond.geometry)]
    total = np.zeros((len(fips) + 1, 256), np.int64)
    salida = []
    for ruta in rutas:
        with rasterio.open(ruta) as src:
            a = src.read(1)
            ids = rasterize(formas, out_shape=a.shape, transform=src.transform, fill=0,
                            dtype="int32")
        cuenta = conteo_por_condado(a, ids, len(fips))
        if sumar:
            total += cuenta
        else:
            salida.append(_tabla(cuenta, fips, Path(ruta).name))
    if sumar:
        return _tabla(total, fips, f"{len(rutas)} recortes sumados")
    return pd.concat(salida, ignore_index=True)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--escribir", action="store_true", help="reescribe clases_cdl.csv")
    ap.add_argument("--efecto", nargs="+", type=Path, help="recortes del CDL a medir")
    ap.add_argument("--sumar", action="store_true",
                    help="suma los conteos de todos los recortes antes de calcular")
    ap.add_argument("--salida", type=Path, help="CSV para la tabla del efecto")
    a = ap.parse_args(argv)
    if a.escribir:
        escribir_clases(CLASES)
        print(f"clases_cdl.csv: grupos de {sorted(GRUPOS_EXTRA)} actualizados", flush=True)
    if a.efecto:
        df = efecto_tifs(a.efecto, sumar=a.sumar)
        if a.salida:
            df.to_csv(a.salida, index=False, encoding="utf-8")
        else:
            df.to_csv(sys.stdout, index=False)


if __name__ == "__main__":
    main()
