# Referencia de altura — confirmado con Franco (26/09)

Pregunta pendiente desde hacía tiempo: ¿el altímetro que usan en el club
mide altura sobre el nivel del mar (QNH) o arranca en cero en cada
despegue? Respuesta de Franco: **siempre arranca en 0 en el despegue.**

## Qué significa esto para el modelo

No hace falta cambiar nada — es la convención que ya se venía usando sin
haberla confirmado explícitamente. En `decision_maccready.py` y
`zona_aterrizaje.py`, `altura_actual_m` nunca se compara contra una cota
absoluta (nivel del mar); solo se usa en términos relativos:

- `altura_perdida_en_transito()`: cuánta altura se pierde volando cierta
  distancia a cierta velocidad.
- `alcance_maximo_km()`: hasta dónde se llega planeando desde la altura
  actual.
- Los márgenes de seguridad (`margen_seguridad_m`, `margen_comodo_m`) son
  metros de colchón sobre el punto de llegada, no una cota absoluta.

Es decir: "altura" en el modelo ya significa "metros sobre el punto de
largada", que es exactamente lo que muestra el altímetro en cabina. Los
dos hablan el mismo idioma.

## Aproximación conocida (no corregida, despreciable en esta zona)

El margen de seguridad al llegar a una zona de aterrizaje candidata
(`zona_aterrizaje.py`) se calcula respecto a la altura de despegue en el
**club de Zárate**, no respecto al terreno específico de esa zona
candidata. Si el campo de destino está a una cota distinta del club, el
margen real sería un poco distinto al calculado.

En la pampa bonaerense (zona Zárate–San Andrés de Giles–Baradero) las
diferencias de cota entre puntos son de pocos metros — el error que esto
introduce es despreciable comparado con el margen de seguridad
(150m por defecto). No se justifica agregar corrección de elevación de
terreno por ahora.
