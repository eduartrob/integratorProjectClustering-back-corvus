# Sistema de Gestión de Energía IoT para Edificios Inteligentes

## Resumen
Plataforma de gestión energética basada en IoT para edificios comerciales y residenciales que monitorea el consumo eléctrico por circuito, detecta equipos ineficientes y optimiza automáticamente el encendido y apagado de sistemas de climatización, iluminación y equipos industriales mediante algoritmos de aprendizaje automático que aprenden los patrones de ocupación del edificio.

## Introducción
El sector de edificios representa aproximadamente el 40% del consumo energético global. En México, las tarifas eléctricas comerciales e industriales tienen componentes de demanda máxima que penalizan los picos de consumo. Un sistema inteligente de gestión energética puede reducir la factura eléctrica hasta un 30% sin comprometer el confort de los ocupantes.

## Objetivo General
Desarrollar un sistema IoT de gestión energética para edificios que monitoree el consumo en tiempo real, identifique patrones de desperdicio y automatice el control de cargas eléctricas optimizando la demanda máxima y el consumo total.

## Objetivos Específicos
- Instalar medidores de energía inteligentes por circuito con módulos CT (transformadores de corriente) y ESP32 para comunicación.
- Implementar algoritmos de clustering para identificar perfiles de consumo y detectar anomalías energéticas.
- Desarrollar sistema de control automático de climatización con integración de termostatos Nest y equipos VRF.
- Crear gemelo digital del edificio en plataforma BIM (Building Information Modeling) conectado con datos IoT en tiempo real.
- Implementar predicción de demanda eléctrica con 24 horas de anticipación usando modelos Prophet y LSTM.

## Justificación
Los sistemas BMS (Building Management Systems) comerciales tienen costos de implementación que superan los 500,000 pesos por edificio, inaccesibles para la mayoría de propietarios de edificios medianos. Esta solución ofrece funcionalidades equivalentes al 20% del costo utilizando hardware de código abierto y software libre.

## Metodología
Implementación en tres fases: instrumentación del edificio (mes 1-2), desarrollo del sistema de control (mes 3-4) y optimización y validación (mes 5-6). La validación se realizará comparando las facturas eléctricas de los 3 meses anteriores y posteriores a la implementación.

## Stack Tecnológico
- Hardware: ESP32, transformadores de corriente SCT-013, relay modules
- Backend: Node-RED, InfluxDB, MQTT Broker Mosquitto
- ML: Python Prophet, LSTM, scikit-learn KMeans
- BIM: Autodesk Revit API, Forge Platform
- Frontend: Grafana, Vue.js

## Alcance
Implementación en un edificio universitario de 4 pisos con 80 circuitos monitoreados. El sistema de control automático se limita a iluminación y climatización. Los sistemas de seguridad y contra incendios quedan fuera del alcance.

## Conclusión
La gestión energética inteligente basada en IoT y machine learning tiene el potencial de transformar la eficiencia energética del sector inmobiliario, reduciendo costos operativos y la huella de carbono de los edificios.
