# Control de Calidad de Piezas Automotrices mediante Visión Artificial

## Resumen
Sistema de inspección óptica automatizada (AOI) diseñado para líneas de producción del sector automotriz. Emplea cámaras industriales GigE Vision de alta velocidad e iluminación estructurada para inspeccionar piezas metálicas maquinadas en la banda transportadora. Utiliza redes neuronales profundas (Deep Learning) especializadas en detección de anomalías para identificar micro-fisuras, porosidades, rayones y rebabas, separando neumáticamente las piezas defectuosas antes de que pasen a la etapa de ensamblaje final.

## Introducción
En la manufactura de autopartes y aviación, el estándar de calidad es "cero defectos", ya que una pieza fallida puede provocar accidentes fatales. Tradicionalmente, las inspecciones se realizan manualmente por operarios bajo lupas de luz, un proceso que sufre de altas tasas de error debido a la fatiga visual, distracciones e inconsistencia en los criterios de inspección entre diferentes turnos laborales. Los sistemas de visión artificial clásicos (basados en reglas y contraste) son frágiles ante cambios mínimos de iluminación y variaciones naturales de las piezas.

## Objetivo General
Automatizar el aseguramiento de la calidad de piezas maquinadas mediante un sistema de visión basado en Inteligencia Artificial, aumentando la velocidad de inspección a 120 piezas por minuto mientras se reduce la tasa de "falsos aceptados" (defectos que escapan la inspección) al 0.01%.

## Objetivos Específicos
- Diseñar la estación de inspección (cabina oscura) especificando la óptica de las cámaras, la resolución necesaria para detectar fisuras de 50 micras y la iluminación (Ring lights o Domos de luz rasante) para maximizar el contraste de los defectos superficiales superficiales.
- Entrenar un modelo de "Anomaly Detection" no supervisado (como PaDiM o PatchCore) usando únicamente imágenes de piezas "buenas" para enseñarle al modelo el patrón de la normalidad, detectando cualquier irregularidad como anomalía.
- Desarrollar la integración en tiempo real del software de visión con los autómatas programables (PLC) de la línea usando el protocolo Profinet u OPC-UA.
- Construir actuadores de rechazo mecánicos (brazos neumáticos o eyectores de aire) sincronizados milimétricamente con el procesamiento de imágenes para descartar la pieza defectuosa sin detener la banda.
- Generar un portal estadístico OEE (Overall Equipment Effectiveness) que almacene un registro fotográfico en la nube de cada defecto para análisis de causa raíz y trazabilidad de los lotes.

## Justificación
La adopción del Deep Learning permite a los sistemas de visión generalizar y tolerar variaciones naturales en el proceso de maquinado (como manchas de aceite o ligeros cambios de textura) que antes causaban miles de falsos rechazos en la visión tradicional. Este sistema paga su costo de desarrollo rápidamente al evitar multas contractuales de las ensambladoras OEM (Original Equipment Manufacturer) por rechazo de lotes enteros.

## Metodología
Ingeniería óptica y desarrollo MLOps industrial. Adquisición de cientos de imágenes bajo condiciones controladas de laboratorio emulando la línea de producción. Comparativa de modelos de redes neuronales orientados a segmentación de defectos. El modelo se implementará con optimización TensorRT en computadoras industriales sin ventilador (fanless). Pruebas de velocidad de obturación y tiempo de exposición con el objeto en movimiento. Despliegue piloto durante un mes operando en paralelo ("modo shadow") con la inspección humana antes de la automatización del rechazo físico.

## Stack Tecnológico
- IA / Computer Vision: PyTorch, biblioteca Anomalib, OpenCV
- Hardware Computacional: IPC (Industrial PC) con GPU NVIDIA RTX A2000, tarjetas capturadoras de red (NICs GigE)
- Optoelectrónica: Cámaras industriales Basler o Cognex, iluminación LED controlada por estroboscopios, sensores fotoeléctricos de disparo (Triggers)
- Control Industrial: PLC Allen-Bradley / Siemens, actuadores neumáticos Festo
- Software Integración: C++ (para latencia ultra-baja en el bucle principal), Python (para inferencia IA)

## Alcance
El sistema cubre la inspección superficial geométrica (2D) de piezas maquinadas con acabados no altamente reflectantes (espejo). Las tolerancias dimensionales extremas (metrología de micrones en 3D) requieren perfilómetros láser fuera del alcance de este proyecto de visión 2D. Diseñado para un solo flujo o producto; el cambio de producto requiere ajuste de foco o perfiles de iluminación.

## Conclusión
La conjunción de iluminación óptica avanzada e inteligencia artificial de borde (Edge AI) cierra la brecha entre la consistencia mecánica robótica y el juicio visual subjetivo, garantizando que cada producto que abandona la línea de producción cumple rigurosamente con los estándares mundiales de seguridad manufacturera.
