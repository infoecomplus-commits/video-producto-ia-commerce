#!/usr/bin/env python3
"""doctor.py — revisa que el equipo tenga lo necesario para montar videos de producto.

  python3 doctor.py          solo diagnóstico
  python3 doctor.py --fix    instala HyperFrames (npm) si falta

Funciona en macOS, Linux y Windows. Solo usa la biblioteca estándar de Python.
"""
import json
import platform
import re
import shutil
import subprocess
import sys

FIX = "--fix" in sys.argv
OK = True


def ok(msg):
    print("  [ok]  " + msg)


def falta(msg, como):
    global OK
    OK = False
    print("  [!!]  " + msg)
    print("        -> " + como)


def salida(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=(platform.system() == "Windows"))
        return (r.stdout or "") + (r.stderr or "")
    except Exception:
        return ""


def main():
    sistema = platform.system()
    instala = {"Darwin": "brew install", "Windows": "winget install", "Linux": "sudo apt install"}.get(sistema, "instala")
    print("-- video-producto-ia-commerce · doctor --")

    v = sys.version_info
    if v >= (3, 9):
        ok("Python %d.%d.%d" % (v[0], v[1], v[2]))
    else:
        falta("Python %d.%d es muy viejo (se necesita 3.9 o más)" % (v[0], v[1]), "https://www.python.org/downloads/")

    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        m = re.search(r"ffmpeg version (\S+)", salida(["ffmpeg", "-version"]))
        ok("ffmpeg " + (m.group(1) if m else ""))
    else:
        falta("ffmpeg no está instalado", instala + " ffmpeg")

    node = shutil.which("node")
    if node:
        mayor = 0
        m = re.match(r"v(\d+)", salida(["node", "-v"]).strip())
        if m:
            mayor = int(m.group(1))
        if mayor >= 22:
            ok("Node v%d" % mayor)
        else:
            falta("Node v%d es viejo (HyperFrames pide 22 o más)" % mayor,
                  {"Darwin": "brew install node@22", "Windows": "winget install OpenJS.NodeJS.LTS"}.get(sistema, "usa nvm: nvm install 22"))
    else:
        falta("Node no está instalado", {"Darwin": "brew install node@22", "Windows": "winget install OpenJS.NodeJS.LTS"}.get(sistema, "usa nvm: nvm install 22"))

    if node:
        tiene = "hyperframes" in salida(["npm", "ls", "-g", "hyperframes", "--depth=0"])
        if tiene:
            ok("HyperFrames")
        elif FIX:
            print("  ...   instalando HyperFrames")
            subprocess.run(["npm", "install", "-g", "hyperframes"], shell=(sistema == "Windows"))
            if "hyperframes" in salida(["npm", "ls", "-g", "hyperframes", "--depth=0"]):
                ok("HyperFrames instalado")
            else:
                falta("No se pudo instalar HyperFrames", "npm install -g hyperframes")
        else:
            falta("HyperFrames no está instalado", "npm install -g hyperframes   (o corre este script con --fix)")

    # el filtro loudnorm y los generadores de audio vienen con ffmpeg estándar
    if shutil.which("ffmpeg"):
        filtros = salida(["ffmpeg", "-hide_banner", "-filters"])
        for f in ("loudnorm", "anoisesrc", "aevalsrc"):
            if f in filtros:
                ok("filtro ffmpeg " + f)
            else:
                falta("a este ffmpeg le falta el filtro " + f, "reinstala ffmpeg con su build completa")

    print("--")
    print("Todo listo." if OK else "Falta algo. Pégale este resultado a Claude y dile: ayúdame a arreglarlo.")
    sys.exit(0 if OK else 1)


if __name__ == "__main__":
    main()
