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
- [x] Revisar visualmente el mapa de score contra el conocimiento real de la zona — hecho, llevó a los ajustes de hotspots y arado/rastrojo.
- [x] Mapa legible para uso general (`scripts/mapa_claro.py`) y mapa de decisión por vuelo puntual (`scripts/mapa_decision.py`, muestra posición del piloto + térmica sugerida + ruta) — feedback de Franco sobre falta de claridad, resuelto.
- [ ] Bajar DEM (SRTM) de la misma zona (pendiente, hoy el script no lo usa — la zona es chata y pesa poco, pero falta sumarlo para el borde del Delta).

## Zona de escape / aterrizaje de emergencia (24/09, idea de Franco)

- [x] Alcance máximo de planeo (`mejor_planeo()`, `alcance_maximo_km()` en `decision_maccready.py`).
- [x] Score de aptitud de aterrizaje distinto del de térmica, y búsqueda de zonas seguras (`scripts/zona_aterrizaje.py`) + mapa (`scripts/mapa_aterrizaje.py`) — ver `13-zona-escape-aterrizaje.md`.
- [ ] Sumar coordenadas de los aeroclubes de San Andrés de Giles y Baradero (si los tienen) como destinos alternativos al club de Zárate.
- [ ] Orientar el cono de planeo con el viento del día (hoy es un círculo completo) — ídea pendiente, no bloqueante.

## Ideas evaluadas y descartadas por ahora (24/09)

Franco trajo una lista grande de ideas (interfaz de audio/pantalla, filtrado por coeficiente del planeador vía OGN, "térmicas fantasma", filtro de rivales en competencia, efecto río Paraná dinámico). Triage:
- **Requieren red OGN** (coeficiente del planeador, térmicas fantasma, filtro de rivales): descartadas por ahora — no hay cobertura OGN en la zona (ver `06-historial-iteraciones.md`). Si algún día arman una estación receptora propia, se reconsideran.
- **Requieren la app/interfaz real** (canal de alertas, tonos, pantalla de modo térmica, botón de resumen de voz): no bloqueantes, pero necesitan primero la interfaz para celular que todavía no se armó.
- **Efecto río Paraná dinámico**: buena idea, quedó como próxima candidata después de esta (zona de escape) — no implementada todavía.

## Roles (pendiente definir con Fran)

- [ ] Definir quién se enfoca en qué: lógica de decisión (software/matemática) vs. hardware/integración/pruebas en vuelo.

## Definiciones de negocio (más adelante, no bloqueante para arrancar)

- [ ] Presupuesto inicial.
- [ ] Plan de testeo: primero el usuario mismo, después hermano/papá. Si gusta, recién ahí evaluar vender.
