"""
Compara lo que el modelo predice (score de terreno -> fuerza estimada)
contra lo que realmente se encontro volando, registrado en
registro_vuelos/termicas.csv via registrar_termica.py.

Esta es la herramienta de calibracion real (Fase 5 del plan, ver
docs/03-plan-trabajo.md): mientras no haya suficientes registros no
dice mucho, pero apenas junten unos cuantos vuelos ya sirve para ver
si el modelo esta sobre o subestimando, y por que tipo de terreno.

Uso:
    python3 scripts/comparar_registro_vs_modelo.py
"""

import csv
import os

import rasterio

from copiloto import score_a_fuerza_ms, distancia_km, SCORE_TIF
from config import HOTSPOTS_CONOCIDOS

REGISTRO_CSV = "registro_vuelos/termicas.csv"


def score_del_modelo_en_punto(lat, lon, banda, transform):
    fila, columna = rasterio.transform.rowcol(transform, lon, lat)
    try:
        score = banda[fila, columna]
    except IndexError:
        return None
    if score <= 0:
        return None
    return float(score)


def hotspot_cercano(lat, lon, radio_km=1.0):
    for h in HOTSPOTS_CONOCIDOS:
        if distancia_km(lat, lon, h["lat"], h["lon"]) <= radio_km:
            return h["nombre"]
    return None


def main():
    if not os.path.isfile(REGISTRO_CSV):
        print(f"No existe {REGISTRO_CSV} todavia. Usa registrar_termica.py primero.")
        return

    with open(REGISTRO_CSV, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))

    if not filas:
        print(f"{REGISTRO_CSV} todavia no tiene registros. Cuando carguen datos de vuelo, corran este script de nuevo.")
        return

    if not os.path.isfile(SCORE_TIF):
        print(f"No existe {SCORE_TIF}. Corre analizar_terreno.py primero.")
        return

    with rasterio.open(SCORE_TIF) as ds:
        banda = ds.read(1)
        transform = ds.transform

        print(f"{'Fecha':<11} {'Terreno real':<16} {'Fuerza real':<12} {'Score modelo':<13} {'Fuerza predicha':<16} {'Diferencia':<10} {'Hotspot?'}")
        diferencias = []
        for fila in filas:
            lat, lon = float(fila["lat"]), float(fila["lon"])
            fuerza_real = float(fila["fuerza_termica_ms"])

            hotspot = hotspot_cercano(lat, lon)
            if hotspot:
                score_modelo = 95
            else:
                score_modelo = score_del_modelo_en_punto(lat, lon, banda, transform)

            if score_modelo is None:
                print(f"{fila['fecha']:<11} {fila['tipo_terreno_debajo']:<16} {fuerza_real:<12} {'sin dato':<13}")
                continue

            fuerza_predicha = score_a_fuerza_ms(score_modelo)
            diferencia = fuerza_predicha - fuerza_real
            diferencias.append(diferencia)

            print(
                f"{fila['fecha']:<11} {fila['tipo_terreno_debajo']:<16} {fuerza_real:<12.1f} "
                f"{score_modelo:<13.0f} {fuerza_predicha:<16.2f} {diferencia:+.2f}      {hotspot or '-'}"
            )

        if diferencias:
            promedio = sum(diferencias) / len(diferencias)
            print(f"\nDiferencia promedio (predicho - real): {promedio:+.2f} m/s sobre {len(diferencias)} registros.")
            if abs(promedio) > 0.5:
                sesgo = "el modelo esta prediciendo mas fuerte de lo real" if promedio > 0 else "el modelo esta prediciendo mas debil de lo real"
                print(f"Sesgo sistematico detectado: {sesgo}. Considerar ajustar SCORE_MIN_MS/SCORE_MAX_MS en copiloto.py.")
            else:
                print("Sin sesgo sistematico grande por ahora (necesita mas datos para ser concluyente).")


if __name__ == "__main__":
    main()
