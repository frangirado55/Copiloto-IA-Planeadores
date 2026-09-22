# Zona de vuelo: Zárate → San Andrés de Giles → Baradero

## Club

**Club de Planeadores Zárate** — Aeródromo de Zárate, Ruta Nacional 9 y Av. Antártida Argentina, Zárate, Buenos Aires.
Coordenadas aproximadas del aeródromo: **-34.120, -59.084**

## Cuadrante habitual de vuelo (aprox.)

Rectángulo de ~60×60 km cubriendo:
- **Esquina sur-este** (club): -34.12, -59.08
- **Esquina norte** (hacia Baradero, sobre el Paraná): -33.80, -59.50
- **Esquina oeste** (hacia San Andrés de Giles): -34.45, -59.45

## Características del terreno (relevantes para el Módulo 1 vía análisis de terreno)

- **Pampa húmeda típica**: relieve prácticamente plano, variaciones de pocos metros en decenas de km. El dato de elevación (DEM/SRTM) va a pesar poco acá comparado con zonas serranas.
- **Variable más relevante: tipo de cultivo/uso del suelo.** Campo recién arado y seco calienta muy distinto a una pastura o a un monte de forestación — esta es la señal principal a clasificar desde imágenes satelitales.
- **Cercanía al río Paraná y al Delta** (zona norte, hacia Baradero): el agua enfría el aire cerca y tiende a inhibir térmicas en esa franja. Tierra firme más al oeste (hacia Giles) calienta más parejo.
- **Zonas urbanizadas y rutas** (Ruta 9 en particular): disparador clásico de térmica por contraste térmico asfalto/campo.

## Fuentes de datos para bajar (gratuitas)

- **Imágenes ópticas de terreno**: Sentinel-2 vía [Copernicus Data Space](https://dataspace.copernicus.eu/) (requiere registro gratuito) o Google Earth Engine (requiere cuenta Google).
- **Modelo de elevación**: SRTM vía [USGS EarthExplorer](https://earthexplorer.usgs.gov/) o directamente desde Earth Engine.
- **Red FLARM/OGN**: consultar cobertura en vivo en [glidernet.org](http://www.glidernet.org) centrando el mapa en las coordenadas de arriba.

## Pendiente de confirmar

- Si los FLARM de papá y otros socios del club suben efectivamente a la red OGN pública (requiere estación receptora cerca — puede que ya exista y no se sepa, o que haya que averiguarlo/armarla).
- Cobertura real de glidernet.org sobre el cuadrante de vuelo.
