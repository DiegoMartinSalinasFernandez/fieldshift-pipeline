"""Figuras simples para la demo de Space Apps, hechas solo con los datos publicados en los Releases.

Baja con `gh release download` (o, si `gh` no está o no tiene permiso, por la URL pública del release) los zips de `datos-ia-il-in` (y de `datos-ks` / `datos-oh-ne-mn` si ya
existen), los lee sin descomprimir a disco y guarda PNG en `docs/demo/fig/`:

  fig1_corn_yield_july_rain.png      rendimiento de maíz vs lluvia de julio, 2012 resaltado
  fig2_ndvi_max_vs_yield.png         NDVI máximo de píxeles de maíz / soja vs rendimiento
  fig3_smap_may_vs_planting.png      humedad SMAP de mayo (media de condados del estado) vs 50 % sembrado
  fig4_corn_after_soy_vs_corn.png    % del maíz tras soja vs % tras maíz, por condado
  fig5_corn_yield_by_year.png        rendimiento de maíz por condado y año (cajas), 2012 resaltado
  fig6_lluvia.png                    lluvia mensual IMERG vs POWER por condado-mes, un panel por estado

No hay modelos, tendencias ni ajustes: cada punto es una fila de un CSV publicado. Si falta un zip, un
archivo o una columna, esa figura se saltea con un aviso.

Uso:
  .venv/bin/python -X utf8 docs/demo/figuras.py                 # baja (si hace falta) y dibuja
  .venv/bin/python -X utf8 docs/demo/figuras.py --sin-bajar     # usa los zips que ya están en --zips
  .venv/bin/python -X utf8 docs/demo/figuras.py --https         # sin gh: urllib + URL pública, controla .sha256
  .venv/bin/python -X utf8 docs/demo/figuras.py --https --etiquetas datos-oh-ne-mn --sufijo oh_ne_mn \
      --nota "Only OH, NE and MN (release datos-oh-ne-mn); IA, IL, IN and KS not included."
  .venv/bin/python -X utf8 docs/demo/figuras.py --zips DIR --salida DIR
  .venv/bin/python -X utf8 docs/demo/figuras.py --entrega fieldshift_datos_v1.2.zip   # entrega unida, sin bajar
"""
from __future__ import annotations

import argparse
import io
import subprocess
import sys
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
ETIQUETAS = ["datos-ia-il-in", "datos-ks", "datos-oh-ne-mn"]
ZIPS = REPO / "data" / "demo_zips"          # data/ no va en git
SALIDA = Path(__file__).resolve().parent / "fig"

FIPS_ESTADO = {"19": "IA", "17": "IL", "18": "IN", "39": "OH", "31": "NE", "27": "MN", "20": "KS"}
COLORES = {"IA": "#1f77b4", "IL": "#ff7f0e", "IN": "#2ca02c", "OH": "#d62728", "NE": "#9467bd",
           "MN": "#8c564b", "KS": "#e377c2"}

SRC_NASS = "USDA NASS Quick Stats (county survey, ALL PRODUCTION PRACTICES)"
SRC_POWER = "NASA POWER (AG community, daily, county centroid)"
SRC_MODIS = "NASA MODIS MOD13Q1 NDVI 250 m (CDL corn/soy pixel masks)"
SRC_SMAP = "NASA SMAP L4 SPL4SMGP (Crop-CASMA daily layers)"
SRC_PROG = "USDA NASS Crop Progress (state, weekly)"
SRC_CDL = "USDA NASS Cropland Data Layer 30 m"
SRC_IMERG = ("GPM IMERG Final V07, served by the NASA POWER API (IMERG_PRECTOT; Late V07 for 2025-10 to "
             "2025-12), daily, county mean of 0.1° cells")
ORIGEN = "published release CSVs"             # con --entrega se cambia por el nombre del zip
NOTA = ""                                     # p. ej. "Only OH, NE and MN"; va en el pie de cada figura
SUFIJO = ""                                   # se agrega al nombre de cada PNG


def aviso(msg: str) -> None:
    print(f"AVISO: {msg}", file=sys.stderr)


# --------------------------------------------------------------------------- descarga y lectura

PAQUETES = ["clima", "cultivos", "vegetacion", "agua"]   # los zips que usan las figuras


def repo_github() -> str | None:
    """`dueño/repo` del remoto origin, para bajar por HTTPS si `gh` no está o no tiene permiso."""
    r = subprocess.run(["git", "-C", str(REPO), "remote", "get-url", "origin"], capture_output=True, text=True)
    url = r.stdout.strip()
    if r.returncode != 0 or "github.com" not in url:
        return None
    slug = url.split("github.com", 1)[1].lstrip(":/")
    return slug.removesuffix(".git") or None


def _get(url: str, timeout: int = 120) -> bytes:
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": "fieldshift-figuras"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def sha256_ok(z: Path) -> bool | None:
    """Compara `z` con `z.sha256` (formato de sha256sum). None si no hay .sha256 al lado."""
    import hashlib

    f = z.with_name(z.name + ".sha256")
    if not f.exists():
        return None
    esperado = f.read_text().split()[0].strip().lower()
    h = hashlib.sha256()
    with z.open("rb") as fh:
        for bloque in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest() == esperado


def bajar_https(et: str, d: Path) -> int:
    """Sin `gh` ni token: baja `<et>_<paquete>.zip` y su `.sha256` de la URL pública del release."""
    import urllib.error

    slug = repo_github()
    if not slug:
        aviso("HTTPS: el remoto origin no es de GitHub; no sé de dónde bajar")
        return 0
    n = 0
    for paq in PAQUETES:
        nombre = f"{et}_{paq}.zip"
        z = d / nombre
        base = f"https://github.com/{slug}/releases/download/{et}/{nombre}"
        try:
            sha = d / (nombre + ".sha256")
            if not sha.exists():
                sha.write_bytes(_get(base + ".sha256"))
            if not z.exists() or sha256_ok(z) is False:
                tmp = z.with_name(z.name + ".part")
                tmp.write_bytes(_get(base, timeout=600))
                tmp.replace(z)
            n += 1
        except (urllib.error.URLError, TimeoutError) as e:
            aviso(f"HTTPS: no se pudo bajar {nombre} de {et}: {e}")
    return n


def controlar_sha256(d: Path) -> None:
    """Saca de la carpeta (renombra a .malo) los zips cuyo .sha256 no coincide, para que no se lean."""
    for z in sorted(d.glob("*.zip")):
        ok = sha256_ok(z)
        if ok is None:
            aviso(f"{z.name}: no hay .sha256 para controlarlo")
        elif not ok:
            aviso(f"{z.name}: el sha256 NO coincide; se descarta")
            z.replace(z.with_name(z.name + ".malo"))
        else:
            print(f"sha256 ok: {z.name}")


def bajar(etiquetas: list[str], destino: Path, https: bool = False) -> None:
    for et in etiquetas:
        d = destino / et
        d.mkdir(parents=True, exist_ok=True)
        if https:
            bajar_https(et, d)
        else:
            patrones = []
            for paq in PAQUETES:
                patrones += ["--pattern", f"{et}_{paq}.zip", "--pattern", f"{et}_{paq}.zip.sha256"]
            try:
                r = subprocess.run(["gh", "release", "download", et, *patrones, "--dir", str(d),
                                    "--skip-existing"], capture_output=True, text=True)
                ok, err = r.returncode == 0, r.stderr.strip() or r.stdout.strip()
            except FileNotFoundError:
                ok, err = False, "gh no está instalado"
            if not ok:
                aviso(f"gh no pudo bajar el release {et} ({err}); pruebo por HTTPS")
                bajar_https(et, d)
        controlar_sha256(d)
        print(f"{et}: {len(list(d.glob('*.zip')))} zips en {d}")


def leer(zips: Path | list[Path], archivo: str) -> pd.DataFrame | None:
    """Une `archivo` (p. ej. 'produccion_anual.csv') de todos los zips que haya bajo `zips` (una o varias carpetas)."""
    partes = []
    carpetas = zips if isinstance(zips, list) else [zips]
    for z in sorted(x for c in carpetas for x in c.rglob("*.zip")):
        try:
            with zipfile.ZipFile(z) as zf:
                for n in zf.namelist():
                    if n.startswith("data/processed/") and Path(n).name == archivo:
                        df = pd.read_csv(io.BytesIO(zf.read(n)), dtype={"fips": str, "fips_estado": str})
                        df["origen_zip"] = z.name
                        partes.append(df)
        except zipfile.BadZipFile:
            aviso(f"{z.name} no es un zip válido")
    if not partes:
        aviso(f"{archivo} no está en ningún zip bajo {zips}")
        return None
    df = pd.concat(partes, ignore_index=True)
    claves = [c for c in ("fips", "fips_estado", "anio", "mes", "cultivo") if c in df.columns]
    return df.drop_duplicates(subset=claves, keep="last").drop(columns="origen_zip")


def leer_entrega(zip_entrega: Path) -> dict[str, pd.DataFrame | None]:
    """Plan C: arma los mismos cuadros desde un zip de la entrega unida (`fieldshift_datos_v1.x.zip`).

    Ahí no están los CSV por paquete sino `condado/tabla_anual.csv` (fips × anio × cultivo, con el clima, la
    rotación, la fenología y la fenología por estado ya unidas) y `condado/tabla_mensual.csv` (fips × mes).
    Las columnas que no dependen del cultivo se toman una vez por (fips, anio).
    """
    with zipfile.ZipFile(zip_entrega) as zf:
        def una(sufijo: str) -> pd.DataFrame | None:
            n = [x for x in zf.namelist() if x.endswith(sufijo)]
            if not n:
                aviso(f"{sufijo} no está en {zip_entrega.name}")
                return None
            return pd.read_csv(io.BytesIO(zf.read(n[0])), dtype={"fips": str})
        anual, mensual = una("condado/tabla_anual.csv"), una("condado/tabla_mensual.csv")
    out: dict[str, pd.DataFrame | None] = {"prod": anual, "agua": mensual,
                                          "clima": None, "clima_m": mensual, "fen": None, "rot": None, "fenest": None}
    if anual is not None:
        por_condado = anual.drop_duplicates(subset=["fips", "anio"])
        out["clima"] = out["rot"] = por_condado
        out["fen"] = por_condado
        if "doy_50_sembrado" in anual.columns:
            f = anual[["fips", "anio", "cultivo", "doy_50_sembrado"]].copy()
            f["fips_estado"] = f["fips"].str.zfill(5).str[:2]
            out["fenest"] = f.drop(columns="fips").dropna().drop_duplicates(
                subset=["fips_estado", "anio", "cultivo"])
    return out


def faltan(df: pd.DataFrame | None, columnas: list[str], fig: str) -> bool:
    if df is None:
        aviso(f"{fig}: se saltea (falta el archivo)")
        return True
    f = [c for c in columnas if c not in df.columns]
    if f:
        aviso(f"{fig}: se saltea (faltan columnas {f})")
        return True
    return False


def estado(fips: pd.Series) -> pd.Series:
    return fips.astype(str).str.zfill(5).str[:2].map(FIPS_ESTADO).fillna(fips.astype(str).str[:2])


def pie(fig, fuentes: list[str], extra: str = "") -> None:
    texto = "Source: " + "; ".join(fuentes) + f". Field Shift data pipeline, {ORIGEN}."
    if extra:
        texto += "\n" + extra
    if NOTA:
        texto += "\n" + NOTA
    fig.text(0.01, 0.01, texto, fontsize=7, color="#555555", ha="left", va="bottom", wrap=True)


def guardar(fig, salida: Path, nombre: str) -> None:
    salida.mkdir(parents=True, exist_ok=True)
    if NOTA:  # una línea más de pie: subir los ejes para que no se pise con el título del eje x
        fig.subplots_adjust(bottom=fig.subplotpars.bottom + 0.04)
    if SUFIJO:
        nombre = nombre.replace(".png", f"_{SUFIJO}.png")
    fig.savefig(salida / nombre, dpi=150)
    plt.close(fig)
    print(f"guardada {salida / nombre}")


def dispersion_por_estado(ax, df: pd.DataFrame, x: str, y: str, **kw) -> None:
    for est, g in df.groupby("estado", sort=True):
        ax.scatter(g[x], g[y], s=kw.get("s", 8), alpha=kw.get("alpha", 0.5),
                   color=COLORES.get(est, "#777777"), label=est, edgecolors="none")


# --------------------------------------------------------------------------- figuras

def fig_lluvia_julio(prod, clima, salida: Path) -> None:
    nombre = "fig1_corn_yield_july_rain.png"
    if faltan(prod, ["fips", "anio", "cultivo", "rend_bu_ac"], nombre) or \
            faltan(clima, ["fips", "anio", "prec_jul_mm"], nombre):
        return
    m = prod.loc[prod["cultivo"] == "maiz", ["fips", "anio", "rend_bu_ac"]].merge(
        clima[["fips", "anio", "prec_jul_mm"]], on=["fips", "anio"]).dropna()
    if m.empty or 2012 not in set(m["anio"]):
        aviso(f"{nombre}: se saltea (no hay maíz con lluvia de julio en 2012)")
        return
    otros, a12 = m[m["anio"] != 2012], m[m["anio"] == 2012]
    ests = sorted(estado(m["fips"]).unique())
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.scatter(otros["prec_jul_mm"], otros["rend_bu_ac"], s=5, alpha=0.25, color="#9e9e9e",
               edgecolors="none", label=f"Other years ({otros['anio'].min()}–{otros['anio'].max()})")
    ax.scatter(a12["prec_jul_mm"], a12["rend_bu_ac"], s=12, alpha=0.8, color="#c62828",
               edgecolors="none", label="2012 (drought year; docs/research/eventos_extremos.md)")
    ax.set_xlabel("July precipitation (mm), NASA POWER")
    ax.set_ylabel("Corn grain yield (bu/ac)")
    ax.set_title("County corn yield vs July rainfall: 2012 against all other years")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.3)
    fig.subplots_adjust(bottom=0.19)
    pie(fig, [SRC_NASS, SRC_POWER], f"One point per county-year; n = {len(m)} "
        f"({len(a12)} in 2012). States: {', '.join(ests)}. Yields: ALL PRODUCTION PRACTICES"
        + (" (mixes irrigated and rainfed corn; large irrigated share in NE and KS)." if {"NE", "KS"} & set(ests)
           else "."))
    guardar(fig, salida, nombre)


def fig_rend_por_anio(prod, salida: Path) -> None:
    nombre = "fig5_corn_yield_by_year.png"
    if faltan(prod, ["fips", "anio", "cultivo", "rend_bu_ac"], nombre):
        return
    m = prod.loc[prod["cultivo"] == "maiz", ["anio", "rend_bu_ac"]].dropna()
    if m.empty:
        aviso(f"{nombre}: se saltea (no hay rendimiento de maíz)")
        return
    anios = sorted(m["anio"].unique())
    datos = [m.loc[m["anio"] == a, "rend_bu_ac"].values for a in anios]
    fig, ax = plt.subplots(figsize=(10, 5))
    bp = ax.boxplot(datos, tick_labels=[str(a) for a in anios], showfliers=False, patch_artist=True)
    for a, caja in zip(anios, bp["boxes"]):
        caja.set_facecolor("#c62828" if a == 2012 else "#cfd8dc")
    ax.set_xlabel("Harvest year")
    ax.set_ylabel("Corn grain yield (bu/ac)")
    ax.set_title("Distribution of county corn yields by year (2012 highlighted)")
    ax.tick_params(axis="x", rotation=90, labelsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.subplots_adjust(bottom=0.2)
    pie(fig, [SRC_NASS], "Boxes: county quartiles; whiskers 1.5 IQR; outliers hidden. No detrending.")
    guardar(fig, salida, nombre)


def fig_ndvi_rend(prod, fen, salida: Path) -> None:
    nombre = "fig2_ndvi_max_vs_yield.png"
    if faltan(prod, ["fips", "anio", "cultivo", "rend_bu_ac"], nombre) or \
            faltan(fen, ["fips", "anio"], nombre):
        return
    paneles = [(c, col, t) for c, col, t in (("maiz", "ndvi_max_maiz", "Corn"), ("soja", "ndvi_max_soja", "Soybean"))
               if col in fen.columns]
    if not paneles:
        aviso(f"{nombre}: se saltea (faltan ndvi_max_maiz y ndvi_max_soja)")
        return
    fig, axs = plt.subplots(1, len(paneles), figsize=(6 * len(paneles), 5), squeeze=False)
    n_total = 0
    for ax, (cult, col, titulo) in zip(axs[0], paneles):
        m = prod.loc[prod["cultivo"] == cult, ["fips", "anio", "rend_bu_ac"]].merge(
            fen[["fips", "anio", col]], on=["fips", "anio"]).dropna()
        m["estado"] = estado(m["fips"])
        n_total += len(m)
        dispersion_por_estado(ax, m, col, "rend_bu_ac", s=6, alpha=0.4)
        ax.set_xlabel(f"Peak NDVI of {titulo.lower()} pixels (MODIS)")
        ax.set_ylabel(f"{titulo} yield (bu/ac)")
        ax.set_title(f"{titulo}: peak NDVI vs yield (n = {len(m)})")
        ax.grid(alpha=0.3)
        if len(m):
            ax.legend(fontsize=7, markerscale=2)
    if n_total == 0:
        plt.close(fig)
        aviso(f"{nombre}: se saltea (no hay filas en común entre NDVI y rendimiento)")
        return
    fig.subplots_adjust(bottom=0.17, wspace=0.25)
    pie(fig, [SRC_MODIS, SRC_NASS], "One point per county-year.")
    guardar(fig, salida, nombre)


def fig_smap_siembra(agua, fenest, salida: Path) -> None:
    nombre = "fig3_smap_may_vs_planting.png"
    if faltan(agua, ["fips", "mes", "sm_rootzone_m3m3"], nombre) or \
            faltan(fenest, ["fips_estado", "anio", "cultivo", "doy_50_sembrado"], nombre):
        return
    a = agua[agua["mes"].astype(str).str.endswith("-05")].copy()
    a["anio"] = a["mes"].astype(str).str[:4].astype(int)
    a["fips_estado"] = a["fips"].astype(str).str.zfill(5).str[:2]
    # media simple de los condados del estado (sin ponderar por área): se dice en el pie
    s = a.groupby(["fips_estado", "anio"], as_index=False)["sm_rootzone_m3m3"].mean()
    f = fenest[fenest["cultivo"] == "maiz"].copy()
    f["fips_estado"] = f["fips_estado"].astype(str).str.zfill(2)
    m = s.merge(f[["fips_estado", "anio", "doy_50_sembrado"]], on=["fips_estado", "anio"]).dropna()
    if m.empty:
        aviso(f"{nombre}: se saltea (no hay años con SMAP de mayo y fecha de siembra)")
        return
    m["estado"] = m["fips_estado"].map(FIPS_ESTADO).fillna(m["fips_estado"])
    fig, ax = plt.subplots(figsize=(8, 5.5))
    dispersion_por_estado(ax, m, "sm_rootzone_m3m3", "doy_50_sembrado", s=30, alpha=0.85)
    for _, r in m.iterrows():
        ax.annotate(str(int(r["anio"]))[2:], (r["sm_rootzone_m3m3"], r["doy_50_sembrado"]),
                    fontsize=6, xytext=(3, 2), textcoords="offset points", color="#444444")
    ax.set_xlabel("May root-zone soil moisture (m³/m³), SMAP L4, mean of the state's counties")
    ax.set_ylabel("Day of year when 50% of corn was planted")
    ax.set_title("Wet springs and corn planting date, by state and year")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.subplots_adjust(bottom=0.16)
    pie(fig, [SRC_SMAP, SRC_PROG], f"Labels = year (two digits). Years {m['anio'].min()}–{m['anio'].max()}; "
        "SMAP starts 2015-03. Unweighted mean over counties.")
    guardar(fig, salida, nombre)


def fig_rotacion(rot, salida: Path) -> None:
    nombre = "fig4_corn_after_soy_vs_corn.png"
    if faltan(rot, ["fips", "anio", "pct_maiz_tras_soja", "pct_maiz_tras_maiz"], nombre):
        return
    r = rot[["fips", "anio", "pct_maiz_tras_soja", "pct_maiz_tras_maiz"]].dropna()
    if r.empty:
        aviso(f"{nombre}: se saltea (no hay transiciones)")
        return
    anio = int(r["anio"].max())
    r = r[r["anio"] == anio].copy()
    r["estado"] = estado(r["fips"])
    fig, ax = plt.subplots(figsize=(7, 6))
    dispersion_por_estado(ax, r, "pct_maiz_tras_soja", "pct_maiz_tras_maiz", s=14, alpha=0.7)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel(f"% of {anio} corn pixels that were soybean in {anio - 1}")
    ax.set_ylabel(f"% of {anio} corn pixels that were corn in {anio - 1}")
    ax.set_title(f"Corn after soybean vs corn after corn, by county ({anio})")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.subplots_adjust(bottom=0.15)
    pie(fig, [SRC_CDL], f"Pixel-by-pixel CDL transitions {anio - 1}→{anio}; one point per county (n = {len(r)}).")
    guardar(fig, salida, nombre)


def fig_lluvia_imerg_power(clima_m, salida: Path) -> None:
    """Lluvia mensual IMERG vs POWER por condado-mes, un panel por estado, recta 1:1 y razón media.

    La razón es la de los totales (suma de IMERG / suma de POWER) sobre los condado-mes del panel; no hay ajuste.
    """
    nombre = "fig6_lluvia.png"
    if faltan(clima_m, ["fips", "mes", "prec_imerg_mm", "prec_power_mm"], nombre):
        return
    m = clima_m[["fips", "mes", "prec_imerg_mm", "prec_power_mm"]].dropna().copy()
    if m.empty:
        aviso(f"{nombre}: se saltea (no hay condado-mes con las dos lluvias)")
        return
    m["estado"] = estado(m["fips"])
    ests = sorted(m["estado"].unique())
    tope = float(max(m["prec_imerg_mm"].max(), m["prec_power_mm"].max())) * 1.03
    fig, axs = plt.subplots(1, len(ests), figsize=(4.6 * len(ests), 5), squeeze=False, sharex=True, sharey=True)
    for ax, est in zip(axs[0], ests):
        g = m[m["estado"] == est]
        razon = g["prec_imerg_mm"].sum() / g["prec_power_mm"].sum()
        r = g["prec_imerg_mm"].corr(g["prec_power_mm"])
        ax.scatter(g["prec_power_mm"], g["prec_imerg_mm"], s=3, alpha=0.12, color=COLORES.get(est, "#777777"),
                   edgecolors="none", rasterized=True)
        ax.plot([0, tope], [0, tope], color="#222222", lw=1, label="1:1")
        ax.set_xlim(0, tope)
        ax.set_ylim(0, tope)
        ax.set_aspect("equal")
        ax.set_title(f"{est}: IMERG/POWER = {razon:.2f}, r = {r:.2f}", fontsize=10)
        ax.text(0.03, 0.97, f"n = {len(g):,} county-months\n{g['mes'].min()} to {g['mes'].max()}",
                transform=ax.transAxes, fontsize=7, va="top", color="#444444")
        ax.set_xlabel("NASA POWER monthly precipitation (mm)")
        ax.grid(alpha=0.3)
        ax.legend(loc="lower right", fontsize=7)
    axs[0][0].set_ylabel("GPM IMERG monthly precipitation (mm)")
    fig.suptitle("Two NASA rainfall products, county by month (no ground gauges)", fontsize=11)
    fig.subplots_adjust(bottom=0.2, top=0.86, wspace=0.12)
    pie(fig, [SRC_IMERG, SRC_POWER], "One point per county-month (clima_mensual.csv). Ratio = total IMERG / "
        "total POWER over all points of the panel; r = Pearson correlation. This is not a validation against "
        "gauges (PRISM).")
    guardar(fig, salida, nombre)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zips", type=Path, default=ZIPS, help="carpeta para los zips bajados")
    ap.add_argument("--salida", type=Path, default=SALIDA, help="carpeta de los PNG")
    ap.add_argument("--sin-bajar", action="store_true", help="no llamar a gh; usar los zips que ya están")
    ap.add_argument("--https", action="store_true",
                    help="bajar por la URL pública del release con urllib (sin gh ni token)")
    ap.add_argument("--etiquetas", nargs="+", default=ETIQUETAS)
    ap.add_argument("--nota", default="", help="línea extra para el pie de todas las figuras")
    ap.add_argument("--sufijo", default="", help="sufijo para los nombres de los PNG (p. ej. oh_ne_mn)")
    ap.add_argument("--entrega", type=Path,
                    help="zip de la entrega unida (fieldshift_datos_v1.x.zip); no baja nada")
    a = ap.parse_args()
    global NOTA, SUFIJO
    NOTA, SUFIJO = a.nota, a.sufijo

    if a.entrega:
        global ORIGEN
        ORIGEN = f"data release {a.entrega.stem}"
        d = leer_entrega(a.entrega)
        prod, clima, fen, agua, fenest, rot, clima_m = (d[k] for k in ("prod", "clima", "fen", "agua", "fenest",
                                                                       "rot", "clima_m"))
    else:
        if not a.sin_bajar:
            bajar(a.etiquetas, a.zips, https=a.https)
        zips_dirs = [a.zips / et for et in a.etiquetas if (a.zips / et).is_dir()]
        if not zips_dirs:
            aviso(f"no hay carpetas de {a.etiquetas} bajo {a.zips}")
        fuente = zips_dirs or a.zips
        prod = leer(fuente, "produccion_anual.csv")
        clima = leer(fuente, "clima_anual.csv")
        fen = leer(fuente, "fenologia_anual.csv")
        agua = leer(fuente, "agua_mensual.csv")
        fenest = leer(fuente, "fenologia_estado.csv")
        rot = leer(fuente, "rotacion_anual.csv")
        clima_m = leer(fuente, "clima_mensual.csv")

    fig_lluvia_julio(prod, clima, a.salida)
    fig_ndvi_rend(prod, fen, a.salida)
    fig_smap_siembra(agua, fenest, a.salida)
    fig_rotacion(rot, a.salida)
    fig_rend_por_anio(prod, a.salida)
    fig_lluvia_imerg_power(clima_m, a.salida)


if __name__ == "__main__":
    main()
