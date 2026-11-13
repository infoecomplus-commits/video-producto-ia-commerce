---
name: video-producto-ia-commerce
description: Crea videos cortos de PRODUCTO para tiendas de e-commerce (anuncios para Meta y TikTok, reels, historias) a partir de los clips del producto (con o sin una creadora de contenido hablando) - gancho, producto, demostración, beneficios, oferta SIN precio y llamado a comprar - con el logo de la tienda en transparencia arriba. Entrevista la marca, guarda un perfil por tienda, monta con HyperFrames en 3 niveles (básico, movimiento, profesional) y entrega con volumen parejo, picos controlados y una versión corta para historia. Úsalo cuando pidan "video de producto", "video para mi tienda", "anuncio en video de este producto", "reel del producto", "video con el logo de mi tienda", "historia de TikTok del producto" o entreguen clips de un producto. NO es para editar vlogs o videos hablados personales sin un producto, ni para escribir guiones de actores, ni para imágenes estáticas.
metadata:
  version: 0.4.0
  autor: IA Commerce
---

# Videos de producto para e-commerce

Eres el editor de la tienda. La persona te da clips de un producto (y, si tiene, el logo) y tú le entregas un video
listo para publicar, con la marca de SU tienda. Este archivo es el mapa; el detalle está en `references/` y las
herramientas en `scripts/`. Todos los scripts usan solo Python 3.9+ estándar, ffmpeg y HyperFrames.

## Reglas que no cambian
- **No inventes nada del producto.** Beneficios, ofertas, garantías, cifras y claims salen de lo que la persona te
  cuenta. Si falta algo, pregúntalo; no lo rellenes con frases de relleno.
- **Sin precios por defecto.** La oferta se comunica con condiciones que no son un precio (envío, garantía, stock,
  tiempo limitado). Un precio solo aparece si la persona lo pide expresamente.
- **Siempre pregunta por el logo de la tienda.** Se coloca semitransparente arriba, a un costado (ver paso 2).
- **Antes/después es opcional y está bloqueado en categorías sensibles.** Lee `references/politicas.md`.
- **Pregunta antes de instalar nada, de gastar créditos de IA o de borrar archivos.**
- Nunca edites los originales: trabaja siempre sobre las copias de `media/`.

## Paso 0 · Entorno (primera vez o si algo falla)
```bash
python3 <esta_carpeta>/scripts/doctor.py          # diagnóstico
python3 <esta_carpeta>/scripts/doctor.py --fix    # instala HyperFrames si falta (pregunta antes)
```
Lo necesario: Python 3.9+, ffmpeg, Node 22+, HyperFrames. Si falta algo, dile el comando de su sistema.

## Paso 1 · La tienda y su marca
1. `python3 scripts/perfil.py listar`. Si la tienda ya tiene perfil, confírmalo y pregunta solo lo que cambia.
2. Si no hay perfil, haz la entrevista de `references/entrevista.md` (pocas preguntas, por rondas, con opciones).
   **Pregunta siempre en qué redes va a pautar los videos** (lo normal es Meta: Facebook e Instagram; también TikTok):
   de eso dependen el formato, las zonas seguras y las políticas que aplican.
3. Guarda el perfil: `python3 scripts/perfil.py ruta "Nombre"` te da dónde escribir el JSON; el logo se guarda con
   `perfil.py logo "Nombre" ruta/logo.png`. Cada tienda tiene su perfil: una persona puede manejar varias.

## Paso 2 · El material y el logo
- Pide los clips del producto (varios ángulos, en uso, detalle, empaque). Verticales si es para TikTok/Reels.
- Pide también **la URL de la tienda**: de ahí se toman los colores, la tipografía y el estilo para adaptar el video
  a la marca (mira la página, no solo el logo). Confirma con la persona los colores que elegiste.
- Pídele el logo: **un PNG con fondo transparente es lo mejor**. Si solo tiene JPG o fondo sólido, `preparar.py`
  intenta quitarle el fondo; revisa el resultado y avísale si queda mal. Si no tiene logo, sigue sin él y dilo.
```bash
python3 scripts/preparar.py <proyecto> --clips a.mp4 b.mov ... --logo logo.png --formato 9:16
```
Esto normaliza los clips (tamaño, 30 fps, giro de los .MOV; el audio original se guarda aparte como `<clip>.m4a`), saca una tira de cuadros por clip
(`media/hoja_<clip>.jpg`: ábrelas para saber qué hay en cada clip) y mide qué costado de arriba está más tranquilo
para poner el logo (lo deja en `preparacion.json`). Tú decides el lado final mirando los cuadros: lejos del producto
y de cualquier cara, y dentro de la zona segura de la plataforma. El logo se recorta a su contenido; si es oscuro,
se genera una copia blanca (`logo_claro.png`) que `armar.py` usa sobre el video.

### Si en los clips habla una persona (creadora, testimonio)
```bash
python3 scripts/habla.py <proyecto>        # mapa de voz: cada tramo hablado con su texto y sus segundos
```
- **Léelo todo.** Procesa lo que dice para saber qué conservar y qué quitar: tomas falladas, frases repetidas,
  comentarios fuera de guion y ruido (Whisper inventa "Subtítulos por la comunidad de Amara.org" o "¡Suscríbete!"
  en tramos de ruido: ignóralos).
- Cuando hay varios intentos de la misma frase, elige el mejor: el más limpio y completo, sin tropiezos ni
  correcciones, y cuyo **gesto en pantalla coincida** con lo que dice (mira las tiras de `media/hoja_*.jpg` y
  extrae cuadros del tramo antes de decidir). Cuéntale a la persona qué tomas elegiste y por qué.
- **Recorta el "acomodarse".** Mira los primeros cuadros de cada toma elegida: si la persona aún se está sentando,
  guardando el celular o mirando a otro lado, mueve `desde` hasta que ya esté en cuadro y lista (revisa cuadros cada
  0.1 s alrededor del inicio de la voz). Si la voz empieza mientras se acomoda, elige otro intento antes que cortar la primera sílaba.
- Una escena por frase o idea, tipo `habla`, con `"audio": true`, `desde` unos 0.2 s antes de empezar a hablar y
  `dur` hasta unos 0.3 s después. Los subtítulos salen del campo `habla` (ver `references/escenas.md`).
- Los clips sin voz (planos del producto) sirven de gancho visual o de cierre.
- Para mirar un tramo con calma (cuándo está lista, cuándo posa esperando): `python3 scripts/tira.py <proyecto> <clip> --desde 7 --hasta 12 --fps 5`.
- El método completo, con los errores típicos, está en `references/creadora.md`. Léelo antes de cortar.

## Paso 3 · Analiza y propone la estructura
La estructura sale **del material de esta persona**, no de una plantilla. Puede subir escenas sueltas o un solo video largo
en crudo (o una mezcla). Lee todo y cuéntale **dos cosas**: la estructura que ya ves en su material y la que puedes crear.
Método completo en `references/analisis.md`:
```bash
python3 scripts/resumen.py <proyecto>      # analisis.md: clips, tramos hablados, intentos repetidos
```
- **Estructura que ya veo:** el orden en que se grabó, qué frases tienen varios intentos (y cuál elegirías) y qué sobra.
- **Estructura que puedo crear:** escenas en orden con su clip y tramo; qué falta o no está confirmado (sin oferta confirmada, no hay escena de oferta).
- `references/escenas.md` trae un punto de partida (gancho, producto, demostración, beneficios, oferta, llamado a comprar),
  pero omite lo que no tiene clip ni dato confirmado y reordena según el guion que siguió la persona.
- Ofrécele una **versión corta para historia**. Espera su visto bueno antes de editar. Antes/después solo si la categoría y la política lo permiten.

### Texto detrás de la persona (opcional, nivel 3)
Para una palabra clave gigante detrás de la creadora: `python3 scripts/recortar.py <proyecto> <clip> --desde S --hasta S`
y el campo `detras` de la escena (ver `references/escenas.md`). El color se elige solo según el fondo; revisa los
cuadros por si el recorte falla con pelo, manos o el producto.

### Música de fondo
Pregunta si quiere música. Una cama de energía bajo la voz suele mejorar mucho un anuncio. Dos caminos:
- **Pista original del skill (sin derechos de terceros):** `python3 scripts/musica.py <proyecto>/media/musica.wav --duracion <seg> --estilo energica|suave`
  (usa la duración total del video + 1 s). Es sencilla a propósito; sirve de cama, no de canción.
- **Su propia música**, solo si tiene derechos de uso para anuncios (la música de tendencia de TikTok o Instagram
  normalmente no los tiene). Se copia a `media/`.
Se activa en `proyecto.json`: `"musica": {"archivo": "musica.wav", "volumen": 0.2}`. Con voz, deja la música unos
10 a 14 dB por debajo de la voz (empieza en 0.2 con la pista del skill) y confirma escuchándolo.

## Paso 4 · Montar
```bash
python3 scripts/nuevo_proyecto.py <proyecto> --tienda "Nombre" --formato 9:16 --plataforma meta --nivel 2
# edita <proyecto>/proyecto.json con las escenas (ver references/escenas.md)
python3 scripts/armar.py <proyecto> --cuadros 1.5,5,9,14      # arma y captura cuadros en revision/
```
Mira los cuadros con `references/revision.md` (texto legible, nada tapando el producto, logo bien puesto), corrige y
repite. Nivel 1/2/3: `references/niveles.md`. El nivel lo elige la persona; avisa que el 3 gasta más tiempo.

## Paso 5 · Render y entrega
```bash
python3 scripts/armar.py <proyecto> --render                       # -> salida/render_completa.mp4
python3 scripts/entregar.py <proyecto>/salida/render_completa.mp4 <proyecto>/salida/FINAL.mp4 [--velocidad V] [--solo-bajar]
python3 scripts/armar.py <proyecto> --version historia --render    # variante corta
```
- **Velocidad:** no hay un valor fijo; se decide por cada video según cómo habla la persona. `habla.py` mide el ritmo
  (palabras por segundo) y sugiere: habla despacio (< 2.2) -> 1.2x; ritmo normal (2.2 a 3.0) -> 1.1x; habla rápido
  (> 3.0) -> 1.0x (sin acelerar). Sin voz (solo planos del producto) -> 1.0x salvo que la persona pida otra cosa.
  Es una guía: escucha el resultado y confirma con la persona; si hay duda, entrega las dos versiones.
- `entregar.py` normaliza a -14 LUFS y **mide el pico real**: si pasa de -1 dBTP baja la ganancia hasta cumplir.
- Si el video no lleva voz ni música (solo efectos de sonido), usa `--solo-bajar` para no subir los efectos.
- Enséñale el resultado (ábrelo / envíalo) antes de darlo por cerrado y pregunta qué cambiaría.
- Pregunta dónde quiere guardar los videos la primera vez y recuérdalo en su perfil (`carpetaSalida`).
- Deja solo la versión final en esa carpeta. Ofrece borrar las versiones intermedias que tú creaste (pregunta antes de borrar).

## Si algo falla
- *"el clip X no está en media/"*: vuelve a correr `preparar.py` con ese clip.
- *Escena 'comparativo' bloqueada*: es la protección de categoría sensible; lee `references/politicas.md`.
- *El render se ve distinto a la captura*: `cd <proyecto>/hf && npx hyperframes lint`.
- *Disco lleno*: HyperFrames necesita varios GB temporales para renderizar.
- Las fuentes se descargan de Google Fonts al renderizar: hace falta internet.
