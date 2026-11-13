# Cambios

## 0.4.0
- Paso de análisis: `resumen.py` y `references/analisis.md`. El skill lee el material (escenas sueltas o un video largo en crudo) y cuenta
  la estructura que ya ve y la que puede crear antes de editar; la plantilla de seis escenas pasa a ser solo un punto de partida.

## 0.3.0
- Texto gigante detrás de la persona (`recortar.py` + campo `detras`) con recorte de IA local (HyperFrames).
  El color se elige solo para que contraste con el fondo y se avisa si el color pedido casi no se lee.

## 0.2.0
- Clips con una persona hablando: el audio original se guarda aparte, escenas `habla` con subtítulos automáticos,
  `habla.py` (mapa de voz con texto y segundos, y ritmo de habla para decidir la velocidad), `tira.py` (tiras de cuadros).
- Guía `references/creadora.md`: cómo elegir el mejor intento, recortar el "acomodarse" y las pausas posando.
- Música de fondo original con `musica.py` (sin derechos de terceros) o la propia de la persona.
- Logo: recorte de márgenes, soporte de PNG con paleta y transparencia, copia blanca si el logo es oscuro.
- Plataforma `meta` (Facebook e Instagram) con zonas seguras propias; pregunta por las redes donde se pautará.
- Íconos en emoji (por defecto), lineales o ninguno; etiquetas con tiempo (`etiqueta_t`); corte seco (`transicion: false`).
- Velocidad según el ritmo de cada video; `entregar.py` mide el pico real y no entrega por encima de -1 dBTP.

## 0.1.0
- Primera versión: perfil por tienda, `preparar.py`, `armar.py` (3 niveles), `entregar.py`, efectos de sonido propios.
