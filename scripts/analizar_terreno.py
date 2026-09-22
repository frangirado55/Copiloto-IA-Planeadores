"""
Módulo 1-B: análisis de terreno para detectar zonas candidatas a térmica.

Genera, para el cuadrante de vuelo Zárate-Giles-Baradero:
  - Un mosaico Sentinel-2 sin nubes reciente.
  - Índices espectrales (NDVI, NDWI, BSI).
  - Un mapa de score de potencial térmico (0-100) combinando
    ESA WorldCover (cobertura de suelo) con esos índices.
  - Salidas: PNG de inspección visual + GeoTIFF del score.

Ver docs/08-modulo1b-diseno-terreno.md para el diseño completo.
"""

import os
import datetime
import urllib.request

import ee
import geemap

from config import get_aoi, init_earth_engine, CLUB_ZARATE

OUTPUT_DIR = "data/salida_terreno"

# Scores base por clase de ESA WorldCover (0-100, mayor = mas favorable a termica)
WORLDCOVER_SCORE = {
    10: 45,   # Tree cover (monte)
    20: 60,   # Shrubland
    30: 55,   # Grassland (pastura)
    40: 70,   # Cropland (campo trabajado; se ajusta despues con NDVI/BSI)
    50: 90,   # Built-up (urbano/rutas/fabricas): disparador termico clasico por
              # contraste asfalto/chapa vs. campo. Confirmado por conocimiento
              # local de la zona (Zarate: fabricas + Ruta 9) - ver docs/08.
    60: 85,   # Bare / sparse vegetation (suelo desnudo)
    70: 0,    # Snow / ice (no aplica a la zona)
    80: 5,    # Permanent water bodies
    90: 10,   # Herbaceous wetland
    95: 5,    # Mangroves
    100: 40,  # Moss and lichen
}


def mask_s2_clouds(image):
    qa = image.select("QA60")
    cloud_bit = 1 << 10
    cirrus_bit = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit).eq(0).And(qa.bitwiseAnd(cirrus_bit).eq(0))
    return (
        image.updateMask(mask)
        .divide(10000)
        .copyProperties(image, ["system:time_start"])
    )


def get_cloud_free_composite(aoi, days_back=60, max_days_back=180):
    """Busca un mosaico Sentinel-2 sin nubes; si no hay escenas, amplia la ventana."""
    end = ee.Date(datetime.datetime.utcnow().strftime("%Y-%m-%d"))
    window = days_back
    while window <= max_days_back:
        start = end.advance(-window, "day")
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(aoi)
            .filterDate(start, end)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40))
            .map(mask_s2_clouds)
        )
        if collection.size().getInfo() > 0:
            return collection.median().clip(aoi), window
        window += 60
    raise RuntimeError(
        f"No se encontraron escenas Sentinel-2 utilizables en los ultimos {max_days_back} dias."
    )


def add_indices(image):
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
    bsi = image.expression(
        "((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))",
        {
            "SWIR": image.select("B11"),
            "RED": image.select("B4"),
            "NIR": image.select("B8"),
            "BLUE": image.select("B2"),
        },
    ).rename("BSI")
    return image.addBands([ndvi, ndwi, bsi])


def get_worldcover(aoi):
    return ee.ImageCollection("ESA/WorldCover/v200").first().clip(aoi).select("Map")


def build_score(composite, worldcover):
    from_classes = list(WORLDCOVER_SCORE.keys())
    to_scores = list(WORLDCOVER_SCORE.values())
    base_score = worldcover.remap(from_classes, to_scores, 40).rename("base_score")

    # Suelo seco/desnudo (NDVI bajo, BSI alto) sube el score dentro de cropland/grassland;
    # agua (NDWI alto) lo baja a piso, sin importar la clase base.
    # BSI pesa mas que NDVI-bajo: BSI detecta mejor tierra realmente expuesta
    # (mas asociado a arado), mientras que NDVI bajo solo tambien incluye
    # rastrojo/pasto seco. La literatura de meteorologia de vuelo a vela dice
    # que un arado seco suele dar mejor termica que un rastrojo/campo plano
    # (los surcos actuan como colectores solares y protegen el aire caliente
    # del viento - ver docs/08). El satelite (10m/pixel) no resuelve el
    # ancho real de un surco (30-75cm), asi que esto es una aproximacion,
    # no una deteccion real de arado vs rastrojo.
    ndvi = composite.select("NDVI")
    bsi = composite.select("BSI")
    ndwi = composite.select("NDWI")

    dryness_boost = ndvi.multiply(-1).add(1).clamp(0, 1).multiply(10)
    bsi_boost = bsi.clamp(0, 1).multiply(20)

    is_agri = worldcover.eq(40).Or(worldcover.eq(30))
    adjusted = base_score.add(dryness_boost.add(bsi_boost).multiply(is_agri))

    water_mask = ndwi.gt(0.2)
    final_score = adjusted.where(water_mask, 5).clamp(0, 100).rename("score_termico")

    return final_score


def export_png(image, vis_params, aoi, path):
    url = image.getThumbURL({**vis_params, "region": aoi, "dimensions": 1024, "format": "png"})
    urllib.request.urlretrieve(url, path)
    print(f"PNG guardado: {path}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Autenticando con Earth Engine...")
    init_earth_engine()
    aoi = get_aoi()

    print("Buscando mosaico Sentinel-2 sin nubes...")
    composite, window = get_cloud_free_composite(aoi)
    print(f"Mosaico armado con escenas de los ultimos {window} dias.")

    composite = add_indices(composite)
    worldcover = get_worldcover(aoi)
    score = build_score(composite, worldcover)

    print("Exportando PNG de color real (referencia visual)...")
    export_png(
        composite,
        {"bands": ["B4", "B3", "B2"], "min": 0, "max": 0.3},
        aoi,
        os.path.join(OUTPUT_DIR, "color_real.png"),
    )

    print("Exportando PNG de score de potencial termico...")
    export_png(
        score,
        {"min": 0, "max": 100, "palette": ["0000FF", "FFFF00", "FF8800", "FF0000"]},
        aoi,
        os.path.join(OUTPUT_DIR, "score_termico.png"),
    )

    print("Exportando GeoTIFF del score (para uso por el Modulo 3)...")
    geemap.ee_export_image(
        score,
        filename=os.path.join(OUTPUT_DIR, "score_termico.tif"),
        scale=30,
        region=aoi,
        file_per_band=False,
    )

    stats = score.reduceRegion(
        reducer=ee.Reducer.mean().combine(ee.Reducer.minMax(), sharedInputs=True),
        geometry=aoi,
        scale=100,
        maxPixels=1e9,
    ).getInfo()
    print("Estadisticas del score de potencial termico sobre el cuadrante:")
    print(stats)

    print(f"\nListo. Salidas en {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
