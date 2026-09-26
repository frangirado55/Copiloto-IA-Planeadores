# Cambio de planeador: ASK-13 reemplaza al Blanik L-13 (26/09)

Franco confirmó que el club **no tiene Blanik y no lo va a usar** — el
planeador real del curso es el **Schleicher ASK-13**. Se reemplazó la
polar del modelo, que hasta ahora usaba el LET L-13 Blanik (dato que
nunca se pudo verificar contra un planeador real del club, solo contra
Wikipedia).

## Qué se cambió

- `scripts/decision_maccready.py`: `POLAR_BLANIK_L13` se borró (no se
  va a usar nunca, no tiene sentido mantenerla). Se agregó `POLAR_ASK13`
  con el mismo método de 2 puntos críticos (vértice + mejor planeo, sin
  inventar un tercer dato).
- `decidir()` (en `decision_maccready.py`), `recomendar()` (en
  `copiloto.py`) y `buscar_zona_aterrizaje()` (en `zona_aterrizaje.py`):
  el parámetro `polar` por defecto ahora es `POLAR_ASK13`.

## Origen del dato — sin verificar todavía

A diferencia del Blanik (cuyos 2 puntos venían de Wikipedia, al menos
confirmados en su momento), los datos del ASK-13 salieron de una
búsqueda web — **no se pudo leer la fuente original directamente**
porque el sandbox bloquea el acceso a Wikipedia (misma política que ya
afectó la consulta de SkySight). Los valores usados:

- Mejor planeo: 27:1 a 85 km/h
- Mínimo hundimiento: 0.80 m/s a 68 km/h

Quedan marcados como **pendientes de confirmar contra el manual de
vuelo oficial** — está en la lista de cosas para preguntar/buscar en el
club.

## Pendiente

Si Franco consigue el manual de vuelo del ASK-13 en el club (o el club
tiene otra fuente confiable), reemplazar estos 2 valores por los reales,
y considerar buscar el tercer punto de la polar (alta velocidad) si está
publicado, para pasar de `desde_puntos_criticos()` a `desde_tres_puntos()`
con más precisión.
