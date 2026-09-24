# Copiloto IA Planeadores

Sistema de asistencia para vuelo a vela (planeadores) que ayuda al piloto a decidir mejor durante el vuelo: si conviene seguir centrando la térmica actual o dirigirse hacia una mejor, calcular llegada al club, y sumar información predictiva de zonas candidatas a térmica.

**Autor:** Franco (frangirado55@gmail.com) + Fran (compañero de proyecto)
**Club:** Club de Planeadores Zárate (Ruta 9 y Av. Antártida Argentina, Zárate, Buenos Aires)
**Zona de vuelo habitual:** cuadrante Zárate → San Andrés de Giles → Baradero

## Estado actual

Proyecto en etapa de definición de alcance. Ver `docs/00-decision-final.md` para la versión más actualizada del plan — el proyecto pasó por varias iteraciones antes de asentarse (ver `docs/06-historial-iteraciones.md` para el porqué de cada descarte).

## Estructura de este repo

- `docs/00-decision-final.md` — **léase primero.** Alcance oficial del proyecto y diferencial frente a la competencia.
- `docs/01-modulos.md` — los 5 módulos funcionales y sus dependencias.
- `docs/02-comparacion-weglide.md` — qué ya resuelve WeGlide Copilot y dónde queda el hueco.
- `docs/03-plan-trabajo.md` — fases y orden de implementación sugerido.
- `docs/04-zona-vuelo.md` — datos geográficos de la zona de vuelo (Zárate-Giles-Baradero) para el análisis de terreno.
- `docs/05-notas-tecnicas.md` — apuntes técnicos sueltos (FLARM/OGN, física de cámara térmica, diferencia de temperatura en térmicas, herramientas de datos satelitales).
- `docs/06-historial-iteraciones.md` — registro de qué enfoques se descartaron y por qué (para no repetir el mismo análisis).
- `docs/07-proximos-pasos.md` — checklist accionable, el punto de partida para la próxima sesión de trabajo.
- `docs/08-modulo1b-diseno-terreno.md` — diseño técnico de la IA de lectura de terreno (Módulo 1-B): señales de entrada, pipeline de procesamiento, por qué no hace falta entrenar un modelo propio al principio, e integración con el Módulo 3.
- `docs/09-modulo3-diseno-decision.md` — diseño técnico de la IA de decisión (Módulo 3): teoría MacCready, lógica de quedarse/virar, integración con el Módulo 1-B.
- `docs/10-patron-diurno-temperatura.md` — investigación con datos satelitales reales (GOES-19) de cómo cambia la temperatura del terreno a lo largo del día, y el efecto de isla de calor urbana en Zárate al atardecer.
- `docs/11-teoria-completa-termicas.md` — teoría de térmicas más allá del terreno: nubes como indicador, cómo el viento organiza las térmicas (calles de nubes), líneas de convergencia (incluida la brisa del río Paraná), y libros de referencia.
- `docs/12-fuentes-meteo-alternativas.md` — investigación de RASP (sin cobertura para Argentina) y SkySight (alternativa con cobertura confirmada, pendiente de verificar sobre la zona exacta).
- `docs/13-zona-escape-aterrizaje.md` — módulo de seguridad: alcance máximo de planeo y zonas seguras para aterrizaje de emergencia, distinto del score de potencial térmico.
- `docs/14-efecto-rio-dinamico.md` — cuántos km tierra adentro se extiende la franja fría del río Paraná, calculado según el viento real del día (no un valor fijo).

## Cómo continuar en Claude Code

Empezá cada sesión nueva leyendo `docs/00-decision-final.md` y `docs/07-proximos-pasos.md` — ahí está el estado real del proyecto y lo próximo por hacer.
