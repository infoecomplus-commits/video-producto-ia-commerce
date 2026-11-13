# Entrevista de marca (una vez por tienda)

Objetivo: que cada tienda tenga su propio look y que no tengas que volver a preguntarlo. Hazla en 2 o 3 rondas cortas,
con opciones concretas y siempre una salida de "otra / lo defino yo". Si la persona tiene prisa, basta con: tienda,
logo, plataforma y un estilo; el resto toma valores por defecto.

## Ronda 1 · La tienda
1. **Nombre de la tienda** (así se guarda el perfil) y **la URL de su tienda online**. Con la URL abre la página,
   mira sus colores, tipografía y estilo (botones, barra de anuncios, fotos) y adapta el video a esa marca; después
   confirma con la persona los colores elegidos. Si la URL y el logo no coinciden, pregunta cuál manda.
2. **Logo.** Siempre pregúntalo. Explica para qué: va semitransparente arriba, a un costado, durante todo el video, y
   grande en el cierre. Lo ideal es un PNG con fondo transparente. Si no lo tiene, sigue sin logo.
3. **¿En qué redes va a pautar estos videos?** Pregúntalo siempre; cambia el formato, las zonas seguras y las
   políticas que aplican. Lo más común es **Meta (Facebook e Instagram)**, en Reels, Stories y feed; también TikTok.
   - Meta en Reels/Stories -> `"plataforma": "meta"` (9:16). Meta tapa ~14 % arriba y ~35 % abajo con su interfaz,
     así que el contenido se concentra al centro; el motor ya ajusta el diseño.
   - Si además pauta en el feed de Meta, ofrece una versión 4:5 (`--formato 4:5` en `preparar.py` y en el proyecto).
   - TikTok -> `"plataforma": "tiktok"`. Si pauta en ambas, haz una versión por plataforma.
4. **Categoría del producto** (hogar, tecnología, moda, mascotas, juguetes, belleza/piel/salud/peso, otra).
   Sirve para decidir qué escenas se pueden usar (ver `politicas.md`).

## Ronda 2 · La marca
5. **¿Tiene colores de marca?** Si sí, pide los hex (o saca los colores del logo). Si no, enséñale los estilos base de
   `estilos.json` (neón urbano, boutique, pop naranja, técnico, natural) y deja que elija o los ajuste.
6. **Sensación:** energética, tranquila y elegante, cinematográfica, técnica. Mapea a `movimiento`:
   energico / suave / cinematico.
7. **Tipografías:** las del estilo elegido, o las suyas si existen en Google Fonts.
   **Íconos:** emojis (por defecto, más cercanos y coloridos) o íconos lineales (más sobrios) o ninguno. Se guarda en
   `marca.iconos` como `emoji`, `lineal` o `ninguno`.

## Ronda 3 · El producto de este video (se pregunta cada vez)
8. **¿Qué producto es** y quién lo compra? Una frase.
9. **¿Qué lo hace útil?** Pide 2 o 3 beneficios en sus palabras. No los inventes ni los infles.
10. **¿Qué oferta o condiciones hay?** Envío, garantía, stock, tiempo limitado. Sin precio salvo que lo pida.
11. **Llamado a comprar:** qué debe hacer la persona (tocar el botón, link en la bio, escribir por WhatsApp) y el texto
    del botón.
12. **Clips disponibles** y si tiene voz en off.
13. **Música de fondo:** ¿quiere música? Ofrece la pista original del skill (`musica.py`, energética o suave) o que use
    la suya si tiene derechos de uso para anuncios.

## El perfil que se guarda
`python3 scripts/perfil.py ruta "Nombre"` devuelve la ruta; escribe ahí:
```json
{
  "tienda": "Nombre",
  "url": "https://...",
  "marca": {
    "estilo": "neon-urbano",
    "colores": {"fondo": "#0B0B14", "texto": "#FFFFFF", "acento": "#00E5FF", "apoyo": "#FF4D8D"},
    "fuentes": {"titulos": "Syne", "pesoTitulos": 800, "texto": "Manrope", "pesoTexto": 700},
    "movimiento": "energico",
    "iconos": "emoji"
  },
  "redesPauta": ["meta"],
  "plataformaHabitual": "meta",
  "categoria": "hogar",
  "carpetaSalida": "",
  "velocidad": 1.0,
  "notas": "Lo que le gusta y lo que no, en sus palabras."
}
```
- `colores` y `fuentes` pisan al estilo base solo en lo que se indique.
- `notas` es la memoria de la tienda: cada vez que diga "esto no me gusta / esto sí", anótalo.
- El logo se guarda aparte con `perfil.py logo`.
