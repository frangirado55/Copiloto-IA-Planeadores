"""Configuración compartida para los scripts de análisis de terreno."""

import ee

PROJECT_ID = "sunny-shadow-476422-a9"
SERVICE_ACCOUNT = "copiloto-ia-planeadores@sunny-shadow-476422-a9.iam.gserviceaccount.com"
KEY_PATH = "credentials/earth-engine-key.json"

# Rectángulo que cubre el cuadrante de vuelo Zárate - San Andrés de Giles - Baradero
# (ver docs/04-zona-vuelo.md para las coordenadas de referencia)
AOI_BOUNDS = {
    "min_lon": -59.50,
    "min_lat": -34.45,
    "max_lon": -59.00,  # extendido desde -59.08 para incluir la planta de Toyota (-59.0637)
    "max_lat": -33.80,
}

CLUB_ZARATE = (-34.120, -59.084)

# Hotspots conocidos: disparadores termicos confirmados por conocimiento
# local (pilotos del club), no por clasificacion satelital. Coordenadas
# estimadas visualmente sobre imagen Sentinel-2 (margen de error, no
# son coordenadas oficiales/geocodificadas) - ver docs/08 para el detalle
# de como se ubicaron.
HOTSPOTS_CONOCIDOS = [
    {
        "nombre": "Toyota Argentina (planta)",
        "lat": -34.1289,
        "lon": -59.0637,
        "nota": "Planta industrial grande, techo chapa. Confirmado por Franco (22/09) como disparador termico confiable.",
    },
    {
        "nombre": "Mercedes-Benz Centro Industrial/Logistico",
        "lat": -34.1205,
        "lon": -59.0933,
        "nota": "Complejo industrial sobre RN9. Confirmado por Franco (22/09) como disparador termico confiable.",
    },
]


def get_aoi():
    b = AOI_BOUNDS
    return ee.Geometry.Rectangle([b["min_lon"], b["min_lat"], b["max_lon"], b["max_lat"]])


def init_earth_engine():
    credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
    ee.Initialize(credentials, project=PROJECT_ID)
