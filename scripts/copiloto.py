"""
Conecta el Modulo 1-B (lectura de terreno) con el Modulo 3 (decision
MacCready): dado donde estas volando ahora, busca la mejor zona
candidata en el mapa de score de terreno y le pide al Modulo 3 que
decida si conviene quedarse o virar hacia ahi.

Requiere haber corrido antes scripts/analizar_terreno.py (genera
data/salida_terreno/score_termico.tif).
"""

import math
import datetime

import numpy as np
import rasterio

from decision_maccready import POLAR_BLANIK_L13, decidir
from config import HOTSPOTS_CONOCIDOS
from patron_horario import multiplicador_horario

SCORE_TIF = "data/salida_terreno/score_termico.tif"
SCORE_HOTSPOT_CONOCIDO = 95  # score fijo para hotspots confirmados por pilotos

# Conversion score de terreno (0-100) -> fuerza termica estimada (m/s).
# Heuristica de arranque, sin calibrar con vuelos reales todavia (ver
# docs/09-modulo3-diseno-decision.md): score 0 -> 0.5 m/s (casi nada),
# score 100 -> 4.0 m/s (termica fuerte). Lineal entre medio.
SCORE_MIN_MS = 0.5
SCORE_MAX_MS = 4.0


def score_a_fuerza_ms(score_0_100):
    return SCORE_MIN_MS + (score_0_100 / 100.0) * (SCORE_MAX_MS - SCORE_MIN_MS)


def distancia_km(lat1, lon1, lat2, lon2):
    """Distancia aproximada en km entre dos puntos (formula haversine)."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def mejores_candidatas(lat, lon, radio_km=10, excluir_radio_km=0.5, top_n=3, archivo_score=SCORE_TIF):
    """Busca, dentro de radio_km alrededor de (lat, lon), las top_n zonas
    con mejor score de potencial termico (excluyendo un radio chico
    alrededor del punto actual, para no proponer la misma termica en la
    que ya estas).
    """
    with rasterio.open(archivo_score) as ds:
        banda = ds.read(1)
        transform = ds.transform

        filas, columnas = np.indices(banda.shape)
        xs, ys = rasterio.transform.xy(transform, filas.ravel(), columnas.ravel())
        lons = np.array(xs).reshape(banda.shape)
        lats = np.array(ys).reshape(banda.shape)

        # Aproximacion rapida en grados (suficiente para filtrar antes de
        # calcular la distancia real solo sobre los candidatos filtrados)
        deg_radio = radio_km / 111.0
        mascara_bbox = (
            (lats > lat - deg_radio) & (lats < lat + deg_radio)
            & (lons > lon - deg_radio) & (lons < lon + deg_radio)
        )

        candidatos = []
        idx_filas, idx_cols = np.where(mascara_bbox)
        for f, c in zip(idx_filas, idx_cols):
            score = banda[f, c]
            if np.isnan(score) or score <= 0:
                continue
            clat, clon = lats[f, c], lons[f, c]
            d = distancia_km(lat, lon, clat, clon)
            if excluir_radio_km < d <= radio_km:
                candidatos.append({"lat": float(clat), "lon": float(clon), "score": float(score), "distancia_km": d, "fuente": "terreno (satelital)"})

    # Sumar hotspots conocidos (confirmados por pilotos, no por clasificacion
    # satelital) que caigan dentro del radio de busqueda.
    for h in HOTSPOTS_CONOCIDOS:
        d = distancia_km(lat, lon, h["lat"], h["lon"])
        if excluir_radio_km < d <= radio_km:
            candidatos.append({
                "lat": h["lat"], "lon": h["lon"], "score": SCORE_HOTSPOT_CONOCIDO,
                "distancia_km": d, "fuente": f"hotspot conocido: {h['nombre']}",
            })

    candidatos.sort(key=lambda c: c["score"], reverse=True)
    return candidatos[:top_n]


def recomendar(lat, lon, altura_actual_m, fuerza_actual_ms, radio_busqueda_km=10, polar=POLAR_BLANIK_L13, hora_local=None):
    """Pipeline completo: busca candidatas en el mapa de terreno y le pide
    al Modulo 3 que decida sobre la mejor.

    hora_local: hora decimal (ej 14.5 = 14:30) para aplicar el
    multiplicador horario a la fuerza estimada de la candidata (ver
    patron_horario.py). Si no se pasa, usa la hora actual en Argentina.
    La fuerza_actual_ms NO se ajusta por hora porque es un dato real del
    variometro, no una estimacion.
    """
    if hora_local is None:
        hora_local = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).hour + \
                     (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).minute / 60

    candidatas = mejores_candidatas(lat, lon, radio_km=radio_busqueda_km)
    if not candidatas:
        return {"decision": "QUEDARSE", "razon": f"No se encontraron zonas candidatas dentro de {radio_busqueda_km}km."}

    mejor = candidatas[0]
    es_hotspot = mejor["fuente"].startswith("hotspot conocido")
    mult_horario = multiplicador_horario(hora_local, es_hotspot=es_hotspot)
    fuerza_candidata_ms = score_a_fuerza_ms(mejor["score"]) * mult_horario

    resultado = decidir(
        fuerza_actual_ms=fuerza_actual_ms,
        fuerza_candidata_ms=fuerza_candidata_ms,
        distancia_candidata_km=mejor["distancia_km"],
        altura_actual_m=altura_actual_m,
        polar=polar,
    )
    resultado["candidata"] = mejor
    resultado["fuerza_candidata_estimada_ms"] = round(fuerza_candidata_ms, 2)
    resultado["multiplicador_horario"] = round(mult_horario, 2)
    resultado["hora_local_usada"] = round(hora_local, 2)
    resultado["candidatas_evaluadas"] = len(candidatas)
    return resultado


def main():
    # Ejemplo: planeador centrando una termica floja cerca del club, con
    # buena altura, buscando alternativas en 10km a la redonda.
    lat, lon = -34.10, -59.15
    altura_actual_m = 1200
    fuerza_actual_ms = 1.2

    print(f"Posicion actual: {lat}, {lon} | altura: {altura_actual_m}m | termica actual: {fuerza_actual_ms} m/s")
    print("Buscando candidatas en el mapa de terreno (radio 10km)...\n")

    resultado = recomendar(lat, lon, altura_actual_m, fuerza_actual_ms)

    print(f"Candidatas evaluadas dentro del radio: {resultado.get('candidatas_evaluadas', 0)}")
    if "candidata" in resultado:
        c = resultado["candidata"]
        print(f"Mejor candidata: {c['lat']:.4f}, {c['lon']:.4f} — score {c['score']:.0f}/100, a {c['distancia_km']:.1f}km ({c['fuente']})")
        print(f"Hora usada: {resultado['hora_local_usada']}hs | multiplicador horario: {resultado['multiplicador_horario']}")
        print(f"Fuerza estimada de la candidata (ya ajustada por hora): {resultado['fuerza_candidata_estimada_ms']} m/s")
    print(f"\nDECISION: {resultado['decision']}")
    print(f"Razon: {resultado['razon']}")


if __name__ == "__main__":
    main()
