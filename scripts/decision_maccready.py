"""
Módulo 3: IA de decisión — quedarse centrando la térmica actual o virar
hacia una térmica candidata, usando teoría MacCready + polar del planeador.

Ver docs/09-modulo3-diseno-decision.md para el diseño completo.
"""

import numpy as np


class PolarPlaneador:
    """Polar de hundimiento (m/s) en funcion de la velocidad (km/h),
    ajustada como parabola.
    """

    def __init__(self, coeficientes, nombre="planeador generico"):
        self.nombre = nombre
        self.coeficientes = coeficientes  # (a, b, c) de a*v^2 + b*v + c

    @classmethod
    def desde_tres_puntos(cls, puntos_v_kmh, puntos_hundimiento_ms, nombre="planeador generico"):
        """Ajusta la parabola a 3 puntos (v_kmh, hundimiento_ms) medidos/publicados."""
        coeficientes = np.polyfit(puntos_v_kmh, puntos_hundimiento_ms, 2)
        return cls(coeficientes, nombre)

    @classmethod
    def desde_puntos_criticos(cls, v_min_hundimiento_kmh, min_hundimiento_ms, v_mejor_planeo_kmh, ld_max, nombre="planeador generico"):
        """Ajusta la parabola usando el punto de minimo hundimiento (que es el
        vertice de la curva: ahi la derivada es cero) calibrado con el punto
        de mejor planeo. Requiere solo 2 datos reales en vez de 3, evitando
        inventar un tercer punto sin verificar.
        """
        v_mejor_planeo_ms = v_mejor_planeo_kmh / 3.6
        hundimiento_mejor_planeo_ms = v_mejor_planeo_ms / ld_max
        # Forma vertice: hundimiento(v) = a*(v - v_vertice)^2 + hundimiento_vertice
        a = (hundimiento_mejor_planeo_ms - min_hundimiento_ms) / (v_mejor_planeo_kmh - v_min_hundimiento_kmh) ** 2
        b = -2 * a * v_min_hundimiento_kmh
        c = min_hundimiento_ms + a * v_min_hundimiento_kmh**2
        return cls((a, b, c), nombre)

    def hundimiento(self, v_kmh):
        """Hundimiento en m/s (positivo = cae) a una velocidad dada en km/h."""
        a, b, c = self.coeficientes
        return a * v_kmh**2 + b * v_kmh + c


# LET L-13 Blanik: planeador de entrenamiento biplaza, comun en escuelas
# (club de Zarate incluido). Datos reales verificados:
#   - Mejor planeo: 28:1 a 93 km/h
#   - Minimo hundimiento: 0.84 m/s a 83 km/h
#   (fuente: https://en.wikipedia.org/wiki/LET_L-13_Blan%C3%ADk)
# No hay un tercer punto verificado a alta velocidad publicado, por eso se
# ajusta con el metodo de 2 puntos criticos (vertice + mejor planeo) en vez
# de inventar un tercer dato. Si en algun momento aparece la polar oficial
# del manual de vuelo con mas puntos, conviene reemplazar esto por
# desde_tres_puntos() con esos valores.
POLAR_BLANIK_L13 = PolarPlaneador.desde_puntos_criticos(
    v_min_hundimiento_kmh=83,
    min_hundimiento_ms=0.84,
    v_mejor_planeo_kmh=93,
    ld_max=28,
    nombre="LET L-13 Blanik (2 puntos reales verificados, sin tercer punto de alta velocidad)",
)


def velocidad_optima_crucero(mc_setting_ms, polar, v_min_kmh=60, v_max_kmh=200, paso_kmh=1):
    """Velocidad de crucero (km/h) que maximiza la velocidad media de
    recorrido, dado un MacCready setting (fuerza esperada de la proxima
    termica, en m/s). Busqueda numerica sobre la polar.
    """
    mejor_v = v_min_kmh
    mejor_velocidad_media = -np.inf
    for v in np.arange(v_min_kmh, v_max_kmh + paso_kmh, paso_kmh):
        hundimiento = polar.hundimiento(v)
        velocidad_media = v * mc_setting_ms / (mc_setting_ms + hundimiento)
        if velocidad_media > mejor_velocidad_media:
            mejor_velocidad_media = velocidad_media
            mejor_v = v
    return mejor_v


def altura_perdida_en_transito(distancia_km, v_kmh, hundimiento_ms):
    """Altura (m) que se pierde volando a v_kmh durante distancia_km,
    con un hundimiento de hundimiento_ms."""
    tiempo_seg = (distancia_km * 1000) / (v_kmh / 3.6)
    return hundimiento_ms * tiempo_seg


def decidir(
    fuerza_actual_ms,
    fuerza_candidata_ms,
    distancia_candidata_km,
    altura_actual_m,
    polar=POLAR_BLANIK_L13,
    margen_seguridad_m=150,
    margen_comodo_m=None,
    umbral_mejora=1.15,
):
    """Recomienda 'QUEDARSE', 'VIRAR' o 'QUEDARSE_Y_LUEGO_VIRAR', con el
    razonamiento y los numeros intermedios usados.

    'QUEDARSE_Y_LUEGO_VIRAR': la candidata es mejor y se llega, pero con
    un margen justo (entre margen_seguridad_m y margen_comodo_m) — en vez
    de partir ya, conviene seguir centrando la termica actual unos
    minutos mas para juntar colchon de altura, y recien ahi virar.
    margen_comodo_m por defecto es el doble de margen_seguridad_m.
    """
    if margen_comodo_m is None:
        margen_comodo_m = margen_seguridad_m * 2

    v_optima = velocidad_optima_crucero(fuerza_candidata_ms, polar)
    hundimiento_v_optima = polar.hundimiento(v_optima)
    altura_perdida = altura_perdida_en_transito(distancia_candidata_km, v_optima, hundimiento_v_optima)
    altura_llegada = altura_actual_m - altura_perdida

    resultado = {
        "velocidad_optima_kmh": round(v_optima, 1),
        "hundimiento_a_v_optima_ms": round(hundimiento_v_optima, 2),
        "altura_perdida_m": round(altura_perdida, 0),
        "altura_estimada_al_llegar_m": round(altura_llegada, 0),
    }

    if altura_llegada < margen_seguridad_m:
        resultado["decision"] = "QUEDARSE"
        resultado["razon"] = (
            f"No se llega con margen de seguridad: altura estimada al llegar "
            f"({altura_llegada:.0f}m) por debajo del margen minimo ({margen_seguridad_m}m)."
        )
        return resultado

    candidata_mejor = fuerza_candidata_ms >= fuerza_actual_ms * umbral_mejora

    if candidata_mejor and altura_llegada < margen_comodo_m:
        # Se llega con seguridad pero justo, no comodo. Calcular cuanto
        # falta girar en la termica actual (mas floja) para juntar el
        # colchon extra antes de partir.
        altura_necesaria = margen_comodo_m + altura_perdida
        altura_extra = altura_necesaria - altura_actual_m
        tiempo_extra_seg = altura_extra / fuerza_actual_ms
        tiempo_extra_min = tiempo_extra_seg / 60

        resultado["decision"] = "QUEDARSE_Y_LUEGO_VIRAR"
        resultado["minutos_extra_antes_de_virar"] = round(tiempo_extra_min, 1)
        resultado["altura_extra_necesaria_m"] = round(altura_extra, 0)
        resultado["razon"] = (
            f"La candidata ({fuerza_candidata_ms:.1f} m/s) es mejor que la actual "
            f"({fuerza_actual_ms:.1f} m/s), pero el margen al llegar ({altura_llegada - margen_seguridad_m:.0f}m "
            f"sobre el minimo) es justo, no comodo. Conviene seguir centrando "
            f"~{tiempo_extra_min:.1f} min mas acá (ganando ~{altura_extra:.0f}m a {fuerza_actual_ms:.1f} m/s) "
            f"y recien ahi virar, para llegar con {margen_comodo_m - margen_seguridad_m:.0f}m de margen extra en vez de justo."
        )
        return resultado

    if candidata_mejor:
        resultado["decision"] = "VIRAR"
        resultado["razon"] = (
            f"La candidata ({fuerza_candidata_ms:.1f} m/s) supera a la actual "
            f"({fuerza_actual_ms:.1f} m/s) por mas del umbral ({(umbral_mejora - 1) * 100:.0f}%), "
            f"y se llega con {altura_llegada - margen_seguridad_m:.0f}m de margen extra (comodo)."
        )
    else:
        resultado["decision"] = "QUEDARSE"
        resultado["razon"] = (
            f"La candidata ({fuerza_candidata_ms:.1f} m/s) no mejora lo suficiente "
            f"a la actual ({fuerza_actual_ms:.1f} m/s) para justificar el cambio."
        )
    return resultado


def imprimir_decision(titulo, resultado):
    print(f"\n--- {titulo} ---")
    print(f"Velocidad optima de crucero: {resultado['velocidad_optima_kmh']} km/h")
    print(f"Hundimiento a esa velocidad: {resultado['hundimiento_a_v_optima_ms']} m/s")
    print(f"Altura que se perderia en transito: {resultado['altura_perdida_m']} m")
    print(f"Altura estimada al llegar: {resultado['altura_estimada_al_llegar_m']} m")
    print(f"DECISION: {resultado['decision']}")
    print(f"Razon: {resultado['razon']}")


def main():
    print("Polar en uso:", POLAR_BLANIK_L13.nombre)

    # Escenario 1: candidata mucho mejor, buena altura -> deberia virar
    r1 = decidir(
        fuerza_actual_ms=1.0,
        fuerza_candidata_ms=3.0,
        distancia_candidata_km=5,
        altura_actual_m=1200,
    )
    imprimir_decision("Escenario 1: candidata mucho mejor, altura de sobra", r1)

    # Escenario 2: candidata mejor pero muy lejos / poca altura -> deberia quedarse
    r2 = decidir(
        fuerza_actual_ms=1.0,
        fuerza_candidata_ms=3.0,
        distancia_candidata_km=15,
        altura_actual_m=500,
    )
    imprimir_decision("Escenario 2: candidata mejor pero sin altura para llegar", r2)

    # Escenario 3: candidata similar a la actual -> deberia quedarse
    r3 = decidir(
        fuerza_actual_ms=2.0,
        fuerza_candidata_ms=2.1,
        distancia_candidata_km=4,
        altura_actual_m=1000,
    )
    imprimir_decision("Escenario 3: candidata similar, no vale la pena cambiar", r3)

    # Escenario 4: candidata bastante mejor pero margen justo -> deberia
    # sugerir quedarse un poco mas y despues virar (no ahora mismo)
    r4 = decidir(
        fuerza_actual_ms=2.5,
        fuerza_candidata_ms=3.5,
        distancia_candidata_km=6,
        altura_actual_m=550,
    )
    imprimir_decision("Escenario 4: candidata mejor pero margen justo -> esperar y virar", r4)


if __name__ == "__main__":
    main()
