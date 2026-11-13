# Revisión antes de enseñar nada

Captura cuadros con `armar.py <proyecto> --cuadros 1.5,5,9,14` (un cuadro por escena, ~1 s después de que empiece,
cuando ya entraron los textos) y abre `revision/<version>/contact-sheet.jpg`. Juzga lo que ves, no lo que querías hacer.

## Checklist por cuadro
- [ ] El texto se lee en un celular, también sobre fondos claros (los contornos y sombras ya ayudan; si no basta,
      acorta el texto o cambia el tramo del clip).
- [ ] Nada importante tapa el producto. Los textos van arriba o abajo del producto, no encima.
- [ ] El logo se ve, no estorba y está dentro de la zona segura. No choca con una cara ni con el producto.
- [ ] En Meta, nada clave queda en el 14 % de arriba ni en el 35 % de abajo.
- [ ] Un mensaje por escena; no hay más de 3 elementos de texto a la vez.
- [ ] Las palabras en color de acento son las que importan, no decoración.
- [ ] Los primeros 0.5 s de cada toma con voz: nadie acomodándose, sentándose o buscando la cámara.
- [ ] Si hay música, se oye bajo la voz y nunca la tapa.
- [ ] El cierre muestra el logo grande, el llamado y el botón completos.
- [ ] Ningún texto promete algo que la persona no confirmó. Ningún precio salvo pedido.

## Qué hacer con los defectos
Anota los 3 peores con su segundo, corrígelos en `proyecto.json` y vuelve a capturar. Máximo 2 vueltas antes de
enseñarle el resultado; después ajustas con lo que ella o él diga.

## Después del render
Mira el video terminado (o una hoja de cuadros) antes de entregarlo, confirma duración y que `entregar.py` reportó
el pico dentro del techo, y pregunta qué cambiaría.
