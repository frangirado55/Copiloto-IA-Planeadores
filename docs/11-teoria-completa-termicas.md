# Teoría completa de térmicas: nubes, viento y convergencia

Investigación más profunda sobre todo lo que genera y organiza térmicas — no solo el disparador en el suelo (ya cubierto en `08-modulo1b-diseno-terreno.md`), sino cómo el viento las organiza, cómo las nubes las marcan, y qué es una línea de convergencia. Objetivo: entender qué más se puede leer desde datos satelitales además del terreno estático.

## Libros de referencia (para profundizar más adelante)

- **"Cross-Country Soaring" (Streckensegelflug), Helmut Reichmann** — el clásico. Reichmann era piloto de competencia y matemático; el libro explica de dónde salen las térmicas, táctica de vuelo y la teoría MacCready con las ecuaciones completas (la misma base que usa nuestro Módulo 3).
- **"Meteorology for Glider Pilots", C.E. Wallington** — meteorología aplicada a vuelo a vela: presión, viento, frentes, y cómo leer todo eso para encontrar térmica.
- **Dennis Pagen (varios títulos)** — orientado a ala delta/parapente pero con muy buena cobertura de técnica de centrado y lectura de nubes.
- **"Reading Clouds", Bill Palmer** — guía práctica corta y visual, específicamente sobre qué forma de nube indica qué (térmica activa vs. muriendo, sobre-desarrollo).
- **FAA Glider Flying Handbook, capítulos 10 (Soaring Techniques) y 16 (Soaring Weather)** — gratuitos, oficiales, ya citados en docs anteriores.

Fuentes: [Best Gliding Books (BookAuthority)](https://bookauthority.org/books/best-gliding-books), [Reading Clouds - Bill Palmer (PDF)](https://thesoaringpage.com/docs/Reading%20Clouds.pdf), [FAA Glider Flying Handbook Cap. 10](https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/glider_handbook/gfh_chapter_10.pdf)

## Las nubes como indicador (no solo decoración del cielo)

Un cúmulo se forma porque el aire de una térmica sube, se enfría, y a cierta altura el vapor de agua condensa — el cúmulo **marca dónde hay (o hubo) una térmica**, no es un fenómeno aparte.

Cómo leerlo:
- **Base plana y oscura, con crecimiento vertical activo** → térmica activa debajo, probablemente fuerte.
- **Nube que empieza a deshilacharse por abajo o se aplana arriba (yunque)** → la térmica se está muriendo o sobre-desarrollando; no vale la pena ir.
- **Núcleos fuertes suben casi verticales; núcleos débiles suben en ángulo** — el punto de origen en el suelo no está justo debajo de la nube, sino corrido en la dirección de donde viene el viento (la térmica se inclina mientras sube, arrastrada por el viento). Buscar la térmica implica corregir esa deriva, no ir directo al punto de la nube.

Fuente: [Reading Clouds - Bill Palmer](https://thesoaringpage.com/docs/Reading%20Clouds.pdf), [CFI Notebook - Thermal Soaring](https://www.cfinotebook.net/notebook/aircraft-operations/gliding/thermal-soaring)

## El viento organiza las térmicas — no son aleatorias

- Con viento en calma o muy suave, las térmicas salen como burbujas más o menos aisladas y desordenadas.
- Con viento moderado (10-20 km/h) las térmicas se **organizan en filas alineadas con la dirección del viento** — si hay cúmulos arriba, esas filas se ven como **"calles de nubes"** (cloud streets). La distancia entre calles es aproximadamente 3 veces la altura de la capa convectiva (la altura hasta donde llegan las térmicas).
- Con viento fuerte, la cizalladura (wind shear, el viento cambiando de velocidad/dirección con la altura) puede destruir la organización de la térmica o inclinarla tanto que se hace difícil de centrar.
- **Una calle de nubes es oro**: en vez de una térmica aislada, es una línea larga y continua de ascenso — se puede volar en línea recta debajo de ella ganando altura, en vez de tener que centrar cada burbuja por separado.

Fuente: [UBC ATSC 113 - Updrafts and Soaring](https://www.eoas.ubc.ca/courses/atsc113/flying/met_concepts/02-met_concepts/02f-soaring/index.html), [Cloud Streets - CIRA/RAMMB](https://rammb.cira.colostate.edu/wmovl/vrl/tutorials/satmanu-eumetsat/satmanu/cms/clstr/index.htm)

## Líneas de convergencia: más fuertes que una térmica suelta

Una convergencia pasa donde **dos masas de aire distintas chocan** y no tienen a dónde ir más que hacia arriba — genera una línea de ascenso mucho más fuerte, ancha y sostenida que una térmica individual.

**Relevante para nuestra zona en particular**: el río Paraná genera su propia "brisa de río" (el aire sobre el agua se mantiene más fresco, y ese aire fresco avanza tierra adentro). Donde esa brisa de río choca con el aire caliente del interior (más hacia el oeste/sur, lejos de la costa), se puede formar una **línea de convergencia** — potencialmente una zona de ascenso fuerte y sostenido, distinta de la franja fría pegada al río que ya habíamos anotado en `04-zona-vuelo.md` (esa franja es donde la brisa todavía no se calentó; la convergencia está más adentro, donde la brisa fría se topa con el aire caliente).

Esto agrega un tercer tipo de "hotspot" a los dos que ya teníamos (terreno + hotspots puntuales conocidos): **líneas dinámicas que dependen del viento del día**, no fijas en el mapa. No se pueden precalcular como el score de terreno — dependen de la dirección y fuerza del viento de cada jornada.

Fuente: [Understanding Seabreeze Convergence - XCmag](https://xcmag.com/news/understanding-seabreeze-convergence/), [Convergence - Chess in the Air](https://chessintheair.com/convergence/)

## Qué de todo esto ya se puede traer con datos (implementado ahora)

- **Viento**: GFS (`NOAA/GFS0P25` en Earth Engine) da dirección y velocidad del viento pronosticado a 10m y en la capa límite planetaria, actualizado varias veces al día. Ya lo pudimos consultar para la zona.
- **Nubes/desarrollo convectivo actual**: GOES-19 (el mismo dataset del patrón diurno) también tiene canales visibles/infrarrojos que muestran nubosidad en desarrollo cada 10 minutos — se puede usar para ver si hay cúmulos formándose sobre la zona en este momento.

## Qué queda para más adelante (no trivial)

- Detectar automáticamente una calle de nubes o una línea de convergencia específica (no solo "hay nubes" sino "están alineadas" o "hay una línea clara") requiere procesamiento de imagen más elaborado (detección de líneas/orientación) — se puede hacer, pero es un desarrollo aparte, no una consulta simple.
- Modelar la deriva de una térmica con el viento (dónde está el punto de origen real de una térmica marcada por una nube) es geometría simple (desplazar en la dirección del viento proporcional a la altura) pero todavía no está en el código.
