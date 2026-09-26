"""
Zonas de escape / cono de planeo seguro (idea de Franco, sección 3 de
su brainstorm del 24/09): dado dónde estás y tu altura, hasta dónde
llegás planeando si no encontrás más térmica, y qué tan apto para
aterrizar de emergencia es el campo dentro de ese alcance.

Reutiliza el mismo terreno clasificado que el Módulo 1-B (ESA
WorldCover), pero con un score DISTINTO: acá lo que importa no es
"da térmica" sino "es seguro para tocar tierra" — campo abierto y
chato puntúa alto, agua/monte/urbano puntúan bajísimo (aunque el
urbano sea buenísimo para térmica, es letal para aterrizar).

Uso:
    python3 scripts/zona_aterrizaje.py --lat -34.15 --lon -59.20 --altura 500
"""

import argparse
import os

import ee
import numpy as np
import rasterio

from config import init_earth_engine, get_aoi, CLUB_ZARATE
from analizar_terreno import get_worldcover
from decision_maccready import POLAR_ASK13, alcance_maximo_km, mejor_planeo
from copiloto import distancia_km

OUTPUT_DIR = "data/salida_terreno"
APTITUD_TIF = os.path.join(OUTPUT_DIR, "aptitud_aterrizaje.tif")

# Score de aptitud para aterrizaje de emergencia (0-100, mayor = mas
# seguro para tocar tierra) — nota que esto NO es el mismo score que
# el de potencial termico: built-up es excelente para termica pero
# pesimo para aterrizar (postes, casas, cables), y viceversa un campo
# recien arado puede ser buena termica pero superficie irregular.
APTITUD_ATERRIZAJE = {
    10: 5,    # Tree cover (monte) - no aterrizable
    20: 20,   # Shrubland - riesgoso
    30: 70,   # Grassland (pastura) - buena opcion, superficie pareja
    40: 85,   # Cropland - la mejor opcion en general si esta cosechado (no se puede
              # distinguir altura de cultivo desde satelite - ver limitacion abajo)
    50: 0,    # Built-up (urbano/rutas/fabricas) - PELIGROSO, obstaculos
    60: 75,   # Bare / sparse vegetation - buena opcion, chato y firme
    70: 0,    # Snow / ice - no aplica
    80: 0,    # Water - PELIGROSO
    90: 5,    # Herbaceous wetland - riesgoso, terreno blando
    95: 0,    # Mangroves - no aplica
    100: 30,  # Moss and lichen - no aplica, valor generico
}


def calcular_aptitud_aterrizaje(worldcover):
    from_classes = list(APTITUD_ATERRIZAJE.keys())
    to_scores = list(APTITUD_ATERRIZAJE.values())
    return worldcover.remap(from_classes, to_scores, 0).rename("aptitud_aterrizaje")


def generar_mapa_aptitud():
    """Genera y exporta el GeoTIFF de aptitud de aterrizaje para toda la
    zona (se corre una vez, como analizar_terreno.py; despues se
    consulta localmente)."""
    init_earth_engine()
    aoi = get_aoi()
    worldcover = get_worldcover(aoi)
    aptitud = calcular_aptitud_aterrizaje(worldcover)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    import geemap
    print("Exportando GeoTIFF de aptitud de aterrizaje...")
    geemap.ee_export_image(
        aptitud, filename=APTITUD_TIF, scale=30, region=aoi, file_per_band=False,
    )
    print(f"Guardado: {APTITUD_TIF}")


def buscar_zona_aterrizaje(lat, lon, altura_actual_m, polar=POLAR_ASK13, factor_seguridad=0.8, top_n=3):
    """Dentro del alcance maximo de planeo, busca las mejores zonas para
    un aterrizaje de emergencia, y si el club queda al alcance."""
    alcance_km = alcance_maximo_km(altura_actual_m, polar, factor_seguridad)
    v_mejor_planeo, ld = mejor_planeo(polar)

    club_lat, club_lon = CLUB_ZARATE
    dist_club_km = distancia_km(lat, lon, club_lat, club_lon)
    club_alcanzable = dist_club_km <= alcance_km

    zonas = []
    if os.path.isfile(APTITUD_TIF):
        with rasterio.open(APTITUD_TIF) as ds:
            banda = ds.read(1)
            transform = ds.transform
            filas, columnas = np.indices(banda.shape)
            xs, ys = rasterio.transform.xy(transform, filas.ravel(), columnas.ravel())
            lons = np.array(xs).reshape(banda.shape)
            lats = np.array(ys).reshape(banda.shape)

            deg_radio = (alcance_km / 111.0) * 1.05
            mascara = (
                (lats > lat - deg_radio) & (lats < lat + deg_radio)
                & (lons > lon - deg_radio) & (lons < lon + deg_radio)
            )
            idx_f, idx_c = np.where(mascara)
            for f, c in zip(idx_f, idx_c):
                score = banda[f, c]
                if np.isnan(score) or score < 60:  # solo zonas razonablemente seguras
                    continue
                clat, clon = lats[f, c], lons[f, c]
                d = distancia_km(lat, lon, clat, clon)
                if d <= alcance_km:
                    zonas.append({"lat": float(clat), "lon": float(clon), "aptitud": float(score), "distancia_km": d})
            zonas.sort(key=lambda z: (-z["aptitud"], z["distancia_km"]))

    # Filtrar duplicados cercanos: sin esto, las top_n terminan siendo
    # practicamente el mismo pixel repetido (el campo justo debajo tuyo
    # y sus vecinos inmediatos, todos con la misma aptitud).
    separacion_minima_km = max(alcance_km * 0.15, 1.0)
    zonas_diversas = []
    for z in zonas:
        if all(distancia_km(z["lat"], z["lon"], zd["lat"], zd["lon"]) >= separacion_minima_km for zd in zonas_diversas):
            zonas_diversas.append(z)
        if len(zonas_diversas) >= top_n:
            break
    zonas = zonas_diversas

    return {
        "alcance_maximo_km": round(alcance_km, 1),
        "velocidad_mejor_planeo_kmh": v_mejor_planeo,
        "relacion_planeo": round(ld, 1),
        "club_alcanzable": club_alcanzable,
        "distancia_al_club_km": round(dist_club_km, 1),
        "zonas_seguras": zonas[:top_n],
    }


def main():
    parser = argparse.ArgumentParser(description="Zona de escape: hasta donde llego planeando y donde es seguro aterrizar")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--altura", type=float, required=True)
    parser.add_argument("--generar-mapa", action="store_true", help="Regenerar el GeoTIFF de aptitud (correr una vez, tarda unos minutos)")
    args = parser.parse_args()

    if args.generar_mapa or not os.path.isfile(APTITUD_TIF):
        generar_mapa_aptitud()

    r = buscar_zona_aterrizaje(args.lat, args.lon, args.altura)

    print(f"\nAltura actual: {args.altura}m")
    print(f"Mejor relacion de planeo: {r['relacion_planeo']}:1 a {r['velocidad_mejor_planeo_kmh']} km/h")
    print(f"Alcance maximo (con 20% de margen de seguridad): {r['alcance_maximo_km']} km")
    print(f"\nClub (Zarate) a {r['distancia_al_club_km']}km: {'ALCANZABLE' if r['club_alcanzable'] else 'FUERA DE ALCANCE'}")

    print(f"\nZonas seguras dentro del alcance:")
    if not r["zonas_seguras"]:
        print("  Ninguna encontrada (o falta generar el mapa de aptitud con --generar-mapa)")
    for z in r["zonas_seguras"]:
        print(f"  {z['lat']:.4f}, {z['lon']:.4f} — aptitud {z['aptitud']:.0f}/100, a {z['distancia_km']:.1f}km")


if __name__ == "__main__":
    main()
