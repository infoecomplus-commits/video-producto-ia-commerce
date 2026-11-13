#!/usr/bin/env python3
"""armar.py — monta el video de producto a partir de proyecto.json y lo renderiza con HyperFrames.

  python3 armar.py <carpeta_proyecto>                      # arma la composición (hf/index.html)
  python3 armar.py <carpeta_proyecto> --cuadros 1,4,9      # + capturas en <proyecto>/revision/
  python3 armar.py <carpeta_proyecto> --render             # + video en <proyecto>/salida/
  python3 armar.py <carpeta_proyecto> --version historia   # variante corta (escenas con "historia": false se omiten)

La estructura de proyecto.json está explicada en references/escenas.md y en plantillas/proyecto.ejemplo.json.
No inventa nada: todo texto, beneficio u oferta que aparece en el video viene escrito en proyecto.json.
"""
import argparse
import html
import json
import math
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
import sfx as generador_sfx  # noqa: E402

TAMANOS = {"9:16": (1080, 1920), "1:1": (1080, 1080), "4:5": (1080, 1350), "16:9": (1920, 1080)}
# franja superior (fracción del alto) donde va el logo, según dónde se publicará
LOGO_Y = {"tiktok": 0.10, "meta": 0.13, "reels": 0.13, "stories": 0.13, "feed": 0.05}
# Meta (Facebook/Instagram) en Reels y Stories tapa ~14 % arriba y ~35 % abajo con su interfaz: el contenido va en el centro
PLATAFORMAS_META = {"meta", "reels", "stories"}
CATEGORIAS_SENSIBLES = {"salud", "belleza", "piel", "peso", "cosmetica", "cosméticos", "suplementos", "cuerpo", "estetica", "estética"}
MOVIMIENTO = {"energico": ("back.out(1.7)", 0.45), "suave": ("power2.out", 0.6), "cinematico": ("expo.out", 0.8)}

ICONOS = {  # trazos propios, viewBox 24, solo línea
    "check": "M5 12.5l4.5 4.5L19 7",
    "star": "M12 3.2l2.6 5.5 6 .8-4.4 4.2 1.1 6-5.3-2.9-5.3 2.9 1.1-6L3.4 9.5l6-.8z",
    "truck": "M2.5 6.5h11v9h-11zM13.5 9.5h4l3 3.2v2.8h-7zM6.5 17.5a1.6 1.6 0 1 0 .01 0M16.5 17.5a1.6 1.6 0 1 0 .01 0",
    "shield": "M12 3l7.5 2.8v5.7c0 4.4-3 7.7-7.5 9.5-4.5-1.8-7.5-5.1-7.5-9.5V5.8z",
    "bolt": "M13 2.5L5 13.5h6l-1 8 8-11h-6z",
    "heart": "M12 20s-7-4.3-7-9.8A4.1 4.1 0 0 1 12 7.6a4.1 4.1 0 0 1 7 2.6C19 15.7 12 20 12 20z",
    "box": "M12 3l8 4.5v9L12 21l-8-4.5v-9zM12 12l8-4.5M12 12v9M12 12L4 7.5",
    "clock": "M12 7.5V12l3 2M12 3a9 9 0 1 0 .01 0",
    "sparkle": "M12 3v5M12 16v5M3 12h5M16 12h5M6 6l3 3M15 15l3 3M18 6l-3 3M9 15l-3 3",
    "gift": "M4 10.5h16V20H4zM3 7.5h18v3H3zM12 7.5V20M12 7.5C10 4 6.5 4.6 7 6.3c.4 1.4 3 1.2 5 1.2zM12 7.5C14 4 17.5 4.6 17 6.3c-.4 1.4-3 1.2-5 1.2z",
}


EMOJIS = {"check": "✅", "star": "⭐", "truck": "🚚", "shield": "🛡️", "bolt": "⚡", "heart": "❤️", "box": "📦",
          "clock": "⏰", "sparkle": "✨", "gift": "🎁"}


def luminancia_relativa(hexcolor):
    h = hexcolor.lstrip("#")
    r, g, b = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contraste(l1, l2):
    a, b = max(l1, l2), min(l1, l2)
    return (a + 0.05) / (b + 0.05)


def hex_a_rgba(h, a):
    h = h.lstrip("#")
    return "rgba(%d,%d,%d,%s)" % (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def sonda_dur(ruta):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def fallo(msg):
    sys.exit("ERROR: " + msg)


class Montaje:
    def __init__(self, base, spec, version):
        self.base = base
        self.spec = spec
        self.version = version
        self.nivel = int(spec.get("nivel", 2))
        self.formato = spec.get("formato", "9:16")
        if self.formato not in TAMANOS:
            fallo("formato '%s' no válido. Usa: %s" % (self.formato, ", ".join(TAMANOS)))
        self.W, self.H = TAMANOS[self.formato]
        m = min(self.W, self.H)
        self.m = m
        self.vertical = self.H > self.W * 1.2
        marca = spec.get("marca", {})
        estilos = json.load(open(RAIZ / "estilos.json"))
        preset = estilos.get(marca.get("estilo", ""), {})
        self.C = dict(preset.get("colores", estilos["neon-urbano"]["colores"]))
        self.C.update(marca.get("colores", {}))
        self.F = dict(preset.get("fuentes", estilos["neon-urbano"]["fuentes"]))
        self.F.update(marca.get("fuentes", {}))
        mov = marca.get("movimiento", preset.get("movimiento", "energico"))
        self.EASE, self.DUR_E = MOVIMIENTO.get(mov, MOVIMIENTO["energico"])
        self.X = self.W * 0.06
        self.SAFE_R = self.W * (0.86 if self.vertical else 0.94)
        self.AW = self.SAFE_R - self.X
        self.meta = self.vertical and spec.get("plataforma", "tiktok") in PLATAFORMAS_META
        if self.meta:
            self.Y_TIT, self.Y_MID, self.Y_LOW, self.Y_CAP = self.H * 0.19, self.H * 0.37, self.H * 0.50, self.H * 0.60
            self.Y_CTA = (0.20, 0.38, 0.50, 0.58)   # logo grande, texto, botón, subtexto
        else:
            self.Y_TIT, self.Y_MID, self.Y_LOW, self.Y_CAP = self.H * 0.20, self.H * 0.44, self.H * 0.60, self.H * 0.74
            self.Y_CTA = (0.22, 0.42, 0.54, 0.64)
        # "emoji" (por defecto, más cercano al público de Meta/TikTok) o "lineal" (íconos de trazo, más sobrio) o "ninguno"
        self.iconos = marca.get("iconos", spec.get("iconos", "emoji"))
        self.html, self.tl, self.sfx, self.usados, self.audios = [], [], [], [], []
        self.factor_sfx = 1.0
        self.uid = 0
        self.rnd = random.Random(7)

    # ---- utilidades de timeline -------------------------------------------------
    def nid(self, pref):
        self.uid += 1
        return "%s%d" % (pref, self.uid)

    def fromto(self, sel, t, desde, hasta, d=None, ease=None):
        h = dict(hasta)
        h.update({"duration": round(d if d is not None else self.DUR_E, 3), "ease": ease or self.EASE, "immediateRender": False})
        self.tl.append("tl.fromTo(%s,%s,%s,%.3f);" % (json.dumps(sel), json.dumps(desde), json.dumps(h), t))

    def to(self, sel, t, vars_, d, ease="power2.out"):
        h = dict(vars_)
        h.update({"duration": round(d, 3), "ease": ease})
        self.tl.append("tl.to(%s,%s,%.3f);" % (json.dumps(sel), json.dumps(h), t))

    def set(self, sel, t, vars_):
        self.tl.append("tl.set(%s,%s,%.3f);" % (json.dumps(sel), json.dumps(vars_), t))

    def aparece(self, sel, t0, t1, desde=None, d=None):
        """Entra en t0 y sale en t1."""
        desde = desde or {"opacity": 0, "y": 40, "scale": 0.92}
        self.fromto(sel, t0, desde, {"opacity": 1, "x": 0, "y": 0, "scale": 1, "rotation": 0}, d)
        self.to(sel, max(t1 - 0.22, t0 + 0.2), {"opacity": 0}, 0.2, "power1.in")

    def sonido(self, t, nombre, vol=0.35, minimo=1):
        if self.spec.get("sonidos", True) and self.nivel >= minimo:
            self.sfx.append((round(max(0.0, t), 3), nombre, round(vol * self.factor_sfx, 3)))

    # ---- piezas -----------------------------------------------------------------
    def acento(self, texto):
        t = html.escape(texto)
        return re.sub(r"\*(.+?)\*", r'<span class="ac">\1</span>', t)

    def texto(self, pref, contenido, clase, x, y, ancho=None, extra=""):
        i = self.nid(pref)
        ancho = ancho if ancho is not None else self.AW
        self.html.append('<div id="%s" class="%s" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;%s">%s</div>'
                         % (i, clase, x, y, ancho, extra, contenido))
        return "#" + i

    def icono_svg(self, nombre, px):
        """Ícono de una escena. `nombre` puede ser un nombre de la lista o un emoji escrito directamente."""
        if self.iconos == "ninguno" or not nombre:
            return ""
        literal = not nombre.isascii()
        if literal or self.iconos == "emoji":
            e = nombre if literal else EMOJIS.get(nombre, EMOJIS["check"])
            return '<span class="emo" style="font-size:%dpx">%s</span>' % (int(px * 0.9), e)
        d = ICONOS.get(nombre, ICONOS["check"])
        return ('<svg viewBox="0 0 24 24" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2.4" '
                'stroke-linecap="round" stroke-linejoin="round"><path d="%s"/></svg>' % (px, px, self.C["acento"], d))

    def chip(self, pref, texto, icono, x, y, t0, t1):
        px = int(self.m * 0.05)
        ic = self.icono_svg(icono, px) if icono else ""
        cuerpo = ("<span class='ci'>%s</span>" % ic if ic else "") + "<span>%s</span>" % self.acento(texto)
        sel = self.texto(pref, cuerpo, "chip", x, y, None, "max-width:%.1fpx" % self.AW)
        self.aparece(sel, t0, t1, {"opacity": 0, "x": -60, "scale": 0.95})
        self.sonido(t0, "pop", 0.3)
        return sel

    def particulas(self, t, cx, cy, n=34):
        pid = self.nid("pt")
        puntos = "".join('<i style="width:%dpx;height:%dpx;background:%s"></i>'
                         % (s, s, self.C["acento"] if k % 3 else self.C["apoyo"])
                         for k, s in enumerate(self.rnd.randint(int(self.m * 0.012), int(self.m * 0.026)) for _ in range(n)))
        self.html.append('<div id="%s" class="parts" style="left:%.1fpx;top:%.1fpx">%s</div>' % (pid, cx, cy, puntos))
        self.set("#" + pid, t, {"opacity": 1})
        for k in range(n):
            ang, dist = self.rnd.uniform(0, 6.283), self.rnd.uniform(0.35, 1) * self.m * 0.42
            dk = self.rnd.uniform(0.8, 1.2)
            self.fromto("#%s i:nth-child(%d)" % (pid, k + 1), t, {"x": 0, "y": 0, "scale": 0.5, "opacity": 1},
                        {"x": round(dist * math.cos(ang), 1), "y": round(dist * math.sin(ang), 1), "scale": 1.1}, dk, "power3.out")
            self.to("#%s i:nth-child(%d)" % (pid, k + 1), t + dk * 0.6, {"opacity": 0}, dk * 0.4, "power1.in")
        self.set("#" + pid, t + 1.5, {"opacity": 0})
        self.sonido(t, "brillo", 0.3, 3)

    # ---- clips ------------------------------------------------------------------
    def clip(self, nombre, desde, t0, d, estilo=""):
        origen = self.base / "media" / Path(nombre).name
        if not origen.exists():
            disponibles = sorted(p.name for p in (self.base / "media").glob("*.mp4") if not p.name.startswith("hoja_"))
            fallo("el clip '%s' no está en media/. Disponibles: %s. ¿Corriste preparar.py?" % (nombre, ", ".join(disponibles) or "ninguno"))
        largo = sonda_dur(origen)
        if desde >= largo:
            fallo("el clip %s dura %.1fs y pides empezar en %.1fs" % (nombre, largo, desde))
        if desde + d > largo + 0.05:
            print("aviso: %s dura %.1fs; recorto la escena de %.1fs a %.1fs" % (nombre, largo, d, largo - desde))
            d = largo - desde
        if nombre not in self.usados:
            self.usados.append(Path(nombre).name)
        i = self.nid("v")
        filtro = "filter:contrast(1.06) saturate(1.12);" if self.nivel >= 3 else ""
        self.html.append('<video id="%s" class="clip fondo" src="media/%s" muted playsinline data-start="%.3f" data-duration="%.3f" '
                         'data-media-start="%.3f" style="%s%s"></video>' % (i, Path(nombre).name, t0, d, desde, filtro, estilo))
        return "#" + i, d

    def movimiento_camara(self, sel, t0, d):
        if self.nivel >= 2:
            fin = 1.10 if self.nivel >= 3 else 1.06
            self.fromto(sel, t0, {"scale": 1}, {"scale": fin}, d, "none")

    # ---- escenas ----------------------------------------------------------------
    def escena(self, i, e, t0, d):
        tipo = e.get("tipo")
        t1 = t0 + d
        sin_clip = tipo == "cta" and not e.get("clip")
        if sin_clip:
            self.html.append('<div class="fondo" style="background:%s;z-index:1" data-start="%.3f" data-duration="%.3f"></div>' % (self.C["fondo"], t0, d))
        elif tipo != "comparativo":
            sel, d2 = self.clip(e["clip"], float(e.get("desde", 0)), t0, d)
            self.movimiento_camara(sel, t0, d2)
            if e.get("detras"):
                self.texto_detras(e, t0, d2)
        hay_voz = bool(self.spec.get("voz", {}).get("archivo"))
        x, ancho = self.X, self.AW

        if tipo == "gancho":
            s = self.texto("tx", self.acento(e["texto"]), "tit", x, self.Y_TIT, ancho)
            desde = {"opacity": 0, "scale": 1.5, "rotation": -4} if self.nivel >= 3 else {"opacity": 0, "y": 50, "scale": 0.9}
            self.aparece(s, t0 + 0.15, min(t1, t0 + 3.2), desde)
            self.sonido(t0 + 0.15, "whoosh" if self.nivel >= 2 else "pop", 0.3)
            if e.get("subtexto"):
                s2 = self.texto("tx", self.acento(e["subtexto"]), "sub", x, self.Y_MID, ancho)
                self.aparece(s2, t0 + 0.9, t1)

        elif tipo == "producto":
            s = self.texto("tx", self.acento(e["texto"]), "tit chico", x, self.Y_LOW - self.m * 0.10, ancho, "text-align:left")
            self.aparece(s, t0 + 0.2, t1, {"opacity": 0, "x": -80})
            self.sonido(t0 + 0.2, "pop", 0.3)
            if e.get("subtexto"):
                s2 = self.texto("tx", self.acento(e["subtexto"]), "sub", x, self.Y_LOW + self.m * 0.10, ancho, "text-align:left")
                self.aparece(s2, t0 + 0.6, t1, {"opacity": 0, "x": -60})

        elif tipo == "demo":
            if e.get("paso"):
                pid = self.nid("pa")
                px = int(self.m * 0.13)
                self.html.append('<div id="%s" class="paso" style="left:%.1fpx;top:%.1fpx;width:%dpx;height:%dpx;font-size:%dpx">%s</div>'
                                 % (pid, x, self.Y_LOW - px * 0.2, px, px, int(px * 0.6), html.escape(str(e["paso"]))))
                self.aparece("#" + pid, t0 + 0.15, t1, {"opacity": 0, "scale": 0.2, "rotation": -30})
                self.sonido(t0 + 0.15, "pop", 0.3)
            if e.get("texto"):
                s = self.texto("tx", self.acento(e["texto"]), "chip", x, self.Y_LOW + self.m * 0.14, None, "max-width:%.1fpx" % ancho)
                self.aparece(s, t0 + 0.45, t1, {"opacity": 0, "y": 40})
            if e.get("icono") and self.nivel >= 2:
                ic = self.nid("ic")
                px = int(self.m * 0.16)
                self.html.append('<div id="%s" class="icono" style="left:%.1fpx;top:%.1fpx">%s</div>'
                                 % (ic, self.SAFE_R - px - self.m * 0.02, self.Y_MID, self.icono_svg(e["icono"], px)))
                self.fromto("#" + ic, t0 + 0.7, {"opacity": 0, "scale": 0, "rotation": -25}, {"opacity": 1, "scale": 1, "rotation": 0}, 0.6, "elastic.out(1,0.45)")
                self.to("#" + ic, t0 + 1.3, {"y": -14, "yoyo": True, "repeat": max(1, int((d - 1.5) / 0.6)), "ease": "sine.inOut"}, 0.6, "sine.inOut")
                self.to("#" + ic, t1 - 0.25, {"opacity": 0}, 0.2, "power1.in")
                self.sonido(t0 + 0.7, "pop", 0.3, 2)

        elif tipo == "beneficios":
            items = e.get("items", [])[:4]
            if e.get("texto"):
                s = self.texto("tx", self.acento(e["texto"]), "tit chico", x, self.Y_TIT, ancho)
                self.aparece(s, t0 + 0.1, t1)
            alto = self.m * 0.105
            y0 = self.Y_MID - (len(items) - 1) * alto * 0.15
            paso = (d - 0.6) / max(len(items), 1)
            for k, it in enumerate(items):
                ic = it.get("icono", "check") if isinstance(it, dict) else "check"
                tx = it.get("texto") if isinstance(it, dict) else it
                self.chip("ch", tx, ic, x, y0 + k * alto, t0 + 0.4 + k * min(0.5, paso), t1)

        elif tipo == "oferta":
            s = self.texto("tx", self.acento(e["texto"]), "tit", x, self.Y_TIT, ancho)
            desde = {"opacity": 0, "scale": 1.4, "rotation": -3} if self.nivel >= 3 else {"opacity": 0, "y": 50}
            self.aparece(s, t0 + 0.15, t1, desde)
            self.sonido(t0 + 0.15, "pop", 0.35)
            y = self.Y_MID
            if e.get("precio"):  # solo si la persona lo pidió expresamente
                sp = self.texto("tx", html.escape(str(e["precio"])), "precio", x, y, ancho)
                self.aparece(sp, t0 + 0.6, t1, {"opacity": 0, "scale": 0.5})
                self.sonido(t0 + 0.6, "ding", 0.3, 2)
                y += self.m * 0.2
            for k, it in enumerate(e.get("items", [])[:3]):
                ic = it.get("icono", "gift") if isinstance(it, dict) else "gift"
                tx = it.get("texto") if isinstance(it, dict) else it
                self.chip("ch", tx, ic, x, y + k * self.m * 0.105, t0 + 0.7 + k * 0.4, t1)
            if self.nivel >= 3:
                self.particulas(t0 + 0.2, self.W * 0.5, self.Y_TIT + self.m * 0.1)

        elif tipo == "cta":
            if not sin_clip:
                dim = self.nid("dm")
                self.html.append('<div id="%s" class="dim clip" data-start="%.3f" data-duration="%.3f"></div>' % (dim, t0, d + 1))
                self.fromto("#" + dim, t0, {"opacity": 0}, {"opacity": 1}, 0.4, "none")
            logo = self.spec.get("_logo_archivo")
            if logo:
                li = self.nid("lg")
                w = self.W * 0.5
                self.html.append('<img id="%s" class="logo-grande" src="media/%s" style="left:%.1fpx;top:%.1fpx;width:%.1fpx">'
                                 % (li, logo, (self.W - w) / 2, self.H * self.Y_CTA[0], w))
                self.aparece("#" + li, t0 + 0.2, t1 + 1, {"opacity": 0, "scale": 0.6})
            else:
                nm = self.texto("tx", html.escape(self.spec.get("tienda", "")), "tit", x, self.H * (self.Y_CTA[0] + 0.02), ancho)
                self.aparece(nm, t0 + 0.2, t1 + 1)
            if e.get("texto"):
                s = self.texto("tx", self.acento(e["texto"]), "tit chico", x, self.H * self.Y_CTA[1], ancho)
                self.aparece(s, t0 + 0.5, t1 + 1)
            if e.get("boton"):
                bi = self.nid("bt")
                self.html.append('<div id="%s" class="btn" style="left:%.1fpx;top:%.1fpx;width:%.1fpx">%s</div>'
                                 % (bi, x + ancho * 0.1, self.H * self.Y_CTA[2], ancho * 0.8, html.escape(e["boton"])))
                self.aparece("#" + bi, t0 + 0.9, t1 + 1, {"opacity": 0, "scale": 0.6})
                self.sonido(t0 + 0.9, "ding", 0.3)
                if self.nivel >= 2:
                    self.to("#" + bi, t0 + 1.6, {"scale": 1.06, "yoyo": True, "repeat": max(1, int((d - 1.8) / 0.5)), "ease": "sine.inOut"}, 0.5, "sine.inOut")
            if e.get("subtexto"):
                s2 = self.texto("tx", self.acento(e["subtexto"]), "sub", x, self.H * self.Y_CTA[3], ancho)
                self.aparece(s2, t0 + 1.2, t1 + 1)
            if self.nivel >= 3:
                self.particulas(t0 + 0.9, self.W * 0.5, self.H * 0.56)

        elif tipo == "comparativo":
            self.comparativo(e, t0, d)

        elif tipo == "habla":
            pass  # clip con una persona hablando: solo lleva audio, subtítulos y, si se pide, una etiqueta

        else:
            fallo("tipo de escena '%s' no existe. Usa: gancho, producto, demo, beneficios, oferta, cta, comparativo, habla" % tipo)

        if e.get("audio") and e.get("clip"):  # voz/sonido original del clip (lo dejó preparar.py como <clip>.m4a)
            a = Path(e["clip"]).stem + ".m4a"
            if not (self.base / "media" / a).exists():
                fallo("el clip %s no tiene audio guardado (%s). Corre preparar.py con ese clip" % (e["clip"], a))
            if a not in self.usados:
                self.usados.append(a)
            self.audios.append('<audio id="%s" class="clip" src="media/%s" data-start="%.3f" data-duration="%.3f" data-media-start="%.3f" data-volume="%.2f"></audio>'
                               % (self.nid("au"), a, t0, d, float(e.get("desde", 0)), float(e.get("volumen", 1.0))))
        self.subtitulos_habla(e, t0, d)

        if e.get("etiqueta"):  # etiqueta suelta opcional en cualquier escena
            a0, a1 = t0 + 0.4, t1
            if e.get("etiqueta_t"):   # [desde, hasta] en segundos del CLIP
                dsd = float(e.get("desde", 0))
                a0, a1 = t0 + float(e["etiqueta_t"][0]) - dsd, min(t0 + float(e["etiqueta_t"][1]) - dsd, t1)
            s = self.texto("tx", "<span>%s</span>" % self.acento(e["etiqueta"]), "chip", x, self.Y_CAP - self.m * 0.12, None, "max-width:%.1fpx" % ancho)
            self.aparece(s, a0, a1)
            self.sonido(a0, "pop", 0.3)

    def luminancia_fondo(self, clip, seg, y0, y1):
        """Luminancia relativa (0-1) del fondo donde irá el texto: mide los costados de la franja (donde casi nunca está
        la persona) en el clip, en el segundo `seg`."""
        W = self.W
        vals = []
        for x0 in (0, int(W * 0.8)):
            vf = "crop=%d:%d:%d:%d,scale=1:1,format=gray" % (int(W * 0.2), max(int(y1 - y0), 8), x0, max(int(y0), 0))
            r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.2f" % max(seg, 0), "-i", str(clip), "-vf", vf, "-frames:v", "1",
                                "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)
            if r.stdout:
                vals.append(r.stdout[0] / 255.0)
        if not vals:
            return 0.5
        g = sum(vals) / len(vals)
        return g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4

    def color_detras(self, pedido, lum_fondo):
        """Color del texto detrás de la persona con contraste suficiente contra el fondo (texto grande: mínimo 3:1)."""
        oscuro = "#0B0E13"
        candidatos = []
        if pedido and pedido != "auto":
            candidatos.append(pedido)
        candidatos += [self.C["acento"], "#FFFFFF", oscuro]
        for c in candidatos:
            if contraste(luminancia_relativa(c), lum_fondo) >= 3.0:
                if pedido and pedido != "auto" and c != pedido:
                    print("aviso: el color %s casi no se lee sobre ese fondo (contraste %.1f:1); uso %s" %
                          (pedido, contraste(luminancia_relativa(pedido), lum_fondo), c))
                return c
        blanco, negro = contraste(luminancia_relativa("#FFFFFF"), lum_fondo), contraste(luminancia_relativa(oscuro), lum_fondo)
        return "#FFFFFF" if blanco >= negro else oscuro

    def texto_detras(self, e, t0, d):
        """Texto grande DETRÁS de la persona: fondo (clip) -> texto -> recorte de la persona (con transparencia) encima.
        Necesita media/<clip>_recorte.webm (recortar.py). `detras` = {"texto", "de", "a", "y", "color", "tam"} o lista de esos."""
        stem = Path(e["clip"]).stem
        rec = self.base / "media" / (stem + "_recorte.webm")
        if not rec.exists():
            fallo("'detras' necesita el recorte de la persona: python3 scripts/recortar.py <proyecto> %s" % e["clip"])
        offset = 0.0
        meta = self.base / "media" / (stem + "_recorte.json")
        if meta.exists():
            offset = float(json.load(open(meta)).get("desde", 0))
        desde = float(e.get("desde", 0)) - offset
        if desde < 0:
            fallo("el recorte de %s empieza en %.2fs y la escena pide desde %.2fs; vuelve a correr recortar.py con un tramo mayor"
                  % (e["clip"], offset, float(e.get("desde", 0))))
        if rec.name not in self.usados:
            self.usados.append(rec.name)
        i = self.nid("rc")
        self.html.append('<video id="%s" class="clip recorte" src="media/%s" muted playsinline data-start="%.3f" data-duration="%.3f" '
                         'data-media-start="%.3f"></video>' % (i, rec.name, t0, d, desde))
        self.movimiento_camara("#" + i, t0, d)
        items = e["detras"] if isinstance(e["detras"], list) else [e["detras"]]
        dsd = float(e.get("desde", 0))
        for it in items:
            a0 = t0 + max(float(it.get("de", dsd)) - dsd, 0.0)
            a1 = min(t0 + float(it.get("a", dsd + d)) - dsd, t0 + d)
            tam = int(self.m * float(it.get("tam", 0.24)))
            lineas = it["texto"].replace("\\n", "\n").count("\n") + 1
            y_ini = self.H * float(it.get("y", 0.30))
            seg_clip = dsd + max(((a0 + a1) / 2.0) - t0, 0.0)
            lum = self.luminancia_fondo(self.base / "media" / Path(e["clip"]).name, seg_clip, y_ini, y_ini + tam * 0.95 * lineas)
            color = self.color_detras(it.get("color"), lum)
            cuerpo = "<br>".join(html.escape(p) for p in it["texto"].replace("\\n", "\n").split("\n"))
            sel = self.texto("dt", cuerpo, "detras", 0, self.H * float(it.get("y", 0.30)), self.W,
                             "font-size:%dpx;color:%s;text-shadow:0 8px 30px rgba(0,0,0,.18)" % (tam, color))
            self.fromto(sel, a0, {"opacity": 0, "scale": 1.18}, {"opacity": 1, "scale": 1}, 0.45, "power3.out")
            self.to(sel, max(a1 - 0.2, a0 + 0.3), {"opacity": 0}, 0.2, "power1.in")
            self.sonido(a0, "whoosh", 0.3, 2)

    def subtitulos_habla(self, e, t0, d):
        """`habla`: lista de {"texto", "de", "a"} con tiempos del CLIP (segundos). Se reparten en bloques de pocas palabras
        proporcionales a su largo. Marca con *asteriscos* lo que va en color de acento (puede cruzar varias palabras)."""
        desde = float(e.get("desde", 0))
        por_bloque = int(self.spec.get("palabras_por_bloque", 3))
        for h in e.get("habla", []):
            palabras, acento = [], False
            for tok in h["texto"].split():
                es_ac, limpio = acento, ""
                for ch in tok:
                    if ch == "*":
                        acento = not acento
                        es_ac = es_ac or acento
                    else:
                        limpio += ch
                if limpio:
                    palabras.append((limpio, es_ac))
            bloques = [palabras[i:i + por_bloque] for i in range(0, len(palabras), por_bloque)]
            a0, a1 = max(float(h["de"]) - desde, 0.0) + t0, min(float(h["a"]) - desde, d) + t0
            if a1 <= a0 or not bloques:
                continue
            pesos = [sum(len(w) + 1 for w, _ in b) for b in bloques]
            total, cur = float(sum(pesos)), a0
            for b, p in zip(bloques, pesos):
                fin = cur + (a1 - a0) * p / total
                cuerpo = " ".join('<span class="ac">%s</span>' % html.escape(w) if ac else html.escape(w) for w, ac in b)
                sel = self.texto("sb", cuerpo, "sub cap", self.X, self.Y_CAP, self.AW)
                self.fromto(sel, cur, {"opacity": 0, "y": 14, "scale": 0.96}, {"opacity": 1, "y": 0, "scale": 1}, 0.12, "power2.out")
                self.to(sel, max(fin - 0.05, cur + 0.1), {"opacity": 0}, 0.05, "none")
                cur = fin

    def comparativo(self, e, t0, d):
        cat = str(e.get("categoria", "")).lower()
        if cat in CATEGORIAS_SENSIBLES and not e.get("permitido"):
            fallo("escena 'comparativo' en categoría sensible ('%s'). Meta y TikTok restringen o prohíben antes/después en salud, belleza, "
                  "piel, peso y suplementos, y la política cambia seguido. Revisa la política vigente de la plataforma; si estás seguro de que "
                  "aplica, agrega \"permitido\": true a esa escena." % cat)
        A, B = e["clip"], e.get("clip2")
        if not B:
            fallo("'comparativo' necesita clip (antes/sin) y clip2 (después/con)")
        la, lb = e.get("etiqueta_a", "Antes"), e.get("etiqueta_b", "Después")
        W, H = self.W, self.H
        t1 = t0 + d
        if self.nivel >= 2:
            self.clip(B, float(e.get("desde2", 0)), t0, d)  # "después": capa de fondo
            cid = self.nid("cp")
            self.clip(A, float(e.get("desde", 0)), t0, d)  # "antes": va dentro de la cortina que se encoge
            vid = self.html.pop()
            self.html.append('<div id="%s" class="cmp" style="width:%dpx;height:%dpx">%s</div>' % (cid, W, H, vid))
            lin = self.nid("ln")
            self.html.append('<div id="%s" class="linea" style="height:%dpx"></div>' % (lin, H))
            ini, dur_w = t0 + d * 0.38, d * 0.34
            self.set("#" + cid, t0, {"width": W})
            self.fromto("#" + lin, ini, {"x": W, "opacity": 1}, {"x": 0, "opacity": 1}, dur_w, "power2.inOut")
            self.fromto("#" + cid, ini, {"width": W}, {"width": 0}, dur_w, "power2.inOut")
            self.set("#" + lin, t0, {"opacity": 0})
            self.set("#" + lin, ini + dur_w, {"opacity": 0})
            self.sonido(ini, "whoosh", 0.3, 2)
            marcas = [(la, t0 + 0.2, ini + dur_w * 0.5), (lb, ini + dur_w * 0.6, t1)]
        else:
            m1, d1 = self.clip(A, float(e.get("desde", 0)), t0, d / 2)
            m2, d2 = self.clip(B, float(e.get("desde2", 0)), t0 + d / 2, d / 2)
            marcas = [(la, t0 + 0.2, t0 + d / 2), (lb, t0 + d / 2 + 0.1, t1)]
        for txt, a, b in marcas:
            s = self.texto("tx", html.escape(txt), "chip", self.X, self.Y_LOW, None)
            self.aparece(s, a, b, {"opacity": 0, "y": 30})
            self.sonido(a, "pop", 0.3)

    # ---- marca de agua ----------------------------------------------------------
    def logo_marca(self, fin):
        logo = self.spec.get("_logo_archivo")
        if not logo:
            return
        cfg = self.spec.get("logo", {})
        lado = cfg.get("lado", "auto")
        if lado == "auto":
            prep = self.base / "preparacion.json"
            lado = "izquierda"
            if prep.exists():
                lado = json.load(open(prep)).get("lado_logo", {}).get("sugerido", "izquierda")
        self.lado_logo = lado
        op = float(cfg.get("opacidad", 0.7))
        y = self.H * LOGO_Y.get(self.spec.get("plataforma", "tiktok"), 0.10) if self.vertical else self.H * 0.05
        alto = self.H * (0.055 if self.vertical else 0.09)
        pos = "left:%.1fpx" % self.X if lado == "izquierda" else "right:%.1fpx" % (self.W - self.SAFE_R if self.vertical else self.X)
        self.html.append('<img id="marca" class="marca" src="media/%s" style="%s;top:%.1fpx;height:%.1fpx;max-width:%.1fpx">'
                         % (logo, pos, y, alto, self.W * 0.3))
        self.fromto("#marca", 0.3, {"opacity": 0}, {"opacity": op}, 0.5, "power1.out")
        self.to("#marca", max(fin - 0.2, 0.5), {"opacity": 0}, 0.2, "power1.in")

    # ---- arma todo --------------------------------------------------------------
    def construir(self):
        escenas = [e for e in self.spec["escenas"] if not (self.version == "historia" and e.get("historia") is False)]
        if not escenas:
            fallo("no quedan escenas para la versión '%s'" % self.version)
        # logo: usar el procesado por preparar.py si existe
        cfg = self.spec.get("logo") or {}
        if cfg.get("archivo") is not None or (self.base / "media" / "logo.png").exists():
            nombre = Path(cfg.get("archivo") or "logo.png").name
            prep = self.base / "preparacion.json"
            if prep.exists() and cfg.get("version", "auto") != "original":
                lg = (json.load(open(prep)).get("logo") or {})
                if lg.get("oscuro") and lg.get("archivo_claro") and (self.base / "media" / lg["archivo_claro"]).exists():
                    nombre = lg["archivo_claro"]   # un logo oscuro no se ve sobre el video: se usa su copia blanca
            if (self.base / "media" / nombre).exists():
                self.spec["_logo_archivo"] = nombre
                if nombre not in self.usados:
                    self.usados.append(nombre)
        t = 0.0
        inicios = []
        for e in escenas:
            d = float(e.get("dur_historia", e.get("dur", 3))) if self.version == "historia" else float(e.get("dur", 3))
            inicios.append((t, d))
            t += d
        self.total = round(t, 3)
        if any(e.get("audio") for e in escenas):
            self.factor_sfx = 0.55   # hay voz: los efectos van más bajos
        cta_ini = next((a for (a, _), e in zip(inicios, escenas) if e.get("tipo") == "cta"), self.total)
        self.logo_marca(cta_ini)
        for i, (e, (t0, d)) in enumerate(zip(escenas, inicios)):
            self.escena(i, e, t0, d)
            if i > 0 and e.get("transicion", True):   # "transicion": false = corte seco (p. ej. para saltar una pausa dentro del mismo clip)
                self.transicion(t0)
        for s in self.spec.get("subtitulos", []):
            sel = self.texto("sb", self.acento(s["texto"]), "sub cap", self.X, self.Y_CAP, self.AW)
            self.aparece(sel, float(s["desde"]), float(s["hasta"]), {"opacity": 0, "y": 20})
        return escenas

    def transicion(self, t):
        if self.nivel < 2:
            return
        cid = self.nid("ct")
        self.html.append('<div id="%s" class="cortina"></div>' % cid)
        self.set("#" + cid, 0, {"xPercent": -101})
        self.fromto("#" + cid, t - 0.22, {"xPercent": -101}, {"xPercent": 0}, 0.22, "power3.in")
        self.to("#" + cid, t, {"xPercent": 101}, 0.28, "power3.out")
        self.sonido(t - 0.22, "whoosh", 0.3, 2)
        if self.nivel >= 3:
            self.sonido(t, "impacto", 0.3, 3)

    # ---- salida -----------------------------------------------------------------
    def css(self):
        C, F, m = self.C, self.F, self.m
        tit = int(m * 0.105)
        contorno = "-webkit-text-stroke:.07em #000;paint-order:stroke fill;stroke-linejoin:round"
        return """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:%(fondo)s}
#root{position:absolute;inset:0;overflow:hidden;font-family:'%(ft)s',sans-serif;color:#fff}
.fondo{position:absolute;left:0;top:0;width:%(W)dpx;height:%(H)dpx;object-fit:cover;z-index:1;transform-origin:50%% 50%%}
.detras{position:absolute;text-align:center;opacity:0;z-index:3;font-family:'%(fh)s',sans-serif;font-weight:%(wh)s;line-height:.95;letter-spacing:-.03em;text-transform:uppercase}
.recorte{position:absolute;left:0;top:0;width:%(W)dpx;height:%(H)dpx;object-fit:cover;z-index:4;transform-origin:50%% 50%%}
.cmp{position:absolute;left:0;top:0;overflow:hidden;z-index:2}
.cmp video{object-fit:cover}
.linea{position:absolute;left:0;top:0;width:6px;background:%(acento)s;z-index:3;opacity:0;margin-left:-3px}
.sombra{position:absolute;inset:0;z-index:2;pointer-events:none;background:linear-gradient(180deg,rgba(0,0,0,.38) 0%%,rgba(0,0,0,0) 26%%,rgba(0,0,0,0) 58%%,rgba(0,0,0,.45) 100%%)}
.dim{position:absolute;inset:0;z-index:4;background:%(dim)s;opacity:0}
.tit{position:absolute;text-align:center;opacity:0;z-index:6;font-family:'%(fh)s',sans-serif;font-weight:%(wh)s;font-size:%(tit)dpx;line-height:1.04;
 letter-spacing:-.02em;color:#fff;text-shadow:0 5px 0 rgba(0,0,0,.6),0 0 30px rgba(0,0,0,.7);%(contorno)s}
.tit.chico{font-size:%(tit2)dpx}
.sub{position:absolute;text-align:center;opacity:0;z-index:6;font-weight:%(wt)s;font-size:%(sub)dpx;line-height:1.15;color:#fff;
 text-shadow:0 3px 0 rgba(0,0,0,.6),0 0 18px rgba(0,0,0,.6);%(contorno)s}
.sub.cap{font-size:%(cap)dpx}
.ac{color:%(acento)s}
.chip{position:absolute;opacity:0;z-index:6;display:inline-flex;align-items:center;gap:.5em;font-weight:%(wt)s;font-size:%(chip)dpx;
 line-height:1.1;color:%(texto)s;background:%(chipbg)s;padding:.35em .8em;border-radius:999px;box-shadow:0 10px 28px rgba(0,0,0,.35);width:auto}
.chip .ac{color:%(acento)s;-webkit-text-stroke:.04em %(fondo)s;paint-order:stroke fill}
.ci{display:inline-flex}
.emo{line-height:1}
.paso{position:absolute;opacity:0;z-index:6;display:flex;align-items:center;justify-content:center;border-radius:50%%;background:%(acento)s;color:%(fondo)s;
 font-family:'%(fh)s',sans-serif;font-weight:%(wh)s;box-shadow:0 10px 28px rgba(0,0,0,.4)}
.icono{position:absolute;opacity:0;z-index:6;filter:drop-shadow(0 4px 10px rgba(0,0,0,.6))}
.precio{position:absolute;text-align:center;opacity:0;z-index:6;font-family:'%(fh)s',sans-serif;font-weight:%(wh)s;font-size:%(precio)dpx;color:%(acento)s;%(contorno)s}
.btn{position:absolute;opacity:0;z-index:7;text-align:center;background:%(acento)s;color:%(fondo)s;font-weight:%(wh)s;font-family:'%(fh)s',sans-serif;
 font-size:%(chip)dpx;padding:.55em 0;border-radius:999px;box-shadow:0 14px 36px rgba(0,0,0,.45)}
.logo-grande{position:absolute;opacity:0;z-index:6;height:auto;filter:drop-shadow(0 6px 18px rgba(0,0,0,.5))}
.marca{position:absolute;opacity:0;z-index:12;width:auto;filter:drop-shadow(0 2px 6px rgba(0,0,0,.45))}
.cortina{position:absolute;inset:0;z-index:20;background:%(acento)s}
.parts{position:absolute;opacity:0;z-index:8}.parts i{position:absolute;border-radius:50%%;display:block}""" % {
            "W": self.W, "H": self.H, "fondo": C["fondo"], "acento": C["acento"], "texto": C["texto"],
            "ft": F["texto"], "wt": F.get("pesoTexto", 700), "fh": F["titulos"], "wh": F.get("pesoTitulos", 800),
            "tit": tit, "tit2": int(tit * 0.72), "sub": int(m * 0.052), "cap": int(m * 0.06), "chip": int(m * 0.046), "precio": int(m * 0.2),
            "chipbg": hex_a_rgba(C["fondo"], 0.92), "dim": hex_a_rgba(C["fondo"], 0.72), "contorno": contorno}

    def documento(self):
        fam = lambda f, p: f.replace(" ", "+") + ":wght@%s" % p
        fuentes = "https://fonts.googleapis.com/css2?family=%s&family=%s&display=swap" % (
            fam(self.F["titulos"], self.F.get("pesoTitulos", 800)), fam(self.F["texto"], self.F.get("pesoTexto", 700)))
        audio = []
        k = 0
        for t, n, v in sorted(self.sfx):
            dur = min(self.dur_sfx[n], self.total - t)
            if dur <= 0.02:
                continue
            k += 1
            audio.append('<audio id="sx%d" class="clip" src="sfx/%s.wav" data-start="%.3f" data-duration="%.3f" data-volume="%.2f"></audio>' % (k, n, t, dur, v))
        audio.extend(self.audios)
        for clave, vol_def, fade in (("musica", 0.12, 1.5), ("voz", 1.0, 0)):
            c = self.spec.get(clave) or {}
            if c.get("archivo"):
                nombre = Path(c["archivo"]).name
                audio.append('<audio id="%s" class="clip" src="media/%s" data-start="0" data-duration="%.3f" data-volume="%.2f"%s></audio>' % (
                    clave, nombre, self.total, float(c.get("volumen", vol_def)), (' data-fade-out="%s"' % fade) if fade else ""))
        return """<!doctype html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=%(W)d, height=%(H)d">
<link href="%(fuentes)s" rel="stylesheet"><script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<style>%(css)s</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="%(T).3f" data-width="%(W)d" data-height="%(H)d">
%(cuerpo)s
<div class="sombra"></div>
%(audio)s
<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});
%(tl)s
window.__timelines["main"]=tl;</script></div></body></html>""" % {
            "W": self.W, "H": self.H, "fuentes": fuentes, "css": self.css(), "T": self.total,
            "cuerpo": "\n".join(self.html), "audio": "\n".join(audio), "tl": "\n".join(self.tl)}


def npx(args, cwd):
    shell = sys.platform.startswith("win")
    return subprocess.run(["npx"] + args, cwd=str(cwd), shell=shell)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proyecto")
    ap.add_argument("--version", default="completa", choices=["completa", "historia"])
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--cuadros", help="segundos separados por coma para capturar en revision/")
    a = ap.parse_args()

    base = Path(a.proyecto).expanduser().resolve()
    ruta = base / "proyecto.json"
    if not ruta.exists():
        fallo("no encuentro %s. Crea el proyecto con nuevo_proyecto.py" % ruta)
    spec = json.load(open(ruta))
    mt = Montaje(base, spec, a.version)
    mt.construir()

    hf = base / "hf"
    (hf / "media").mkdir(parents=True, exist_ok=True)
    (hf / "sfx").mkdir(parents=True, exist_ok=True)
    generador_sfx.generar(RAIZ / "assets" / "sfx")
    # una sola fuente de verdad: media/ del proyecto; hf/media se rehace SIEMPRE desde ahí
    for viejo in (hf / "media").glob("*"):
        viejo.unlink()
    extras = [Path(spec[k]["archivo"]).expanduser() for k in ("musica", "voz") if (spec.get(k) or {}).get("archivo")]
    for nombre in mt.usados:
        shutil.copy2(str(base / "media" / nombre), str(hf / "media" / nombre))
    for ex in extras:
        origen = ex if ex.exists() else base / "media" / ex.name
        if not origen.exists():
            fallo("no encuentro el audio %s" % ex)
        shutil.copy2(str(origen), str(hf / "media" / origen.name))
    mt.dur_sfx = {}
    for t, n, v in mt.sfx:
        if n not in mt.dur_sfx:
            origen = RAIZ / "assets" / "sfx" / (n + ".wav")
            shutil.copy2(str(origen), str(hf / "sfx" / (n + ".wav")))
            mt.dur_sfx[n] = sonda_dur(origen)

    (hf / "index.html").write_text(mt.documento(), encoding="utf-8")
    json.dump({"version": "1", "compositions": [{"id": "main", "file": "index.html"}]}, open(hf / "hyperframes.json", "w"), indent=2)
    print("composición lista: %s · %dx%d · %.1fs · nivel %d · versión %s · %d efectos de sonido" % (
        hf / "index.html", mt.W, mt.H, mt.total, mt.nivel, a.version, len(mt.sfx)))
    if getattr(mt, "lado_logo", None):
        print("logo: lado %s" % mt.lado_logo)

    if npx(["hyperframes", "lint"], hf).returncode != 0:
        print("aviso: lint devolvió errores; revisa antes de renderizar")
    if a.cuadros:
        out = base / "revision" / a.version
        out.mkdir(parents=True, exist_ok=True)
        for viejo in out.glob("*"):
            viejo.unlink()
        npx(["hyperframes", "snapshot", "--at", a.cuadros, "--no-end", "-o", str(out)], hf)
        print("capturas en %s" % out)
    if a.render:
        (base / "salida").mkdir(exist_ok=True)
        destino = base / "salida" / ("render_%s.mp4" % a.version)
        r = npx(["hyperframes", "render", "--quality", "high", "--output", str(destino)], hf)
        if r.returncode != 0:
            fallo("el render falló")
        print("render listo: %s -> sigue con entregar.py" % destino)


if __name__ == "__main__":
    main()
