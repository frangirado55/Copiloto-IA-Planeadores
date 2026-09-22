# Los 5 módulos del proyecto

## Módulo 1 — Detección de térmicas (activas y candidatas)

Dos enfoques complementarios, elegidos según cobertura disponible:

**A. Vía red FLARM/OGN** (cuando hay cobertura):
- Cada planeador con FLARM transmite posición/altura por radio de corto alcance.
- Si hay una estación receptora OGN cerca, esa señal sube a la red pública Open Glider Network — consultable en tiempo real (ver glidernet.org).
- Detectar el patrón de giro de otro planeador (círculos consecutivos casi en el mismo punto, ganando altura) indica que está centrando una térmica — de ahí se estima ubicación y fuerza aproximada.
- Limitación: es **reactivo** — recién se detecta cuando otro planeador ya está girando ahí. Y en Argentina la cobertura OGN es floja.

**B. Vía análisis de terreno** (cuando no hay cobertura, o como complemento predictivo):
- Clasificación del terreno por tipo de superficie (campo trabajado/seco, pastura, monte, agua, asfalto/rutas) usando imágenes satelitales (Sentinel-2, gratuitas vía Copernicus).
- Cruce con modelo de elevación (DEM, SRTM) para relieve — poco relevante en la zona de Zárate-Giles-Baradero por ser pampa chata.
- Este análisis se hace **antes del vuelo** (sobre un mapa estático), no depende de ángulo ni distancia de cámara en vivo.
- Complemento opcional en vuelo: cámara térmica apuntando hacia abajo (no hacia adelante — ver `05-notas-tecnicas.md` sobre por qué el alcance hacia adelante no es viable físicamente).

**Descartado como punto de partida:** predicción física pura basada solo en cámara infrarroja detectando el nacimiento de una térmica en tiempo real. Ver `06-historial-iteraciones.md`.

## Módulo 2 — Fuerza de la térmica (m/s)

Técnicamente el más simple: un variómetro digital ya da esto en tiempo real (rango típico 1-5+ m/s). El desafío real aparece cuando se quiere **estimarla antes de entrar** (parte del Módulo 1) — ahí se necesita correlacionar la señal de detección con la intensidad real, lo que requiere datos históricos de calibración propios del club.

Dato de referencia: la diferencia de temperatura del aire dentro de una térmica de 3 m/s (buena/moderada) respecto al entorno es de solo ~1-2°C — señal sutil, del mismo orden que el margen de error de sensores baratos. El contraste en el **suelo** (punto de origen) es mucho mayor y más fácil de captar.

## Módulo 3 — IA de decisión (el diferencial del proyecto)

Seguir centrando la térmica actual vs. virar hacia una mejor detectada más adelante. Necesita:
- Comparar la térmica actual (fuerza, altura, tendencia) contra estimaciones de térmicas candidatas (depende del Módulo 1).
- Teoría de polar del planeador + teoría MacCready (ya usada en XCSoar, SeeYou) como base matemática — no arrancar de cero, es matemática de optimización bien documentada.
- Opcional/fase avanzada: incorporar datos meteorológicos en tiempo real (viento, humedad) para afinar la estimación de si las térmicas candidatas se van a sostener.

## Módulo 4 — Distancia y llegada al club

Resuelto conceptualmente: GPS + polar de planeo = llegada calculada (final glide). Ya existe en instrumentos comerciales (LX Nav, XCSoar) y en WeGlide Copilot. No vale la pena reinventarlo — se puede usar como referencia de implementación o directamente delegar en una app existente mientras se prioriza el Módulo 3.

## Módulo 5 — Carga de tarea/torneo

Cargar waypoints y zonas de giro del día para que las recomendaciones del Módulo 3 tengan en cuenta el recorrido, no solo la térmica suelta. También resuelto en apps existentes; baja prioridad de desarrollo propio.

## Dependencias entre módulos

- **Módulo 1** es la base: sin detección (red o terreno) confiable, no hay con qué alimentar al Módulo 3.
- **Módulo 2** está embebido en el Módulo 1 cuando se busca estimar fuerza antes de entrar.
- **Módulo 3** depende directamente de que 1 y 2 den datos utilizables.
- **Módulos 4 y 5** son independientes — se pueden resolver ya, o directamente apoyarse en herramientas existentes.
