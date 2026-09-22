# Diseño técnico — Módulo 1-B: IA de lectura de terreno

Diseño de la parte del Módulo 1 que analiza terreno como lo haría el piloto: monte, campo trabajado, zonas altas/húmedas, nubes, sombras, piedra. Ver `01-modulos.md` para el resumen funcional; acá se detalla cómo se construye.

## Objetivo

Producir, antes de cada vuelo, un mapa de la zona (Zárate → San Andrés de Giles → Baradero) con dos capas:
1. **Clasificación de terreno** por tipo de superficie.
2. **Score de potencial térmico** por zona, derivado de esa clasificación — la señal que va a consumir el Módulo 3 cuando no hay térmicas activas detectadas por red OGN.

No es tiempo real: es una foto estática generada antes de volar, que se actualiza cuando conviene (nueva imagen satelital sin nubes disponible).

## Señales de entrada (qué datos se leen)

| Señal | Fuente | Para qué sirve |
|---|---|---|
| Imagen óptica (RGB + infrarrojo) | Sentinel-2 (vía Earth Engine) | Base para calcular índices espectrales |
| NDVI (índice de vegetación) | Calculado de Sentinel-2 (NIR/Red) | Distingue vegetación viva (pastura, monte) de suelo desnudo (campo arado, seco) |
| NDWI (índice de agua) | Calculado de Sentinel-2 (Green/NIR) | Detecta agua (río Paraná, lagunas, canales) — zonas que inhiben térmica |
| BSI (índice de suelo desnudo) | Calculado de Sentinel-2 | Refuerza la distinción "campo recién arado y seco" vs. pastura — la superficie que más calienta |
| Máscara de nubes | Sentinel-2 QA60 / `COPERNICUS/S2_CLOUD_PROBABILITY` | Descarta píxeles nublados al armar el mosaico; evita clasificar una nube como terreno |
| Cobertura de suelo pre-clasificada | ESA WorldCover 10m (o Dynamic World) vía Earth Engine | Clasificación ya entrenada por Google/ESA (bosque, cultivo, pastizal, agua, urbano) — se usa como base en vez de entrenar un modelo propio desde cero |
| Elevación | SRTM (30m) vía Earth Engine | Pendiente/relieve — pesa poco en esta zona (pampa chata), se incluye por completitud y para detectar el borde del Delta |

## Por qué no se entrena un clasificador propio (al principio)

Hay dos datasets globales ya entrenados y gratuitos (ESA WorldCover, Dynamic World) que resuelven "¿qué hay en este pixel: bosque, cultivo, pastizal, agua, urbano?" con buena precisión. Entrenar algo propio desde cero requeriría etiquetar manualmente miles de píxeles de la zona — trabajo que no aporta nada que estos datasets no den ya.

Lo que estos datasets **no** distinguen bien es el matiz que más importa para térmicas: *campo recién arado y seco* (calienta mucho) vs. *rastrojo* vs. *pastura verde* (calienta distinto) — todos caen dentro de la misma clase genérica "cropland". Ahí es donde entran los índices calculados (NDVI, BSI) como refinamiento sobre la clase base, con reglas simples (no un modelo entrenado):

- Cropland + NDVI bajo + BSI alto → campo trabajado/seco (score térmico alto)
- Cropland + NDVI alto → cultivo en pie o pastura verde (score térmico medio)
- Tree cover → monte (score térmico variable, depende de densidad)
- Water → agua (score térmico muy bajo, inhibe)
- Built-up / cerca de rutas → disparador térmico puntual (score alto en el borde de contraste, no en el área en sí)

**Calibración con conocimiento local (Franco, 22/09)**: confirmado que en la zona de Zárate las fábricas y la Ruta 9 son disparadores térmicos muy fuertes (mejor opción que un campo seco promedio), y que los lagos/ríos alrededor inhiben térmica como se esperaba. Por eso el score de la clase "Built-up" se subió de 75 a 90/100 (casi al tope, a la par del suelo desnudo) — el valor original lo subestimaba.

### Hotspots conocidos (puntos concretos, no solo clase de terreno)

Además de calibrar la clase genérica "Built-up", se agregaron dos puntos concretos confirmados por Franco como disparadores confiables: la planta de **Toyota Argentina** y el **Centro Industrial/Logístico de Mercedes-Benz**, ambas en Zárate. Se ubicaron visualmente sobre la imagen Sentinel-2 (inspeccionando manualmente la imagen y las coordenadas de referencia dibujadas sobre ella) — no son coordenadas geocodificadas oficiales, tienen margen de error de algunos cientos de metros:

- Toyota Argentina (planta): -34.1289, -59.0637 (~2.1km del club)
- Mercedes-Benz Centro Industrial/Logístico: -34.1205, -59.0933 (~0.85km del club)

Estos puntos se guardan en `scripts/config.py` (`HOTSPOTS_CONOCIDOS`) y se suman a la búsqueda de candidatas en `scripts/copiloto.py` con un score fijo alto (95/100), independientemente de lo que diga la clasificación satelital en ese píxel puntual — el conocimiento directo de un piloto de la zona vale más que la heurística genérica ahí donde ambos coinciden en existir.

### Arado vs. rastrojo (investigado, 22/09)

Según fuentes de meteorología de vuelo a vela (ej. el manual de la FAA sobre clima para planeadores — [AC 00-6A Cap. 16](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC%2000-6A%20Chap%2016-index.pdf)), un **campo arado seco generalmente da mejor térmica que un rastrojo/campo plano**: los surcos actúan como pequeños colectores solares (sus caras quedan encaradas al sol) y además protegen las bolsas de aire caliente del viento mientras se desarrollan. El rastrojo es una fuente válida pero en general más débil, salvo que esté rodeado de vegetación verde (ahí el contraste ayuda).

**Limitación real**: Sentinel-2 tiene 10m de resolución por píxel; un surco de arado mide 30-75cm de ancho. El satélite no puede ver la textura de los surcos — no hay forma de distinguir "arado con buenos surcos" de "campo plano recién trabajado" con esta fuente de datos. Por eso el ajuste que se pudo hacer fue indirecto: subir el peso de BSI (suelo realmente desnudo, más asociado a arado) por sobre NDVI-bajo solo (que también incluye rastrojo, pasto seco, etc.) en `build_score()` — de 15/15 a 20/10. Es una aproximación razonable, no una detección real de arado vs. rastrojo. Si en el futuro se consigue imagen de mayor resolución (ej. PlanetScope, ~3m, pago) o fotos de dron propias, ahí sí se podría distinguir mejor.

## Pipeline (orden de procesamiento)

1. Definir el área de interés (AOI): polígono con las coordenadas de `04-zona-vuelo.md`.
2. Buscar en Earth Engine las escenas Sentinel-2 más recientes con baja nubosidad sobre el AOI (últimos 15-30 días, filtrando por `CLOUDY_PIXEL_PERCENTAGE`).
3. Armar un mosaico sin nubes: mediana de varias escenas, enmascarando con la capa de probabilidad de nubes.
4. Calcular NDVI, NDWI, BSI sobre el mosaico.
5. Traer la capa base de ESA WorldCover recortada al mismo AOI.
6. Cruzar clase base + índices con las reglas de arriba → mapa de score de potencial térmico (por ejemplo, escala 0-100 por celda de ~10-30m, o agregado por polígono de zona).
7. Exportar dos salidas:
   - **GeoTIFF/PNG** del mapa clasificado, para inspección visual antes de volar.
   - **GeoJSON** con polígonos/celdas y su score, para que el Módulo 3 lo consulte por código (dado un punto y un radio, devolver las N zonas candidatas con mejor score).

### Mapa legible para el piloto (`scripts/mapa_claro.py`)

El GeoTIFF/PNG crudo de Earth Engine no tiene leyenda ni referencias — sirve para que el código lo procese, pero no para que un piloto lo mire y entienda rápido qué zona es cuál. `scripts/mapa_claro.py` toma el `score_termico.tif` ya generado y arma una versión para humanos:

- Leyenda/barra de colores explicando la escala (azul=malo, rojo=bueno).
- Club y los dos hotspots conocidos (Toyota, Mercedes-Benz) marcados y etiquetados, con las etiquetas separadas a mano para que no se superpongan entre sí (están a menos de 2km de distancia).
- Indicadores de dirección hacia San Andrés de Giles y hacia Baradero/río Paraná (para orientarse sin tener que leer coordenadas).
- Norte, escala en km, título.
- **Flecha de viento real del día** (dirección y velocidad actuales, vía GFS — ver `11-teoria-completa-termicas.md` sobre por qué el viento importa, no solo el terreno).

## Integración con el Módulo 3

El Módulo 3 (IA de decisión) consulta este GeoJSON cuando evalúa térmicas candidatas y no hay datos de red OGN cerca: dado el rumbo y alcance actual del planeador, filtra las zonas dentro de ese radio y las ordena por score. Ese ranking entra como una de las "térmicas candidatas" en la comparación MacCready, con una fuerza estimada más incierta que una térmica confirmada por OGN (esto se refleja bajándole peso/confianza al dato, no tratándolo igual que una detección en vivo).

## Rol de los datos propios (Fase 4)

Los datos que se junten volando (variómetro + GPS + anotación manual de dónde hubo térmica fuerte/débil, de `03-plan-trabajo.md` Fase 4) **no** se usan para reentrenar la clasificación de terreno en sí — para eso ya alcanza con WorldCover + índices. Se usan para **calibrar el score de potencial térmico**: ajustar los pesos de las reglas (¿cuánto vale realmente "campo seco" vs. "cerca de ruta" en esta zona particular, en esta época del año?) comparando la predicción contra lo que efectivamente se encontró volando.

Si con el tiempo esa calibración no alcanza y hace falta algo más fino, recién ahí se evaluaría un modelo supervisado liviano (ej. Random Forest sobre los índices espectrales, usando las anotaciones de vuelo como etiquetas) — pero es una optimización de fase avanzada, no el punto de partida.

## Limitaciones conocidas

- **No es tiempo real**: no ve nubosidad ni viento del día de vuelo, solo terreno. La nubosidad/condiciones del día las cubre, más adelante, el cruce con datos meteorológicos (GFS/RASP, ver `05-notas-tecnicas.md`) — es un complemento futuro, no parte de este módulo.
- **Score sin calibrar al inicio**: hasta que la Fase 4 aporte suficientes datos reales, el score de potencial térmico es una heurística razonada pero no validada contra vuelos reales de la zona.
- **No reemplaza RASP**: RASP predice *cuándo* y *qué tan fuerte* va a haber térmica según meteorología; este módulo dice *dónde* el terreno tiende a favorecerla. Son complementarios (ver Módulo 1-A en `01-modulos.md`).

## Requisitos técnicos ya resueltos

- Cuenta de Google Earth Engine registrada (proyecto `sunny-shadow-476422-a9`, tier Community, no comercial).
- Cuenta de servicio (`copiloto-ia-planeadores@sunny-shadow-476422-a9.iam.gserviceaccount.com`) con su clave JSON, guardada localmente en `credentials/` (excluida de git vía `.gitignore` — nunca se sube al repo).

## Pendiente antes de retomar código

- La cuenta de servicio devolvió `403 USER_PROJECT_DENIED` al inicializar Earth Engine — falta agregarle el rol `roles/serviceusage.serviceUsageConsumer` (además de `Earth Engine Resource Viewer`) en el proyecto de Google Cloud. Se resuelve en 2 minutos desde IAM & Admin cuando retomemos la parte de código.
