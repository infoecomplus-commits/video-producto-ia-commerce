# Videos de producto para e-commerce · IA Commerce

Skill para Claude Code que convierte los clips de un producto en un video listo para pautar en Meta
(Facebook e Instagram) o TikTok, con el logo de la tienda, en 3 niveles de acabado.

Flujo: **gancho → producto → demostración → beneficios → oferta (sin precio) → llamado a comprar.**

## Instalación
La forma fácil: abre **Claude Code** y pégale esto:

> Instala el siguiente skill https://github.com/infoecomplus-commits/video-producto-ia-commerce, revisa mi equipo con su diagnóstico (scripts/doctor.py) y hazme las preguntas para armar mi primer video de producto.

**Qué vas a ver (es normal):**
- Claude clona el repositorio y te pide permiso para correr el diagnóstico `scripts/doctor.py`. Acéptalo: solo lee tu equipo y no cambia nada.
- Claude Code no ejecuta por su cuenta código descargado de internet (por ejemplo `install.sh`). Si te lo dice, corre tú el diagnóstico en la terminal: `python3 ~/.claude/skills/video-producto-ia-commerce/scripts/doctor.py`.
- **Abre una sesión nueva de Claude Code** cuando termine la instalación: los skills se cargan al iniciar la sesión.

A mano:
1. Descarga o clona este repositorio en `~/.claude/skills/video-producto-ia-commerce` (en Windows: `%USERPROFILE%\.claude\skills\`).
2. Abre Claude Code y escribe: *"Haz un video de este producto"* y pásale tus clips.
3. La primera vez revisa el entorno solo; si falta algo te dice cómo instalarlo
   (Python 3.9+, ffmpeg, Node 22+ y HyperFrames).

## Qué hace
- Te pregunta por tu tienda, tu logo y **en qué redes vas a pautar**, y lo guarda en un perfil por tienda.
- Normaliza tus clips (también los .MOV del iPhone) y elige de qué lado poner tu logo en transparencia.
- Si hay una creadora hablando: transcribe lo que dice, elige el mejor intento de cada frase y recorta cuando se acomoda.
- Te ofrece música de fondo original (sin derechos de terceros) o usa la tuya.
- Monta las escenas con tu marca y te muestra cuadros de muestra antes de renderizar.
- Entrega con volumen parejo (-14 LUFS), picos controlados, velocidad opcional y versión corta para historia.

## Qué no hace
- No inventa beneficios, ofertas ni precios: usa solo lo que tú le cuentas.
- No es para editar vlogs o videos hablados personales sin un producto, ni para escribir guiones de actores.
- No decide por ti si un antes/después cumple las políticas de tu plataforma.

## Créditos
Creado por **Carlos Mora** para su comunidad en Skool **IA Commerce**.

Animación con [HyperFrames](https://github.com/heygen-com/hyperframes) y GSAP. Los efectos de sonido se generan
con ffmpeg; esta carpeta no incluye audios ni imágenes de terceros.

## Licencia
Todos los derechos reservados · IA Commerce. Ver `LICENSE`.
