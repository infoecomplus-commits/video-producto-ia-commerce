#!/usr/bin/env python3
"""entregar.py — último paso: velocidad opcional, volumen parejo y techo de picos garantizado.

  python3 entregar.py render.mp4 FINAL.mp4 [--velocidad V] [--lufs -14] [--pico -1.5]

1. Si pides velocidad distinta de 1, acelera imagen y voz (sin cambiar el tono).
2. Normaliza el volumen a --lufs (por defecto -14, lo habitual en TikTok, Reels y YouTube).
   Con --solo-bajar nunca lo sube (para videos sin voz ni música).
3. MIDE el pico real del resultado. Si queda por encima de -1.0 dBTP, baja la ganancia y repite
   (hasta 4 veces). Nunca entrega un archivo que no cumpla el techo.
Los videos sin pista de audio se copian tal cual (no hay nada que normalizar).
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

LIMITE_PICO = -1.0


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def tiene_audio(ruta):
    r = run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(ruta)])
    return "audio" in r.stdout


def medir(ruta, lufs, pico):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(ruta), "-af",
             "loudnorm=I=%s:TP=%s:LRA=11:print_format=json" % (lufs, pico), "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if not m:
        sys.exit("no pude medir el audio:\n" + r.stderr[-400:])
    return json.loads(m.group(0))


def acelerar(entrada, salida, v, audio):
    if audio:
        fc = "[0:v]setpts=PTS/%s[v];[0:a]atempo=%s[a]" % (v, v)
        maps = ["-map", "[v]", "-map", "[a]"]
    else:
        fc, maps = "[0:v]setpts=PTS/%s[v]" % v, ["-map", "[v]"]
    r = run(["ffmpeg", "-v", "error", "-y", "-i", str(entrada), "-filter_complex", fc] + maps +
            ["-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(salida)])
    if r.returncode != 0:
        sys.exit("falló la aceleración: " + r.stderr[-300:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--velocidad", type=float, default=1.0)
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--pico", type=float, default=-1.5, help="techo objetivo de pico real (dBTP)")
    ap.add_argument("--solo-bajar", action="store_true",
                    help="no subir el volumen (úsalo si el video no tiene voz ni música: solo hay efectos de sonido)")
    a = ap.parse_args()

    entrada, salida = Path(a.entrada), Path(a.salida)
    audio = tiene_audio(entrada)
    tmp = Path(tempfile.mkdtemp())
    fuente = entrada
    if abs(a.velocidad - 1.0) > 1e-3:
        fuente = tmp / "veloz.mp4"
        acelerar(entrada, fuente, a.velocidad, audio)
    if not audio:
        salida.write_bytes(fuente.read_bytes())
        print("sin audio: copiado tal cual -> %s" % salida)
        return

    objetivo = a.pico
    if a.solo_bajar:
        actual = float(medir(fuente, a.lufs, objetivo)["input_i"])
        if actual < a.lufs:
            print("solo-bajar: el audio ya está en %.1f LUFS (más bajo que %.1f); no lo subo" % (actual, a.lufs))
            a.lufs = actual
    for intento in range(1, 5):
        m = medir(fuente, a.lufs, objetivo)
        filtro = ("loudnorm=I=%s:TP=%s:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true"
                  % (a.lufs, objetivo, m["input_i"], m["input_tp"], m["input_lra"], m["input_thresh"], m["target_offset"]))
        r = run(["ffmpeg", "-v", "error", "-y", "-i", str(fuente), "-c:v", "copy", "-af", filtro, "-ar", "48000",
                 "-c:a", "aac", "-b:a", "192k", str(salida)])
        if r.returncode != 0:
            sys.exit("falló la normalización: " + r.stderr[-300:])
        f = medir(salida, a.lufs, objetivo)
        lufs_real, pico_real = float(f["input_i"]), float(f["input_tp"])
        print("intento %d: %.1f LUFS · pico real %.2f dBTP" % (intento, lufs_real, pico_real))
        if pico_real <= LIMITE_PICO:
            print("listo -> %s  (%.1f LUFS, pico %.2f dBTP, techo %.1f)" % (salida, lufs_real, pico_real, LIMITE_PICO))
            return
        objetivo -= (pico_real - LIMITE_PICO) + 0.5
    sys.exit("no logré bajar el pico de %.2f dBTP; avisa antes de publicar" % pico_real)


if __name__ == "__main__":
    main()
