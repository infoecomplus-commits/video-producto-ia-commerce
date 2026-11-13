#!/usr/bin/env python3
"""tira.py — tira de cuadros de un tramo de un clip, para ver qué pasa antes de cortar.

  python3 tira.py <proyecto> <clip.mp4> --desde 7.0 --hasta 12.0 [--fps 5]

Genera <proyecto>/media/tira_<clip>_<desde>.jpg con un cuadro cada 1/fps segundos (el primero es `desde`).
Úsala para:
  - encontrar el momento en que la persona ya está lista (no sentándose, no guardando el celular, no mirando a otro lado);
  - detectar pausas en las que se queda posando antes de hablar;
  - ver si el gesto de la toma coincide con lo que dice.
La posición de cada cuadro en la tira = desde + posición / fps.
"""
import argparse
import subprocess
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proyecto")
    ap.add_argument("clip")
    ap.add_argument("--desde", type=float, required=True)
    ap.add_argument("--hasta", type=float, required=True)
    ap.add_argument("--fps", type=float, default=5.0)
    ap.add_argument("--ancho", type=int, default=105, help="ancho de cada cuadro en píxeles")
    a = ap.parse_args()

    media = Path(a.proyecto).expanduser() / "media"
    clip = media / Path(a.clip).name
    if not clip.exists():
        sys.exit("no existe %s (¿corriste preparar.py?)" % clip)
    n = max(1, int((a.hasta - a.desde) * a.fps))
    salida = media / ("tira_%s_%g.jpg" % (clip.stem, a.desde))
    cols = min(n, 20)
    filas = (n + cols - 1) // cols
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % a.desde, "-t", "%.3f" % (a.hasta - a.desde), "-i", str(clip),
                        "-vf", "fps=%s,scale=%d:-1,tile=%dx%d" % (a.fps, a.ancho, cols, filas), "-frames:v", "1", "-q:v", "4", str(salida)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ffmpeg falló: " + r.stderr[-300:])
    print("tira: %s  (%d cuadros, 1 cada %.2fs desde %.2fs, %d por fila)" % (salida, n, 1.0 / a.fps, a.desde, cols))


if __name__ == "__main__":
    main()
