# Analizar el material y proponer la estructura

La estructura del video NO es una plantilla: sale del material que sube cada persona. Antes de editar nada, lees todo y
le cuentas a la persona **dos cosas**. Después espera su visto bueno.

## 1. Lee todo
1. `preparar.py` con todos los clips y el logo.
2. `habla.py` si hay voz.
3. `resumen.py` -> `analisis.md`: tabla por clip con duración, tramos hablados con su texto y segundos, y los posibles intentos repetidos.
4. Mira las tiras `media/hoja_*.jpg` (y `tira.py` donde haga falta): qué se ve, qué hace la persona, cuándo se acomoda.

## 2. Reconoce con qué caso estás
- **Escenas sueltas** (varios clips cortos): cada clip suele ser una idea o un intento. Hay que ordenarlos y elegir el mejor intento.
- **Un video largo en crudo** (un solo clip con todo): ya trae una estructura grabada de corrido, con errores, repetidos y pausas.
  Hay que detectar sus partes y hacer los cortes.
- **Mezcla:** un largo más planos sueltos del producto. Es lo más común.

## 3. Cuéntale a la persona (en este formato, corto)
**Estructura que ya veo en tu material**
- El orden en que se grabó (por ejemplo: gancho 0:00-0:03 -> problema 0:12-0:17 -> producto 0:11-0:19 -> demo -> cierre),
  qué frases tienen varios intentos y cuál elegiría, y qué sobra (comentarios fuera de guion, errores, pausas).

**Estructura que puedo crear**
- La propuesta de escenas, en orden, con el clip y el tramo de cada una y lo que dice. Qué escenas faltan o no están
  confirmadas (por ejemplo: "no hay oferta confirmada, no hago escena de oferta") y qué clip habría que grabar si quiere sumarlas.
- Duración total estimada y si conviene una versión corta para historia.

Después pregunta: redes donde pautará, nivel, música y velocidad (según el ritmo de habla).

## 4. Con un solo video largo en crudo
Es el mismo método: `habla.py` da el mapa de voz de TODO el clip; `tira.py` muestra los tramos dudosos; cada parte buena se
convierte en una escena con `desde`/`dur` del mismo clip (puedes usar el mismo clip en varias escenas). Las pausas
y errores simplemente no entran. Si dos partes consecutivas salen del mismo clip y saltas una pausa, usa corte seco
(`"transicion": false`).

## 5. Reglas
- No rellenes huecos con textos o datos que la persona no dijo o confirmó.
- Si hay duda entre dos estructuras, ofrécelas las dos en una línea cada una.
- No empieces a editar hasta tener su visto bueno.
