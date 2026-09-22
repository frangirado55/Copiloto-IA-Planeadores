# Próximos pasos (checklist accionable)

## Confirmar con el club / familia

- [ ] Preguntarle a papá (o algún socio con FLARM) qué modelo/versión tiene y si sabe si hay estación receptora OGN cerca del club.
- [ ] Chequear cobertura real de la zona del club en [glidernet.org](http://www.glidernet.org) — poner el mapa en -34.12, -59.08 y ver si aparecen planeadores en vivo.
- [ ] Confirmar si hay cobertura RASP para la zona de Zárate.

## Fase 1 — MVP de decisión (arrancar por acá)

- [ ] Definir la polar del planeador que van a usar como referencia (marca/modelo del planeador del club o de papá).
- [ ] Implementar la fórmula MacCready básica en Python: dado (fuerza térmica actual, fuerza térmica candidata, distancia a la candidata, polar del planeador), calcular si conviene quedarse o virar.
- [ ] Probarlo con datos inventados/manuales primero, antes de conectar cualquier fuente de datos real.

## Fase de datos (en paralelo, cada fin de semana de vuelo)

- [ ] Registrar variómetro + GPS durante los vuelos.
- [ ] Anotar manualmente dónde y cuándo aparecieron térmicas fuertes vs. débiles (hora, ubicación aproximada, tipo de terreno debajo).

## Análisis de terreno (si se confirma poca cobertura OGN)

- [ ] Registrarse en [Copernicus Data Space](https://dataspace.copernicus.eu/) o crear cuenta de Google Earth Engine.
- [ ] Bajar/acceder a imagen Sentinel-2 reciente sin nubes del cuadrante Zárate-Giles-Baradero.
- [ ] Bajar DEM (SRTM) de la misma zona.
- [ ] Correr clasificación básica de terreno (campo trabajado / pastura / monte / agua / asfalto) — pedir el script de Python/Earth Engine en la próxima sesión.

## Roles (pendiente definir con Fran)

- [ ] Definir quién se enfoca en qué: lógica de decisión (software/matemática) vs. hardware/integración/pruebas en vuelo.

## Definiciones de negocio (más adelante, no bloqueante para arrancar)

- [ ] Presupuesto inicial.
- [ ] Plan de testeo: primero el usuario mismo, después hermano/papá. Si gusta, recién ahí evaluar vender.
