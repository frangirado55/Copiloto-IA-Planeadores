"""
Efecto río Paraná dinámico (idea de Franco, sección 3 de su
brainstorm del 24/09): en vez de asumir una franja fría fija cerca
del río, calcula cuántos km tierra adentro se extiende según el
viento REAL del día (dirección + velocidad, vía GFS).

Física simplificada (ver docs/11-teoria-completa-termicas.md sobre
brisa de río/convergencia):
  - Si el viento sopla DESDE el río hacia el interior (component norte,
    ya que el Paraná está al norte de nuestra zona), empuja el aire
    fresco del río tierra adentro -> la franja muerta se extiende MAS.
  - Si el viento sopla DESDE el interior hacia el río (componente sur),
    empuja en contra de la brisa de río -> la franja se achica, queda
    pegada a la orilla.
  - Perpendicular (este/oeste) -> efecto neutro, se usa un valor base.

Esto es una heurística direccional, no un modelo atmosférico validado
-- los coeficientes (base_km, escala_km_por_kmh) son un punto de
partida razonable, a calibrar con datos reales de vuelo cuando haya
suficientes (Fase 4/5, igual que el resto del modelo).
"""

import math
import os

import numpy as np
import rasterio
from scipy import ndimage

from mapa_utils import obtener_viento_actual
from config import init_earth_engine

SCORE_TIF = "data/salida_terreno/score_termico.tif"

# Umbral: en score_termico.tif, agua (clase 80 de WorldCover) queda
# fijo en score=5 (ver WORLDCOVER_SCORE en analizar_terreno.py, la
# unica clase que no recibe boost de NDVI/BSI). Se usa como mascara de
# agua sin tener que volver a consultar Earth Engine.
SCORE_AGUA = 5

# Parametros de la heuristica (ver docstring del modulo)
PENETRACION_BASE_KM = 3.0
ESCALA_KM_POR_KMH = 0.3
PENETRACION_MIN_KM = 1.0
PENETRACION_MAX_KM = 15.0
SUPRESION_EN_LA_ORILLA = 0.3  # score se multiplica por esto justo al lado del agua


def calcular_penetracion_km(rumbo_desde_deg, velocidad_kmh):
    """Cuantos km tierra adentro (hacia el sur, alejandose del rio que
    esta al norte de la zona) se extiende la franja fria, segun el
    viento de hoy."""
    # 0 grados (viento DESDE el norte) = maxima amplificacion (empuja
    # el aire del rio hacia el sur/adentro). 180 grados (desde el sur)
    # = maxima supresion (empuja en contra, la brisa no avanza).
    factor_alineacion = math.cos(math.radians(rumbo_desde_deg))
    penetracion = PENETRACION_BASE_KM + factor_alineacion * velocidad_kmh * ESCALA_KM_POR_KMH
    return float(np.clip(penetracion, PENETRACION_MIN_KM, PENETRACION_MAX_KM))


def _mascara_solo_rio_principal(mascara_agua, min_pixeles=5000):
    """El score==5 incluye el rio/delta grande Y cientos de lagunas
    chicas sueltas en el campo (charcos de una escena satelital, o
    lagunas reales pero demasiado chicas para generar brisa propia).
    Nos quedamos solo con los cuerpos de agua conectados grandes -- en
    la practica, el Parana/delta es un solo componente conectado que
    domina ampliamente (~95% del agua total), separado por un salto
    grande del resto (siguiente componente es ~1% del tamano)."""
    etiquetas, n = ndimage.label(mascara_agua)
    if n == 0:
        return mascara_agua
    tamanos = ndimage.sum(mascara_agua, etiquetas, range(1, n + 1))
    etiquetas_grandes = [i + 1 for i, t in enumerate(tamanos) if t >= min_pixeles]
    return np.isin(etiquetas, etiquetas_grandes)


def aplicar_efecto_rio(banda_score, transform, penetracion_km):
    """Devuelve una copia de banda_score con el score reducido cerca
    del rio principal (no lagunas chicas sueltas), con la reduccion
    mas fuerte pegado a la orilla y desvaneciendose hasta
    penetracion_km tierra adentro."""
    mascara_agua = _mascara_solo_rio_principal(banda_score == SCORE_AGUA)
    if not mascara_agua.any():
        return banda_score.copy()

    # Distancia de cada pixel al agua mas cercana, en pixeles -> km
    # (resolucion del raster: ~30m/pixel, ver analizar_terreno.py scale=30)
    resolucion_km = abs(transform.a) * 111.0 * math.cos(math.radians(-34.1))  # aprox grados->km a esta latitud
    distancia_px = ndimage.distance_transform_edt(~mascara_agua)
    distancia_km = distancia_px * resolucion_km

    multiplicador = np.ones_like(banda_score, dtype=float)
    dentro_zona = (distancia_km > 0) & (distancia_km <= penetracion_km)
    multiplicador[dentro_zona] = SUPRESION_EN_LA_ORILLA + (1 - SUPRESION_EN_LA_ORILLA) * (
        distancia_km[dentro_zona] / penetracion_km
    )
    multiplicador[mascara_agua] = 1.0  # el agua misma ya tiene su propio score fijo, no se toca

    return banda_score * multiplicador


def score_ajustado_por_rio(lat_referencia=-34.10, lon_referencia=-59.20):
    """Pipeline completo: consulta el viento de hoy y devuelve el score
    de terreno ajustado por el efecto rio dinamico, junto con los
    parametros usados."""
    init_earth_engine()
    viento = obtener_viento_actual(lat_referencia, lon_referencia)
    penetracion_km = calcular_penetracion_km(viento["rumbo_desde_deg"], viento["velocidad_kmh"])

    with rasterio.open(SCORE_TIF) as ds:
        banda = ds.read(1).astype(float)
        transform = ds.transform
        bounds = ds.bounds

    banda_ajustada = aplicar_efecto_rio(banda, transform, penetracion_km)

    return {
        "banda_original": banda,
        "banda_ajustada": banda_ajustada,
        "transform": transform,
        "bounds": bounds,
        "penetracion_km": round(penetracion_km, 1),
        "viento": viento,
    }


def main():
    r = score_ajustado_por_rio()
    v = r["viento"]
    print(f"Viento actual: {v['velocidad_kmh']:.0f} km/h desde {v['rumbo_desde_deg']:.0f}° ({v['hora_local'].strftime('%d/%m %H:%M')} hora local)")
    print(f"Penetracion de la franja fria del rio hoy: {r['penetracion_km']} km tierra adentro")

    diff = r["banda_original"] - r["banda_ajustada"]
    pixeles_afectados = (diff > 0.5).sum()
    print(f"Pixeles con score reducido por el efecto rio: {pixeles_afectados} de {diff.size}")
    print(f"Reduccion promedio en zona afectada: {diff[diff > 0.5].mean():.1f} puntos" if pixeles_afectados else "Sin zona afectada")


if __name__ == "__main__":
    main()
