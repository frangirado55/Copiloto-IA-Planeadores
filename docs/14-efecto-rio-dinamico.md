# Efecto río Paraná dinámico (24/09)

Idea de Franco: en vez de asumir una franja fría fija cerca del río, calcular cuántos km tierra adentro se extiende según el viento real del día. Ver `11-teoria-completa-termicas.md` (brisa de río) y `04-zona-vuelo.md` (nota original sobre la franja fría) para el contexto previo.

## Física simplificada usada

- El Paraná está al norte de la zona de vuelo.
- **Viento desde el norte** (empuja el aire fresco del río hacia el interior) → la franja fría se extiende **más**.
- **Viento desde el sur** (empuja en contra de la brisa de río) → la franja se achica, queda pegada a la orilla.
- Perpendicular (este/oeste) → efecto neutro, valor base.

Fórmula: `penetracion_km = base_km + cos(rumbo_desde) * velocidad_kmh * escala`, con `base_km=3`, `escala=0.3 km por km/h`, acotado entre 1 y 15km. **Son coeficientes de arranque, no un modelo atmosférico validado** — mismo criterio que el resto del proyecto: heurística razonada, documentada como tal, a calibrar con datos reales cuando haya suficientes.

## Bug encontrado y corregido durante la implementación

La primera versión usaba **cualquier píxel con score de agua** como "el río" — pero eso incluye ~500 lagunas/charcos chicos sueltos por todo el campo (algunos de 1 solo píxel, ruido de la clasificación satelital), no solo el Paraná. Resultado: el 97% del mapa quedaba "afectado", sin sentido.

Se corrigió filtrando por **componentes conectados**: se etiquetan las manchas de agua contiguas (`scipy.ndimage.label`) y solo se usa el componente grande (el río/delta real, ~95% de todos los píxeles de agua en la zona — hay un salto enorme de tamaño entre ese componente y el siguiente más grande, que es ~1% de esa magnitud). Las lagunas sueltas quedan afuera del cálculo de "cerca del río", aunque siguen teniendo su propio score bajo individualmente (siguen siendo agua, solo que no generan su propia "brisa" a escala de kilómetros).

## Qué hace `scripts/efecto_rio.py`

1. Consulta el viento actual (reutiliza `obtener_viento_actual` de `mapa_utils.py`).
2. Calcula la penetración del día con la fórmula de arriba.
3. Identifica el río/delta principal (filtro de componente conectado grande).
4. Calcula la distancia de cada píxel al río (transformada de distancia, `scipy.ndimage.distance_transform_edt`).
5. Reduce el score de terreno cerca del río: más fuerte pegado a la orilla (×0.3), desvaneciéndose a sin efecto (×1.0) en el borde de la penetración calculada.

Probado con el viento real del 23/09 (19km/h desde 356°, casi derecho desde el norte — el peor caso, empuja con fuerza): dio 8.8km de penetración, visualmente coherente con la geografía real del delta (ver imagen enviada en el chat).

## Pendiente

- **No está conectado todavía al pipeline de decisión** (`copiloto.py`) — hoy es un módulo standalone que se puede correr aparte. Integrarlo significa que cada consulta de `recomendar()` tendría que recalcular esto (nueva consulta de viento + transformada de distancia), lo cual es viable pero se dejó para una próxima iteración en vez de meterlo apurado.
- Los coeficientes (`PENETRACION_BASE_KM`, `ESCALA_KM_POR_KMH`) no están calibrados con datos reales — son un punto de partida razonado, no medido.
