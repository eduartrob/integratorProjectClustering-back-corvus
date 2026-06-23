# Predicción de Demanda de Inventario con Machine Learning

## Resumen
Sistema predictivo avanzado basado en aprendizaje automático que utiliza datos históricos de ventas, estacionalidad, factores climáticos, tendencias en redes sociales e indicadores macroeconómicos para prever la demanda futura de productos SKU por SKU. El modelo optimiza las órdenes de compra y los niveles de stock de seguridad para cadenas de retail y centros de distribución.

## Introducción
El desequilibrio entre la oferta y la demanda genera dos de los problemas más costosos en la logística comercial: el quiebre de stock (venta perdida e insatisfacción del cliente) y el sobre-inventario (capital inmovilizado, costos de almacenamiento y obsolescencia). Los métodos estadísticos tradicionales (medias móviles) no logran capturar la complejidad multivariable del comportamiento de compra moderno.

## Objetivo General
Desarrollar un motor de inteligencia artificial para la predicción de la demanda de productos que reduzca el error de pronóstico (MAPE) en un 25% respecto a los métodos tradicionales, optimizando el capital de trabajo inmovilizado en inventario.

## Objetivos Específicos
- Construir un pipeline de ingestión y limpieza de datos (Data Lake) que unifique el historial de ventas del ERP, datos de clima, y calendario de festividades/promociones.
- Entrenar y comparar múltiples modelos predictivos de series temporales incluyendo SARIMA, Prophet (Facebook), XGBoost y Redes Neuronales Recurrentes (LSTM).
- Implementar un sistema de agrupamiento dinámico que trate de forma distinta los productos de alta rotación (fast-moving) de los productos de venta esporádica (intermitentes).
- Desarrollar un recomendador de órdenes de compra que calcule automáticamente el punto de reorden y la cantidad económica de pedido (EOQ) basado en la predicción.
- Crear un dashboard interactivo para el equipo de planeación de la demanda que permita simular escenarios (What-If analysis) modificando variables como campañas de marketing.

## Justificación
Para una cadena minorista mediana, una mejora del 10% en la precisión del pronóstico de demanda puede traducirse en millones de pesos liberados de inventario obsoleto y en un aumento directo de los ingresos al tener el producto disponible cuando el cliente lo busca. El aprendizaje automático permite escalar esta precisión analítica a catálogos de miles de productos simultáneamente.

## Metodología
Metodología CRISP-DM para ciencia de datos. Se utilizará un dataset histórico de 3 años de ventas diarias de una cadena regional de supermercados (anonimizado). Se dividirá en conjuntos de entrenamiento, validación y prueba (Time Series Split). La métrica principal de optimización será el MAPE (Mean Absolute Percentage Error) y el WMAPE ponderado por volumen de ventas.

## Stack Tecnológico
- Procesamiento de Datos: Apache Spark, Pandas, SQL
- Machine Learning: Scikit-learn, XGBoost, Prophet, TensorFlow/Keras (LSTM)
- Base de Datos: Snowflake o BigQuery (Data Warehouse)
- Backend: Python (Flask), Celery (batch processing nocturno)
- Visualización: Streamlit o Tableau Embedded

## Alcance
El modelo predecirá la demanda a nivel diario, semanal y mensual con un horizonte máximo de previsión de 90 días. Soporta hasta 50,000 SKUs. No incluye la automatización de la ejecución de la compra con proveedores, solo genera la recomendación para ser aprobada por el analista de compras.

## Conclusión
La transición de pronósticos basados en intuición o fórmulas estáticas a modelos probabilísticos basados en Machine Learning representa la madurez analítica de la cadena de suministro, permitiendo a las empresas anticiparse al mercado en lugar de solo reaccionar al pasado.
