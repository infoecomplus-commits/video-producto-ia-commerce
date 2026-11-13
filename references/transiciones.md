# Transiciones

El motor trae **15 transiciones** (más el corte seco). Sirven para disimular el corte entre escenas y darle ritmo; no para decorar.
Por defecto el nivel 1 usa corte seco y los niveles 2 y 3 eligen transiciones **variadas** (nunca la misma dos veces seguidas).

## Cómo se piden
- En una escena: `"transicion": "whip"` (la transición que ENTRA en esa escena). `false` o `"corte"` = corte seco. `"auto"` o nada = elige el motor.
- En el proyecto: `"transiciones": {"estilo": "suaves"}` o una lista propia `"transiciones": ["whip", "flash", "zoom"]` que se recorre en orden.
- Estilos: `variadas` (por defecto; en nivel 3 usa un grupo más amplio), `suaves`, `energicas`, `marca`.
- **Salto de una frase a otra de la misma persona (mismo clip): corte seco automático** (jump cut). Se puede forzar otra con `"transicion": "zoom"`.

## Catálogo
| Nombre | Cómo se ve | Úsala para | Estilo |
|---|---|---|---|
| `corte` | Corte seco | Frases de la misma persona, ritmo rápido | todos |
| `cortina` | Franja de color de la marca cruza de izquierda a derecha | Cambio de sección claro | variadas, suaves, marca |
| `cortina_vertical` | La franja cruza de arriba abajo | Variante de la anterior | variadas |
| `cortina_logo` | Cortina con el logo de la tienda al centro | Marca presente (inicio, cierre, cambio de bloque). No abusar | marca, variadas (nivel 3) |
| `flash` | Destello blanco muy corto | Golpe de ritmo, revelar el producto | variadas, energicas |
| `dip` | Fundido a color de marca | Pausa suave, cambio de tema | variadas, suaves |
| `zoom` | Zoom de golpe hacia dentro y se asienta | Producto, detalle, énfasis | variadas, energicas |
| `giro` | Zoom con giro leve | Energía, productos juveniles | energicas |
| `whip` | Latigazo lateral con desenfoque | Cambio rápido de lugar o plano | energicas |
| `empuje` | La cámara empuja hacia un lado | Pasar al siguiente paso o ángulo | variadas, suaves |
| `tembleque` | Sacudida corta de cámara | Impacto, golpe de énfasis | energicas |
| `glitch` | Sacudida con barras de color de la marca | Gancho, tecnología, hooks fuertes | energicas |
| `iris` | Un círculo de color cubre y se retira | Revelar, cierre | variadas, suaves, marca |
| `persianas` | Seis barras verticales de color | Cambio de bloque con estilo | variadas, marca |
| `destello` | Fuga de luz cálida | Ambiente cálido, hogar, moda, momentos "wow" | suaves, marca |
| `desenfoque` | La imagen se desenfoca y se aclara | Transición elegante, cambio de tiempo | suaves |

Las transiciones de cámara (`zoom`, `giro`, `whip`, `empuje`, `tembleque`, `glitch`, `desenfoque`) mueven toda la imagen pero NO el logo
de la tienda, que se queda quieto. Las de color usan los colores de la marca del perfil.

## Criterio
- Una transición fuerte (whip, glitch, tembleque, giro) cada tres o cuatro cortes como máximo; entre frases de una creadora, corte seco.
- Marcas sobrias (boutique, técnico): `suaves` o `marca`. Marcas juveniles o de tecnología: `energicas`.
- Si la persona dice "muy simples" o "siempre la misma": sube a nivel 3 o cambia el estilo; no pongas más de lo que el ritmo aguanta.
- Revisa siempre cuadros justo antes y después del corte (`armar.py --cuadros t-0.07,t+0.09`).

## Tendencias anotadas (13 de noviembre de 2026)
Fuentes: guías de CapCut, plataformas de edición y blogs de marketing. Casi todas son contenido de proveedores y no miden
rendimiento en anuncios pagados: tómalo como panorama, no como ranking. Valida con tus propias pruebas A/B.
- **Speed ramps** (cambios de velocidad sincronizados con la música): de las más citadas de 2026. *Pendiente de implementar.*
- **Whip pans**: latigazo con desenfoque; clave mantener la dirección. *Implementada (`whip`, `empuje`).*
- **Glitch**: sigue en tendencia en ediciones de energía y ganchos. *Implementada (`glitch`).*
- **Light leaks / film burn**: destellos cálidos, ambiente retro o de viaje. *Implementada (`destello`).*
- **Zoom continuo ("seamless zoom")**: popular en producto y revelados. *Implementada (`zoom`); la versión continua con el mismo objeto está pendiente.*
- **Mask reveal**: barrido con máscara de 3 a 5 cuadros para revelar el producto. *Pendiente (hoy: `cortina`, `iris`, `persianas`).*
- **Match cut**: cortar entre dos tomas con la misma forma, color o movimiento. *Pendiente: requiere elegir tomas con ese parecido.*
- **Corte seco / jump cut**: lo que mejor funciona cuando importa la velocidad y la claridad, sobre todo en ganchos y creadoras. *Implementado.*
- Aviso de las propias fuentes: las tendencias envejecen rápido y una transición no arregla material débil.

Fuentes consultadas:
- https://www.capcut.com/help/capcut-transitions
- https://www.capcut.com/create/video-transition-trends-viral-short-form-edits
- https://sendshort.ai/guides/transitions-tiktok-reels-shorts/
- https://wayin.ai/blog/tiktok-transitions/
- https://domer.io/blog/trending-transitions-tiktok-instagram-reels
- https://www.aicut.pro/blog/cool-video-transitions
- https://pippit.capcut.com/resource/the-best-transition-effects-for-instagram-reels-and-ads
- https://www.3l3c.ai/blog/mastering-branded-content-editing-tips-tools-trends/mobile-editing-trends

## Para sumar una transición nueva
En `scripts/armar.py`: agrega su nombre y descripción a `TRANSICIONES`, ponla en los `POOLS_TRANSICION` que correspondan y dibújala en
`transicion()`: las de cámara animan `#stage`; las de color usan `cubrir()` (capas fuera de la cámara). Pruébala con un proyecto
de una escena corta por transición y revisa cuadros antes y después del corte. Anótala aquí.
