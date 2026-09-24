"""
Funciones compartidas para generar mapas (usado por mapa_claro.py y
mapa_decision.py) — colores, norte, escala, viento actual.
"""

import math
import datetime

import ee
from matplotlib.colors import LinearSegmentedColormap

# Mismo esquema de colores en todos los mapas del proyecto: azul=malo,
# amarillo/naranja/rojo=bueno.
CMAP_SCORE = LinearSegmentedColormap.from_list(
    "potencial_termico", ["#0000FF", "#FFFF00", "#FF8800", "#FF0000"]
)


def obtener_viento_actual(lat, lon):
    """Direccion y velocidad de viento a 10m mas reciente disponible (GFS)."""
    punto = ee.Geometry.Point([lon, lat])
    col = (
        ee.ImageCollection("NOAA/GFS0P25")
        .filterDate(
            (datetime.datetime.utcnow() - datetime.timedelta(hours=36)).strftime("%Y-%m-%dT%H:%M:%S"),
            (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%S"),
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


def obtener_temperatura_aire_actual(lat, lon):
    """Temperatura de aire a 2m (grados C) mas reciente disponible (GFS)
    -- distinta de temperatura_actual_c() en patron_horario.py, que mide
    temperatura de SUPERFICIE (GOES) para estimar termicas. Esta es la
    temperatura de aire "de sentir", para dar una nocion general de si
    hace frio o calor, no para el calculo de termicas."""
    punto = ee.Geometry.Point([lon, lat])
    col = (
        ee.ImageCollection("NOAA/GFS0P25")
        .filterDate(
            (datetime.datetime.utcnow() - datetime.timedelta(hours=36)).strftime("%Y-%m-%dT%H:%M:%S"),
            (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%S"),
        )
        .filterBounds(punto)
        .filter(ee.Filter.eq("forecast_hours", 0))
        .sort("system:time_start", False)
    )
    img = col.first()
    temp_c = img.select("temperature_2m_above_ground").reduceRegion(ee.Reducer.first(), punto, 25000).get(
        "temperature_2m_above_ground"
    ).getInfo()
    t_ms = img.get("system:time_start").getInfo()
    hora_utc = datetime.datetime.utcfromtimestamp(t_ms / 1000)
    return {
        "temperatura_c": temp_c,
        "descripcion": descripcion_clima(temp_c),
        "hora_local": hora_utc - datetime.timedelta(hours=3),
    }


def descripcion_clima(temp_c):
    if temp_c < 10:
        return "frío"
    elif temp_c < 18:
        return "fresco"
    elif temp_c < 26:
        return "templado"
    elif temp_c < 32:
        return "caluroso"
    else:
        return "mucho calor"


def rumbo_16_puntas(rumbo_deg):
    rumbos = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]
    idx = round(rumbo_deg / 22.5) % 16
    return rumbos[idx]


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
    ax.plot([x0, x0], [y - (ylim[1] - ylim[0]) * 0.01, y + (ylim[1] - ylim[0]) * 0.01], color="black", linewidth=3)
    ax.plot([x1, x1], [y - (ylim[1] - ylim[0]) * 0.01, y + (ylim[1] - ylim[0]) * 0.01], color="black", linewidth=3)
    ax.text((x0 + x1) / 2, y + (ylim[1] - ylim[0]) * 0.02, f"{km} km", ha="center", fontsize=9)
