"""
Multiplicador de fuerza termica segun cuanto calor hay — PRIORIDAD:
medir la temperatura real de AHORA via GOES-19 (igual que se hace con
el viento en mapa_utils.py). Si no hay dato disponible (nublado, sin
imagen reciente, falla de red), cae a una curva de respaldo basada en
la hora del dia, medida una vez en un dia despejado (17/09/2026) —
ver docs/10-patron-diurno-temperatura.md.

Sin esto, el score de terreno le da la misma fuerza estimada a un
campo seco a las 8am que a las 5pm (o un dia nublado que uno soleado),
lo cual no es realista.

Dos curvas/mediciones separadas (rural vs urbana) porque se detecto
que la zona urbana/industrial (fabricas, rutas) se mantiene mas
caliente que el campo abierto al atardecer (efecto isla de calor) —
asi que un hotspot conserva mejor puntaje mas tarde en el dia.
"""

import datetime

import numpy as np
import ee

# Hora local (Argentina) -> temperatura de superficie medida (C).
# Extraido de la corrida real del 17/09/2026 (dia despejado, confirmado
# comparando varias fechas - ver docs/10). Se normaliza a 0-1 abajo.
TEMPERATURA_RURAL_POR_HORA = {
    5: -1.5, 6: -3.5, 7: 4.1, 8: 9.9, 9: 14.8, 10: 19.5, 11: 23.8,
    12: 27.1, 13: 29.3, 14: 30.4, 15: 29.0, 16: 26.1, 17: 22.3,
    18: 18.2, 19: 12.5, 20: 11.4, 21: 6.5, 22: 5.0, 23: 3.0,
}
TEMPERATURA_URBANA_POR_HORA = {
    5: -2.4, 6: -0.9, 7: 5.5, 8: 10.2, 9: 14.4, 10: 19.8, 11: 24.3,
    12: 27.1, 13: 29.5, 14: 30.2, 15: 28.6, 16: 26.3, 17: 22.8,
    18: 18.6, 19: 14.6, 20: 13.1, 21: 7.4, 22: 6.0, 23: 4.5,
}

# Normalizacion: 0C o menos -> multiplicador 0 (sin potencial termico),
# el maximo medido (~30.4C) -> multiplicador 1 (pico del dia).
TEMP_MIN_NORMALIZACION = 0.0
TEMP_MAX_NORMALIZACION = 30.4


def _interpolar(tabla, hora_decimal):
    horas = sorted(tabla.keys())
    if hora_decimal <= horas[0]:
        temp = tabla[horas[0]]
    elif hora_decimal >= horas[-1]:
        temp = tabla[horas[-1]]
    else:
        temp = float(np.interp(hora_decimal, horas, [tabla[h] for h in horas]))
    mult = (temp - TEMP_MIN_NORMALIZACION) / (TEMP_MAX_NORMALIZACION - TEMP_MIN_NORMALIZACION)
    return float(np.clip(mult, 0.0, 1.0))


def multiplicador_horario(hora_decimal, es_hotspot=False):
    """[Respaldo] Multiplicador 0-1 basado en la curva de un solo dia
    medido, sin ver el clima real de hoy. Se usa solo si la medicion en
    vivo (temperatura_actual_c) no esta disponible.
    """
    if hora_decimal < 5 or hora_decimal > 23:
        return 0.0
    tabla = TEMPERATURA_URBANA_POR_HORA if es_hotspot else TEMPERATURA_RURAL_POR_HORA
    return _interpolar(tabla, hora_decimal)


def temperatura_actual_c(lat, lon, radio_m=5000, ventana_minutos=40):
    """Temperatura de superficie AHORA (grados C), midiendo en vivo con
    GOES-19 (banda CMI_C14, igual metodologia que docs/10: aplicar
    escala/offset de la imagen, filtrar por calidad DQF, y tomar el
    pixel mas caliente del radio para evitar que una nube de paso
    contamine la lectura). Devuelve None si no hay imagen reciente o
    todo esta nublado en la zona (en ese caso, usar multiplicador_horario
    como respaldo).
    """
    try:
        punto = ee.Geometry.Point([lon, lat]).buffer(radio_m)
        col = (
            ee.ImageCollection("NOAA/GOES/19/MCMIPF")
            .filterDate(
                (datetime.datetime.utcnow() - datetime.timedelta(minutes=ventana_minutos)).strftime("%Y-%m-%dT%H:%M:%S"),
                (datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S"),
            )
            .filterBounds(punto)
            .sort("system:time_start", False)
        )
        img = col.first()
        escala = img.get("CMI_C14_scale")
        offset = img.get("CMI_C14_offset")
        dqf_ok = img.select("DQF_C14").eq(0)
        bt_kelvin = img.select("CMI_C14").multiply(ee.Number(escala)).add(ee.Number(offset)).updateMask(dqf_ok)
        maxval = bt_kelvin.reduceRegion(ee.Reducer.max(), punto, 2000, bestEffort=True).get("CMI_C14").getInfo()
        if maxval is None:
            return None
        return maxval - 273.15
    except Exception:
        return None


def multiplicador_en_vivo(lat, lon, es_hotspot=False, hora_decimal=None):
    """Multiplicador 0-1 priorizando la temperatura real de AHORA
    (GOES-19). Si no hay dato disponible, cae al respaldo por hora del
    dia. Devuelve (multiplicador, fuente) donde fuente es 'en_vivo' o
    'respaldo_por_hora'.
    """
    temp_c = temperatura_actual_c(lat, lon)
    if temp_c is not None:
        mult = (temp_c - TEMP_MIN_NORMALIZACION) / (TEMP_MAX_NORMALIZACION - TEMP_MIN_NORMALIZACION)
        return float(np.clip(mult, 0.0, 1.0)), "en_vivo"

    if hora_decimal is None:
        hora_decimal = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).hour + \
                       (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).minute / 60
    return multiplicador_horario(hora_decimal, es_hotspot=es_hotspot), "respaldo_por_hora"
