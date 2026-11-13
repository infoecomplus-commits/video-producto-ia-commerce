#!/usr/bin/env python3
"""resumen.py — informe de análisis del material: clips, lo que se dice y lo que hay que decidir.

  python3 resumen.py <proyecto>

Junta lo que dejaron preparar.py (clips, duración, audio, logo) y habla.py (tramos de voz con texto y segundos) en
<proyecto>/analisis.md: una tabla por clip con sus tramos hablados, los intentos repetidos que detecta (frases casi
iguales) y las preguntas abiertas. No decide la estructura: sirve de base para que tú, después de mirar las tiras de
cuadros (media/hoja_*.jpg), le cuentes a la persona (1) qué estructura YA ves en su material y (2) qué estructura puedes
crear. Ver references/analisis.md.
"""
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return re.sub(r"[^a-z0-9 ]", "", "".join(c for c in t if unicodedata.category(c) != "Mn")).strip()


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    base = Path(sys.argv[1]).expanduser()
    prep = base / "preparacion.json"
    if not prep.exists():
        sys.exit("no hay %s: corre preparar.py primero" % prep)
    info = json.load(open(prep))
    habla = json.load(open(base / "habla.json")) if (base / "habla.json").exists() else {}

    out = ["# Análisis del material", ""]
    total = sum(c["duracion"] for c in info["clips"])
    out.append("%d clips · %.0f s en total · formato %s" % (len(info["clips"]), total, info.get("formato", "?")))
    lg = info.get("logo")
    out.append("Logo: " + ("sí%s" % (" (oscuro: se usa copia blanca)" if lg and lg.get("oscuro") else "") if lg else "no se entregó"))
    out.append("")
    todos = []
    for c in info["clips"]:
        stem = Path(c["archivo"]).stem
        tramos = habla.get(stem, [])
        out.append("## %s · %.1f s%s" % (c["archivo"], c["duracion"], " · con audio" if c.get("tenia_audio") else " · sin audio"))
        out.append("Tira de cuadros: media/hoja_%s.jpg" % stem)
        if not c.get("tenia_audio"):
            out.append("Sin voz: plano visual (gancho, producto, cierre).")
        elif not tramos:
            out.append("Sin voz: solo ambiente." if stem in habla else "Sin tramos de voz medidos (corre habla.py).")
        else:
            out.append("")
            out.append("| Desde | Hasta | Texto | |")
            out.append("|---|---|---|---|")
            for t in tramos:
                nota = "ruido?" if t.get("dudoso") else ""
                out.append("| %.2f | %.2f | %s | %s |" % (t["desde"], t["hasta"], t["texto"].replace("|", "/"), nota))
                if not t.get("dudoso") and t["texto"]:
                    todos.append((stem, t))
        out.append("")

    # intentos repetidos: frases casi iguales (dentro del mismo clip o entre clips)
    repetidos = []
    for i in range(len(todos)):
        for j in range(i + 1, len(todos)):
            r = difflib.SequenceMatcher(None, norm(todos[i][1]["texto"]), norm(todos[j][1]["texto"])).ratio()
            if r >= 0.6:
                repetidos.append((todos[i], todos[j], r))
    out.append("## Posibles intentos repetidos")
    if not repetidos:
        out.append("Ninguno detectado.")
    for (c1, t1), (c2, t2), r in repetidos:
        out.append("- %s %.1f-%.1f s  ~  %s %.1f-%.1f s  (parecido %.0f %%): elige el mejor intento (completo, sin tropiezos, con el gesto correcto)"
                   % (c1, t1["desde"], t1["hasta"], c2, t2["desde"], t2["hasta"], r * 100))
    out.append("")
    out.append("## Para decidir con la persona")
    out.append("- Estructura que YA veo en el material (en qué orden se grabó, qué intentos hay, qué sobra).")
    out.append("- Estructura que PUEDO crear con lo que hay (y qué escenas faltan o no están confirmadas).")
    out.append("- Redes donde pautará, nivel, música, versión para historia y velocidad (según el ritmo de habla).")
    (base / "analisis.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    print("\nescrito en %s" % (base / "analisis.md"))


if __name__ == "__main__":
    main()
