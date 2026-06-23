# Análisis de Mapas de Calor y Tráfico en Tiendas Físicas con Wi-Fi Tracking

## Resumen
Plataforma de inteligencia para el comercio minorista físico (Brick & Mortar Retail Analytics). Utiliza sensores pasivos que escanean las peticiones de búsqueda de redes Wi-Fi (Probe Requests) emitidas automáticamente por los teléfonos inteligentes de los clientes. El sistema triangula la posición de los dispositivos de forma anónima para generar mapas de calor, medir el tiempo de permanencia en pasillos, calcular tasas de conversión de vitrina (cuántos entran vs cuántos pasan de largo) y analizar la efectividad del diseño de la tienda.

## Introducción
Las tiendas de comercio electrónico (como Amazon) miden cada interacción del usuario: dónde hace clic, cuánto tiempo mira una imagen y en qué punto abandona el carrito (Google Analytics). Por el contrario, el retail físico tradicional opera a ciegas; conocen sus ventas, pero no saben por qué un producto en una esquina no se vende o si la vitrina principal está atrayendo tráfico. Es imperativo llevar las métricas detalladas del mundo digital al espacio físico.

## Objetivo General
Desarrollar un sistema de analítica espacial de bajo costo que mapee el comportamiento de tráfico peatonal dentro de las sucursales minoristas, proporcionando datos objetivos para optimizar el visual merchandising y la distribución del personal de ventas.

## Objetivos Específicos
- Construir redes de sensores de rastreo pasivos basados en microcontroladores con antenas Wi-Fi en modo promiscuo, distribuidos estratégicamente por el techo de la tienda.
- Desarrollar un algoritmo de trilateración basado en la potencia de la señal recibida (RSSI) para ubicar dispositivos móviles en un plano 2D con un error menor a 2 metros.
- Implementar un pipeline de ofuscación de direcciones MAC mediante hashing criptográfico salado en el propio dispositivo sensor, garantizando el anonimato absoluto del cliente según normativas de privacidad (GDPR).
- Diseñar un motor de análisis temporal que distinga a los "compradores reales" de los "dispositivos fijos" (routers, computadoras de empleados, transeúntes fuera del local).
- Crear un Dashboard gerencial interactivo que visualice mapas de calor de densidad, flujos de recorrido típicos y analítica de tiempos de permanencia por departamento.

## Justificación
La comprensión del flujo físico de clientes permite optimizar el diseño del plano de la tienda (Store Layout). Si los datos muestran que un pasillo frío (sin tráfico) tiene productos de alto margen, la gerencia puede reubicarlos o modificar la iluminación. Al medir el tráfico externo vs entradas reales, la tienda puede validar el ROI de campañas de vitrinas de temporada. Todo esto se logra de forma no intrusiva, sin obligar al cliente a descargar apps o escanear códigos.

## Metodología
Desarrollo iterativo de hardware IoT e ingeniería de datos espaciales. La fase uno consiste en el calibrado empírico de la constante de pérdida de propagación de la señal Wi-Fi en un entorno lleno de interferencias (estanterías metálicas, cuerpos humanos). Se desplegará un piloto con 10 sensores en un supermercado de 1,000 metros cuadrados. Se validará la precisión del conteo de personas del sistema Wi-Fi contra el registro de cámaras estéreo cuenta-personas instaladas en las entradas durante 4 semanas.

## Stack Tecnológico
- Hardware Sensor: ESP8266 / ESP32 en modo monitor, antenas omnidireccionales
- Backend de Ingestión: MQTT broker (Mosquitto), Node.js, Apache Kafka
- Procesamiento Analítico: Python (Pandas, SciPy para filtrado de señales de Kalman), PostgreSQL
- Frontend y Dashboard: React, D3.js, Leaflet/Mapbox para renderizado de mapas interiores
- Ciberseguridad: Algoritmos SHA-256 para hashing irreversible de identificadores MAC en el Edge

## Alcance
El sistema se enfoca en métricas agregadas de comportamiento espacial de multitudes, no en rastreo individualizado. La precisión espacial promedia los 2-3 metros, ideal para identificar zonas y pasillos, pero no estantes a nivel de centímetros. Solo detecta clientes que lleven un dispositivo con interfaz Wi-Fi activada (aproximadamente el 70-80% de la población urbana).

## Conclusión
Digitalizar el comportamiento en la tienda física democratiza el acceso a la inteligencia de negocios analítica para los minoristas, permitiéndoles competir con el e-commerce optimizando iterativamente su espacio comercial basándose en los verdaderos patrones de movimiento de sus consumidores.
