# Red IoT para Monitoreo Estructural de Puentes y Edificios

## Resumen
Sistema de monitoreo estructural de salud (SHM) basado en acelerómetros, galgas extensométricas y sensores de vibración conectados por IoT para detectar en tiempo real anomalías estructurales en infraestructura civil crítica. El sistema emite alertas preventivas ante eventos sísmicos o deterioro acumulado que puedan comprometer la integridad de puentes y edificios.

## Introducción
México se encuentra en una de las zonas sísmicas más activas del mundo. Los sismos de 1985 y 2017 demostraron la vulnerabilidad de la infraestructura civil ante eventos extremos. El monitoreo continuo de la salud estructural permite identificar fatiga de materiales y daños incipientes antes de que alcancen niveles críticos, salvando vidas y reduciendo costos de reparación.

## Objetivo General
Implementar una red de sensores IoT para monitoreo de salud estructural en tiempo real que detecte vibraciones anómalas, deformaciones y aceleraciones fuera de rango en infraestructura civil, con alertas automáticas a autoridades de protección civil.

## Objetivos Específicos
- Diseñar nodos de monitoreo con acelerómetros MEMS triaxiales ADXL345, galgas extensométricas y sensores LVDT de desplazamiento.
- Implementar procesamiento edge en Raspberry Pi para filtrado de señales con transformadas de Fourier en tiempo real.
- Desarrollar algoritmo de detección de anomalías estructurales basado en redes neuronales LSTM entrenadas con datos sísmicos históricos.
- Establecer comunicación redundante via WiFi y 4G LTE con protocolo MQTT y QoS 2 para garantizar entrega de datos críticos.
- Crear dashboard de monitoreo para ingenieros civiles con visualización de formas modales y alertas sísmicas.

## Justificación
El monitoreo estructural continuo es obligatorio en países desarrollados para infraestructura crítica. En México, su adopción es incipiente y se limita a grandes proyectos de infraestructura. Este proyecto demuestra que es posible implementar SHM de calidad con tecnología de código abierto y hardware accesible.

## Metodología
Se realizará el diseño electrónico y mecánico de los nodos de sensor con simulación en LTspice. La instalación se hará en un puente peatonal universitario para pruebas controladas. El modelo LSTM se entrenará con el catálogo sísmico del SSN con datos de los últimos 30 años.

## Stack Tecnológico
- Hardware: Raspberry Pi 4, ADXL345, galgas HBM, módulo 4G SIM7600
- Procesamiento edge: Python, NumPy, SciPy (FFT)
- ML: TensorFlow, LSTM, autoencoder para anomalías
- Backend: InfluxDB, Telegraf, Grafana
- Alerta: Twilio SMS API

## Alcance
Monitoreo de un puente peatonal con 8 nodos de sensor durante 3 meses. Validación contra datos del SSN. Excluye certificación por autoridades civiles en esta fase académica.

## Conclusión
El monitoreo estructural IoT es una tecnología de alto impacto social que puede salvar vidas al detectar deterioro estructural antes de fallas catastróficas, especialmente en un país de alta sismicidad como México.
