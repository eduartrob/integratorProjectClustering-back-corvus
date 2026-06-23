# Sistema IoT para Agricultura de Precisión con Sensores de Suelo

## Resumen
Plataforma de agricultura de precisión que integra sensores IoT de humedad, temperatura, pH y nutrientes del suelo con sistemas de riego automatizado. Utiliza machine learning para predecir necesidades hídicas y optimizar el consumo de agua hasta un 40% en cultivos hortícolas.

## Introducción
La agricultura consume aproximadamente el 70% del agua dulce disponible a nivel mundial. En México, el sector agrícola enfrenta crecientes restricciones hídricas que amenazan la seguridad alimentaria. Este proyecto desarrolla una solución tecnológica accesible para pequeños y medianos agricultores que permite optimizar el uso del agua mediante sensores IoT y algoritmos de predicción de riego.

## Objetivo General
Implementar un sistema de agricultura de precisión basado en sensores IoT de suelo y microcontroladores de bajo costo que automatice el riego y fertilización aplicando modelos de machine learning para predicción de necesidades del cultivo.

## Objetivos Específicos
- Diseñar sensores de humedad de suelo, temperatura, pH y conductividad eléctrica con Arduino Mega y módulos de telemetría Zigbee.
- Desarrollar modelos de regresión para predicción de evapotranspiración usando datos meteorológicos y de suelo.
- Implementar sistema de riego automatizado por zonas con válvulas solenoides controladas por relés.
- Crear aplicación móvil Android para visualización de datos del campo y control remoto del riego.
- Validar el ahorro de agua mediante experimentos comparativos en parcelas de control durante dos ciclos de cultivo.

## Justificación
El acceso a tecnología de precisión ha estado históricamente limitado a grandes agroempresas. Este sistema reduce la barrera de entrada al ofrecer hardware de bajo costo y software de código abierto, permitiendo a pequeños productores competir con mayores eficiencias productivas.

## Metodología
Investigación aplicada con diseño cuasi-experimental. Se instrumentarán dos parcelas idénticas: una con el sistema propuesto y una de control con riego convencional. Las variables dependientes son: consumo de agua (litros), rendimiento del cultivo (kg/m²) y calidad organoléptica. Los datos se analizarán con pruebas estadísticas t de Student y ANOVA.

## Stack Tecnológico
- Hardware: Arduino Mega, sensores Soil Moisture, pH-meter, Zigbee XBee
- Backend: Python Flask, PostgreSQL, TimescaleDB
- ML: Scikit-learn, regresión lineal múltiple, Random Forest
- Móvil: Android nativo (Java/Kotlin)
- Protocolo: MQTT, HTTP REST

## Alcance
El sistema se implementará en una parcela hortícola de 1 hectárea durante 6 meses. El estudio se limita a cultivos de tomate y chile bajo condiciones de temporal controlado. No incluye integración con drones de aspersión.

## Conclusión
La convergencia de IoT, machine learning y agricultura ofrece una oportunidad real de transformación del sector agrícola nacional hacia la sostenibilidad hídrica sin sacrificar productividad.
