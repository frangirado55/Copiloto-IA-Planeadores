# Fuentes meteorológicas alternativas para pronóstico de térmicas

Investigación sobre RASP y alternativas, para el Módulo 1-A/meteorología (complemento futuro, no bloqueante — ver `01-modulos.md`).

## RASP (Dr. Jack) — sin cobertura confirmada para Argentina

RASP (Regional Atmospheric Soaring Prediction) es el sistema clásico de código abierto para pronóstico de térmicas, corre el modelo WRF. Se investigó su cobertura (22/09) buscando en el sitio de Dr. Jack y directorios de dominios RASP en el mundo — **no se encontró ningún dominio de Argentina ni de Sudamérica**. Las instalaciones públicas que sí aparecen son mayormente de EEUU, Europa, Australia, Nueva Zelanda y Gran Bretaña.

No se pudo verificar de forma 100% concluyente navegando el sitio directamente — este entorno de trabajo tiene bloqueado el acceso a `drjack.info` por política de red (egress proxy). Si alguien quiere confirmarlo de forma definitiva, puede entrar directo a http://www.drjack.info/RASP/index.html desde su propia conexión.

## SkySight — alternativa con cobertura confirmada

[SkySight](https://skysight.io/) es el sucesor moderno de RASP en la comunidad de vuelo a vela (creado por Matthew Scutter, piloto de planeador australiano). Varias fuentes independientes confirman:

- **Cubre Argentina y Brasil explícitamente** (junto con la mayoría de Europa, EEUU, Canadá, Australia, Nueva Zelanda, Japón).
- Ofrece pronóstico de **térmicas, onda, convergencia y sustentación de ladera** — incluye específicamente convergencia, que es justo lo que investigamos en `11-teoria-completa-termicas.md` (brisa del río Paraná).
- Fue usado para el **Perlan Project** (vuelos récord de altitud en planeador de onda) en Argentina — señal de que tiene presencia real en el país, aunque ese uso específico fue en Patagonia (onda de montaña), no en la pampa húmeda.
- **Prueba gratis de 7 días**, después ~USD 89/año.
- Funciona desde el navegador (sin apps), en cualquier dispositivo.

Fuentes: [SkySight Soaring Weather](https://skysight.io/), [SkySight - Wings and Wheels](https://wingsandwheels.com/pilot-supplies/skysight-soaring-weather.html), [SeeYou 9.0 con SkySight - Naviter](https://naviter.com/2017/11/seeyou-9-0-con-skysight/)

## Pendiente de confirmar

No se pudo verificar visualmente si SkySight tiene datos concretos sobre el cuadrante exacto de vuelo (Zárate, -34.12/-59.08) — este entorno de trabajo no puede acceder directamente a `skysight.io` (bloqueado por política de red, igual que drjack.info). Falta que alguien:

1. Entre a https://skysight.io/ desde su propia conexión.
2. Registre la prueba gratuita de 7 días.
3. Mire si hay datos de pronóstico (térmicas/convergencia) sobre las coordenadas del club.
4. Si los hay, decidir si vale la pena el pago anual (~USD 89) una vez terminada la prueba, o si con lo que ya tenemos (Módulo 1-B + GFS para viento) alcanza por ahora.

## Cómo encaja esto en el proyecto

Ninguna de estas dos fuentes es bloqueante — el proyecto ya funciona con lo que se armó (Módulo 1-B con Earth Engine + GFS para viento, Módulo 3 con MacCready). RASP/SkySight serían un complemento de fase avanzada: pronóstico de *cuándo* y *qué tan fuerte* va a haber térmica en el día (antes de volar), en vez de solo *dónde* tiende a haber (que es lo que ya resuelve el Módulo 1-B). Ver `01-modulos.md`.
