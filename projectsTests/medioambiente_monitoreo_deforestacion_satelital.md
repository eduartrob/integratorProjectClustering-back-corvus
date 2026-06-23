# Detección Automática de Deforestación Ilegal usando Imágenes Satelitales

## Resumen
Plataforma de inteligencia geoespacial que analiza continuamente flujos de imágenes satelitales multiespectrales públicas (como las de los programas Sentinel-2 y Landsat) para detectar cambios en la cobertura forestal. Utiliza redes neuronales de segmentación semántica para identificar parches de tala reciente, discriminando entre deforestación antropogénica y cambios estacionales naturales, generando alertas tempranas para autoridades ambientales y ONGs antes de que el daño ecológico sea irreversible.

## Introducción
La Amazonía y las selvas centroamericanas están perdiendo miles de hectáreas diarias debido a la tala ilegal, la minería no regulada y la expansión agrícola clandestina. La vigilancia forestal tradicional mediante patrullajes en tierra es logísticamente inabarcable e ineficiente, y a menudo expone a los guardabosques a riesgos letales frente al crimen organizado. La vigilancia desde el espacio es la única manera de escalar la protección ambiental, pero procesar manualmente terabytes de imágenes diarias es imposible.

## Objetivo General
Desarrollar un sistema automatizado de monitoreo forestal capaz de identificar nuevos eventos de deforestación ilegal de más de 0.5 hectáreas en un plazo máximo de 48 horas tras el evento, alertando automáticamente a las autoridades competentes.

## Objetivos Específicos
- Establecer un pipeline de datos que descargue y pre-procese imágenes ópticas y de radar de apertura sintética (SAR) de agencias espaciales públicas.
- Implementar algoritmos de cálculo de índices de vegetación (como NDVI - Índice de Vegetación de Diferencia Normalizada) como primera capa de filtrado para anomalías fenológicas.
- Entrenar una red neuronal de segmentación semántica (U-Net) para clasificar píxel por píxel el tipo de perturbación en el terreno, diferenciando nubes o sombras de cicatrices de tala.
- Integrar datos de radar (SAR) que permiten "ver a través de las nubes", garantizando el monitoreo continuo durante la temporada de lluvias en zonas tropicales.
- Construir un dashboard geográfico web (GIS) donde los analistas ambientales puedan verificar las alertas, generar polígonos de afectación y exportar coordenadas GPS precisas para el despliegue de operativos.

## Justificación
El tiempo de respuesta es el factor crítico en la conservación ambiental. Una alerta generada semanas después de la tala solo sirve para documentar la tragedia. Un sistema en tiempo casi real que detecte la apertura de caminos clandestinos permite a las autoridades intervenir en el acto, confiscar maquinaria y evitar que un claro de media hectárea se convierta en cien hectáreas arrasadas, protegiendo hábitats de especies en peligro y mitigando emisiones de carbono.

## Metodología
Investigación en teledetección (Remote Sensing) e Inteligencia Artificial aplicada. Se utilizarán series temporales de datos multiespectrales (Sentinel-2) cruzados con datos SAR (Sentinel-1). El modelo de Deep Learning se entrenará con un conjunto de datos etiquetados de parches de deforestación amazónica históricos (ej. PRODES dataset). La validación técnica se realizará calculando el índice F1 y la precisión de intersección sobre unión (IoU) en áreas geográficas nunca vistas por el modelo.

## Stack Tecnológico
- Procesamiento Espacial: Python, Google Earth Engine API, GDAL/Rasterio
- Machine Learning / Deep Learning: TensorFlow, Keras (arquitectura U-Net), Scikit-image
- Base de Datos Espacial: PostgreSQL con extensión PostGIS
- Visualización de Mapas: Mapbox GL JS, GeoJSON, React.js
- Proveedores de Datos: Copernicus Open Access Hub (Agencia Espacial Europea)

## Alcance
El sistema monitoreará continuamente una región piloto delimitada (ej. Reserva de la Biosfera de Calakmul, México). La resolución espacial máxima estará limitada por las imágenes públicas (10x10 metros por píxel en Sentinel-2). No detectará extracción selectiva de un solo árbol bajo el dosel intacto, enfocándose en la tala rasa o perturbación significativa de la cobertura (apertura de caminos).

## Conclusión
La integración de satélites de observación de la tierra públicos con el poder analítico del Deep Learning democratiza la vigilancia ambiental, convirtiendo cada píxel del planeta en un sensor constante de protección ecológica que empodera la acción climática inmediata.
