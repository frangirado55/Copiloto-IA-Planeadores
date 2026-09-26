# Cambio de planeador: ASK-13 en vez de Blanik L-13 (26/09)

Franco confirmó que van a usar el **Schleicher ASK-13** para el curso.
Se cambió la polar por defecto del modelo, que hasta ahora usaba el
LET L-13 Blanik.

## Qué se cambió

- `scripts/decision_maccready.py`: se agregó `POLAR_ASK13` (mismo método
  de 2 puntos críticos que ya se usaba para el Blanik, para no inventar
  un tercer punto). `POLAR_BLANIK_L13` se deja definida, no se borró —
  por si en algún momento se necesita comparar o se sigue volando ese
  planeador también.
- `decidir()` (en `decision_maccready.py`), `recomendar()` (en
  `copiloto.py`) y `buscar_zona_aterrizaje()` (en `zona_aterrizaje.py`):
  el parámetro `polar` por defecto pasó de `POLAR_BLANIK_L13` a
  `POLAR_ASK13`.

## Origen del dato — sin verificar todavía

A diferencia del Blanik (cuyos 2 puntos vienen de Wikipedia, confirmados
en su momento), los datos del ASK-13 salieron de una búsqueda web —
**no se pudo leer la fuente original directamente** porque el sandbox
bloquea el acceso a Wikipedia (misma política que ya afectó la consulta
de SkySight). Los valores usados:

- Mejor planeo: 27:1 a 85 km/h
- Mínimo hundimiento: 0.80 m/s a 68 km/h

Son razonables (el ASK-13 es un poco menos eficiente que el Blanik, lo
cual tiene sentido: es un diseño más viejo y más pesado en relación),
pero quedan marcados como **pendientes de confirmar contra el manual de
vuelo oficial** — está en la lista de cosas para preguntar/buscar en el
club.

## Pendiente

Si Franco consigue el manual de vuelo del ASK-13 en el club (o el club
tiene otra fuente confiable), reemplazar estos 2 valores por los reales,
y considerar buscar el tercer punto de la polar (alta velocidad) si está
publicado, para pasar de `desde_puntos_criticos()` a `desde_tres_puntos()`
con más precisión.
