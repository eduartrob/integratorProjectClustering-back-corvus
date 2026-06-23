# Modelo de Riesgo Predictivo de Incendios Forestales usando Sensores IoT y Datos Climáticos

## Resumen
Sistema de inteligencia climática que calcula el riesgo dinámico de ignición y propagación de incendios forestales en áreas naturales protegidas. El sistema fusiona datos meteorológicos satelitales globales, cartografía de elevación topográfica y lecturas hiper-locales en tiempo real de una red de sensores IoT de bajo costo dispersos en el bosque, introduciendo estas variables en modelos de Machine Learning para generar mapas de calor probabilísticos diarios.

## Introducción
El cambio climático ha extendido severamente las temporadas de sequía, aumentando la frecuencia, intensidad y voracidad de los incendios forestales a niveles nunca antes vistos (megaincendios). Las agencias de protección civil operan principalmente en un modo reactivo: actúan cuando el humo ya es visible. Los modelos de riesgo estáticos (basados solo en estaciones del año y altitud) no reflejan las condiciones del microclima diario del bosque seco que facilitan la chispa inicial.

## Objetivo General
Desarrollar un sistema de pronóstico de riesgo de incendios de alta resolución espacial que permita a las autoridades de protección civil optimizar el despliegue preventivo de recursos y patrullas basándose en mapas dinámicos diarios con una precisión predictiva de áreas de alto peligro superior al 85%.

## Objetivos Específicos
- Desplegar una red de malla (Mesh Network) de sensores meteorológicos IoT en el dosel forestal para medir humedad del aire, temperatura, velocidad del viento y humedad del suelo y hojarasca.
- Integrar bases de datos públicas geoespaciales como modelos de elevación digital (DEM) topográfica y la densidad/tipo de cobertura vegetal (combustible disponible).
- Construir un modelo de Machine Learning supervisado (XGBoost / Random Forest) entrenado con el registro histórico georreferenciado de incendios de los últimos 10 años en la región.
- Desarrollar un algoritmo predictivo espacial que genere rasterizados (mapas) indicando el "Índice de Peligro de Incendio Forestal" categorizado por color para las próximas 24, 48 y 72 horas.
- Diseñar un sistema web de visualización GIS que integre simulaciones de la dirección de propagación potencial basándose en los vectores de viento pronosticados por las estaciones locales.

## Justificación
La prevención es exponencialmente más barata y segura que el combate directo del fuego forestal. Saber exactamente qué cuadrantes específicos de una cadena montañosa tienen hoy las condiciones "barril de pólvora" (hojarasca seca, baja humedad ambiental y vientos cálidos encañonados) permite realizar patrullajes preventivos, cerrar senderos turísticos temporalmente y posicionar equipos de mitigación (cortafuegos) reduciendo la vulnerabilidad de ecosistemas vitales y poblaciones cercanas.

## Metodología
Desarrollo de modelos predictivos y prototipado IoT. La red de sensores servirá para la validación local (ground truth) de los datos meteorológicos macroscópicos. El modelo histórico se construirá dividiendo la región de estudio en un grid de cuadrículas espaciales de 1x1 km. Cada celda será clasificada binariamente (hubo incendio o no hubo) frente a las variables climatológicas de ese día histórico específico. La evaluación del modelo utilizará métricas de curvas ROC-AUC para manejar el desbalance severo de clases (ya que la mayoría de los días no hay incendios).

## Stack Tecnológico
- Machine Learning Espacial: Python (Scikit-Learn, XGBoost, GeoPandas para manejo de datos vectoriales)
- Infraestructura GIS: PostGIS (almacenamiento geográfico), QGIS (análisis offline), Geoserver (publicación de mapas WMS/WFS)
- Hardware Forestal: Nodos sensores basados en microcontroladores de ultra-baja potencia, comunicación por radio de larga distancia LoRa (Topología Malla/Star) a gateways 4G solares.
- Frontend Analítico: React.js, OpenLayers / Leaflet JS para visualización de mapas Raster sobre cartografía base.
- Integración API Clima: Datos históricos y forecast de la NOAA, OpenWeather.

## Alcance
El modelo predictivo calculará el riesgo probabilístico de ocurrencia de incendios pero no predice con exactitud milimétrica cuándo o quién iniciará el fuego intencional. La simulación de propagación del fuego abarcará proyecciones a corto plazo (2-4 horas) una vez el incendio haya iniciado, limitándose a terrenos rurales no poblados urbanamente (Wildland-Urban Interface).

## Conclusión
Combinar la sensorística distribuida en terreno con la capacidad de generalización del Machine Learning convierte el arte de predecir el comportamiento extremo de la naturaleza en una ciencia rigurosa y gestionable, proporcionando el conocimiento anticipado necesario para proteger el patrimonio natural frente al colapso climático.
