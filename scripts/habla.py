#!/usr/bin/env python3
"""habla.py — mapa de lo que se dice en cada clip: tramos de voz con su texto y sus segundos.

  python3 habla.py <proyecto> [--clips a.mp4 b.mp4 ...] [--idioma es] [--modelo small]

Sirve para clips donde una persona habla (creadoras, testimonios): permite ver qué intentos hizo, cuál es el mejor,
y dónde cortar. No decide nada: tú lees el mapa, eliges la toma y escribes los tiempos en proyecto.json.

Cómo funciona (solo ffmpeg + HyperFrames, sin instalar nada más):
  1. Detecta los silencios del audio de cada clip y deja los tramos con voz.
  2. Transcribe cada tramo por separado con `hyperframes transcribe`. Así el texto y los segundos son fiables
     (transcribir el clip entero estira los tiempos cuando hay pausas largas).
Resultado: <proyecto>/habla.json y una tabla en pantalla. Los tiempos son segundos del CLIP preparado (media/).

Ojo con las "alucinaciones" de Whisper en tramos de ruido ("Subtítulos por la comunidad de Amara.org",
"¡Suscríbete!"): son ruido, no voz. Se marcan con "?" cuando el tramo dura menos de 0.8 s.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def duracion(ruta):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def tramos_con_voz(audio, dur, ruido_db=-40, silencio_min=0.4, voz_min=0.25):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(audio), "-af", "silencedetect=noise=%ddB:d=%s" % (ruido_db, silencio_min),
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    silencios = [(s, fin[i] if i < len(fin) else dur) for i, s in enumerate(ini)]
    tramos, t = [], 0.0
    for s, e in silencios:
        if s - t > voz_min:
            tramos.append((t, s))
        t = e
    if dur - t > voz_min:
        tramos.append((t, dur))
    return tramos


def transcribir_tramo(wav, idioma, modelo, trabajo):
    for viejo in Path(trabajo).glob("*"):
        viejo.unlink()
    shutil.copy2(str(wav), str(Path(trabajo) / "t.wav"))
    r = subprocess.run(["npx", "hyperframes", "transcribe", "t.wav", "--model", modelo, "--language", idioma, "--json", "-d", "."],
                       cwd=str(trabajo), capture_output=True, text=True, shell=sys.platform.startswith("win"))
    tj = Path(trabajo) / "transcript.json"
    if not tj.exists():
        return ""
    palabras = json.load(open(tj))
    return " ".join((w.get("text") or w.get("word") or "").strip() for w in palabras).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proyecto")
    ap.add_argument("--clips", nargs="*", help="nombres en media/ (por defecto, todos los que tienen audio)")
    ap.add_argument("--idioma", default="es")
    ap.add_argument("--modelo", default="small", help="small, medium o large-v3 (los .en solo sirven para inglés)")
    a = ap.parse_args()

    base = Path(a.proyecto).expanduser()
    media = base / "media"
    audios = sorted(media.glob("*.m4a"))
    if a.clips:
        audios = [media / (Path(c).stem + ".m4a") for c in a.clips]
    if not audios:
        sys.exit("no hay audios en %s. Corre preparar.py con los clips (guarda el audio como <clip>.m4a)" % media)

    mapa = {}
    trabajo = tempfile.mkdtemp()
    tmp = Path(tempfile.mkdtemp())
    for au in audios:
        if not au.exists():
            print("no existe %s" % au)
            continue
        dur = duracion(au)
        print("== %s (%.1fs)" % (au.stem, dur))
        mapa[au.stem] = []
        for desde, hasta in tramos_con_voz(au, dur):
            a0, b0 = max(0.0, desde - 0.1), min(dur, hasta + 0.1)
            wav = tmp / "tramo.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.2f" % a0, "-to", "%.2f" % b0, "-i", str(au),
                            "-ac", "1", "-ar", "16000", str(wav)], capture_output=True)
            texto = transcribir_tramo(wav, a.idioma, a.modelo, trabajo)
            dudoso = (hasta - desde) < 0.8
            mapa[au.stem].append({"desde": round(desde, 2), "hasta": round(hasta, 2), "texto": texto, "dudoso": dudoso})
            print("  [%6.2f - %6.2f] %s%s" % (desde, hasta, "? " if dudoso else "", texto))
        if not mapa[au.stem]:
            print("  (sin voz: solo ambiente)")
    # ritmo de habla: palabras por segundo de voz (sin contar tramos dudosos)
    pal = seg = 0.0
    for tramos in mapa.values():
        for t in tramos:
            if not t["dudoso"] and t["texto"]:
                pal += len(t["texto"].split())
                seg += t["hasta"] - t["desde"]
    if seg > 0:
        ritmo = pal / seg
        if ritmo < 2.2:
            sug, motivo = 1.2, "habla despacio"
        elif ritmo <= 3.0:
            sug, motivo = 1.1, "ritmo normal"
        else:
            sug, motivo = 1.0, "habla rápido"
        print("\nritmo de habla: %.2f palabras/seg (%s) -> velocidad sugerida %.1fx" % (ritmo, motivo, sug))
        print("Es solo una guía: escúchalo y confirma con la persona antes de acelerar (entregar.py --velocidad).")
    json.dump(mapa, open(base / "habla.json", "w"), ensure_ascii=False, indent=1)
    print("\nlisto -> %s" % (base / "habla.json"))


if __name__ == "__main__":
    main()
