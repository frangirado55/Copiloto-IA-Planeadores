# Diseño técnico — Módulo 3: IA de decisión (MacCready)

Ver `01-modulos.md` para el resumen funcional. Acá el detalle de cómo se calcula la recomendación.

## Qué resuelve

Dada la térmica que estás centrando ahora y una térmica candidata detectada más adelante (por el Módulo 1, o metida a mano en esta primera versión), decide **quedarse** o **virar** — y si conviene virar, a qué velocidad volar.

## Teoría (MacCready, sin reinventar nada)

1. **Polar del planeador**: curva de hundimiento (m/s) en función de la velocidad de vuelo (km/h). Se aproxima con una parábola ajustada a 3 puntos de calibración conocidos (velocidad de mínimo hundimiento, velocidad de mejor planeo, un tercer punto a mayor velocidad).
2. **Velocidad óptima de crucero (speed-to-fly)**: dado un "MacCready setting" (la fuerza esperada de la próxima térmica), la velocidad óptima es la que maximiza la velocidad media de recorrido, contando el tiempo de vuelo entre térmicas *más* el tiempo que hay que volver a subir en la próxima térmica para recuperar la altura perdida en el tramo. Se calcula numéricamente (barrido de velocidades, sin necesidad de resolver la derivada a mano).
3. **Regla de decisión** (la práctica estándar en vuelo a vela): conviene dejar una térmica cuando su tasa de subida cae por debajo del MacCready setting vigente. Acá el MacCready setting se aproxima con la fuerza de la térmica candidata.

## Lógica implementada (MVP)

Con: fuerza térmica actual, fuerza candidata, distancia a la candidata, altura actual, polar:

1. Calcular la velocidad óptima de crucero V\* usando como MacCready setting la fuerza de la candidata.
2. Calcular la altura que se pierde volando a V\* hasta la candidata (hundimiento a esa velocidad × tiempo de vuelo).
3. **Si la altura actual menos esa pérdida no deja margen de seguridad** → **quedarse**, sin importar qué tan buena sea la candidata (no se llega con seguridad).
4. Si se llega con margen mínimo pero no cómodo, y la candidata es significativamente mejor → **quedarse un poco más y después virar** (ver abajo).
5. Si se llega con margen cómodo y la candidata es significativamente mejor (umbral configurable, arranca en +15%) → **virar ahora**.
6. Si la candidata no mejora lo suficiente → **quedarse** (no vale la pena el riesgo/tiempo de la transición).

## Tercer estado: "quedarse un poco más y después virar" (22/09)

Pedido de Franco con un caso concreto: térmica actual 2.5 m/s, candidata 3.5 m/s — vale la pena virar, pero si el margen de altura al llegar es *justo* (por encima del mínimo de seguridad, pero no cómodo), ¿no conviene seguir centrando un poco más la térmica actual (aunque sea más floja) para juntar colchón de altura antes de partir, en vez de salir justo al límite?

Sí, y es una práctica real de vuelo a vela (no es solo intuición): salir con el margen mínimo exacto no deja lugar para imprevistos (un cambio de viento, una térmica que resultó más floja de lo estimado). La lógica:

- Se define un `margen_comodo_m` (por defecto, el doble del margen de seguridad — 300m si el mínimo es 150m).
- Si la altura de llegada estimada cae **entre** el margen mínimo y el margen cómodo, y la candidata es mejor: en vez de "virar ya", se calcula cuánta altura extra hace falta para llegar al margen cómodo, y cuántos minutos tomaría ganarla centrando la térmica actual a su fuerza real (más floja, pero es la que hay ahora).
- La recomendación pasa a ser: **"quedate ~X minutos más acá, después virá"** — con el número de minutos calculado, no una regla fija tipo "esperá 1 minuto".

Ejemplo (Escenario 4 en `scripts/decision_maccready.py`): actual 2.5 m/s, candidata 3.5 m/s, 550m de altura, candidata a 6km → llegarías con 267m (117m sobre el mínimo, no cómodo) → recomienda seguir centrando ~0.8 min más (ganando ~33m) antes de virar.

En el mapa de decisión (`mapa_decision.py`) este estado se ve como una línea punteada naranja (a diferencia del verde sólido de "virar ya" y el gris de "quedarse").

## Qué falta para que sea preciso (no bloqueante para probar la lógica)

- **La polar real** del planeador de referencia (de la escuela o de papá) — hoy usa valores aproximados de un planeador de entrenamiento genérico (tipo ASK-21), marcados explícitamente como placeholder en el código.
- **Calibrar el umbral de "significativamente mejor"** (hoy 15%) y el margen de seguridad de altura (hoy 150m) con datos reales de vuelo — tarea de la Fase 4/5 del plan.

## Integración con el Módulo 1-B (ya implementada)

`scripts/copiloto.py` conecta ambos módulos en un solo pipeline:

1. Dada la posición actual (lat/lon) y un radio de búsqueda, lee el `score_termico.tif` generado por `analizar_terreno.py` y busca las zonas con mejor score dentro de ese radio (excluyendo un radio chico alrededor del punto actual, para no proponer la térmica en la que ya se está).
2. Convierte el score (0-100) a una fuerza estimada en m/s con una heurística lineal simple: score 0 → 0.5 m/s, score 100 → 4.0 m/s. Sin calibrar con vuelos reales todavía — es el primer punto a ajustar con datos de la Fase 4.
3. Le pasa esa fuerza estimada y la distancia real (fórmula haversine) al `decidir()` del Módulo 3.

Con esto, dado solo posición + altura + fuerza de la térmica actual, el sistema devuelve directamente "quedate" o "virá hacia [zona]" sin que haya que pasarle a mano los datos de la candidata.

## Qué falta calibrar (Fase 4/5, no bloqueante)

- La conversión score→fuerza (hoy lineal 0.5-4.0 m/s) es una suposición de arranque.
- El umbral de "significativamente mejor" (15%) y el margen de seguridad de altura (150m).
- La polar real del Blanik más allá de los 2 puntos públicos verificados (falta un tercer punto a alta velocidad, idealmente del manual de vuelo).
