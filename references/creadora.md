# Caso: videos con una creadora de contenido hablando

Pasa mucho: la tienda contrata a una creadora que graba varias tomas sueltas del mismo guion, con varios intentos de
cada frase. Tu trabajo es armar UN video bueno con lo mejor de cada intento. Este es el método que funciona.

## 1. Entender el material
1. `preparar.py` con todos los clips y el logo (guarda también el audio de cada clip).
2. `habla.py`: mapa de voz con el texto y los segundos de cada tramo. Léelo completo.
3. Mira las tiras de `media/hoja_*.jpg` para saber qué hace en cada clip (muestra el producto, camina, se sienta).
4. Ordena el guion que ella siguió (gancho -> problema -> producto -> demo -> cierre). Suele salir del orden de los clips.

## 2. Elegir el mejor intento de cada frase
Un intento es mejor cuando:
- Está completo y sin tropiezos (sin muletillas, sin corregirse a media frase).
- Dice exactamente lo que el producto puede prometer (si en un intento se equivoca de dato, descártalo).
- Su gesto coincide con lo que dice (enseña el producto cuando lo nombra).
- Se ve y se oye natural: energía, sonrisa, sin mirar a otro lado.
Descarta: frases sueltas fuera de guion, comentarios a cámara, y el "ruido" que Whisper transcribe como
"Subtítulos por la comunidad de Amara.org" o "¡Suscríbete!". Cuéntale a la persona qué intentos elegiste y por qué.

## 3. Cortar con cuidado
- **El inicio:** la voz suele empezar mientras la persona aún se acomoda. Usa `tira.py` con `--fps 10` alrededor del
  inicio de la voz y mueve `desde` hasta que esté en cuadro y lista. Deja unos 0.15 a 0.2 s antes de la primera sílaba.
  Si la voz arranca mientras se sienta, mejor otro intento que cortar la primera sílaba.
- **Las pausas posando:** tras una acción (colgar algo, mostrar algo) suelen quedarse quietas esperando para hablar.
  Parte la escena en dos con corte seco (`"transicion": false`): primero la acción, después la voz.
- **El final:** corta 0.3 s después de la última palabra, antes de que baje los brazos o respire hondo.
- **Una escena = una frase o una idea.** Si dos frases vienen de intentos distintos, son dos escenas.

## 4. Montar
- Escenas tipo `habla` con `"audio": true`, `desde`/`dur` y `habla` con los segundos del clip para los subtítulos.
- Etiquetas (`etiqueta` + `etiqueta_t`) solo para datos que ella dice: colores, medidas, "solo 2 clavos".
  No agregues datos que no dijo.
- Cierre con un plano del producto sin voz + logo grande + botón (el texto del botón debe coincidir con lo que ella
  pide hacer, por ejemplo "presiona obtener oferta" -> botón "Obtener oferta").
- Música: bajo la voz (empieza en 0.2 con `musica.py`) y revisa que no la tape.

## 5. Velocidad
Mide el ritmo con `habla.py` (palabras por segundo): despacio -> 1.2x, normal -> 1.1x, rápido -> 1.0x. Es una guía;
escucha el resultado.

## 6. Antes de entregar
- Revisa cuadros del inicio y el final de cada escena con voz (checklist de `revision.md`).
- Confirma que el audio final quedó a -14 LUFS con el pico dentro del techo (`entregar.py` lo mide).
- Guarda solo la versión final en la carpeta que la persona indicó; borra las intermedias.
