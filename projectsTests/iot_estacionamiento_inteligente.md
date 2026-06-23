# Sistema IoT de Gestión de Estacionamiento Inteligente

## Resumen
Sistema de estacionamiento inteligente basado en sensores ultrasónicos y cámaras de visión artificial que detecta la disponibilidad de cajones en tiempo real. Una aplicación móvil guía al conductor al cajón libre más cercano, reduciendo el tiempo de búsqueda y la emisión de CO2 asociada al tráfico vehicular por búsqueda de estacionamiento.

## Introducción
Estudios urbanos indican que entre el 20% y el 30% del tráfico en zonas comerciales y de oficinas corresponde a vehículos buscando estacionamiento. Este tiempo improductivo genera congestión vial, estrés en los conductores y emisiones de gases de efecto invernadero evitables. Una solución tecnológica de bajo costo puede transformar cualquier estacionamiento convencional en uno inteligente.

## Objetivo General
Desarrollar un sistema de detección y gestión de disponibilidad de cajones de estacionamiento basado en sensores IoT y visión artificial, integrado con una aplicación móvil de navegación interna en tiempo real.

## Objetivos Específicos
- Instalar sensores ultrasónicos HC-SR04 en cada cajón conectados a microcontroladores ESP8266 para detección de ocupación.
- Implementar un servidor de telemetría con WebSockets para comunicación de datos en tiempo real.
- Desarrollar algoritmo de visión artificial con OpenCV para contar vehículos en entradas y salidas.
- Crear mapa interactivo del estacionamiento en la aplicación móvil con indicador visual de cajones disponibles u ocupados.
- Integrar sistema de reserva anticipada de cajones y pago digital mediante QR.

## Justificación
Los estacionamientos convencionales no ofrecen información sobre disponibilidad. La integración de sensores IoT de bajo costo permite transformar infraestructura existente sin necesidad de obra civil mayor, con un retorno de inversión estimado en 18 meses por reducción de personal de vigilancia y aumento de rotación de cajones.

## Metodología
Prototipado iterativo con metodología SCRUM. Se implementará en tres sprints: sprint 1 (sensores y backend), sprint 2 (aplicación móvil), sprint 3 (integración y pruebas en campo). Se realizará una prueba piloto en el estacionamiento universitario con 50 cajones durante 4 semanas.

## Stack Tecnológico
- Hardware: ESP8266 NodeMCU, HC-SR04, cámara IP
- Backend: FastAPI Python, Redis pub/sub, PostgreSQL
- Frontend móvil: Flutter
- Visión artificial: OpenCV, YOLOv8
- Protocolos: WebSockets, MQTT

## Alcance
La implementación piloto abarca un estacionamiento de 50 cajones en las instalaciones universitarias. El sistema de pago digital es opcional en la primera versión. No incluye integración con sistemas de nómina o control de acceso de empleados.

## Conclusión
La transformación de estacionamientos convencionales en inteligentes mediante IoT representa una mejora significativa en la experiencia del usuario y en la eficiencia operativa urbana con una inversión tecnológica mínima y escalable.
