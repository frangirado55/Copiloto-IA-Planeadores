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
4. Si se llega con margen: **virar** solo si la candidata es significativamente mejor que la actual (umbral configurable, arranca en +15%) — si son parecidas, no vale la pena el riesgo/tiempo de la transición.

## Qué falta para que sea preciso (no bloqueante para probar la lógica)

- **La polar real** del planeador de referencia (de la escuela o de papá) — hoy usa valores aproximados de un planeador de entrenamiento genérico (tipo ASK-21), marcados explícitamente como placeholder en el código.
- **Calibrar el umbral de "significativamente mejor"** (hoy 15%) y el margen de seguridad de altura (hoy 150m) con datos reales de vuelo — tarea de la Fase 4/5 del plan.

## Integración con el resto

- Con el Módulo 1-B (terreno) ya armado, la "fuerza candidata" se puede aproximar con el score de potencial térmico de la zona hacia donde se mira (más alto el score, mayor la fuerza asumida) — pendiente de definir la conversión score→m/s estimados, hoy son fuentes separadas.
- Con datos de vuelo reales (Fase 4), se recalibra tanto el umbral de decisión como esa conversión score→fuerza.
