"""
Genera un mapa claro y legible del score de potencial termico: con
leyenda, puntos de referencia etiquetados (club, hotspots, direcciones
a los otros pueblos), escala, norte, y una flecha de viento actual
(direccion/velocidad reales del dia, via GFS).

Requiere haber corrido antes analizar_terreno.py (genera el
score_termico.tif que este script lee y dibuja).
"""

import math

import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow

from config import init_earth_engine, get_aoi, CLUB_ZARATE, HOTSPOTS_CONOCIDOS
from mapa_utils import CMAP_SCORE, obtener_viento_actual, obtener_temperatura_aire_actual, dibujar_norte, dibujar_escala, rumbo_16_puntas

SCORE_TIF = "data/salida_terreno/score_termico.tif"
OUT_PATH = "data/salida_terreno/mapa_claro.png"


def main():
    init_earth_engine()

    with rasterio.open(SCORE_TIF) as ds:
        banda = ds.read(1).astype(float)
        bounds = ds.bounds

    banda[banda == 0] = np.nan

    fig, ax = plt.subplots(figsize=(12, 12))
    im = ax.imshow(
        banda, cmap=CMAP_SCORE, vmin=0, vmax=100,
        extent=[bounds.left, bounds.right, bounds.bottom, bounds.top],
        origin="upper", interpolation="nearest",
    )

    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.08)
    cbar.set_label("Score de potencial térmico (0-100)\nazul = malo (agua) · rojo = bueno (campo seco/urbano)", fontsize=10)

    club_lat, club_lon = CLUB_ZARATE
    ax.scatter([club_lon], [club_lat], marker="*", s=400, color="white", edgecolor="black", linewidth=1.5, zorder=5)
    ax.annotate(
        "Club de Planeadores\nZárate", (club_lon, club_lat),
        xytext=(-105, 25), textcoords="offset points", fontsize=10, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.9), zorder=6,
        arrowprops=dict(arrowstyle="-", color="black", lw=0.8),
    )

    # Offsets a mano para que las etiquetas de los hotspots (muy cerca del
    # club) no se superpongan entre si ni con la barra de colores.
    offsets_hotspots = {
        "Toyota Argentina (planta)": (-115, -35),
        "Mercedes-Benz Centro Industrial/Logistico": (-160, 15),
    }
    for h in HOTSPOTS_CONOCIDOS:
        ax.scatter([h["lon"]], [h["lat"]], marker="^", s=180, color="cyan", edgecolor="black", linewidth=1.2, zorder=5)
        offset = offsets_hotspots.get(h["nombre"], (-90, -20))
        ax.annotate(
            h["nombre"], (h["lon"], h["lat"]),
            xytext=offset, textcoords="offset points", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.25", fc="lightcyan", ec="black", alpha=0.9), zorder=6,
            arrowprops=dict(arrowstyle="-", color="black", lw=0.8),
        )

    esquinas = {
        "↖ hacia San Andrés\nde Giles": (bounds.left + 0.02, bounds.top - 0.02, "left", "top"),
        "↗ hacia Baradero\n(río Paraná)": (bounds.right - 0.02, bounds.top - 0.02, "right", "top"),
    }
    for texto, (x, y, ha, va) in esquinas.items():
        ax.text(x, y, texto, fontsize=10, ha=ha, va=va, style="italic",
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.75))

    print("Consultando viento y temperatura actual (GFS)...")
    try:
        viento = obtener_viento_actual(club_lat, club_lon)
        clima = obtener_temperatura_aire_actual(club_lat, club_lon)
        cx, cy = club_lon, bounds.bottom + 0.05
        largo = 0.06
        dx = largo * math.sin(math.radians(viento["rumbo_hacia_deg"]))
        dy = largo * math.cos(math.radians(viento["rumbo_hacia_deg"]))
        ax.add_patch(FancyArrow(cx, cy, dx, dy, width=0.004, head_width=0.015, head_length=0.015,
                                  color="black", zorder=7))
        ax.text(
            cx, cy - 0.025,
            f"Viento: {viento['velocidad_kmh']:.0f} km/h desde el {rumbo_16_puntas(viento['rumbo_desde_deg'])} · "
            f"{clima['temperatura_c']:.0f}°C ({clima['descripcion']})\n({viento['hora_local'].strftime('%d/%m %H:%M')} hora local)",
            fontsize=9, ha="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="black", alpha=0.85), zorder=7,
        )
    except Exception as e:
        print(f"No se pudo obtener el viento: {e}")

    dibujar_norte(ax, 0.95, 0.90)
    dibujar_escala(ax, club_lat)

    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.set_title(
        "Copiloto IA Planeadores — Score de potencial térmico\n"
        "Zona Zárate → San Andrés de Giles → Baradero",
        fontsize=14, fontweight="bold",
    )

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150)
    print(f"Mapa guardado: {OUT_PATH}")


if __name__ == "__main__":
    main()
