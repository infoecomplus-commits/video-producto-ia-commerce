#!/usr/bin/env python3
"""sfx.py — genera efectos de sonido propios con ffmpeg (sin archivos de terceros).

  python3 sfx.py <carpeta_destino>

Crea: pop, whoosh, click, ding, riser, impacto, brillo (.wav). Si ya existen, no los toca.
Son sonidos sintéticos simples: sirven para marcar animaciones, no para sustituir una banda sonora.
"""
import subprocess
import sys
from pathlib import Path

# nombre -> (argumentos de entrada lavfi, cadena de filtros de audio)
EFECTOS = {
    "pop": (["-f", "lavfi", "-i", "sine=frequency=620:duration=0.14"],
            "afade=t=in:d=0.005,afade=t=out:st=0.03:d=0.11,volume=0.9"),
    "click": (["-f", "lavfi", "-i", "anoisesrc=color=white:duration=0.05:amplitude=0.8"],
              "highpass=f=1800,afade=t=out:st=0.005:d=0.045"),
    "whoosh": (["-f", "lavfi", "-i", "anoisesrc=color=pink:duration=0.6:amplitude=0.9"],
               "bandpass=f=1400:width_type=h:w=1800,afade=t=in:d=0.25,afade=t=out:st=0.28:d=0.32,volume=1.4"),
    "ding": (["-f", "lavfi", "-i", "aevalsrc=0.5*sin(2*PI*1318*t)+0.3*sin(2*PI*1975*t):d=0.9:s=44100"],
             "afade=t=in:d=0.004,afade=t=out:st=0.05:d=0.85"),
    "riser": (["-f", "lavfi", "-i", "aevalsrc=0.5*sin(2*PI*(220+520*t)*t)*t/1.2:d=1.2:s=44100"],
              "afade=t=out:st=1.1:d=0.1"),
    "impacto": (["-f", "lavfi", "-i", "aevalsrc=0.9*sin(2*PI*58*t)*exp(-5*t)+0.25*random(0)*exp(-30*t):d=0.7:s=44100"],
                "afade=t=out:st=0.5:d=0.2"),
    "brillo": (["-f", "lavfi", "-i", "aevalsrc=0.35*sin(2*PI*2637*t)+0.3*sin(2*PI*3322*t):d=0.5:s=44100"],
               "afade=t=in:d=0.003,afade=t=out:st=0.04:d=0.46"),
}


def generar(destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    hechos = []
    for nombre, (entrada, filtro) in EFECTOS.items():
        salida = destino / (nombre + ".wav")
        if salida.exists() and salida.stat().st_size > 500:
            continue
        r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + entrada + ["-af", filtro, "-ar", "44100", "-ac", "1", str(salida)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("No se pudo generar %s: %s" % (nombre, r.stderr.strip()[:200]))
        else:
            hechos.append(nombre)
    return hechos


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: python3 sfx.py <carpeta_destino>")
    h = generar(sys.argv[1])
    print("efectos generados: " + (", ".join(h) if h else "ya estaban todos"))
