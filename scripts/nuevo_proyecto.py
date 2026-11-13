#!/usr/bin/env python3
"""nuevo_proyecto.py — crea la carpeta de un video de producto con un proyecto.json de partida.

  python3 nuevo_proyecto.py <carpeta> --tienda "Mi Tienda" [--formato 9:16] [--plataforma tiktok] [--nivel 2]

Si la tienda ya tiene perfil guardado (perfil.py), toma de ahí colores, fuentes y logo.
Después Claude rellena las escenas con lo que la persona contó del producto.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import perfil  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carpeta")
    ap.add_argument("--tienda", required=True)
    ap.add_argument("--formato", default="9:16")
    ap.add_argument("--plataforma", default="meta", choices=["meta", "tiktok", "reels", "stories", "feed"])
    ap.add_argument("--nivel", type=int, default=2, choices=[1, 2, 3])
    a = ap.parse_args()

    base = Path(a.carpeta).expanduser()
    for sub in ("media", "salida"):
        (base / sub).mkdir(parents=True, exist_ok=True)
    spec = json.load(open(AQUI.parent / "plantillas" / "proyecto.ejemplo.json"))
    spec["tienda"] = a.tienda
    spec["formato"] = a.formato
    spec["plataforma"] = a.plataforma
    spec["nivel"] = a.nivel

    p = perfil.carpeta(a.tienda) / "perfil.json"
    if p.exists():
        pf = json.load(open(p))
        spec["marca"] = pf.get("marca", spec["marca"])
        logo = next(iter(sorted(p.parent.glob("logo.*"))), None)
        if logo:
            shutil.copy2(str(logo), str(base / ("logo_original" + logo.suffix)))
            spec["logo"]["_origen"] = str(base / ("logo_original" + logo.suffix))
        print("perfil de '%s' aplicado" % a.tienda)
    else:
        print("'%s' no tiene perfil guardado todavía: se usa el estilo de ejemplo" % a.tienda)

    destino = base / "proyecto.json"
    if destino.exists():
        sys.exit("ya existe %s; no lo sobrescribo" % destino)
    json.dump(spec, open(destino, "w"), ensure_ascii=False, indent=2)
    print("proyecto creado en %s" % base)


if __name__ == "__main__":
    main()
