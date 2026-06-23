# Boyas IoT Autónomas para Monitoreo de Calidad del Agua en Lagos

## Resumen
Desarrollo y despliegue de una red de sensores multiparamétricos encapsulados en boyas flotantes autónomas alimentadas por energía solar. Las boyas transmiten datos continuos sobre la calidad físico-química del agua de cuerpos lacustres (lagos y presas) utilizando telemetría de largo alcance LoRaWAN. El sistema permite la detección y alerta temprana de eventos de contaminación aguda y proliferación de algas nocivas (eutrofización) mediante análisis de tendencias en la nube.

## Introducción
La contaminación de cuerpos de agua dulces por descargas industriales clandestinas y escurrimientos agrícolas cargados de fertilizantes representa una amenaza existencial para la biodiversidad acuática y el suministro de agua potable urbana. El monitoreo tradicional consiste en extraer muestras manuales esporádicas y analizarlas en laboratorios; un proceso lento, costoso y que a menudo solo detecta la contaminación días después del evento crítico, cuando ya ha ocurrido mortandad masiva de peces o riesgo para la salud pública.

## Objetivo General
Establecer un sistema de monitoreo hídrico continuo y en tiempo real mediante boyas IoT de bajo costo, proporcionando alertas tempranas de contaminación química y biológica a las autoridades gestoras de cuencas y protección ambiental.

## Objetivos Específicos
- Diseñar y fabricar un ensamblaje mecánico estanco (clasificación IP68) resistente a la corrosión para la boya flotante, integrando paneles solares marinos y baterías de litio para autonomía perpetua.
- Integrar sondas electroquímicas de precisión para medir cinco parámetros críticos: oxígeno disuelto, pH, conductividad eléctrica, temperatura y turbidez.
- Implementar un nodo de comunicaciones IoT utilizando el protocolo LoRaWAN para enviar paquetes de datos telemetrícos cifrados a distancias superiores a 10 km hasta un gateway costero, superando la falta de cobertura celular en zonas remotas.
- Desarrollar un backend de recepción de datos que aplique calibración estadística a las lecturas crudas de los sensores para compensar la deriva natural (sensor drift) por ensuciamiento biológico (biofouling).
- Construir un dashboard ambiental público y un sistema de alertas SMS para notificar a plantas potabilizadoras e inspectores gubernamentales cuando los umbrales de seguridad son rebasados bruscamente.

## Justificación
Un monitoreo hiper-denso y en tiempo real cambia el paradigma de la protección ambiental de una autopsia forense (analizar por qué murió el ecosistema) a una medicina preventiva (detener la fuga antes de que alcance niveles letales). Construir hardware de código abierto y bajo costo reduce la barrera de entrada técnica para que asociaciones civiles y municipios pequeños puedan vigilar y defender sus propios recursos hídricos locales sin depender de presupuestos federales millonarios.

## Metodología
Diseño mecatrónico y desarrollo de sistemas de información ambiental. La etapa de hardware incluye la fabricación de PCB personalizadas de ultra bajo consumo energético (Modo Sleep profundo) y la calibración de sensores frente a soluciones estándar de laboratorio. El proyecto piloto desplegará 4 boyas en un lago local crítico durante 6 meses, correlacionando las alertas emitidas por los algoritmos en la nube con validaciones visuales en campo (ej. confirmación fotográfica de blooms de algas tras una alerta de alta turbidez y bajo oxígeno).

## Stack Tecnológico
- Hardware: Microcontrolador STM32 o ESP32, transceptor Semtech SX1276 (LoRa), sensores industriales RS485/I2C, celdas solares 5V
- Protocolos IoT: LoRaWAN, The Things Network (TTN) servidor de red, MQTT
- Arquitectura de Datos Cluod: InfluxDB (Time-series database), Telegraf, Grafana para visualización de dashboards
- Lenguajes: C++ para firmware embebido, Python para el motor de calibración estadística en backend
- Diseño CAD: Autodesk Inventor, impresión 3D de alta densidad e impermeabilización con resina epoxi

## Alcance
El sistema piloto estará calibrado para aguas superficiales dulces. Las boyas reportarán datos cada 15 minutos de forma continua. El prototipo no medirá concentración de metales pesados o microplásticos directamente (debido a la falta de sensores comerciales de bajo costo para estas variables en campo), sino que inferirá la contaminación mediante perturbaciones en la conductividad y el pH base.

## Conclusión
La conjunción de sensores de calidad del agua con la telemetría de área extendida y baja potencia (LPWAN) permite visibilizar los ciclos químicos invisibles de los ecosistemas acuáticos, brindando a las autoridades ambientales los ojos necesarios para proteger activamente el recurso más vital del planeta.
