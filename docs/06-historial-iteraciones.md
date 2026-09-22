# Historial de iteraciones (qué se descartó y por qué)

Registro para no repetir el mismo análisis en sesiones futuras.

## 1. Cámara infrarroja como detección predictiva pura (idea original)

**Descartado como punto de partida.** Requeriría modelos termodinámicos de la capa límite atmosférica, calibración con años de datos reales, y hardware caro y validado — nivel de tesis doctoral o empresa con financiamiento, no un proyecto de fines de semana. Queda como posible complemento a futuro (ver Módulo 1 en `01-modulos.md`), no como base.

## 2. Red FLARM/OGN pura (reactiva)

**Aceptado parcialmente.** Es viable y gratuita, pero es puramente reactiva (te enterás cuando otro planeador ya está girando) y en Argentina la cobertura OGN es floja. Se mantiene como una de las dos fuentes del Módulo 1, no como única.

## 3. Modelos meteorológicos tipo RASP

**Aceptado como referencia, no como reconstrucción desde cero.** RASP ya existe y es de código abierto — tiene sentido estudiarlo e idealmente usarlo/adaptarlo en vez de reprogramarlo. Pendiente confirmar cobertura para la zona de Zárate.

## 4. "Competir de frente" con WeGlide Copilot replicando todas sus features

**Descartado.** WeGlide tiene equipo, financiamiento y 10 millones de térmicas analizadas — no hay forma de alcanzar ese volumen en el corto plazo. Replicar su mapa reactivo o sus hotspots es tiempo perdido. Detalle completo en `02-comparacion-weglide.md`.

## 5. Cámara térmica mirando 3-7 km hacia adelante desde ~1 km de altura

**Descartado por física, no por costo.** El ángulo resultante (8-18° bajo la horizontal) es casi rasante: la resolución en el suelo se degrada mucho, la atmósfera atenúa la señal a esa distancia, y objetos intermedios tapan la vista. Detalle en `05-notas-tecnicas.md`.

## 6. IA que "vea como el piloto" analizando terreno, montes, humedad, sombras, nubes

**Aceptado y reformulado como Módulo 1-B.** Es la idea más sólida de las últimas iteraciones porque no depende de ángulo/distancia de cámara en vivo (se puede hacer con imágenes satelitales antes del vuelo) y resuelve el problema de poca cobertura OGN en Argentina. Reformulada en `01-modulos.md` y `04-zona-vuelo.md`.

## Conclusión del proceso

Cada vuelta fue descartando lo físicamente o comercialmente inviable con argumentos concretos, no por indecisión. El plan final (`00-decision-final.md`) combina lo que sobrevivió: red OGN + análisis de terreno satelital para el Módulo 1, y la IA de decisión (Módulo 3) como diferencial central frente a lo que ya existe.
