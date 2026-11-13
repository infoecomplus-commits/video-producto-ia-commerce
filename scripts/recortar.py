#!/usr/bin/env python3
"""recortar.py — recorta a la persona de un clip (fondo transparente) para poner texto DETRÁS de ella.

  python3 recortar.py <proyecto> <clip.mp4> [--desde 2.0 --hasta 9.0]

Usa `hyperframes remove-background` (modelo de IA local; la primera vez descarga el modelo y puede tardar unos minutos).
Deja <proyecto>/media/<clip>_recorte.webm (VP9 con transparencia). Con --desde/--hasta solo procesa ese tramo
(más rápido) y lo anota en <clip>_recorte.json para que armar.py lo alinee solo.

Cuándo usarlo: planos de una persona hablando a cámara, con fondo limpio. Falla más con pelo suelto, manos rápidas
y productos que la persona sostiene (el modelo puede tratarlos como fondo): revisa siempre el resultado.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proyecto")
    ap.add_argument("clip")
    ap.add_argument("--desde", type=float)
    ap.add_argument("--hasta", type=float)
    a = ap.parse_args()

    media = Path(a.proyecto).expanduser() / "media"
    clip = media / Path(a.clip).name
    if not clip.exists():
        sys.exit("no existe %s (¿corriste preparar.py?)" % clip)
    entrada, offset = clip, 0.0
    if a.desde is not None and a.hasta is not None:
        tmp = Path(tempfile.mkdtemp()) / "tramo.mp4"
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % a.desde, "-t", "%.3f" % (a.hasta - a.desde), "-i", str(clip),
                            "-c:v", "libx264", "-crf", "14", "-an", str(tmp)], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("no pude cortar el tramo: " + r.stderr[-300:])
        entrada, offset = tmp, a.desde
    salida = media / (clip.stem + "_recorte.webm")
    r = subprocess.run(["npx", "hyperframes", "remove-background", str(entrada), "-o", str(salida)],
                       shell=sys.platform.startswith("win"))
    if r.returncode != 0 or not salida.exists():
        sys.exit("el recorte falló")
    json.dump({"desde": offset}, open(media / (clip.stem + "_recorte.json"), "w"))
    print("recorte listo: %s (alineado desde el segundo %.2f del clip)" % (salida, offset))


if __name__ == "__main__":
    main()
