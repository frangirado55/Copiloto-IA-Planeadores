"""
Multiplicador de fuerza termica segun la hora del dia — basado en la
curva de temperatura REAL medida con GOES-19 el 17/09/2026 (dia
despejado), ver docs/10-patron-diurno-temperatura.md.

Sin esto, el score de terreno le da la misma fuerza estimada a un
campo seco a las 8am que a las 5pm, lo cual no es realista: el suelo
recien empieza a calentar bien pasada la media manana, pica entre las
13:30-14:00, y se enfria de nuevo hacia el atardecer.

Dos curvas separadas porque la medicion mostro que la zona urbana/
industrial (fabricas, rutas) se mantiene mas caliente que el campo
abierto al atardecer (efecto isla de calor) — asi que un hotspot
conserva mejor puntaje mas tarde en el dia que un campo suelto.
"""

import numpy as np

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
    """Devuelve un multiplicador 0-1 para aplicar a la fuerza termica
    estimada, segun la hora del dia (formato decimal, ej 14.5 = 14:30).
    Fuera del rango 5-23hs (de noche) el multiplicador es 0.
    """
    if hora_decimal < 5 or hora_decimal > 23:
        return 0.0
    tabla = TEMPERATURA_URBANA_POR_HORA if es_hotspot else TEMPERATURA_RURAL_POR_HORA
    return _interpolar(tabla, hora_decimal)
