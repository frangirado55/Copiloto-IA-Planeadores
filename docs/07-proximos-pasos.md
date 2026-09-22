# Próximos pasos (checklist accionable)

## Confirmar con el club / familia

- [ ] Preguntarle a papá (o algún socio con FLARM) qué modelo/versión tiene y si sabe si hay estación receptora OGN cerca del club.
- [ ] Chequear cobertura real de la zona del club en [glidernet.org](http://www.glidernet.org) — poner el mapa en -34.12, -59.08 y ver si aparecen planeadores en vivo.
- [ ] Confirmar si hay cobertura RASP para la zona de Zárate.

## Fase 1 — MVP de decisión (arrancar por acá)

- [ ] Definir la polar del planeador que van a usar como referencia (marca/modelo del planeador del club o de papá).
- [ ] Implementar la fórmula MacCready básica en Python: dado (fuerza térmica actual, fuerza térmica candidata, distancia a la candidata, polar del planeador), calcular si conviene quedarse o virar.
- [ ] Probarlo con datos inventados/manuales primero, antes de conectar cualquier fuente de datos real.

## Fase de datos (en paralelo, cada fin de semana de vuelo)

- [ ] Registrar variómetro + GPS durante los vuelos.
- [ ] Anotar manualmente dónde y cuándo aparecieron térmicas fuertes vs. débiles (hora, ubicación aproximada, tipo de terreno debajo).

## Análisis de terreno — Módulo 1-B (avanzado)

- [x] Registrarse en Google Earth Engine (proyecto `sunny-shadow-476422-a9`, tier Community).
- [x] Diseño técnico del módulo — ver `08-modulo1b-diseno-terreno.md`.
- [x] Script funcional (`scripts/analizar_terreno.py`): arma mosaico Sentinel-2 sin nubes, calcula NDVI/NDWI/BSI, cruza con ESA WorldCover y genera mapa de score de potencial térmico (PNG + GeoTIFF). Corrido con éxito sobre el cuadrante Zárate-Giles-Baradero (score promedio 61/100, rango 5-87).
- [ ] Exportar el score como grilla/GeoJSON consultable por punto+radio (hoy solo exporta GeoTIFF) — necesario para que el Módulo 3 lo use en runtime.
- [ ] Revisar visualmente el mapa de score contra el conocimiento real de la zona (¿tiene sentido dónde marca alto/bajo?) y ajustar los pesos de la heurística si hace falta.
- [ ] Bajar DEM (SRTM) de la misma zona (pendiente, hoy el script no lo usa — la zona es chata y pesa poco, pero falta sumarlo para el borde del Delta).

## Roles (pendiente definir con Fran)

- [ ] Definir quién se enfoca en qué: lógica de decisión (software/matemática) vs. hardware/integración/pruebas en vuelo.

## Definiciones de negocio (más adelante, no bloqueante para arrancar)

- [ ] Presupuesto inicial.
- [ ] Plan de testeo: primero el usuario mismo, después hermano/papá. Si gusta, recién ahí evaluar vender.
