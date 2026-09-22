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
    "max_lon": -59.08,
    "max_lat": -33.80,
}

CLUB_ZARATE = (-34.120, -59.084)


def get_aoi():
    b = AOI_BOUNDS
    return ee.Geometry.Rectangle([b["min_lon"], b["min_lat"], b["max_lon"], b["max_lat"]])


def init_earth_engine():
    credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
    ee.Initialize(credentials, project=PROJECT_ID)
