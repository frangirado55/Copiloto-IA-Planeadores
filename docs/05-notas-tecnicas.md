# Notas técnicas sueltas

## FLARM / OGN

- **FLARM**: sistema de detección de colisiones para planeadores/aeronaves. Cada equipo transmite posición/altura/velocidad por radio de corto alcance (peer-to-peer) y recibe la de otros FLARM cercanos, para avisar riesgo de colisión.
- **OGN (Open Glider Network)**: red pública que capta señales FLARM mediante estaciones receptoras y las sube a internet (protocolo APRS). Solo funciona si hay una estación receptora OGN cerca — un FLARM por sí solo NO sube nada a internet automáticamente.
- **glidernet.org**: visualizador público en vivo de la red OGN. Sirve para chequear cobertura real de una zona.
- Si no hay estación receptora cerca del club, se puede armar una propia (Raspberry Pi + dongle SDR) — proyecto conocido y documentado en la comunidad OGN, relativamente barato.

## Física de la cámara térmica (por qué "mirar adelante" no funciona bien)

- Mirar 3-7 km adelante desde ~1 km de altura implica un ángulo casi rasante (8-18° bajo la horizontal, no perpendicular al suelo).
- En ángulo rasante, cada píxel de la cámara cubre una franja de terreno mucho más grande y distorsionada (factor ~1/sin(ángulo) — a 8°, ~7x peor que mirando derecho hacia abajo).
- La atmósfera atenúa la señal térmica con la distancia (humedad, polvo, bruma) — a varios km la imagen se degrada mucho.
- Objetos intermedios (árboles, lomadas) bloquean la línea de visión en ángulo rasante.
- **Conclusión**: la cámara térmica sirve para el entorno cercano, mirando hacia abajo (altura moderada, terreno bajo el planeador), no para explorar el horizonte lejano. Para eso último conviene la red FLARM/OGN o el análisis de terreno satelital hecho antes del vuelo.

## Diferencia de temperatura en una térmica

- Térmica de 3 m/s (buena/moderada): ~1-2°C de exceso respecto al aire circundante — señal sutil.
- Térmica débil (~1 m/s): ~0.5°C.
- Térmica fuerte (5+ m/s): ~2-4°C.
- Esta diferencia (en el aire, en altura) es mucho menor que la diferencia de temperatura en el **suelo** en el punto de origen (que puede ser de varios grados, 10°C+ en día de sol fuerte) — por eso apuntar la cámara al suelo es más viable que intentar detectar la térmica ya en el aire.
- Referencia de precisión de sensores baratos tipo FLIR Lepton: ±2-5°C — del mismo orden que la señal a detectar en el aire, insuficiente ahí; mejor relación señal/ruido apuntando al suelo.

## Opciones de cámara térmica (si se retoma esa vía como complemento)

| Modelo | Resolución | Precio aprox. | Alcance útil |
|---|---|---|---|
| FLIR Lepton 3.5 | 160×120 | ~USD 200 | Bueno hasta 300-500m de altura |
| FLIR Boson 320 | 320×256 | ~USD 1500+ | Bueno hasta 1000m+ |
| FLIR One (para celular) | 160×120 | ~USD 150-250 | Solo corto alcance, no pensada para esto |

Para un primer prototipo, FLIR Lepton 3.5 + Raspberry Pi es la combinación más razonable en costo.

## Teoría MacCready

Base matemática estándar para la IA de decisión (Módulo 3) — ya usada en software existente (XCSoar, SeeYou). No hace falta reinventarla: define la velocidad óptima de vuelo entre térmicas en función de la fuerza esperada de la próxima térmica y la polar del planeador. Punto de partida obligado para implementar el Módulo 3.

## Herramientas de software sugeridas

- **Python** para prototipar: procesamiento de datos geoespaciales, cálculos de geometría (detección de patrones de giro), lectura de datos meteorológicos (`xarray`/`netCDF4` para formatos GRIB/NetCDF de modelos tipo GFS).
- **Flutter o React Native** si se necesita una app multiplataforma para tablet/celular en cabina.
- **Google Earth Engine** para procesar imágenes satelitales sin necesidad de descargarlas manualmente (corre en la nube de Google, con cuenta gratuita).

## Modelos meteorológicos de referencia

- **GFS** (NOAA) / **ECMWF**: pronóstico numérico gratuito o de bajo costo, base para calcular el "thermal index" (comparación de temperatura de una parcela de aire ascendiendo vs. temperatura real del ambiente por altura).
- **RASP (Regional Atmospheric Soaring Prediction)**: sistema de código abierto ya usado por clubes de vuelo a vela en el mundo, corre el modelo WRF con foco en pronóstico de térmicas (hora de inicio, techo, fuerza estimada). Vale la pena estudiarlo como referencia de implementación antes de intentar algo desde cero — pendiente confirmar si ya hay cobertura RASP para la zona de Zárate.
