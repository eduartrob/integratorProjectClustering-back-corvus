# Gemelo Digital (Digital Twin) para Optimización de Líneas de Ensamblaje

## Resumen
Plataforma de simulación interactiva 3D que refleja el comportamiento físico y operativo en tiempo real de una línea de ensamblaje manufacturera. Este "Gemelo Digital" se sincroniza bidireccionalmente con los sensores, robots y PLCs físicos de la planta, permitiendo a los ingenieros industriales visualizar cuellos de botella, realizar pruebas de "What-If" (¿Qué pasaría si cambiamos el robot A por uno más rápido?) y entrenar algoritmos de optimización sin riesgo de detener la producción real.

## Introducción
Los sistemas de fabricación moderna (Lean Manufacturing) son complejos y están interconectados. Cambiar la velocidad de un transportador o reprogramar un robot a menudo resulta en consecuencias impredecibles y cuellos de botella inesperados en la siguiente estación, debido a la acumulación y variabilidad temporal (efecto látigo). Experimentar directamente en la línea de producción física cuesta millones en tiempo de inactividad. Los simuladores estáticos quedan obsoletos minutos después de crearlos porque no reflejan el deterioro diario de las máquinas reales.

## Objetivo General
Desarrollar un Gemelo Digital sincrónico de una línea de producción discreta que reduzca el tiempo de ciclo (Cycle Time) general en un 15% mediante la simulación predictiva de optimizaciones logísticas y reprogramación robótica en el plano virtual.

## Objetivos Específicos
- Crear el modelado 3D cinemático exacto de las estaciones de trabajo, conveyors, manipuladores robóticos y herramientas usando un motor físico de grado ingenieril.
- Establecer un bus de datos de ultra baja latencia para capturar el estado en tiempo real (posiciones de junta de robots, conteo de piezas, estados de error) desde los PLCs físicos y actualizar el gemelo en pantalla sin lag perceptible.
- Implementar algoritmos de simulación de eventos discretos que permitan adelantar el tiempo en el modelo virtual ("Time Travel") para predecir cuándo se acumulará el inventario en proceso (WIP - Work in Progress).
- Desarrollar un sistema de Machine Learning sobre el simulador que ejecute algoritmos genéticos durante las noches para encontrar el re-balanceo de línea óptimo para la producción del día siguiente.
- Integrar visualización en Realidad Mixta (XR) para que los gerentes puedan caminar por la planta física con gafas holográficas (HoloLens) viendo sobreimpresas las métricas futuras simuladas en las máquinas reales.

## Justificación
La digitalización completa del piso de producción es la columna vertebral de la Industria 4.0. Un Gemelo Digital permite desacoplar la mejora continua (KAIZEN) del riesgo operativo. Actúa como el puente perfecto entre la capa física (OT) y la de software (IT), proporcionando un "sandbox" (caja de arena) hiperrealista donde los ingenieros pueden romper la línea cientos de veces en el mundo digital para garantizar que funcionará impecablemente en el mundo físico.

## Metodología
Investigación en sistemas ciberfísicos (CPS) y simulación de manufactura. Fase inicial de mapeo CAD de la línea. Se implementarán las conexiones telemáticas de planta vía OPC-UA a un servidor de broker MQTT local. Construcción del entorno físico en el motor de juegos (simulador). Validación comparando el OEE (Overall Equipment Effectiveness) reportado por el gemelo virtual contra los reportes históricos del SCADA físico, asegurando una desviación máxima del 2%.

## Stack Tecnológico
- Motor de Simulación: Unity 3D Industrial, NVIDIA Omniverse, o Siemens Process Simulate
- Integración OT/IT: Kepware (OPC-UA server), Node-RED, Apache Kafka, MQTT
- Control Robótico Virtual: ROS2, MoveIt!
- Computación de Alto Rendimiento (HPC): Contenedores Docker en servidores locales con GPUs (para simulaciones aceleradas)
- Visualización: WebGL, gafas Microsoft HoloLens 2 para AR

## Alcance
La simulación contempla una célula de manufactura flexible compuesta por 4 robots y 2 estaciones de trabajo manual. El gemelo físico-virtual opera predominantemente en modo monitorización (Lee datos), la re-escritura en los PLC reales para aplicar optimizaciones automáticas requiere validación humana intermedia por normativas de seguridad (Safety Integrity Levels). No abarca el diseño macro-logístico de toda la fábrica, solo el micro-ensamblaje de una línea.

## Conclusión
Los Gemelos Digitales superan la barrera histórica entre el diseño de ingeniería y las operaciones diarias, habilitando la manufactura ágil capaz de auto-optimizarse frente a la variabilidad de la demanda y las condiciones del taller mecánico, sin sacrificar la estabilidad del proceso de ensamblaje.
