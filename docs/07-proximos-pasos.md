# Próximos pasos (checklist accionable)

## Confirmar con el club / familia

- [x] **Confirmar cobertura OGN en la zona: NO hay.** Descartada definitivamente (22/09) — confirma la decisión de `00-decision-final.md` de no depender de la red FLARM/OGN. El Módulo 1 se apoya solo en el Módulo 1-B (terreno), no en Módulo 1-A (red).
- [x] **RASP (Dr. Jack): sin cobertura para Argentina** — descartado, ver `12-fuentes-meteo-alternativas.md`.
- [x] **SkySight: confirmado, con cuenta de consumidor final (sin API).** Papá de Franco lo tiene y lo usa. Sin API no se puede integrar al código — queda como consulta manual antes de volar. Ver `12-fuentes-meteo-alternativas.md`.

## Fase 1 — MVP de decisión (completa)

- [x] Polar de referencia: LET L-13 Blanik (planeador de entrenamiento del club), calibrada con 2 puntos reales verificados — ver `09-modulo3-diseno-decision.md`.
- [x] Fórmula MacCready implementada (`scripts/decision_maccready.py`) y conectada al mapa de terreno (`scripts/copiloto.py`).
- [x] Probado con escenarios inventados y con datos reales de la zona — funciona de punta a punta.

## Fase de datos (en paralelo, cada fin de semana de vuelo) — herramientas listas

- [x] **Script para registrar cada térmica encontrada** (`scripts/registrar_termica.py`): pide (o recibe por parámetro) posición, altura, fuerza, tipo de terreno debajo, y lo guarda en `registro_vuelos/termicas.csv`. Uso simple:
  ```
  python3 scripts/registrar_termica.py
  ```
  (va preguntando cada dato; también se puede pasar todo por parámetros, ver el `--help` o el docstring del script).
- [x] **Script para comparar lo registrado contra lo que predice el modelo** (`scripts/comparar_registro_vs_modelo.py`): apenas haya un par de registros cargados, muestra fuerza real vs. fuerza que el modelo hubiera predicho ahí, y si hay un sesgo sistemático (el modelo sobre o subestimando). Correrlo después de cada finde de vuelo:
  ```
  python3 scripts/comparar_registro_vs_modelo.py
  ```
- [ ] Empezar a cargar registros reales — el `registro_vuelos/termicas.csv` está vacío, listo para usarse el próximo fin de semana de vuelo.

## Análisis de terreno — Módulo 1-B (avanzado)

- [x] Registrarse en Google Earth Engine (proyecto `sunny-shadow-476422-a9`, tier Community).
- [x] Diseño técnico del módulo — ver `08-modulo1b-diseno-terreno.md`.
- [x] Script funcional (`scripts/analizar_terreno.py`): arma mosaico Sentinel-2 sin nubes, calcula NDVI/NDWI/BSI, cruza con ESA WorldCover y genera mapa de score de potencial térmico (PNG + GeoTIFF). Corrido con éxito sobre el cuadrante Zárate-Giles-Baradero (score promedio 61/100, rango 5-87).
- [x] Consulta por punto+radio resuelta directamente sobre el GeoTIFF (`mejores_candidatas()` en `scripts/copiloto.py`, vía rasterio) — no hizo falta un GeoJSON aparte.
- [ ] Revisar visualmente el mapa de score contra el conocimiento real de la zona (¿tiene sentido dónde marca alto/bajo?) y ajustar los pesos de la heurística si hace falta.
- [ ] Bajar DEM (SRTM) de la misma zona (pendiente, hoy el script no lo usa — la zona es chata y pesa poco, pero falta sumarlo para el borde del Delta).

## Roles (pendiente definir con Fran)

- [ ] Definir quién se enfoca en qué: lógica de decisión (software/matemática) vs. hardware/integración/pruebas en vuelo.

## Definiciones de negocio (más adelante, no bloqueante para arrancar)

- [ ] Presupuesto inicial.
- [ ] Plan de testeo: primero el usuario mismo, después hermano/papá. Si gusta, recién ahí evaluar vender.
