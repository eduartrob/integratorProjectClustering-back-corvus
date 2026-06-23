# Exoesqueleto Pasivo Inteligente para Ergonomía y Reducción de Fatiga Laboral

## Resumen
Desarrollo de un traje tipo exoesqueleto biomecánico (exo-traje pasivo) instrumentado con sensores wearable. El sistema utiliza mecanismos de resortes, poleas y tensores elásticos para descargar el 40% del esfuerzo físico de la zona lumbar y los hombros del trabajador en tareas industriales repetitivas (como ensamblaje bajo la carrocería de automóviles y levantamiento de cajas). Además de la asistencia física, incluye una red de sensores inerciales que envían datos en tiempo real sobre la postura del usuario a un modelo de IA para detectar movimientos de riesgo ergonómico continuo.

## Introducción
Los trastornos musculoesqueléticos (TME) representan la causa principal de absentismo laboral y compensaciones por discapacidad en la industria logística y manufacturera. A pesar del avance robótico, miles de tareas requieren la destreza humana, dejando a los trabajadores expuestos a posturas sostenidas antinaturales. Los rediseños ergonómicos de estaciones de trabajo no siempre son factibles en fábricas existentes. Prolongar la salud articular de los operarios es un imperativo legal, económico y ético urgente en la industria pesada.

## Objetivo General
Diseñar, construir y evaluar una asistencia wearable híbrida (mecánica-digital) que disminuya la fatiga muscular objetiva de la espalda baja en tareas repetitivas de levantamiento, reduciendo la incidencia de lesiones de trabajo y obteniendo datos cuantitativos reales de posturas peligrosas en la planta de producción.

## Objetivos Específicos
- Realizar análisis biomecánicos y estudios antropométricos en una muestra de trabajadores locales para modelar las cinemáticas articulares del traje, asegurando que no limite el rango natural de movimiento.
- Fabricar un exoesqueleto pasivo de estructura blanda-rígida (fibra de carbono, polímeros impresos en 3D y tensores elastoméricos) capaz de almacenar y liberar energía de retorno durante el ciclo de flexión/extensión del tronco.
- Integrar unidades de medición inercial (IMUs de 9 ejes) a lo largo de la columna vertebral del traje y conectarlos a un microcontrolador wearable de baja potencia (BLE).
- Entrenar algoritmos de Machine Learning en un servidor local que interpreten la orientación de los sensores para reconstruir el "maniquí 3D" digital del trabajador y calcular las cargas lumbares estimadas.
- Desarrollar una aplicación de "dashboard ergonómico" para el departamento de Salud y Seguridad Ocupacional (HSE) que alerte si un trabajador ha excedido el límite biomecánico de NIOSH de peso acumulado levantado en un turno.

## Justificación
La robótica no siempre es la solución al desgaste humano; la "ciborgización" temporal y segura ofrece un puente perfecto. Proteger físicamente al trabajador con la fuerza mecánica de un exoesqueleto y vigilar proactivamente su técnica de levantamiento con sensores previene lesiones de columna crónicas y costosas de tratar. Al proteger el bienestar de la mano de obra, las empresas disminuyen sus cuotas de seguros de riesgo de trabajo y mejoran drásticamente el clima laboral de la empresa.

## Metodología
Investigación en biomecánica ocupacional y mecatrónica wearable. El diseño mecánico iterativo usará el software de modelado de sólidos SolidWorks acoplado a AnyBody Modeling System (para simulaciones musculares). La evaluación clínica del impacto del prototipo se realizará bajo supervisión médica: se realizarán pruebas de electromiografía de superficie (sEMG) en los músculos erectores espinales de voluntarios de planta levantando cajas de 15 kg con y sin el exoesqueleto, midiendo la reducción de la amplitud de contracción y el retraso en la aparición de fatiga.

## Stack Tecnológico
- Diseño Mecánico / Materiales: CAD (SolidWorks), Análisis FEA (Ansys), Impresión 3D FDM (Nylon y TPU flexible), Tensores elásticos graduables
- Hardware Wearable: Microcontrolador Arduino Nano 33 BLE Sense, IMUs BNO085 (calibrados para evitar el drift giroscópico del movimiento rápido)
- Procesamiento Algorítmico Biomecánico: Filtros Complementarios / Kalman extendido, Python (SciPy)
- IA de Movimiento: Modelos Hidden Markov Models (HMM) para el reconocimiento del patrón de marcha y tipo de levantamiento
- Sistema de Visualización: Aplicación móvil en Flutter conectada al dispositivo por Bluetooth; panel web para el gerente de seguridad (Node.js)

## Alcance
El exoesqueleto desarrollado es de categoría "pasiva" (no utiliza motores eléctricos o baterías voluminosas para generar torque activo extra), basándose exclusivamente en el almacenamiento de la energía potencial elástica del propio movimiento humano. Se enfoca exclusivamente en el soporte lumbar/cintura escapular; no asiste a rodillas ni brazos distales. Su peso objetivo debe ser menor a 2.5 kg para asegurar su viabilidad como equipo de protección personal (EPP) en turnos de 8 horas.

## Conclusión
Unir el soporte biomecánico clásico con la analítica de datos en tiempo real revoluciona la salud ocupacional corporativa. El exoesqueleto instrumentado no es solo una faja avanzada; es un monitor continuo que garantiza que la interacción entre el ser humano biológico y el proceso de manufactura masivo mantenga los más altos estándares de salud y dignidad laboral para el futuro previsible.
