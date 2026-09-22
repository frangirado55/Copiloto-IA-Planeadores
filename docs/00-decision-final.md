# Decisión final de alcance (21/09/2026)

## Qué es el proyecto

Un **asistente de decisión** para vuelo a vela — no un mapa de térmicas nuevo, no un competidor directo de WeGlide Copilot. La pieza central es la **IA de decisión** (Módulo 3): comparar la térmica en la que estás centrando ahora contra térmicas candidatas detectadas más adelante, y recomendar activamente si conviene quedarse o virar hacia otra.

Está pensado para **complementar** apps ya existentes (WeGlide Copilot y similares), no reemplazarlas — alimentándose de la misma red pública (FLARM/OGN) cuando hay cobertura, y de análisis de terreno propio cuando no la hay.

## Por qué este alcance y no otro

Se evaluaron varios enfoques (cámara térmica sola, predicción física pura, clon completo de WeGlide) y se descartaron como punto de partida por razones concretas — el detalle está en `06-historial-iteraciones.md`. La conclusión en una línea: **ninguna app existente decide activamente por el piloto, todas solo muestran datos.** Ahí está el hueco real, y es alcanzable para dos personas trabajando los fines de semana.

## Los 5 módulos (resumen — detalle en `01-modulos.md`)

1. **Detección de térmicas (activas y candidatas)** — vía red FLARM/OGN donde hay cobertura, y análisis de terreno (satelital) donde no la hay.
2. **Fuerza de la térmica (m/s)** — embebido en el Módulo 1 cuando se busca estimarla antes de entrar.
3. **IA de decisión** — el diferencial real del proyecto. Seguir centrando vs. virar hacia otra, usando teoría MacCready + polar del planeador.
4. **Distancia y llegada calculada al club** — resuelto (GPS + polar), ya existe en varios instrumentos comerciales.
5. **Carga de tarea/torneo** — para que las recomendaciones tengan en cuenta el recorrido del día.

## Lo que el proyecto NO va a prometer

- No promete predicción física perfecta de térmicas antes de que exista ninguna señal (ni de red, ni de terreno, ni meteorológica).
- No compite de frente con WeGlide Copilot en mapa reactivo, hotspots históricos o cobertura satelital — ahí la diferencia de recursos es demasiado grande.
- No depende de una única fuente de datos (si no hay cobertura OGN en la zona, cae al análisis de terreno; no es un punto único de falla).

## Contexto del club y la zona

- Los planeadores de la escuela **no** tienen FLARM. Los de papá y otros socios del club **sí**.
- Zona de vuelo habitual: cuadrante Zárate → San Andrés de Giles → Baradero (pampa húmeda, sin relieve significativo — ver `04-zona-vuelo.md`).
- Franco y Fran vuelan juntos todos los fines de semana (sábado y domingo), con pernocte — buena cadencia para ciclos cortos de prueba/ajuste.

## Próximo paso inmediato

Ver `07-proximos-pasos.md`.
