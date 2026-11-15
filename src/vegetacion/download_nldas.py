"""Descarga ET y PET mensuales de NLDAS-2 Noah (NASA GES DISC) recortados a la zona.

Sustituye a MOD16A2 (no está en Planetary Computer y a 500 m no entra en el límite de 5 GB del
paquete). Usa Harmony (Earthdata, ~/.netrc) con recorte por bbox y variables Evap y PotEvap:
un NetCDF de ~80 KB por mes. Reanudable: saltea los meses que ya están en raw.

Uso: python src/vegetacion/download_nldas.py [anio_desde anio_hasta]
"""
from __future__ import annotations

import csv
import datetime as dt
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from src.vegetacion.download import grupos_bbox, log  # noqa: E402
from src.common.config import cargar_config  # noqa: E402
from src.common.manifest import asegurar_manifest  # noqa: E402

RAW = REPO / "data" / "raw" / "vegetacion" / "nldas_noah_m"
INTERIM = REPO / "data" / "interim" / "vegetacion"
COLECCION = "C1887990023-GES_DISC"  # NLDAS_NOAH0125_M 2.0
HARMONY = (f"https://harmony.earthdata.nasa.gov/{COLECCION}/ogc-api-coverages/1.0.0/collections/"
           "Evap,PotEvap/coverage/rangeset")
_lock = threading.Lock()


def nombre(anio: int, mes: int, sufijo: str = "zona") -> str:
    return f"NLDAS_NOAH0125_M.A{anio}{mes:02d}.020_Evap_PotEvap_{sufijo}.nc"


def consulta(anio: int, mes: int, bbox: list[float]) -> dict:
    fin = (dt.date(anio + (mes == 12), mes % 12 + 1, 1) - dt.timedelta(days=1)).isoformat()
    return {"subset": [f"lat({bbox[1]:.2f}:{bbox[3]:.2f})", f"lon({bbox[0]:.2f}:{bbox[2]:.2f})",
                       f'time("{anio}-{mes:02d}-01T00:00:00Z":"{fin}T23:59:59Z")'],
            "format": "application/x-netcdf4"}


def grupos_nldas() -> dict[str, list[float]]:
    """{sufijo: bbox}: un recorte por grupo de estados contiguos (grupos_bbox de vegetacion).

    Con un solo grupo (por ejemplo IA, IL e IN) el sufijo es "zona" y el bbox es el de antes de T023,
    así los archivos que ya están en raw tienen el mismo nombre y la misma consulta. Con varios grupos
    (OH; MN; KS y NE) cada archivo lleva los estados en el nombre: ..._KS-NE.nc, ..._MN.nc, ..._OH.nc.
    """
    g = grupos_bbox()
    if len(g) == 1:
        return {"zona": g[0][1]}
    return {"-".join(e): b for e, b in g}


def sufijo_de(p: Path) -> str:
    return p.stem.rsplit("_", 1)[1]


def bajar(anio: int, mes: int, bbox: list[float], sufijo: str = "zona") -> None:
    destino = RAW / str(anio) / nombre(anio, mes, sufijo)
    if destino.exists():
        return
    r = requests.get(HARMONY, params=consulta(anio, mes, bbox), timeout=600)
    r.raise_for_status()
    if "netcdf" not in (r.headers.get("content-type") or ""):
        raise RuntimeError(f"respuesta inesperada {r.headers.get('content-type')}: {r.text[:200]}")
    tmp = INTERIM / "_part" / (destino.name + ".part")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(r.content)
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp.replace(destino)


def registrar_manifest(grupos: dict[str, list[float]]) -> None:
    man = REPO / "manifest.csv"
    asegurar_manifest(man)
    with open(man, encoding="utf-8", newline="") as f:
        filas = list(csv.reader(f))
    presentes = {r[1] for r in filas[1:] if len(r) > 1}
    hoy = dt.date.today().isoformat()
    nuevas = []
    for p in sorted(RAW.rglob("*.nc")):
        rel = p.relative_to(REPO).as_posix()
        if rel in presentes:
            continue
        anio, mes = int(p.name[18:22]), int(p.name[22:24])
        if sufijo_de(p) not in grupos:  # de otra configuración de estados: no se sabe su consulta
            log(f"manifest: {rel} no corresponde a los grupos actuales, no se registra")
            continue
        q = consulta(anio, mes, grupos[sufijo_de(p)])
        nuevas.append(["vegetacion", rel, "NASA GES DISC (Harmony)", "NLDAS_NOAH0125_M", "2.0", hoy,
                       f"{HARMONY}?subset={'&subset='.join(q['subset'])}&format={q['format']}"])
    if nuevas:
        with open(man, "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(nuevas)


def main() -> None:
    cfg = cargar_config()
    a0 = int(sys.argv[1]) if len(sys.argv) > 1 else int(cfg["periodo"]["anio_inicio"])
    a1 = int(sys.argv[2]) if len(sys.argv) > 2 else int(cfg["periodo"]["anio_fin"])
    grupos = grupos_nldas()
    log("nldas grupos: " + "; ".join(f"{k} {[round(v, 2) for v in b]}" for k, b in grupos.items()))
    pend = [(a, m, k) for a in range(a0, a1 + 1) for m in range(1, 13) for k in grupos
            if not (RAW / str(a) / nombre(a, m, k)).exists()]
    log(f"nldas {a0}-{a1}: {len(pend)} archivos (mes x grupo) pendientes")
    with ThreadPoolExecutor(8) as ex:
        futs = {ex.submit(bajar, a, m, grupos[k], k): (a, m, k) for a, m, k in pend}
        for fu in as_completed(futs):
            try:
                fu.result()
            except Exception as e:  # se reintenta en la próxima corrida
                log(f"ERROR nldas {futs[fu]}: {type(e).__name__}: {str(e)[:200]}")
    registrar_manifest(grupos)
    log("nldas: listo")


if __name__ == "__main__":
    main()
