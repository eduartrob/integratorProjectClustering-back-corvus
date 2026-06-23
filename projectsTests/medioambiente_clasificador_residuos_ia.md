# Basurero Inteligente con Clasificación Automática de Residuos

## Resumen
Módulo mecatrónico que se adapta a estaciones de reciclaje en espacios públicos y comerciales. Utiliza una cámara integrada y algoritmos ligeros de visión por computadora ejecutados localmente para identificar el tipo de residuo que el usuario está a punto de desechar (plástico PET, aluminio, papel o desperdicio general). Tras clasificar el objeto, un mecanismo interno direcciona automáticamente el residuo al contenedor correspondiente, independientemente del agujero por el que el usuario lo haya introducido.

## Introducción
Las campañas de educación para la separación de residuos en origen tienen una tasa de éxito históricamente baja. En espacios concurridos como centros comerciales, aeropuertos y universidades, los usuarios a menudo tiran la basura en el contenedor equivocado por prisa, confusión sobre los símbolos de reciclaje o indiferencia. Un solo líquido derramado en el contenedor de papel arruina todo el lote, encareciendo enormemente los procesos de separación manual en las plantas de tratamiento y reduciendo el porcentaje real de materiales que logran ser reciclados.

## Objetivo General
Aumentar la pureza de los flujos de materiales reciclables recolectados en espacios públicos del 40% al 90% mediante el diseño e implementación de un sistema electromecánico autónomo de clasificación de residuos por visión artificial.

## Objetivos Específicos
- Entrenar un modelo de redes neuronales convolucionales especializado en el reconocimiento de envases y empaques comunes deformados (botellas aplastadas, latas oxidadas, vasos de café sucios).
- Desarrollar un sistema de inferencia Edge AI capaz de clasificar el objeto en menos de 0.5 segundos localmente, garantizando una respuesta fluida para el usuario final.
- Diseñar y manufacturar el mecanismo de clasificación física (tolva móvil direccional o plataformas basculantes) usando motores paso a paso y materiales resistentes a ambientes corrosivos.
- Implementar sensores ultrasónicos para monitorear el nivel de llenado de cada compartimento de reciclaje interno y transmitir alertas vía IoT a los servicios de recolección.
- Crear una aplicación web para los administradores de mantenimiento que visualice métricas de volumen de material reciclado generado y el estado operativo de la red de basureros inteligentes.

## Justificación
La economía circular no puede prosperar si el insumo primario (el material reciclable) está altamente contaminado. Automatizar la separación en el punto exacto de desecho elimina el eslabón más débil de la cadena: el error humano. Además, optimizar las rutas de recolección basándose en niveles reales de llenado reduce los costos operativos de mantenimiento de los edificios y disminuye la huella de carbono de los camiones recolectores.

## Metodología
Investigación y desarrollo de hardware IoT/Edge AI. Construcción de un dataset propio de imágenes de basura local (basura en México tiene marcas, envases y formas específicas). Entrenamiento del modelo YOLOv5-Lite o MobileNet optimizado para hardware de bajo consumo. Diseño mecánico iterativo y pruebas de fatiga del mecanismo de clasificación sometido a elementos líquidos y sólidos irregulares. Instalación piloto de 3 prototipos en la plaza central de la universidad para evaluación en entorno real durante un mes.

## Stack Tecnológico
- Inteligencia Artificial: TensorFlow Lite, OpenCV, conjunto de datos TrashNet (base) + datos locales
- Hardware Computacional: Raspberry Pi 4 o módulo NVIDIA Jetson Nano, módulo de cámara Raspberry Pi HQ
- Diseño Electromecánico: Autodesk Fusion 360, motores paso a paso NEMA 17, controladores puente H, actuadores de compuerta en PLA impreso 3D
- Telemetría IoT: Protocolo MQTT, red Wi-Fi, sensores ultrasónicos HC-SR04
- Panel Web: React, Node.js, InfluxDB para series temporales de llenado

## Alcance
El prototipo inicial se diseñará para clasificar tres grandes categorías: PET transparente, latas de aluminio y residuos no reciclables. El sistema clasifica el objeto individualmente mientras cae; no puede separar una bolsa entera de basura pre-mezclada depositada de golpe. El tamaño máximo del objeto estará limitado por la boca de admisión del prototipo (aprox. botella de 2.5 litros).

## Conclusión
Combinar la Inteligencia Artificial de borde con ingeniería mecánica resuelve elegantemente el complejo problema social de la separación de residuos. El basurero inteligente asegura que la intención ecológica del diseño de reciclaje se convierta en una realidad operativa efectiva, independientemente del nivel de educación ambiental del usuario pasajero.
