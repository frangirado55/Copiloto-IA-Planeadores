"""
Mapa de zona de escape: el circulo de alcance maximo de planeo, el
club (alcanzable o no), y las zonas seguras para un aterrizaje de
emergencia dentro de ese circulo.

Uso:
    python3 scripts/mapa_aterrizaje.py --lat -34.30 --lon -59.30 --altura 500
"""

import argparse
import math

import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.colors import LinearSegmentedColormap

from config import CLUB_ZARATE
from zona_aterrizaje import buscar_zona_aterrizaje, APTITUD_TIF
from mapa_utils import dibujar_norte, dibujar_escala

OUT_PATH = "data/salida_terreno/mapa_aterrizaje.png"

CMAP_APTITUD = LinearSegmentedColormap.from_list(
    "aptitud_aterrizaje", ["#8B0000", "#FFAA00", "#FFFF66", "#00AA00"]
)


def generar_mapa(lat, lon, altura_actual_m):
    r = buscar_zona_aterrizaje(lat, lon, altura_actual_m)
    alcance_km = r["alcance_maximo_km"]

    with rasterio.open(APTITUD_TIF) as ds:
        banda = ds.read(1).astype(float)
        bounds = ds.bounds

    margen_deg = (alcance_km / 111.0) * 1.3
    min_lon, max_lon = lon - margen_deg, lon + margen_deg
    min_lat, max_lat = lat - margen_deg, lat + margen_deg

    km_por_grado_lon = 111.0 * math.cos(math.radians(lat))
    ancho_km = (max_lon - min_lon) * km_por_grado_lon
    alto_km = (max_lat - min_lat) * 111.0
    alto_fig = 10
    ancho_fig = max(6, min(16, alto_fig * (ancho_km / alto_km)))

    fig, ax = plt.subplots(figsize=(ancho_fig, alto_fig))
    im = ax.imshow(
        banda, cmap=CMAP_APTITUD, vmin=0, vmax=100, alpha=0.6,
        extent=[bounds.left, bounds.right, bounds.bottom, bounds.top],
        origin="upper", interpolation="nearest", zorder=1,
    )
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.06)
    cbar.set_label("Aptitud para aterrizaje de emergencia\n(rojo=peligroso · verde=seguro)", fontsize=9)

    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    ax.set_aspect(1.0 / math.cos(math.radians(lat)))

    # Circulo de alcance maximo de planeo
    circulo = Circle((lon, lat), alcance_km / km_por_grado_lon, fill=False,
                      edgecolor="blue", linewidth=2.5, linestyle="--", zorder=6)
    ax.add_patch(circulo)

    ax.scatter([lon], [lat], marker="o", s=500, color="dodgerblue", edgecolor="black", linewidth=2, zorder=8)
    ax.annotate(
        f"VOS\n{altura_actual_m:.0f}m",
        xy=(lon, lat), xycoords="data", xytext=(0.02, 0.97), textcoords="axes fraction",
        ha="left", va="top", fontsize=11, fontweight="bold", color="white",
        bbox=dict(boxstyle="round,pad=0.4", fc="dodgerblue", ec="black", alpha=0.92),
        arrowprops=dict(arrowstyle="-", color="dodgerblue", lw=2), zorder=9,
    )

    club_lat, club_lon = CLUB_ZARATE
    color_club = "limegreen" if r["club_alcanzable"] else "red"
    if min_lon <= club_lon <= max_lon and min_lat <= club_lat <= max_lat:
        ax.scatter([club_lon], [club_lat], marker="P", s=400, color=color_club, edgecolor="black", linewidth=2, zorder=8)
        ax.annotate(
            f"CLUB ({'alcanzable' if r['club_alcanzable'] else 'FUERA de alcance'})\n{r['distancia_al_club_km']}km",
            xy=(club_lon, club_lat), xycoords="data", xytext=(0.98, 0.97), textcoords="axes fraction",
            ha="right", va="top", fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", fc=color_club, ec="black", alpha=0.92),
            arrowprops=dict(arrowstyle="-", color=color_club, lw=2), zorder=9,
        )

    for i, z in enumerate(r["zonas_seguras"]):
        ax.scatter([z["lon"]], [z["lat"]], marker="s", s=250, color="lime", edgecolor="black", linewidth=1.5, zorder=7)
        ax.annotate(f"{i+1}", (z["lon"], z["lat"]), ha="center", va="center", fontsize=9, fontweight="bold", zorder=8)

    dibujar_norte(ax, 0.93, 0.90)
    dibujar_escala(ax, lat, km=max(1, round(alcance_km / 3)))

    ax.set_title(
        f"Zona de escape — alcance máximo {alcance_km}km (planeo {r['relacion_planeo']}:1, con 20% margen de seguridad)\n"
        f"Cuadrados verdes numerados = mejores zonas para aterrizaje de emergencia",
        fontsize=10, fontweight="bold",
    )
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
    print(f"Mapa guardado: {OUT_PATH}")
    return r


def main():
    parser = argparse.ArgumentParser(description="Mapa de zona de escape / aterrizaje de emergencia")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--altura", type=float, required=True)
    args = parser.parse_args()
    generar_mapa(args.lat, args.lon, args.altura)


if __name__ == "__main__":
    main()
