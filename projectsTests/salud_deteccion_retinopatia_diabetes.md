# Aplicación Móvil para Detección Temprana de Diabetes Tipo 2 mediante Análisis de Retina

## Resumen
Aplicación móvil que utiliza la cámara del smartphone para capturar imágenes del fondo de ojo mediante un adaptador de bajo costo y analiza automáticamente signos de retinopatía diabética con un modelo de deep learning entrenado con 80,000 imágenes retinianas. El sistema provee un diagnóstico preliminar y refiere al paciente al especialista cuando detecta signos de riesgo.

## Introducción
La diabetes tipo 2 afecta a 14 millones de mexicanos y la retinopatía diabética es la principal causa de ceguera evitable en adultos en edad productiva. El diagnóstico convencional requiere un oftalmólogo con equipo de fondoscopia valorado en más de 200,000 pesos. Una solución móvil puede masificar el tamizaje en clínicas del primer nivel de atención.

## Objetivo General
Desarrollar un sistema de inteligencia artificial embebido en aplicación móvil capaz de detectar signos de retinopatía diabética a partir de imágenes de fondo de ojo capturadas con smartphone, con sensibilidad diagnóstica mayor al 85% y especificidad mayor al 90%.

## Objetivos Específicos
- Entrenar un modelo de clasificación de imágenes basado en EfficientNet-B4 con el dataset EyePACS (80,000 imágenes etiquetadas por oftalmólogos).
- Implementar técnicas de data augmentation para manejar el desbalance de clases (95% sin retinopatía vs 5% con retinopatía severa).
- Desarrollar adaptador óptico 3D-imprimible que convierte el flash del smartphone en un iluminador de fondo de ojo de campo estrecho.
- Crear pipeline de preprocesamiento de imagen con corrección de exposición y detección de calidad de imagen antes del análisis.
- Integrar el modelo optimizado con TensorFlow Lite en aplicación Android de consumo máximo de 50MB.

## Justificación
El costo del adaptador óptico imprimible es inferior a 200 pesos. Combinado con la aplicación gratuita, el costo total de un tamizaje es essencialmente el tiempo del médico de primer nivel (10 minutos), comparado con 1,500-3,000 pesos de una consulta oftalmológica especializada.

## Metodología
Investigación y desarrollo con validación clínica prospectiva. Fase 1: entrenamiento y validación del modelo en laboratorio. Fase 2: prueba piloto con 200 pacientes diabéticos en clínica del IMSS, comparando el diagnóstico de la IA contra el de un oftalmólogo certificado como gold standard.

## Stack Tecnológico
- ML: TensorFlow 2.x, EfficientNet-B4, GradCAM para explicabilidad
- Optimización: TensorFlow Lite, cuantización INT8
- Móvil: Kotlin (Android), MLKit
- Backend: FastAPI, PostgreSQL para registros clínicos
- 3D: Fusion 360 para diseño del adaptador óptico

## Alcance
La aplicación se desarrollará exclusivamente para Android 8.0+. La validación clínica se realizará en una clínica del IMSS con aprobación del comité de ética. No incluye diagnóstico de otras patologías oculares ni de glaucoma.

## Conclusión
La democratización del tamizaje de retinopatía diabética mediante smartphone puede salvar la visión de miles de personas al año en México, convirtiendo un examen de especialidad en un procedimiento de primer nivel de atención.
