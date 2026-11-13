# Escenas y estructura de proyecto.json

Un video de producto es una cadena de escenas; cada una usa un tramo de un clip y pone encima textos de la marca.
La duración total es la suma de las escenas (no hay voz que mande el tiempo). Ritmo orientativo: 15 a 30 s para
anuncio; una versión de historia de 10 a 15 s.

## Flujo recomendado
| # | Escena | Para qué | Duración |
|---|---|---|---|
| 1 | `gancho` | Detener el scroll en los primeros 2 o 3 s. Una promesa o pregunta ligada a lo que se ve | 2–3 s |
| 2 | `producto` | Mostrar qué es y cómo se llama | 3 s |
| 3 | `demo` | Verlo funcionando; un paso por escena | 3–4 s c/u |
| 4 | `comparativo` | Sin/con, solo si la categoría y la política lo permiten | 4 s |
| 5 | `beneficios` | 2 o 3 beneficios que la persona confirmó | 3–4 s |
| 6 | `oferta` | Condiciones de compra, **sin precio** salvo pedido | 3 s |
| 7 | `cta` | Qué hacer ahora, con el logo grande y un botón | 3–4 s |

## Campos comunes
- `tipo`: uno de los de arriba. `clip`: nombre del archivo en `media/` (lo dejó `preparar.py`).
- `desde`: segundo del clip donde empieza. `dur`: segundos que dura la escena.
- `historia`: `false` para omitir la escena en la versión corta. `dur_historia`: duración en la versión corta.
- `etiqueta`: texto suelto extra (opcional) en cualquier escena; `etiqueta_t`: `[desde, hasta]` en segundos del clip
  para que aparezca solo en ese momento.
- `audio`: `true` usa la voz/sonido original del clip (el `.m4a` que dejó `preparar.py`); `volumen` lo ajusta.
- `habla`: subtítulos de esa escena: lista de `{"texto": "...", "de": 12.6, "a": 15.3}` con tiempos del CLIP. El texto
  se parte en bloques de 3 palabras repartidos en el tramo; corrige la transcripción a mano (ortografía, signos).
- Marca con `*asteriscos*` la palabra que va en el color de acento: `"Llega tu *pedido*"`.

## Campos por tipo
- **gancho**: `texto`, `subtexto` (opcional). Máximo 5 o 6 palabras; el texto va en el tercio de arriba.
- **producto**: `texto` (nombre), `subtexto` (una línea).
- **demo**: `paso` (número), `texto` (qué se ve), `icono` (solo nivel 2+).
- **beneficios**: `texto` (título), `items`: hasta 4, cada uno `{"texto": "...", "icono": "check"}` o un texto simple.
- **oferta**: `texto`, `items` hasta 3 (condiciones no monetarias), `precio` (**solo si lo pidieron**).
- **cta**: `texto`, `boton` (texto del botón), `subtexto` (dónde/cómo comprar). Sin `clip`, usa el color de fondo.
- **habla**: clip con una persona hablando. Sin textos propios; lleva `audio`, `habla` y, si hace falta, `etiqueta`.
- **comparativo**: `clip` (antes/sin), `clip2` (después/con), `desde`, `desde2`, `etiqueta_a`, `etiqueta_b`,
  `categoria`. Está bloqueado en categorías sensibles salvo `"permitido": true` (ver `politicas.md`).

Iconos: por defecto son **emojis** (✅ ⭐ 🚚 🛡️ ⚡ ❤️ 📦 ⏰ ✨ 🎁), que conectan mejor en anuncios de Meta y TikTok.
Nombres: check, star, truck, shield, bolt, heart, box, clock, sparkle, gift. También puedes escribir un emoji directo
en `icono` (por ejemplo `"🔥"`). Para un look más sobrio (boutique, técnico) pon `"marca": {"iconos": "lineal"}`
y se usan íconos de trazo en el color de acento; con `"iconos": "ninguno"` no se muestran.
Ojo: el emoji se dibuja con la tipografía de emojis del equipo donde se renderiza (Apple en Mac, Segoe en Windows,
Noto Color Emoji en Linux), así que su aspecto cambia un poco de un equipo a otro.

## Nivel, marca y audio a nivel de proyecto
- `nivel`: 1, 2 o 3. `plataforma`: `meta` (Facebook e Instagram), `tiktok`, `reels`, `stories` o `feed`.
- `logo`: `{"archivo": "logo.png", "lado": "auto|izquierda|derecha", "opacidad": 0.7}`. `auto` usa el lado
  sugerido por `preparar.py`; decide tú mirando los cuadros.
- `musica`: `{"archivo": "ruta", "volumen": 0.12}` solo si tiene derechos de uso. `voz`: `{"archivo": "ruta"}`.
- `subtitulos`: lista opcional `{"texto": "...", "desde": 2.0, "hasta": 4.5}` en segundos del video final.
- `sonidos`: `false` para quitar los efectos.

## Cómo escribir los textos (por categoría)
- **Hogar, herramientas, tecnología**: muestra el problema resuelto en una acción. Beneficio = lo que se ve, no un adjetivo.
- **Moda, accesorios**: detalle, caída, uso en contexto; textos cortos y aspiracionales sin prometer resultados.
- **Mascotas, niños, juguetes**: seguridad y uso, solo con lo que el fabricante respalda.
- **Belleza, piel, salud, peso**: cuidado extremo con claims y con antes/después (`politicas.md`). Nada de promesas
  de resultado ni referencias al cuerpo o la condición de quien mira.
- Un mensaje por escena. Si el beneficio no se puede mostrar con un clip, probablemente no va en el video.
