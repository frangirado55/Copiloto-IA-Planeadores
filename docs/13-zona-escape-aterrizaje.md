# Zona de escape / aterrizaje de emergencia (Módulo nuevo, 24/09)

Idea de Franco: dado dónde estás y tu altura, ¿hasta dónde llegás planeando si no encontrás más térmica, y qué tan seguro es el terreno para un aterrizaje de emergencia ahí dentro? Es seguridad, no rendimiento — un módulo distinto del score de potencial térmico, aunque reutiliza la misma base de datos satelital.

## Por qué es un score distinto al de térmica

El score de potencial térmico (Módulo 1-B) y el de aptitud de aterrizaje miden cosas opuestas en algunos casos: **zona urbana/fábricas es excelente para térmica pero pésima para aterrizar** (postes, casas, cables — score 0 acá, score 90 en el otro). Por eso `scripts/zona_aterrizaje.py` calcula su propio raster (`aptitud_aterrizaje.tif`), no reutiliza `score_termico.tif`.

Tabla de aptitud (0-100, mayor = más seguro para tocar tierra), por clase de ESA WorldCover:

| Clase | Aptitud | Motivo |
|---|---|---|
| Cropland | 85 | La mejor opción en general (si está cosechado — ver limitación abajo) |
| Bare/sparse | 75 | Chato y firme |
| Grassland | 70 | Superficie pareja |
| Moss/lichen | 30 | No aplica a la zona, valor genérico |
| Shrubland | 20 | Riesgoso |
| Wetland | 5 | Terreno blando |
| Tree cover | 5 | No aterrizable |
| Built-up, Water, Snow/ice, Mangroves | 0 | Peligroso / no aplica |

**Limitación conocida**: igual que con arado vs. rastrojo (`08-modulo1b-diseno-terreno.md`), el satélite no distingue la altura del cultivo — un campo de "Cropland" recién sembrado con maíz alto puntúa igual que uno recién cosechado, aunque en la realidad uno es aterrizable y el otro no. Sin imagen de mayor resolución o dato de la época de cosecha, esto queda como aproximación.

## Cálculo del alcance máximo

`decision_maccready.py` suma dos funciones nuevas:
- `mejor_planeo(polar)`: la velocidad y relación de planeo (L/D) que dan el **máximo alcance**, distinto de `velocidad_optima_crucero()` que optimiza velocidad media asumiendo que se va a encontrar otra térmica. Acá el supuesto es el peor caso: no hay más térmica, solo importa llegar lo más lejos posible.
- `alcance_maximo_km(altura_actual_m, polar, factor_seguridad=0.8)`: la distancia planeable, con un 20% de margen de seguridad por defecto (viento en contra, aire descendente, error de estimación).

Con el Blanik: ~28:1 a 89-93 km/h.

## Qué hace `scripts/zona_aterrizaje.py`

1. Calcula el alcance máximo desde la posición/altura actual.
2. Chequea si el club (Zárate) está dentro de ese alcance.
3. Busca, dentro del círculo de alcance, las zonas con mejor aptitud — con un filtro de separación mínima entre resultados (sin esto, las "3 mejores zonas" terminaban siendo el mismo campo repetido 3 veces, el de abajo tuyo y sus vecinos inmediatos).

`scripts/mapa_aterrizaje.py` lo visualiza: círculo de alcance, marcador del club (verde si se llega, rojo si no), y las zonas seguras numeradas.

## Pendiente / no resuelto todavía

- Solo chequea el club como aeródromo conocido — si San Andrés de Giles o Baradero tienen aeroclub propio (mencionado en el brainstorm original de Franco), faltan sus coordenadas para agregarlos como destinos alternativos.
- No considera la dirección del viento para el cono de planeo (hoy es un círculo completo, no un cono orientado a favor/en contra del viento) — el viento ya lo tenemos disponible (GFS, usado en los otros mapas), es una extensión natural para más adelante.
