# Sistema IoT de Monitoreo de Calidad del Aire en Zonas Urbanas

## Resumen
Este proyecto desarrolla una red de sensores IoT distribuida para monitorear en tiempo real la calidad del aire en zonas urbanas densamente pobladas. La plataforma integra sensores de partículas PM2.5, CO2, NO2 y ozono conectados mediante protocolo MQTT a una plataforma en la nube que procesa y visualiza los datos para alertas tempranas de contaminación.

## Introducción
La contaminación del aire es uno de los problemas ambientales más críticos en las ciudades modernas. Según la OMS, más del 90% de la población mundial respira aire que supera los límites de seguridad recomendados. Este sistema busca proporcionar datos granulares a nivel de calle para que las autoridades y ciudadanos tomen decisiones informadas sobre movilidad y salud pública.

## Objetivo General
Desarrollar una red de monitoreo de calidad del aire basada en dispositivos IoT de bajo costo que transmita datos en tiempo real a una plataforma web accesible para ciudadanos y autoridades municipales.

## Objetivos Específicos
- Diseñar e implementar nodos sensores con ESP32 capaces de medir PM2.5, CO2, temperatura y humedad relativa.
- Establecer comunicación inalámbrica entre nodos mediante protocolo MQTT sobre WiFi y LoRaWAN para zonas sin cobertura WiFi.
- Desarrollar un backend en Node.js con base de datos InfluxDB para series temporales de datos de sensores.
- Crear un dashboard web con mapas de calor georreferenciados usando Leaflet.js.
- Implementar un sistema de alertas por SMS y notificaciones push cuando los índices superen umbrales críticos.

## Justificación
Las estaciones meteorológicas oficiales son escasas y su cobertura geográfica es limitada. Este sistema permite una densidad de monitoreo significativamente mayor a un costo por nodo inferior al 5% de una estación convencional, democratizando el acceso a datos ambientales de calidad.

## Metodología
Se implementará una arquitectura de tres capas: capa de percepción (sensores ESP32 + módulos de medición), capa de red (MQTT Broker en servidor cloud) y capa de aplicación (dashboard web y API REST). Los nodos se calibrarán contra estaciones de referencia certificadas durante un período de 30 días para validar la precisión de las mediciones.

## Stack Tecnológico
- Hardware: ESP32, sensores SDS011, MH-Z19, DHT22
- Protocolo: MQTT, LoRaWAN
- Backend: Node.js, InfluxDB, Grafana
- Frontend: React, Leaflet.js, Chart.js
- Cloud: AWS IoT Core, Lambda

## Alcance
El sistema cubrirá un área piloto de 5 km² en zona urbana, con instalación de 20 nodos sensores durante el primer semestre académico. Se excluye la integración con sistemas gubernamentales oficiales en esta fase.

## Conclusión
La implementación de una red IoT de monitoreo ambiental a bajo costo representa una solución escalable y replicable para mejorar la salud pública urbana mediante datos ambientales de alta resolución espacial y temporal.
