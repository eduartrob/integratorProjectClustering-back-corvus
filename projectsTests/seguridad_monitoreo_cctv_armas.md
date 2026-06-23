# Detección Automática de Armas en Sistemas de CCTV con IA

## Resumen
Sistema de visión por computadora implementado en dispositivos de computación de borde (edge computing) que analiza en tiempo real el flujo de video de las cámaras de vigilancia (CCTV) existentes en escuelas y centros comerciales. El sistema detecta la exposición de armas de fuego (pistolas y rifles) y genera una alerta visual y sonora inmediata a las autoridades de seguridad, fracciones de segundo antes de que se efectúe un disparo.

## Introducción
En situaciones de tirador activo, el tiempo de respuesta policial es el factor más crítico para minimizar la pérdida de vidas. Sin embargo, los sistemas de CCTV actuales son herramientas puramente forenses: graban el evento para análisis posterior. Los monitores humanos a menudo se fatigan y no pueden vigilar 50 pantallas simultáneamente. Es vital dotar a las cámaras de la capacidad de entender lo que están "viendo" para alertar proactivamente.

## Objetivo General
Desarrollar un sistema de inferencia de video en tiempo real que detecte la presencia de armas de fuego en circuitos cerrados de televisión, logrando un tiempo de alerta menor a 2 segundos con una precisión superior al 95%.

## Objetivos Específicos
- Recopilar, limpiar y aumentar sintéticamente un dataset de imágenes de armas de fuego en manos de personas bajo diversas condiciones de iluminación y ángulos de cámara (CCTV vista en picada).
- Entrenar y optimizar una arquitectura de detección de objetos YOLOv8 (You Only Look Once) para enfocarse específicamente en la firma visual de armas cortas y largas.
- Implementar el modelo en un hardware acelerador de IA de bajo costo instalado físicamente junto al NVR (grabador) del edificio, evitando el envío de video crudo a la nube por razones de privacidad y ancho de banda.
- Desarrollar un sistema de filtrado temporal para reducir falsos positivos causados por objetos similares (ej. taladros, teléfonos móviles oscuros) requiriendo que la detección se mantenga en cuadros de video consecutivos.
- Crear una API que se integre con los sistemas de megafonía del edificio para iniciar automáticamente protocolos de encierro (lockdown) y enviar notificaciones push con fotogramas a la policía local.

## Justificación
Automatizar la detección visual de amenazas transforma la infraestructura pasiva de seguridad que ya poseen miles de instituciones en un sistema de prevención activo. Detectar el arma en el momento que se saca de la mochila o abrigo provee valiosos segundos de ventaja táctica que pueden activar puertas automáticas, notificar a las autoridades y en última instancia, salvar vidas.

## Metodología
Investigación experimental en IA. Se probarán varias arquitecturas ligeras (YOLOv8 nano, MobileNet-SSD) comparando la relación precisión-velocidad (FPS). Las pruebas se realizarán con cámaras IP de 1080p y actores portando réplicas de airsoft y objetos confusos (paraguas, carteras) bajo iluminación diurna y nocturna simulada en el campus universitario.

## Stack Tecnológico
- Visión Artificial: OpenCV, PyTorch, Ultralytics YOLOv8
- Optimización Edge: NVIDIA TensorRT o OpenVINO (para aceleración por hardware)
- Hardware: NVIDIA Jetson Orin Nano
- Ingesta de Video: protocolo RTSP (Real-Time Streaming Protocol), GStreamer
- Alertas y Backend: Python, MQTT, integración webhooks (Twilio/Telegram API)

## Alcance
El sistema requiere que el arma sea visualmente expuesta al menos de forma parcial ante el campo de visión de la cámara. No puede detectar armas ocultas bajo la ropa (no utiliza rayos X o escáneres de microondas). El rango de detección está limitado por la resolución de la cámara (efectivo a no más de 15 metros para pistolas en resolución 1080p).

## Conclusión
La IA aplicada al análisis de video de seguridad tiene el potencial de actuar como un guardia vigilante 24/7 que nunca parpadea, proporcionando la alerta temprana crítica que hace la diferencia en escenarios de violencia extrema urbana y escolar.
