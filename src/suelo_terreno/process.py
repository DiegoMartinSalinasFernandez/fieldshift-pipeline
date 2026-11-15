"""Procesa suelo_terreno: SSURGO (Soil Data Access) y NASADEM → suelo_terreno_estatico.csv.

Suelo (data/raw/suelo_terreno/sda/):
- Horizontes → componente: media ponderada por espesor en 0–30 cm (arena, limo, arcilla, MO,
  pH); factor K del horizonte superficial; SOC 0–30 y 0–100 cm = Σ espesor · MO · 0,58 ·
  densidad aparente · (1 − fragmentos) (g C/m²); profundidad de raíces = mínimo entre la
  primera restricción que limita raíces, el fondo del perfil y 150 cm.
- Componente → unidad cartográfica (MUKEY): media ponderada por comppct_r.
- MUKEY → condado: media ponderada por muacres de la unidad en el área de relevamiento del
  condado (areasymbol IA169 = fips 19169; las áreas que no siguen esa regla están en
  AREAS_ESPECIALES). Clases (drenaje, grupo hidrológico): la de mayor
  superficie.
Terreno (data/raw/suelo_terreno/nasadem/): ver terreno.py.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.common.config import estados_config  # noqa: E402

RAW = REPO / "data" / "raw" / "suelo_terreno" / "sda"
INTERIM = REPO / "data" / "interim" / "suelo_terreno"
SALIDA = REPO / "data" / "processed" / "suelo_terreno" / "suelo_terreno_estatico.csv"

RESTRICCIONES_RAICES = {"Lithic bedrock", "Paralithic bedrock", "Densic material", "Densic bedrock",
                        "Fragipan", "Duripan", "Petrocalcic", "Petrogypsic", "Placic",
                        "Ortstein", "Manufactured layer", "Cemented horizon"}
PROF_RAICES_MAX = 150.0
TEXTURA_TOLERANCIA = 3.0
# Áreas de relevamiento que no son "estado + código de condado" (consultado en SDA, tabla legend,
# 2026-11-15, para IA, IL, IN, OH, NE, MN y KS: solo hay en MN). St. Louis (27137) está partido en
# cinco áreas y Koochiching (27071) tiene un área propia. MN627 (Voyageurs National Park) cae en los
# dos condados y no es agrícola: se deja afuera (None).
AREAS_ESPECIALES = {
    "MN613": "27137", "MN615": "27137", "MN617": "27137", "MN619": "27137", "MN621": "27137",
    "MN625": "27071", "MN627": None,
}
NCCPI = {
    "NCCPI - National Commodity Crop Productivity Index (Ver 3.0)": "nccpi_general",
    "NCCPI - NCCPI Corn Submodel (I)": "nccpi_maiz",
    "NCCPI - NCCPI Soybeans Submodel (I)": "nccpi_soja",
}


def leer(tabla: str) -> pd.DataFrame:
    partes = [pd.read_csv(RAW / f"{tabla}_{alfa}.csv", dtype={"areasymbol": str})
              for alfa in estados_config()]
    return pd.concat(partes, ignore_index=True).drop_duplicates()


def media_pond(df: pd.DataFrame, grupo: str, peso: str, cols: list[str]) -> pd.DataFrame:
    """Media ponderada de cada columna ignorando faltantes (el peso solo cuenta donde hay dato)."""
    out = {}
    for c in cols:
        v = df[[grupo, peso, c]].dropna()
        v = v[v[peso] > 0]
        num = (v[c] * v[peso]).groupby(v[grupo]).sum()
        den = v[peso].groupby(v[grupo]).sum()
        out[c] = num / den
    return pd.DataFrame(out)


def horizontes_a_componente(h: pd.DataFrame, r: pd.DataFrame) -> pd.DataFrame:
    h = h.dropna(subset=["hzdept_r", "hzdepb_r"]).copy()
    h["kwfact"] = pd.to_numeric(h["kwfact"], errors="coerce")
    # 0–30 cm: espesor de cada horizonte dentro de la capa
    h["esp30"] = (h["hzdepb_r"].clip(upper=30) - h["hzdept_r"].clip(upper=30)).clip(lower=0)
    h["esp100"] = (h["hzdepb_r"].clip(upper=100) - h["hzdept_r"].clip(upper=100)).clip(lower=0)
    sup = h[h["esp30"] > 0]
    # textura: solo horizontes con las tres fracciones, para que sumen 100
    tex = sup.dropna(subset=["sandtotal_r", "silttotal_r", "claytotal_r"])
    suma = tex["sandtotal_r"] + tex["silttotal_r"] + tex["claytotal_r"]
    tex = tex[(suma - 100).abs() <= TEXTURA_TOLERANCIA]  # fuera: horizontes orgánicos (muck)
    comp = media_pond(tex, "cokey", "esp30", ["sandtotal_r", "silttotal_r", "claytotal_r"])
    comp = comp.join(media_pond(sup, "cokey", "esp30", ["om_r", "ph1to1h2o_r"]), how="outer")
    # factor K del horizonte más superficial
    prim = h.sort_values(["cokey", "hzdept_r"]).groupby("cokey").head(1).set_index("cokey")
    comp = comp.join(prim["kwfact"], how="outer")
    # SOC (g C/m²): MO % · 0,58 · densidad (g/cm³) · espesor (cm) · (1 − frag) · 10⁴ cm²/m²
    frag = 1 - h["fragvol_r"].fillna(0).clip(0, 100) / 100
    base = h["om_r"] / 100 * 0.58 * h["dbthirdbar_r"] * frag * 1e4
    for col, esp, tope in (("soc0_30_gm2", "esp30", 30), ("soc0_100_gm2", "esp100", 100)):
        h[col] = base * h[esp]
        ok = h[h[esp] > 0]
        suma = ok.groupby("cokey")[col].sum(min_count=1)
        incompleto = ok[col].isna().groupby(ok["cokey"]).any()
        cubre = ok.groupby("cokey")["hzdepb_r"].max() >= tope
        comp[col] = suma.where(~incompleto & cubre)
    # profundidad de raíces
    fondo = h.groupby("cokey")["hzdepb_r"].max()
    rr = r[r["reskind"].isin(RESTRICCIONES_RAICES)].groupby("cokey")["resdept_r"].min()
    prof = pd.concat([fondo, rr], axis=1).min(axis=1).clip(upper=PROF_RAICES_MAX)
    comp["prof_raices_cm"] = prof
    return comp


def main() -> None:
    t0 = time.time()
    mu = leer("mapunit")
    co = leer("component")
    h = leer("chorizon")
    r = leer("restricciones")
    nc = leer("nccpi")
    print(f"lectura {time.time() - t0:.1f}s", flush=True)

    comp = horizontes_a_componente(h, r)
    nc = nc[nc["rulename"].isin(NCCPI)]
    nc = nc.assign(col=nc["rulename"].map(NCCPI)).pivot_table(
        index="cokey", columns="col", values="interphr", aggfunc="mean")
    comp = comp.join(nc, how="outer")
    vars_comp = list(comp.columns)
    co = co.merge(comp, left_on="cokey", right_index=True, how="left")
    mukey = media_pond(co, "mukey", "comppct_r", vars_comp)
    print(f"componentes {time.time() - t0:.1f}s", flush=True)

    mu = mu.merge(mukey, left_on="mukey", right_index=True, how="left")
    mu["aws0100_mm"] = mu["aws0100wta"] * 10  # muaggatt en cm
    mu["aws0150_mm"] = mu["aws0150wta"] * 10
    mu["fips"] = mu["areasymbol"].map(fips_de_area)
    sin_condado = sorted(set(mu.loc[mu["fips"].isna(), "areasymbol"]) - set(AREAS_ESPECIALES))
    if sin_condado:
        print(f"AVISO: áreas de relevamiento sin condado (quedan afuera): {sin_condado}", flush=True)
    mu = mu.dropna(subset=["fips"])
    num = vars_comp + ["aws0100_mm", "aws0150_mm", "wtdepannmin"]
    cond = media_pond(mu, "fips", "muacres", num)
    for col, src in (("clase_drenaje", "drclassdcd"), ("grupo_hidrologico", "hydgrpdcd")):
        v = mu.dropna(subset=[src, "muacres"])
        cond[col] = (v.groupby(["fips", src])["muacres"].sum().reset_index()
                     .sort_values(["fips", "muacres", src], ascending=[True, False, True])
                     .groupby("fips").head(1).set_index("fips")[src])

    out = pd.DataFrame(index=cond.index)
    out["aws0_100_mm"] = cond["aws0100_mm"]
    out["aws0_150_mm"] = cond["aws0150_mm"]
    out["soc0_30_gm2"] = cond["soc0_30_gm2"]
    out["soc0_100_gm2"] = cond["soc0_100_gm2"]
    out["nccpi_general"] = cond["nccpi_general"]
    out["nccpi_maiz"] = cond["nccpi_maiz"]
    out["nccpi_soja"] = cond["nccpi_soja"]
    out["prof_raices_cm"] = cond["prof_raices_cm"]
    out["clase_drenaje"] = cond["clase_drenaje"]
    out["grupo_hidrologico"] = cond["grupo_hidrologico"]
    out["napa_min_cm"] = cond["wtdepannmin"]
    out["arcilla_pct"] = cond["claytotal_r"]
    out["arena_pct"] = cond["sandtotal_r"]
    out["limo_pct"] = cond["silttotal_r"]
    out["materia_organica_pct"] = cond["om_r"]
    out["ph_agua"] = cond["ph1to1h2o_r"]
    out["clase_textural_usda"] = [clase_textural(a, l, c) for a, l, c in
                                  zip(out["arena_pct"], out["limo_pct"], out["arcilla_pct"])]
    out["factor_k_rusle"] = cond["kwfact"]

    condados = pd.read_csv(REPO / "data" / "reference" / "condados.csv", dtype={"fips": str})
    out = condados[["fips"]].merge(out, left_on="fips", right_index=True, how="left")

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import terreno  # noqa: E402
    ter = terreno.terreno_por_condado()
    out = out.merge(ter, on="fips", how="left")
    print(f"terreno {time.time() - t0:.1f}s", flush=True)

    out = out.sort_values("fips")
    decimales = {"aws0_100_mm": 1, "aws0_150_mm": 1, "soc0_30_gm2": 0, "soc0_100_gm2": 0,
                 "nccpi_general": 4, "nccpi_maiz": 4, "nccpi_soja": 4, "prof_raices_cm": 1,
                 "napa_min_cm": 1, "arcilla_pct": 2, "arena_pct": 2, "limo_pct": 2,
                 "materia_organica_pct": 3, "ph_agua": 2, "factor_k_rusle": 4,
                 "elevacion_media_m": 1, "elevacion_desvio_m": 2, "pendiente_media_pct": 3,
                 "pendiente_gt2_pct": 2, "twi_medio": 3, "twi_decil_sup_pct": 2}
    for c, d in decimales.items():
        if c in out:
            out[c] = out[c].map(lambda x, d=d: "" if pd.isna(x) else f"{x:.{d}f}")
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(SALIDA, index=False, encoding="utf-8", lineterminator="\n")
    import data_card  # noqa: E402
    data_card.main()
    print(f"listo {len(out)} condados, {time.time() - t0:.1f}s", flush=True)


def fips_de_area(area: str):
    estados = {alfa: e["fips"] for alfa, e in estados_config().items()}
    alfa, cod = area[:2], area[2:]
    if area in AREAS_ESPECIALES:
        f = AREAS_ESPECIALES[area]
        return f if f is not None and alfa in estados else np.nan
    if alfa in estados and cod.isdigit() and len(cod) == 3:
        return estados[alfa] + cod
    return np.nan


def clase_textural(arena: float, limo: float, arcilla: float) -> str:
    """Triángulo textural USDA (reglas del Soil Survey Manual / calculadora del NRCS)."""
    if pd.isna(arena) or pd.isna(limo) or pd.isna(arcilla):
        return ""
    s, si, c = arena, limo, arcilla
    if si + 1.5 * c < 15:
        return "arenoso"
    if si + 1.5 * c >= 15 and si + 2 * c < 30:
        return "areno_franco"
    if (7 <= c < 20 and s > 52 and si + 2 * c >= 30) or (c < 7 and si < 50 and si + 2 * c >= 30):
        return "franco_arenoso"
    if 7 <= c < 27 and 28 <= si < 50 and s <= 52:
        return "franco"
    if (si >= 50 and 12 <= c < 27) or (50 <= si < 80 and c < 12):
        return "franco_limoso"
    if si >= 80 and c < 12:
        return "limoso"
    if 20 <= c < 35 and si < 28 and s > 45:
        return "franco_arcillo_arenoso"
    if 27 <= c < 40 and 20 < s <= 45:
        return "franco_arcilloso"
    if 27 <= c < 40 and s <= 20:
        return "franco_arcillo_limoso"
    if c >= 35 and s > 45:
        return "arcillo_arenoso"
    if c >= 40 and si >= 40:
        return "arcillo_limoso"
    if c >= 40 and s <= 45 and si < 40:
        return "arcilla"
    return ""


if __name__ == "__main__":
    main()
