# Sistema de Mantenimiento Predictivo para Motores Industriales usando Análisis de Vibraciones

## Resumen
Plataforma de mantenimiento predictivo (PdM) industrial orientada a maquinaria rotativa pesada (motores, bombas, compresores). Utiliza sensores piezoeléctricos de aceleración acoplados directamente a la carcasa de las máquinas para capturar firmas de vibración de alta frecuencia. Estas señales acústicas/mecánicas son analizadas en la nube mediante algoritmos de Machine Learning (como Random Forest y SVM) para diagnosticar desgaste de rodamientos, desalineación o desbalanceo, prediciendo el momento exacto del fallo catastrófico (RUL - Remaining Useful Life) semanas antes de que ocurra.

## Introducción
En la manufactura pesada y plantas de generación de energía, una interrupción no planificada de la maquinaria crítica (Downtime) puede costar decenas de miles de dólares por hora. El "Mantenimiento Preventivo" tradicional (cambiar piezas por calendario, estén desgastadas o no) es económicamente ineficiente. El "Mantenimiento Reactivo" (esperar a que la máquina se rompa) es catastrófico. La Industria 4.0 requiere intervenir la máquina en el punto exacto donde la vida útil de la pieza se agota, maximizando la producción y minimizando las paradas operativas.

## Objetivo General
Desarrollar un sistema integral de mantenimiento predictivo basado en IoT y Machine Learning capaz de diagnosticar fallas mecánicas en desarrollo y estimar la Vida Útil Remanente (RUL) de motores de inducción con una anticipación mínima de 14 días.

## Objetivos Específicos
- Seleccionar e instalar sensores de vibración (acelerómetros triaxiales) y temperatura, integrándolos a nodos transmisores industriales inalámbricos (WirelessHART o ISA100.11a).
- Desarrollar un pipeline de procesamiento de señales digitales (DSP) para realizar la Transformada Rápida de Fourier (FFT) y análisis de envolvente, extrayendo las frecuencias características de falla de los rodamientos.
- Construir modelos de aprendizaje automático supervisado utilizando datasets de degradación acelerada de rodamientos (como el de NASA/PRONOSTIA) para clasificar severidad de falla.
- Desarrollar modelos predictivos (Deep Learning, LSTM recurrentes) para proyectar la curva de degradación futura y estimar el tiempo restante antes del paro catastrófico.
- Implementar un dashboard de operación (HMI web) que consolide el estado de salud de los activos, genere órdenes de trabajo (integración con ERP/SAP) y emita alertas visuales al equipo de mantenimiento.

## Justificación
El diagnóstico de vibraciones es una ciencia compleja que típicamente requiere técnicos certificados de Nivel III caminando la planta con analizadores portátiles costosos. Automatizar la recolección continua de datos y delegar el diagnóstico base a algoritmos de IA permite una cobertura 24/7 de todos los activos críticos, democratizando la confiabilidad industrial y extendiendo el ciclo de vida de bienes de capital millonarios.

## Metodología
Desarrollo de prototipo y ciencia de datos industrial. La extracción de características del dominio del tiempo y la frecuencia se realizará con ventanas rodantes (rolling windows). Los modelos se entrenarán offline y se desplegarán mediante contenedores Docker en un servidor perimetral (Edge computing). Se realizará una prueba de concepto instrumentando 3 motores de bombas centrífugas en una planta tratadora de agua local durante 3 meses, verificando las alertas del sistema mediante inspección visual y análisis tribológico del aceite.

## Stack Tecnológico
- Análisis de Señales / IA: Python, SciPy, Scikit-Learn, TensorFlow/Keras (Redes LSTM)
- Ingestión de Datos: Apache Kafka, InfluxDB (para almacenar formas de onda de alta velocidad)
- Nodos IoT: Sensores piezoeléctricos 4-20mA, conversores ADC de 24 bits, pasarelas industriales Siemens/Phoenix Contact
- Backend y Visualización: Node.js, Grafana
- Protocolos Industriales: MQTT, OPC-UA (para integración con sistemas SCADA existentes)

## Alcance
El sistema se enfoca en el diagnóstico de maquinaria rotativa con velocidad de operación constante o moderadamente variable. Cubre fallos mecánicos (desbalanceo, desalineación, rodamientos, soltura mecánica). No cubre diagnósticos eléctricos profundos del estator o fallos en las tarjetas electrónicas de los variadores de frecuencia (VFD). Requiere conexión eléctrica constante y red en planta para transmitir los datos pesados de vibración.

## Conclusión
Convertir la firma mecánica invisible de una máquina en un pronóstico claro de tiempo de vida transforma a los departamentos de mantenimiento industrial de centros de costo reactivos a generadores de rentabilidad y disponibilidad estratégica en la empresa.
