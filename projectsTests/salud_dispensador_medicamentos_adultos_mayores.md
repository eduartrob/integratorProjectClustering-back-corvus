# Plataforma de Gestión de Medicamentos para Adultos Mayores con Polifarmacia

## Resumen
Aplicación móvil y sistema dispensador inteligente de medicamentos para adultos mayores con polifarmacia (5 o más medicamentos simultáneos). El sistema gestiona los horarios de toma, emite recordatorios personalizados, detecta interacciones medicamentosas peligrosas y genera reportes de adherencia para el médico tratante. El dispensador físico entrega las pastillas correctas en el momento preciso para evitar errores de medicación.

## Introducción
Más del 40% de los adultos mayores en México toman 5 o más medicamentos simultáneamente. Los errores de medicación (dosis incorrectas, olvidos, confusión de pastillas) son la causa del 10-20% de las hospitalizaciones en este grupo etario. Un sistema integrado de gestión y dispensación inteligente puede prevenir miles de hospitalizaciones evitables al año.

## Objetivo General
Desarrollar un sistema integrado de gestión y dispensación automatizada de medicamentos para adultos mayores con polifarmacia que garantice la adherencia terapéutica, detecte interacciones medicamentosas y reporte al médico tratante en tiempo real.

## Objetivos Específicos
- Diseñar un dispensador electrónico de pastillas con 14 compartimentos (2 semanas de medicación), motor paso a paso y sensor de confirmación de extracción.
- Integrar base de datos de interacciones medicamentosas (DrugBank) con algoritmo de alerta en el momento de la prescripción o carga de medicamentos.
- Desarrollar aplicación móvil con recordatorios adaptativos que aprenden los horarios reales de toma del usuario para optimizar las notificaciones.
- Crear portal web para médicos con dashboard de adherencia, reportes de tomas perdidas y alertas de interacciones.
- Implementar reconocimiento de voz para usuarios con baja escolaridad o deterioro visual que no pueden leer la interfaz.

## Justificación
El costo de una hospitalización por error de medicación en un adulto mayor supera los 50,000 pesos. El costo del dispensador es inferior a 3,000 pesos. El retorno de inversión desde la perspectiva del sistema de salud es inmediato y significativo, especialmente considerando la creciente proporción de adultos mayores en la pirámide demográfica mexicana.

## Metodología
Investigación y desarrollo con prototipado iterativo. El dispensador se diseñará en CAD e imprimirá en 3D para la fase de pruebas. La aplicación se probará con 30 adultos mayores durante 3 meses, midiendo la adherencia terapéutica antes y durante el uso del sistema mediante conteo de pastillas residuales.

## Stack Tecnológico
- Hardware: Arduino Uno, motor paso a paso NEMA 17, sensor de peso HX711
- Backend: Django, PostgreSQL, DrugBank API
- Móvil: Flutter, push notifications con FCM
- Voz: Google Speech-to-Text API, síntesis de voz TTS
- Portal médico: React, Chart.js

## Alcance
Prueba piloto con 30 adultos mayores usuarios de INAPAM con polifarmacia. El dispensador maneja hasta 7 medicamentos diferentes en horarios de hasta 4 tomas diarias. No incluye medicamentos líquidos, inyectables ni controlados.

## Conclusión
La gestión tecnológica de la polifarmacia en adultos mayores es una necesidad urgente en una sociedad que envejece aceleradamente. Un sistema integrado de dispensación inteligente puede reducir significativamente la morbimortalidad asociada a errores de medicación en este grupo vulnerable.
