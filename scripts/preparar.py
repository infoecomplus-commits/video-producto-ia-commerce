#!/usr/bin/env python3
"""preparar.py — deja los clips del producto y el logo listos para montar.

  python3 preparar.py <carpeta_proyecto> --clips a.mp4 b.mov ... [--logo logo.png] [--formato 9:16]

Qué hace:
  1. Copia cada clip a <proyecto>/media/ ya normalizado: tamaño del formato, 30 cuadros por segundo,
     H.264, sin rotación pendiente (los .MOV del iPhone vienen girados). El original NO se toca.
  2. Saca una tira de cuadros por clip (<proyecto>/media/hoja_<clip>.jpg) para poder mirarlos.
  3. Si hay logo: lo deja en <proyecto>/media/logo.png. Si no tiene transparencia (fondo sólido, típico
     de un JPG), intenta quitarle el fondo.
  4. Sugiere de qué lado poner el logo: el costado de arriba con menos movimiento visual en los clips.
  5. Escribe <proyecto>/preparacion.json con todo lo anterior.

Importante: media/ es la ÚNICA copia de trabajo de los clips; armar.py siempre vuelve a copiar de ahí.
Si cambias un clip, vuelve a correr este script.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TAMANOS = {"9:16": (1080, 1920), "1:1": (1080, 1080), "4:5": (1080, 1350), "16:9": (1920, 1080)}


def run(cmd, binario=False):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode(errors="ignore")[-400:])
    return r.stdout if binario else r.stdout.decode(errors="ignore")


def sonda(ruta):
    d = json.loads(run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(ruta)]))
    v = [s for s in d["streams"] if s.get("codec_type") == "video"]
    a = [s for s in d["streams"] if s.get("codec_type") == "audio"]
    return d, (v[0] if v else None), bool(a)


def normalizar_clip(origen, destino, W, H):
    vf = "scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,fps=30,format=yuv420p" % (W, H, W, H)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(origen), "-vf", vf, "-c:v", "libx264", "-crf", "17",
         "-preset", "medium", "-an", "-movflags", "+faststart", str(destino)])


def tira(clip, salida, dur):
    n = 6
    fps = n / max(dur, 1.0)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-vf", "fps=%f,scale=200:-1,tile=%dx1" % (fps, n),
         "-frames:v", "1", "-q:v", "4", str(salida)])


def esquina_pixel(logo):
    """Color (r,g,b,a) de la esquina superior izquierda del logo (también para PNG de paleta con transparencia)."""
    raw = run(["ffmpeg", "-v", "error", "-i", str(logo), "-vf", "format=rgba,crop=4:4:0:0,scale=1:1", "-frames:v", "1",
               "-f", "rawvideo", "-pix_fmt", "rgba", "-"], binario=True)
    return tuple(raw[:4]) if len(raw) >= 4 else (255, 255, 255, 255)


def recorte_contenido(origen, ancho, alto, esquina):
    """Rectángulo 'w:h:x:y' que contiene el logo sin márgenes (transparentes o del color de fondo), o None."""
    n = 256
    raw = run(["ffmpeg", "-v", "error", "-i", str(origen), "-vf", "format=rgba,scale=%d:%d" % (n, n), "-frames:v", "1",
               "-f", "rawvideo", "-pix_fmt", "rgba", "-"], binario=True)
    if len(raw) < n * n * 4:
        return None
    er, eg, eb, ea = esquina
    x0, y0, x1, y1 = n, n, -1, -1
    for i in range(0, n * n * 4, 4):
        r, g, b, al = raw[i], raw[i + 1], raw[i + 2], raw[i + 3]
        if al <= 16:
            continue
        if ea >= 250 and abs(r - er) + abs(g - eg) + abs(b - eb) < 60:
            continue
        p = i // 4
        x, y = p % n, p // n
        x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
    if x1 < 0:
        return None
    m = 3
    fx, fy = ancho / float(n), alto / float(n)
    X0, Y0 = max(0, int((x0 - m) * fx)), max(0, int((y0 - m) * fy))
    X1, Y1 = min(ancho, int((x1 + 1 + m) * fx)), min(alto, int((y1 + 1 + m) * fy))
    return "%d:%d:%d:%d" % (X1 - X0, Y1 - Y0, X0, Y0)


def luminosidad_logo(png):
    """Luminosidad media (0-255) de los píxeles opacos del logo."""
    raw = run(["ffmpeg", "-v", "error", "-i", str(png), "-vf", "scale=64:64,format=rgba", "-frames:v", "1",
               "-f", "rawvideo", "-pix_fmt", "rgba", "-"], binario=True)
    tot, n = 0.0, 0
    for i in range(0, len(raw) - 3, 4):
        if raw[i + 3] > 128:
            tot += 0.299 * raw[i] + 0.587 * raw[i + 1] + 0.114 * raw[i + 2]
            n += 1
    return tot / n if n else 128.0


def procesar_logo(origen, destino):
    _, v, _ = sonda(origen)
    if v is None:
        raise RuntimeError("el logo no se pudo leer como imagen")
    r, g, b, alfa = esquina_pixel(origen)
    tiene_alfa = alfa < 250   # si la esquina ya es transparente, el logo trae su propio fondo transparente
    info = {"original": str(origen), "alfa_original": bool(tiene_alfa), "fondo_quitado": False}
    cadena = ["format=rgb24"] if not tiene_alfa else []
    corte = recorte_contenido(origen, v["width"], v["height"], (r, g, b, alfa))
    if corte:
        cadena.append("crop=" + corte)
        info["recortado"] = corte
    if not tiene_alfa:
        clave = "0x%02X%02X%02X" % (r, g, b)
        cadena.append("colorkey=%s:0.18:0.06" % clave)
        info["fondo_quitado"] = True
        info["color_fondo"] = clave
    cadena.append("format=rgba")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(origen), "-vf", ",".join(cadena), str(destino)])
    lum = luminosidad_logo(destino)
    info["luminosidad"] = round(lum, 1)
    info["oscuro"] = lum < 110
    if info["oscuro"]:   # sobre el video un logo oscuro no se ve: se genera una copia blanca
        claro = destino.with_name("logo_claro.png")
        run(["ffmpeg", "-v", "error", "-y", "-i", str(destino), "-vf", "lutrgb=r=255:g=255:b=255", str(claro)])
        info["archivo_claro"] = claro.name
    return info


def energia(clip, dur, W, H, lado):
    """Movimiento/detalle visual de la franja superior de un lado. Menor = más tranquilo."""
    cw, ch = int(W * 0.30), int(H * 0.14)
    x = 0 if lado == "izquierda" else W - cw
    y = int(H * 0.06)
    total = 0.0
    muestras = 4
    for k in range(muestras):
        t = dur * (k + 0.5) / muestras
        vf = "crop=%d:%d:%d:%d,edgedetect=low=0.1:high=0.3,scale=32:32:flags=area,format=gray" % (cw, ch, x, y)
        raw = run(["ffmpeg", "-v", "error", "-ss", "%.2f" % t, "-i", str(clip), "-vf", vf, "-frames:v", "1",
                   "-f", "rawvideo", "-pix_fmt", "gray", "-"], binario=True)
        total += (sum(raw) / float(len(raw)) if raw else 0.0)
    return total / muestras


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proyecto")
    ap.add_argument("--clips", nargs="+", default=[])
    ap.add_argument("--logo")
    ap.add_argument("--formato", default="9:16", choices=list(TAMANOS))
    a = ap.parse_args()

    W, H = TAMANOS[a.formato]
    proy = Path(a.proyecto).expanduser()
    media = proy / "media"
    media.mkdir(parents=True, exist_ok=True)
    info = {"formato": a.formato, "ancho": W, "alto": H, "clips": [], "logo": None}
    previo = proy / "preparacion.json"
    if previo.exists():   # se pueden preparar clips y logo en corridas distintas sin perder lo anterior
        try:
            viejo = json.load(open(previo))
            if viejo.get("formato") == a.formato:
                info.update({k: viejo[k] for k in ("clips", "logo", "lado_logo") if k in viejo})
        except ValueError:
            pass

    for c in a.clips:
        origen = Path(c).expanduser()
        if not origen.exists():
            print("NO EXISTE: %s" % origen)
            continue
        destino = media / (origen.stem.replace(" ", "_") + ".mp4")
        d, v, tiene_audio = sonda(origen)
        if v is None:
            print("sin video: %s" % origen)
            continue
        normalizar_clip(origen, destino, W, H)
        if tiene_audio:   # el audio (p. ej. la voz de una creadora) se conserva aparte: armar.py lo usa si la escena lo pide
            run(["ffmpeg", "-v", "error", "-y", "-i", str(origen), "-vn", "-ac", "2", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                 str(media / (destino.stem + ".m4a"))])
        dur = float(json.loads(run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", str(destino)]))["format"]["duration"])
        tira(destino, media / ("hoja_" + destino.stem + ".jpg"), dur)
        info["clips"] = [c for c in info["clips"] if c["archivo"] != destino.name]
        info["clips"].append({"archivo": destino.name, "duracion": round(dur, 2), "original": str(origen), "tenia_audio": tiene_audio,
                              "audio": (destino.stem + ".m4a") if tiene_audio else None})
        print("clip listo: %-28s %5.1fs %s" % (destino.name, dur, "(con audio)" if tiene_audio else ""))

    if a.logo:
        lg = Path(a.logo).expanduser()
        if not lg.exists():
            print("NO EXISTE el logo: %s" % lg)
        else:
            lo = procesar_logo(lg, media / "logo.png")
            lo["archivo"] = "logo.png"
            info["logo"] = lo
            print("logo listo: media/logo.png" + (" (le quité el fondo %s: revísalo)" % lo.get("color_fondo") if lo["fondo_quitado"] else "")
                  + (" · es oscuro: también media/logo_claro.png (blanco)" if lo["oscuro"] else ""))

    if info["clips"] and (a.clips or "lado_logo" not in info):
        e = {"izquierda": 0.0, "derecha": 0.0}
        peso = 0.0
        for c in info["clips"]:
            p = media / c["archivo"]
            for lado in e:
                e[lado] += energia(p, c["duracion"], W, H, lado) * c["duracion"]
            peso += c["duracion"]
        e = {k: round(v / peso, 2) for k, v in e.items()}
        # a igualdad, izquierda: los botones de TikTok/Reels viven a la derecha
        sugerido = "derecha" if e["derecha"] < e["izquierda"] * 0.85 else "izquierda"
        info["lado_logo"] = {"energia": e, "sugerido": sugerido}
        print("logo: energía visual arriba-izquierda %.2f · arriba-derecha %.2f -> lado sugerido: %s" % (e["izquierda"], e["derecha"], sugerido))

    json.dump(info, open(proy / "preparacion.json", "w"), ensure_ascii=False, indent=1)
    print("listo -> %s" % (proy / "preparacion.json"))


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as err:
        sys.exit("error: %s" % err)
