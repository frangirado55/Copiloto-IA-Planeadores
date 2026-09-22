# Plan de trabajo por fases

## Fase 1 — MVP de decisión, chico y específico

No construir un mapa nuevo. Arrancar con una "calculadora de decisión" simple:
- Input manual o semi-automático: fuerza/altura de la térmica actual, y datos de térmicas candidatas (al principio, incluso metidos a mano desde lo que se ve en WeGlide u otra app).
- Lógica: teoría MacCready + polar del planeador propio → recomendación de quedarse o virar.
- Objetivo: validar si la recomendación matemática tiene sentido y es útil en vuelo real, sin todavía resolver la parte difícil de detección automática.

## Fase 2 — Conexión a datos de red (OGN)

- Confirmar si los FLARM de papá/socios suben a la red OGN pública (no todo FLARM lo hace automáticamente — depende de si hay estación receptora cerca).
- Si hay cobertura: conectar el sistema directo a la red OGN (protocolo APRS) para automatizar el input del Módulo 1, en paralelo a lo que muestran apps como WeGlide.
- Si no hay cobertura: pasar a Fase 3 en paralelo.

## Fase 3 — Análisis de terreno (si la cobertura OGN es floja)

- Bajar imágenes satelitales (Sentinel-2, vía Copernicus o Google Earth Engine) y DEM (SRTM) de la zona Zárate-Giles-Baradero.
- Clasificar terreno por tipo de superficie (campo trabajado, pastura, monte, agua, asfalto).
- Generar un mapa estático de "zonas candidatas" a consultar antes de volar — no en tiempo real.
- Ver `04-zona-vuelo.md` y `05-notas-tecnicas.md` para el detalle técnico y las herramientas.

## Fase 4 — Recolección de datos propios (en paralelo a todo lo anterior)

- Durante los vuelos de los findes, registrar variómetro + GPS + anotaciones manuales de dónde y cuándo aparecieron térmicas fuertes vs. débiles.
- Esta es la materia prima para calibrar, con el tiempo, cualquier modelo más preciso (correlacionar terreno/condiciones con intensidad real de térmica).

## Fase 5 — Afinar el Módulo 3 con datos reales

- Una vez que Fases 2-4 dan datos utilizables, reemplazar el input manual de la Fase 1 por datos automáticos.
- Evaluar sumar datos meteorológicos en tiempo real (viento, humedad) para mejorar la comparación entre térmica actual y candidatas.

## Nota sobre orden

No es estrictamente secuencial — Fases 2, 3 y 4 pueden avanzar en paralelo según lo que se vaya confirmando cada fin de semana (por ejemplo, cobertura OGN real en la zona). La Fase 1 es la única que conviene tener lista antes que las demás, porque valida si el corazón del proyecto (la lógica de decisión) tiene sentido antes de invertir en automatizar el input.
