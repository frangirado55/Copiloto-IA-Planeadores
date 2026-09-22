"""
Genera un mapa claro y legible del score de potencial termico: con
leyenda, puntos de referencia etiquetados (club, hotspots, direcciones
a los otros pueblos), escala, norte, y una flecha de viento actual
(direccion/velocidad reales del dia, via GFS).

Requiere haber corrido antes analizar_terreno.py (genera el
score_termico.tif que este script lee y dibuja).
"""

import math
import datetime

import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrow

import ee
from config import init_earth_engine, get_aoi, CLUB_ZARATE, HOTSPOTS_CONOCIDOS

SCORE_TIF = "data/salida_terreno/score_termico.tif"
OUT_PATH = "data/salida_terreno/mapa_claro.png"

# Mismo esquema de colores que las salidas de Earth Engine (azul=malo,
# amarillo/naranja/rojo=bueno), para que todos los mapas del proyecto
# se lean igual.
CMAP_SCORE = LinearSegmentedColormap.from_list(
    "potencial_termico", ["#0000FF", "#FFFF00", "#FF8800", "#FF0000"]
)


def obtener_viento_actual(lat, lon):
    """Direccion y velocidad de viento a 10m mas reciente disponible (GFS)."""
    punto = ee.Geometry.Point([lon, lat])
    col = (
        ee.ImageCollection("NOAA/GFS0P25")
        .filterDate(
            (datetime.datetime.utcnow() - datetime.timedelta(hours=12)).strftime("%Y-%m-%d"),
            (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).strftime("%Y-%m-%d"),
        )
        .filterBounds(punto)
        .filter(ee.Filter.eq("forecast_hours", 0))
        .sort("system:time_start", False)
    )
    img = col.first()
    valores = img.select(
        ["u_component_of_wind_10m_above_ground", "v_component_of_wind_10m_above_ground"]
    ).reduceRegion(ee.Reducer.first(), punto, 25000).getInfo()
    u = valores["u_component_of_wind_10m_above_ground"]
    v = valores["v_component_of_wind_10m_above_ground"]
    velocidad_kmh = math.sqrt(u**2 + v**2) * 3.6
    rumbo_hacia = (90 - math.degrees(math.atan2(v, u))) % 360  # hacia donde sopla
    rumbo_desde = (rumbo_hacia + 180) % 360  # de donde viene (convencion meteorologica)
    t_ms = img.get("system:time_start").getInfo()
    hora_utc = datetime.datetime.utcfromtimestamp(t_ms / 1000)
    return {
        "velocidad_kmh": velocidad_kmh,
        "rumbo_hacia_deg": rumbo_hacia,
        "rumbo_desde_deg": rumbo_desde,
        "hora_local": hora_utc - datetime.timedelta(hours=3),
    }


def dibujar_norte(ax, x, y, tamano=0.03):
    ax.annotate(
        "N", xy=(x, y + tamano), xycoords="axes fraction",
        ha="center", fontsize=13, fontweight="bold", color="black",
    )
    ax.annotate(
        "", xy=(x, y + tamano * 0.8), xytext=(x, y - tamano * 0.5),
        xycoords="axes fraction",
        arrowprops=dict(arrowstyle="-|>", color="black", lw=2),
    )


def dibujar_escala(ax, lat_centro, x0_frac=0.05, y_frac=0.05, km=10):
    xlim = ax.get_xlim()
    ancho_total_deg = xlim[1] - xlim[0]
    km_por_grado = 111.0 * math.cos(math.radians(lat_centro))
    largo_deg = km / km_por_grado
    x0 = xlim[0] + x0_frac * ancho_total_deg
    x1 = x0 + largo_deg
    ylim = ax.get_ylim()
    y = ylim[0] + y_frac * (ylim[1] - ylim[0])
    ax.plot([x0, x1], [y, y], color="black", linewidth=3)
    ax.plot([x0, x0], [y - 0.01, y + 0.01], color="black", linewidth=3)
    ax.plot([x1, x1], [y - 0.01, y + 0.01], color="black", linewidth=3)
    ax.text((x0 + x1) / 2, y + 0.015, f"{km} km", ha="center", fontsize=9)


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

    print("Consultando viento actual (GFS)...")
    try:
        viento = obtener_viento_actual(club_lat, club_lon)
        cx, cy = club_lon, bounds.bottom + 0.05
        largo = 0.06
        dx = largo * math.sin(math.radians(viento["rumbo_hacia_deg"]))
        dy = largo * math.cos(math.radians(viento["rumbo_hacia_deg"]))
        ax.add_patch(FancyArrow(cx, cy, dx, dy, width=0.004, head_width=0.015, head_length=0.015,
                                  color="black", zorder=7))
        rumbos = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]
        idx = round(viento["rumbo_desde_deg"] / 22.5) % 16
        ax.text(
            cx, cy - 0.025,
            f"Viento: {viento['velocidad_kmh']:.0f} km/h desde el {rumbos[idx]}\n({viento['hora_local'].strftime('%d/%m %H:%M')} hora local)",
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
