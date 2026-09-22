# Comparación con WeGlide Copilot (y apps similares)

## Qué ya hace WeGlide Copilot

- **Térmicas activas en tiempo real vía OGN**: cuando un planeador empieza a girar, se ve en el mapa con altura, fuerza y hace cuánto está activa. Se regenera cada ~2 minutos usando los últimos 60 minutos de datos.
- **Mapas de "hotspots"**: probabilidad de térmica por hora del día y dirección del viento, basados en el análisis histórico de más de 10 millones de térmicas registradas. Es estadística acumulada, no predicción en tiempo real.
- **Llegada final (final glide)**: altura de llegada, L/D, control MacCready — fórmula estándar de aviación a vela.
- **Carga de waypoints/tareas** del día.
- **Logger de vuelo** válido para competencias nacionales.
- **Imágenes satelitales** de alta frecuencia (cada 5-10 min) con radar de lluvia.

## Dónde está el hueco (el diferencial real)

- **Todo lo de WeGlide es reactivo o histórico** — te muestra dónde HAY o SUELE haber térmica, pero no decide nada por el piloto. El piloto sigue mirando el mapa y decidiendo a ojo.
- **Nadie hace la capa de decisión activa**: "quedate acá 40 segundos más y después andá 800m al norte, ahí vas a encontrar algo mejor" — comparando matemáticamente ambas opciones (MacCready + polar) en vez de solo mostrar datos.
- **Nadie combina esto con análisis de terreno propio** para zonas sin buena cobertura OGN (relevante en Argentina).

## Por qué no conviene "competir de frente"

WeGlide tiene equipo, financiamiento, años de desarrollo y 10 millones de térmicas analizadas. Replicar su mapa reactivo o sus hotspots desde cero, para dos personas en los fines de semana, es tiempo perdido — no hay forma de alcanzar ese volumen de datos ni esa infraestructura en el corto plazo.

## Veredicto

El proyecto vale la pena **solo si se mantiene enfocado en el Módulo 3** (decisión activa) como pieza central, usando los mismos datos de red que ya existen (en vez de reconstruir el mapa) y complementando con terreno donde la red falla. Si el proyecto deriva hacia "hacer otro WeGlide completo", es plata y tiempo perdidos — no hay ventaja competitiva ahí.
