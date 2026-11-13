#!/usr/bin/env python3
"""musica.py — genera una pista de fondo ORIGINAL (sin derechos de terceros) para el video.

  python3 musica.py <salida.wav> --duracion 32 [--estilo energica|suave] [--tono 0]

Sintetiza con la biblioteca estándar de Python (sin instalar nada) una pista instrumental corta:
  - energica: 112 BPM, bombo en cada tiempo, palmas, hi-hat, bajo con "bombeo", arpegio brillante y colchón de acordes.
  - suave: 92 BPM, sin bombo ni palmas, arpegio tranquilo y colchón de acordes; para marcas sobrias.
Progresión I - V - vi - IV (alegre y de ritmo constante). `--tono` sube o baja la tonalidad en semitonos.

La pista es sencilla a propósito: sirve de cama de energía bajo la voz, no de canción. Úsala con volumen bajo
(0.12 a 0.18 en `musica.volumen` de proyecto.json). Si la persona prefiere su propia música, puede usarla siempre que
tenga derechos de uso para anuncios (la música de tendencia de TikTok/Instagram normalmente no los tiene).
"""
import argparse
import array
import math
import random
import struct
import wave

SR = 44100


def freq(midi):
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def suma_nota(buf, inicio, dur, f, amp, tipo="tri", decaimiento=6.0, ataque=0.004):
    i0 = int(inicio * SR)
    n = min(int(dur * SR), len(buf) - i0)
    if n <= 0:
        return
    w = 2 * math.pi * f / SR
    na = max(1, int(ataque * SR))
    for i in range(n):
        t = i / SR
        env = math.exp(-decaimiento * t) * (i / na if i < na else 1.0)
        fase = (f * t) % 1.0
        if tipo == "sine":
            s = math.sin(w * i)
        elif tipo == "saw":
            s = 2 * fase - 1
        else:  # triángulo
            s = 4 * abs(fase - 0.5) - 1
        buf[i0 + i] += amp * env * s


def suma_bombo(buf, inicio, amp):
    i0 = int(inicio * SR)
    n = min(int(0.30 * SR), len(buf) - i0)
    fase = 0.0
    for i in range(max(n, 0)):
        t = i / SR
        f = 48 + 110 * math.exp(-t * 30)
        fase += 2 * math.pi * f / SR
        buf[i0 + i] += amp * math.sin(fase) * math.exp(-t * 9)


def suma_ruido(buf, inicio, dur, amp, decaimiento, rnd):
    i0 = int(inicio * SR)
    n = min(int(dur * SR), len(buf) - i0)
    prev = 0.0
    for i in range(max(n, 0)):
        x = rnd.uniform(-1, 1)
        s = x - prev          # filtro pasa-altos muy simple: queda brillo, sin graves
        prev = x
        buf[i0 + i] += amp * s * math.exp(-decaimiento * (i / SR))


def generar(salida, duracion, estilo, tono):
    rnd = random.Random(11)
    n = int(duracion * SR)
    ritmo = array.array("f", [0.0]) * n     # percusión
    tonal = array.array("f", [0.0]) * n     # bajo + arpegio + colchón (recibe el "bombeo")
    energica = estilo == "energica"
    bpm = 112 if energica else 92
    beat = 60.0 / bpm
    compas = 4 * beat
    octavo = beat / 2
    base = 60 + tono
    # I - V - vi - IV (notas MIDI de cada acorde, de grave a agudo)
    acordes = [[0, 4, 7, 12], [-1, 2, 7, 11], [-3, 0, 4, 9], [-7, -3, 0, 5]]
    raices = [0, -5, -3, -7]
    patron_arpegio = [0, 1, 2, 3, 2, 1, 2, 1]
    patron_bajo = [(0, 1.6), (3, 1.0), (6, 1.4)]
    bombos = []

    total_compases = int(duracion / compas) + 1
    for c in range(total_compases):
        t0 = c * compas
        if t0 >= duracion:
            break
        acorde = acordes[c % 4]
        raiz = raices[c % 4]
        # colchón de acordes
        for nota in acorde[:3]:
            suma_nota(tonal, t0, compas * 0.98, freq(base + nota - 12), 0.045 if energica else 0.06, "tri", 0.35, 0.12)
        # bajo
        for pos, largo in patron_bajo:
            suma_nota(tonal, t0 + pos * octavo, largo * octavo, freq(base + raiz - 24), 0.26, "saw" if energica else "tri", 3.5)
        # arpegio
        for k, idx in enumerate(patron_arpegio):
            suma_nota(tonal, t0 + k * octavo, octavo * 2.2, freq(base + acorde[idx] + 12), 0.07, "tri", 7.0)
        # percusión
        for b in range(4):
            tb = t0 + b * beat
            if energica:
                suma_bombo(ritmo, tb, 0.55)
                bombos.append(tb)
                if b in (1, 3):
                    suma_ruido(ritmo, tb, 0.12, 0.12, 22, rnd)          # palma
                suma_ruido(ritmo, tb + octavo, 0.05, 0.07, 70, rnd)     # hi-hat a contratiempo
            else:
                suma_ruido(ritmo, tb, 0.04, 0.03, 80, rnd)

    # "bombeo" del bajo y el arpegio con cada bombo
    if bombos:
        largo = int(0.22 * SR)
        for tb in bombos:
            i0 = int(tb * SR)
            for i in range(min(largo, n - i0)):
                g = 0.30 + 0.70 * (i / largo) ** 1.6
                tonal[i0 + i] *= g if g < 1.0 else 1.0

    mezcla = array.array("f", [0.0]) * n
    pico = 1e-9
    for i in range(n):
        v = ritmo[i] + tonal[i]
        mezcla[i] = v
        if abs(v) > pico:
            pico = abs(v)
    ganancia = 0.7 / pico                       # pico a -3 dBFS
    entrada, salida_f = int(0.25 * SR), int(1.5 * SR)
    with wave.open(salida, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        trozo = bytearray()
        for i in range(n):
            g = ganancia
            if i < entrada:
                g *= i / float(entrada)
            if i > n - salida_f:
                g *= max(0.0, (n - i) / float(salida_f))
            x = max(-1.0, min(1.0, mezcla[i] * g))
            trozo += struct.pack("<hh", int(x * 32767), int(x * 32767))
            if len(trozo) > 400000:
                w.writeframes(bytes(trozo))
                trozo = bytearray()
        w.writeframes(bytes(trozo))
    return bpm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("salida")
    ap.add_argument("--duracion", type=float, default=30.0)
    ap.add_argument("--estilo", choices=["energica", "suave"], default="energica")
    ap.add_argument("--tono", type=int, default=0, help="semitonos para subir/bajar la tonalidad")
    a = ap.parse_args()
    bpm = generar(a.salida, a.duracion, a.estilo, a.tono)
    print("pista generada: %s (%.1fs, %s, %d BPM)" % (a.salida, a.duracion, a.estilo, bpm))


if __name__ == "__main__":
    main()
