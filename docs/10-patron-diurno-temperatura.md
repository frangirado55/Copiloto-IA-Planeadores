# Patrón diurno de temperatura — investigación con datos reales

Investigación de cómo cambia la temperatura de superficie a lo largo del día en la zona, usando datos satelitales reales (no solo teoría). Ver `05-notas-tecnicas.md` para las notas técnicas previas sobre térmicas.

## Fuente de datos

**GOES-19** (satélite geoestacionario, cubre toda Sudamérica de forma continua) vía Earth Engine (`NOAA/GOES/19/MCMIPF`), banda **CMI_C14** (~11.2 micrones, ventana atmosférica limpia — da temperatura de brillo de la superficie/nubes). A diferencia de satélites de órbita polar (Sentinel-2, Landsat, MODIS) que pasan 1-2 veces por día a horario fijo, GOES-19 toma una imagen del disco completo **cada 10 minutos**, permitiendo ver la evolución de la temperatura durante todo el día — no solo una foto fija.

## Metodología

- Se compararon dos zonas de 5km de radio: una **urbana/industrial** (centrada en el club, incluye zona urbana de Zárate) y una **rural** (hacia San Andrés de Giles, campo abierto).
- Los valores crudos de la banda vienen como número entero sin escala (0-65535) — hace falta aplicar `CMI_C14_scale` y `CMI_C14_offset` (propiedades de cada imagen) para convertir a temperatura real en Kelvin.
- **Nubes**: el primer intento (20/09) dio resultados sin sentido (temperaturas de -50°C al mediodía) porque ese día estuvo parcialmente nublado — las nubes se ven mucho más frías que el suelo. Se resolvió: (1) filtrando por el flag de calidad `DQF_C14`, y (2) usando el **píxel más caliente** de cada zona en vez del promedio (el máximo tiene más chance de ser suelo despejado en vez de nube).
- Se buscó un día efectivamente despejado comparando la temperatura máxima al mediodía entre varias fechas recientes — se usó **17/09/2026** (29.5°C al mediodía, el más alto y consistente de la muestra).

## Resultado

Ver el gráfico enviado en el chat. Dos hallazgos concretos:

1. **Curva de calentamiento**: la temperatura sube de forma bastante pareja desde ~5:00 (cerca de 0°C) hasta un pico entre las **13:30 y las 14:00** (~30°C), y después baja gradualmente durante la tarde/noche. Esto es consistente con la ventana clásica de mejor térmica (media mañana a media tarde), pero ahora con un dato concreto de esta zona en particular en vez de una regla general.

2. **La zona urbana/industrial se mantiene más caliente que el campo durante el atardecer** (~18:30 a 20:30, diferencia de +1.6°C a +2.3°C) — mientras el campo ya empezó a enfriarse, el asfalto/las construcciones siguen liberando el calor acumulado. Esto es el efecto de "isla de calor urbana", y **confirma por qué Ruta 9/las fábricas pueden seguir dando térmica más tarde en el día que el campo abierto** — no es solo que "calientan más", sino que retienen el calor por más tiempo.

## Cómo se podría usar esto en el modelo (pendiente, no implementado todavía)

Hoy `scripts/analizar_terreno.py` y `scripts/copiloto.py` calculan el score de potencial térmico **sin considerar la hora del día** — un campo seco puntúa igual a las 8am que a las 5pm, lo cual sabemos que no es realista. Un próximo paso natural sería:

## Implementado (24/09): `scripts/patron_horario.py`

Se agregó el multiplicador horario, usando directamente esta curva medida (no una forma inventada tipo campana genérica): la tabla hora→temperatura de la corrida del 17/09 (rural y urbana por separado) se normaliza a un multiplicador 0-1 (0°C o menos → 0, el pico medido ~30.4°C → 1), interpolando entre horas.

`copiloto.py` lo aplica en `recomendar()`: la fuerza estimada de una candidata (`score_a_fuerza_ms(score)`) se multiplica por `multiplicador_horario(hora_local, es_hotspot)` antes de pasarla al Módulo 3. Se usa la curva urbana (que se mantiene alta más tarde, por la isla de calor) para hotspots conocidos, y la rural para el resto. La fuerza de la térmica **actual** no se ajusta — es un dato real del variómetro, no una estimación.

Probado con la misma posición a distintas horas: a las 8hs la candidata (Toyota, hotspot) estima 1.28 m/s y el sistema recomienda quedarse; a las 14hs (pico) la misma candidata estima 3.8 m/s y recomienda virar. Antes de este cambio daba exactamente lo mismo a cualquier hora del día.

**Limitación (resuelta el mismo día, ver abajo)**: la tabla horaria era de un solo día despejado de septiembre — no medía el clima real de hoy (un día nublado o más frío daría el mismo multiplicador que uno despejado, solo por compartir la hora).

## Corregido (24/09, mismo día): medición en vivo, no solo tabla histórica

Pregunta de Franco: "¿y el calor no medís?" — tenía razón, el multiplicador horario usaba una curva fija en vez de medir la temperatura real del momento, a pesar de que ya sabíamos cómo pedirle esa medición a GOES-19 (la misma metodología de este documento). Se agregó `temperatura_actual_c()` y `multiplicador_en_vivo()` en `patron_horario.py`:

- Consulta GOES-19 en vivo (últimos ~40 minutos), con la misma corrección de escala/offset y filtro de nubes (DQF) que se validó acá.
- Si hay dato disponible, ese es el que se usa (no la tabla).
- Si no hay dato (nublado, sin imagen reciente, falla de red) → cae a la tabla histórica de este documento como respaldo, no se rompe la recomendación.

`copiloto.py` ahora usa `multiplicador_en_vivo()` en vez de `multiplicador_horario()` directamente, y guarda en el resultado de qué fuente salió el número (`fuente_multiplicador`: `en_vivo` o `respaldo_por_hora`), para poder distinguir cuándo la recomendación se basó en clima real vs. una suposición.

**Bug encontrado en el camino**: `copiloto.py` nunca inicializaba Earth Engine por su cuenta (antes no lo necesitaba, la búsqueda de candidatas es puramente local con rasterio) — la medición en vivo fallaba silenciosamente y siempre caía al respaldo. Se corrigió agregando `init_earth_engine()` al arranque de `main()`.

## Temperatura de aire general (24/09, mismo día): "¿hace frío o calor?"

Pedido de Franco: mostrar el clima general (frío/calor), no solo el número técnico usado para calcular térmicas. Es una medición **distinta** de `temperatura_actual_c()` (que mide temperatura de *superficie* vía GOES, específica para estimar térmicas) — acá se usa `obtener_temperatura_aire_actual()` en `mapa_utils.py`, que consulta **temperatura de aire a 2 metros** vía GFS (banda `temperature_2m_above_ground`, la misma fuente que ya se usaba para el viento), con una descripción en palabras (frío / fresco / templado / caluroso / mucho calor, según rangos de °C).

Se agregó al cuadro de viento que ya aparecía en `mapa_claro.py` y `mapa_decision.py` — ahora dice, por ejemplo, "Viento: 16 km/h desde el N · 20°C (templado)".
