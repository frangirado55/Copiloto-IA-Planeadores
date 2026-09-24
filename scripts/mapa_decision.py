"""
Mapa de decision: a diferencia de mapa_claro.py (que muestra toda la
zona), este mapa esta enfocado en un vuelo puntual — muestra DONDE
ESTA EL PILOTO ahora, CUAL ES LA TERMICA SUGERIDA por el Modulo 3, y
la ruta entre las dos, con distancia y rumbo. Es el mapa que se mira
en vuelo, no el mapa de referencia general.

Uso:
    python3 scripts/mapa_decision.py --lat -34.10 --lon -59.15 \
        --altura 1200 --fuerza 1.2

Requiere haber corrido antes analizar_terreno.py.
"""

import argparse
import math

import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow

from config import init_earth_engine, CLUB_ZARATE
from copiloto import recomendar, SCORE_TIF
from mapa_utils import CMAP_SCORE, obtener_viento_actual, obtener_temperatura_aire_actual, dibujar_norte, dibujar_escala, rumbo_16_puntas

OUT_PATH = "data/salida_terreno/mapa_decision.png"


def rumbo_y_distancia(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    distancia_km = 2 * R * math.asin(math.sqrt(a))
    rumbo = (math.degrees(math.atan2(
        math.sin(dlon) * math.cos(p2),
        math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dlon),
    ))) % 360
    return rumbo, distancia_km


def generar_mapa(lat, lon, altura_actual_m, fuerza_actual_ms, radio_busqueda_km=10):
    init_earth_engine()

    print("Calculando recomendacion...")
    resultado = recomendar(lat, lon, altura_actual_m, fuerza_actual_ms, radio_busqueda_km=radio_busqueda_km)

    with rasterio.open(SCORE_TIF) as ds:
        banda = ds.read(1).astype(float)
        bounds = ds.bounds
    banda[banda == 0] = np.nan

    # Calcular la extension del zoom ANTES de crear la figura, para poder
    # armar un figsize con la proporcion real (ancho/alto en km, no en
    # grados) y que el mapa ocupe toda la figura sin bandas en blanco.
    if "candidata" in resultado:
        c = resultado["candidata"]
        clat, clon = c["lat"], c["lon"]
        _, distancia_km_preview = rumbo_y_distancia(lat, lon, clat, clon)
        margen_zoom = max(distancia_km_preview / 111.0 * 0.5, 0.03)
        min_lon, max_lon = min(lon, clon) - margen_zoom, max(lon, clon) + margen_zoom
        min_lat, max_lat = min(lat, clat) - margen_zoom, max(lat, clat) + margen_zoom
    else:
        margen_zoom = radio_busqueda_km / 111.0 * 1.3
        min_lon, max_lon = lon - margen_zoom, lon + margen_zoom
        min_lat, max_lat = lat - margen_zoom, lat + margen_zoom

    km_por_grado_lon = 111.0 * math.cos(math.radians(lat))
    ancho_km = (max_lon - min_lon) * km_por_grado_lon
    alto_km = (max_lat - min_lat) * 111.0
    proporcion = ancho_km / alto_km
    alto_fig = 10
    ancho_fig = max(6, min(18, alto_fig * proporcion))

    fig, ax = plt.subplots(figsize=(ancho_fig, alto_fig))
    im = ax.imshow(
        banda, cmap=CMAP_SCORE, vmin=0, vmax=100, alpha=0.55,
        extent=[bounds.left, bounds.right, bounds.bottom, bounds.top],
        origin="upper", interpolation="nearest", zorder=1,
    )
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.06)
    cbar.set_label("Score de terreno (fondo, de referencia)", fontsize=9)

    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    ax.set_aspect(1.0 / math.cos(math.radians(lat)))

    # Posicion del piloto: marcador bien visible, imposible de confundir.
    # La caja de info va anclada en una esquina fija (no pegada al punto),
    # con una flecha que apunta al punto real — asi nunca se corta contra
    # el borde de la figura, sin importar donde caiga el punto en el mapa.
    ax.scatter(
        [lon], [lat], marker="o", s=550, color="dodgerblue", edgecolor="black",
        linewidth=2.5, zorder=8, label="Vos (posición actual)",
    )
    ax.annotate(
        f"VOS\n{altura_actual_m:.0f}m · térmica actual {fuerza_actual_ms:.1f} m/s",
        xy=(lon, lat), xycoords="data",
        xytext=(0.02, 0.97), textcoords="axes fraction",
        ha="left", va="top", fontsize=11, fontweight="bold", color="white",
        bbox=dict(boxstyle="round,pad=0.4", fc="dodgerblue", ec="black", alpha=0.92),
        arrowprops=dict(arrowstyle="-", color="dodgerblue", lw=2), zorder=9,
    )

    if "candidata" in resultado:
        c = resultado["candidata"]
        clat, clon = c["lat"], c["lon"]
        rumbo, distancia_km = rumbo_y_distancia(lat, lon, clat, clon)

        estilos_decision = {
            "VIRAR": ("limegreen", "-"),
            "QUEDARSE_Y_LUEGO_VIRAR": ("orange", ":"),
            "QUEDARSE": ("gray", "--"),
        }
        color_decision, linea_decision = estilos_decision.get(resultado["decision"], ("gray", "--"))

        ax.annotate(
            "", xy=(clon, clat), xytext=(lon, lat),
            arrowprops=dict(arrowstyle="-|>", color=color_decision, lw=3.5, linestyle=linea_decision),
            zorder=7,
        )

        ax.scatter(
            [clon], [clat], marker="*", s=700, color=color_decision, edgecolor="black",
            linewidth=2, zorder=8,
        )
        nombre_fuente = c["fuente"]
        if len(nombre_fuente) > 28:
            nombre_fuente = nombre_fuente.split(":")[-1].strip()[:28]
        ax.annotate(
            f"CANDIDATA ({nombre_fuente})\nscore {c['score']:.0f}/100 · ~{resultado['fuerza_candidata_estimada_ms']:.1f} m/s estimado",
            xy=(clon, clat), xycoords="data",
            xytext=(0.98, 0.03), textcoords="axes fraction",
            ha="right", va="bottom", fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", fc=color_decision, ec="black", alpha=0.92),
            arrowprops=dict(arrowstyle="-", color=color_decision, lw=2), zorder=9,
        )

        # Etiqueta de distancia/rumbo en el punto medio de la flecha
        mid_lon, mid_lat = (lon + clon) / 2, (lat + clat) / 2
        ax.annotate(
            f"{distancia_km:.1f} km\nrumbo {rumbo:.0f}° ({rumbo_16_puntas(rumbo)})",
            (mid_lon, mid_lat), fontsize=10, fontweight="bold", ha="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color_decision, linewidth=2, alpha=0.95),
            zorder=9,
        )

    print("Consultando viento actual...")
    try:
        viento = obtener_viento_actual(lat, lon)
        clima = obtener_temperatura_aire_actual(lat, lon)
        # Zona libre: arriba al centro (esquinas ya ocupadas por VOS,
        # norte y candidata).
        largo = (max_lon - min_lon) * 0.06
        cx = min_lon + (max_lon - min_lon) * 0.5
        cy = min_lat + (max_lat - min_lat) * 0.94
        dx = largo * math.sin(math.radians(viento["rumbo_hacia_deg"]))
        dy = largo * math.cos(math.radians(viento["rumbo_hacia_deg"]))
        ax.add_patch(FancyArrow(cx - dx / 2, cy - dy / 2, dx, dy, width=largo * 0.06, head_width=largo * 0.3, head_length=largo * 0.3,
                                  color="black", zorder=7))
        ax.text(
            cx, cy - (max_lat - min_lat) * 0.06,
            f"Viento: {viento['velocidad_kmh']:.0f} km/h desde el {rumbo_16_puntas(viento['rumbo_desde_deg'])} · "
            f"{clima['temperatura_c']:.0f}°C ({clima['descripcion']})",
            fontsize=8, ha="center",
            bbox=dict(boxstyle="round,pad=0.25", fc="lightyellow", ec="black", alpha=0.85), zorder=7,
        )
    except Exception as e:
        print(f"No se pudo obtener el viento: {e}")

    dibujar_norte(ax, 0.93, 0.90)
    dibujar_escala(ax, lat, km=max(1, round(max(max_lon - min_lon, max_lat - min_lat) * 111 / 4)))

    colores_titulo = {"VIRAR": "#d4f7d4", "QUEDARSE_Y_LUEGO_VIRAR": "#ffe4b5", "QUEDARSE": "#e8e8e8"}
    decision_color_fondo = colores_titulo.get(resultado["decision"], "#e8e8e8")
    ax.set_title(
        f"DECISIÓN: {resultado['decision']}\n{resultado['razon']}",
        fontsize=12, fontweight="bold", wrap=True,
        bbox=dict(boxstyle="round,pad=0.5", fc=decision_color_fondo, ec="black"),
    )
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150)
    print(f"\nMapa guardado: {OUT_PATH}")
    print(f"Decision: {resultado['decision']}")
    print(f"Razon: {resultado['razon']}")


def main():
    parser = argparse.ArgumentParser(description="Mapa de decision: donde estas y hacia donde conviene ir")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--altura", type=float, required=True, help="Altura actual en metros")
    parser.add_argument("--fuerza", type=float, required=True, help="Fuerza de la termica actual en m/s")
    parser.add_argument("--radio", type=float, default=10, help="Radio de busqueda de candidatas en km")
    args = parser.parse_args()
    generar_mapa(args.lat, args.lon, args.altura, args.fuerza, args.radio)


if __name__ == "__main__":
    main()
