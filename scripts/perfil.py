#!/usr/bin/env python3
"""perfil.py — perfiles de tienda (marca) guardados en el equipo de cada persona.

Cada tienda tiene su propio perfil, así una misma persona puede manejar varias.

  python3 perfil.py listar
  python3 perfil.py ruta "Mi Tienda"      -> imprime la ruta del JSON del perfil (créalo o edítalo ahí)
  python3 perfil.py ver "Mi Tienda"
  python3 perfil.py logo "Mi Tienda" ruta/al/logo.png   -> guarda una copia del logo junto al perfil

Los perfiles viven en ~/.config/video-producto-ia-commerce/tiendas/<tienda>/perfil.json
"""
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

BASE = Path.home() / ".config" / "video-producto-ia-commerce" / "tiendas"


def slug(nombre):
    s = unicodedata.normalize("NFD", nombre.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "tienda"


def carpeta(nombre):
    return BASE / slug(nombre)


def main(argv):
    if len(argv) < 2 or argv[1] not in ("listar", "ruta", "ver", "logo"):
        sys.exit(__doc__)
    cmd = argv[1]
    if cmd == "listar":
        if not BASE.exists() or not any(BASE.iterdir()):
            print("(todavía no hay tiendas guardadas)")
            return
        for d in sorted(BASE.iterdir()):
            p = d / "perfil.json"
            if p.exists():
                print("%s  ->  %s" % (json.load(open(p)).get("tienda", d.name), p))
        return
    if len(argv) < 3:
        sys.exit("falta el nombre de la tienda")
    d = carpeta(argv[2])
    p = d / "perfil.json"
    if cmd == "ruta":
        d.mkdir(parents=True, exist_ok=True)
        print(p)
    elif cmd == "ver":
        print(open(p).read() if p.exists() else "(esa tienda no tiene perfil todavía)")
    elif cmd == "logo":
        if len(argv) < 4:
            sys.exit("falta la ruta del logo")
        d.mkdir(parents=True, exist_ok=True)
        origen = Path(argv[3]).expanduser()
        destino = d / ("logo" + origen.suffix.lower())
        shutil.copy2(str(origen), str(destino))
        print(destino)


if __name__ == "__main__":
    main(sys.argv)
