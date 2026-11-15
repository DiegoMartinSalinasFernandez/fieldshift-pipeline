"""Baja los reportes de texto de Crop Progress del archivo ESMIS (tarea T077; copia de nass_mi_nd_bajar_cp.py).

Recorre https://esmis.nal.usda.gov/publication/crop-progress?page=N hasta que una página no trae enlaces .txt,
y guarda cada .txt en la carpeta que se le pasa (fuera del repo). No vuelve a bajar lo que ya está.
Los lee después `nass_ky_crop_progress.py`.

Uso:
  .venv/bin/python -X utf8 docs/research/nass_ky_bajar_cp.py /tmp/t077/txt
"""
import re
import sys
import time
from pathlib import Path

import requests

BASE = "https://esmis.nal.usda.gov"
UA = {"User-Agent": "Mozilla/5.0 (fieldshift-research)"}
TXT = re.compile(r'href="(/sites/default/release-files/[^"]+\.txt)"')


def main() -> None:
    carpeta = Path(sys.argv[1])
    carpeta.mkdir(parents=True, exist_ok=True)
    pagina = 0
    while True:
        html = requests.get(f"{BASE}/publication/crop-progress", params={"page": pagina}, headers=UA,
                            timeout=120).text
        enlaces = TXT.findall(html)
        if not enlaces:
            break
        for e in enlaces:
            # el nombre puede repetirse entre años (prog4625.txt): se le antepone la carpeta del release
            destino = carpeta / ("_".join(e.split("/")[4:]))
            if destino.exists():
                continue
            r = requests.get(BASE + e, headers=UA, timeout=120)
            if r.ok:
                destino.write_bytes(r.content)
            else:
                print(f"{r.status_code} {e}", file=sys.stderr)
        print(f"página {pagina}: {len(enlaces)}", file=sys.stderr)
        pagina += 1
        time.sleep(0.3)


if __name__ == "__main__":
    main()
