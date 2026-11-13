#!/usr/bin/env python3
"""instalar.py — copia este skill a la carpeta de skills de Claude Code y revisa el entorno.

  python3 scripts/instalar.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

ORIGEN = Path(__file__).resolve().parent.parent
DESTINO = Path.home() / ".claude" / "skills" / ORIGEN.name


def main():
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    if DESTINO.resolve() != ORIGEN:
        if DESTINO.exists():
            print("Ya existe %s: la actualizo" % DESTINO)
            shutil.rmtree(str(DESTINO))
        shutil.copytree(str(ORIGEN), str(DESTINO), ignore=shutil.ignore_patterns(".git", "__pycache__", "assets"))
    print("Skill instalado en %s" % DESTINO)
    subprocess.run([sys.executable, str(DESTINO / "scripts" / "doctor.py")])
    print("Listo. Abre Claude Code y di: haz un video de este producto.")


if __name__ == "__main__":
    main()
