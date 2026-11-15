"""Mapa de los análogos: docs/research/fig/analogos_argentina.png.

Panel izquierdo: variables de clima fuera del rango de los condados (de 16), todo el país.
Panel derecho: región pampeana, clima + suelo (de 20), si existe suelo_sg.csv.
Uso: python src/analogos/figura.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
OUT = RAIZ / "data" / "processed" / "analogos"
FIG = RAIZ / "docs" / "research" / "fig" / "analogos_argentina.png"
COLORES = {"0: dentro del dominio": "#1a7f37", "1–2": "#7cc08a", "3–5": "#e3b341", "6 o más": "#c9c9c9"}


def puntos(ax, d, col, titulo, s):
    cat = pd.cut(d[col], [-1, 0, 2, 5, 99], labels=list(COLORES))
    # "dentro del dominio" también pide Mahalanobis ≤ p99: los de 0 fuera de rango que no cumplen van con 1–2
    dentro = d["dentro_dominio" if col == "n_fuera_rango" else "dentro_dominio_cs"].fillna(False).astype(bool)
    cat = cat.where(~((cat == "0: dentro del dominio") & ~dentro), "1–2")
    for k, c in COLORES.items():
        x = d[cat == k]
        ax.scatter(x.lon_centroide, x.lat_centroide, s=s, c=c, label=f"{k} ({len(x)})", edgecolors="none")
    ax.set_title(titulo, fontsize=9)
    ax.set_xlabel("longitud")
    ax.set_ylabel("latitud")
    for e in ("top", "right"):
        ax.spines[e].set_visible(False)


def main() -> int:
    d = pd.read_csv(OUT / "analogos_departamento.csv", dtype={"id_depto": str})
    d = d[d.lat_centroide > -56]
    n_cond = len(pd.read_csv(OUT / "analogos_condado_ref.csv"))
    hay_suelo = "n_fuera_rango_cs" in d.columns
    fig, axs = plt.subplots(1, 2 if hay_suelo else 1, figsize=(11 if hay_suelo else 6.2, 8.6), dpi=150,
                            squeeze=False)
    ax = axs[0, 0]
    puntos(ax, d, "n_fuera_rango", f"Clima: variables fuera del rango\nde los {n_cond} condados (de 16)", 14)
    ax.set_xlim(-74, -53)
    ax.set_ylim(-55.5, -21.5)
    ax.set_aspect(1.15)
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.04), fontsize=7.5, title="Fuera de rango", title_fontsize=7.5,
              frameon=False)
    if hay_suelo:
        p = d.dropna(subset=["n_fuera_rango_cs"])
        ax = axs[0, 1]
        puntos(ax, p, "n_fuera_rango_cs", "Región pampeana, clima + suelo SoilGrids\n(de 20 variables)", 30)
        ax.set_aspect(1.2)
        ax.legend(loc="lower right", fontsize=7.5, title="Fuera de rango", title_fontsize=7.5, frameon=False)
    meta = json.loads((OUT / "analogos_meta.json").read_text(encoding="utf-8"))
    fig.text(0.02, 0.012, f"Fuente: NASA POWER mensual {meta['periodo'][0]}–{meta['periodo'][1]} (AG) en centroides de "
             "Georef (datos.gob.ar); suelo ISRIC SoilGrids v2.0 (1 km). Temporada alineada: abr–sep (EE.UU.) = "
             "oct–mar (Argentina).", fontsize=6.5, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG)
    print(FIG.relative_to(RAIZ).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
