"""
Registrar una termica real encontrada en vuelo (Fase de datos, ver
docs/03-plan-trabajo.md y docs/07-proximos-pasos.md). Esto es la
materia prima para calibrar el modelo con la realidad, en vez de solo
teoria/satelite.

Uso interactivo (te va preguntando cada dato):
    python3 scripts/registrar_termica.py

Uso directo (para cargar varias de una sentada, o desde otro script):
    python3 scripts/registrar_termica.py --lat -34.15 --lon -59.20 \
        --altura 900 --fuerza 2.5 --terreno "campo arado" --piloto Franco \
        --notas "cerca de la ruta, buena hasta los 1200m"
"""

import argparse
import csv
import datetime
import os

REGISTRO_CSV = "registro_vuelos/termicas.csv"
CAMPOS = ["fecha", "hora", "lat", "lon", "altura_m", "fuerza_termica_ms", "tipo_terreno_debajo", "piloto", "notas"]


def pedir(nombre, valor_actual, obligatorio=True):
    if valor_actual is not None:
        return valor_actual
    while True:
        respuesta = input(f"{nombre}: ").strip()
        if respuesta or not obligatorio:
            return respuesta


def main():
    parser = argparse.ArgumentParser(description="Registrar una termica encontrada en vuelo")
    parser.add_argument("--fecha", help="YYYY-MM-DD (default: hoy)")
    parser.add_argument("--hora", help="HH:MM (default: ahora)")
    parser.add_argument("--lat", type=float, help="Latitud (ej: -34.150)")
    parser.add_argument("--lon", type=float, help="Longitud (ej: -59.200)")
    parser.add_argument("--altura", type=float, help="Altura en metros donde se encontro")
    parser.add_argument("--fuerza", type=float, help="Fuerza de la termica en m/s")
    parser.add_argument("--terreno", help="Que habia debajo: campo arado, rastrojo, pastura, monte, urbano, ruta, agua, etc.")
    parser.add_argument("--piloto", help="Quien la registra")
    parser.add_argument("--notas", default="", help="Cualquier otra observacion")
    args = parser.parse_args()

    ahora = datetime.datetime.now()
    fecha = args.fecha or ahora.strftime("%Y-%m-%d")
    hora = args.hora or ahora.strftime("%H:%M")
    lat = args.lat if args.lat is not None else float(pedir("Latitud", None))
    lon = args.lon if args.lon is not None else float(pedir("Longitud", None))
    altura = args.altura if args.altura is not None else float(pedir("Altura (m)", None))
    fuerza = args.fuerza if args.fuerza is not None else float(pedir("Fuerza de la termica (m/s)", None))
    terreno = args.terreno or pedir("Tipo de terreno debajo (arado/rastrojo/pastura/monte/urbano/ruta/agua)", None)
    piloto = args.piloto or pedir("Piloto", None, obligatorio=False)
    notas = args.notas or pedir("Notas (opcional)", "", obligatorio=False)

    fila = {
        "fecha": fecha, "hora": hora, "lat": lat, "lon": lon,
        "altura_m": altura, "fuerza_termica_ms": fuerza,
        "tipo_terreno_debajo": terreno, "piloto": piloto, "notas": notas,
    }

    existe = os.path.isfile(REGISTRO_CSV)
    with open(REGISTRO_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS)
        if not existe:
            writer.writeheader()
        writer.writerow(fila)

    print(f"\nRegistrado en {REGISTRO_CSV}:")
    print(fila)


if __name__ == "__main__":
    main()
