# Sistema de Detección de Dislexia y Apoyo al Aprendizaje para Niños de Primaria

## Resumen
Plataforma de screening y apoyo al aprendizaje para niños con dislexia en educación primaria. El sistema aplica pruebas de lectura gamificadas adaptadas al español para detección temprana de indicadores de dislexia, genera reportes diagnósticos para maestros y padres, y provee ejercicios de intervención terapéutica personalizados basados en el perfil cognitivo específico del niño detectado.

## Introducción
La dislexia afecta entre el 5% y el 10% de la población escolar. En México, más del 70% de los casos no reciben diagnóstico durante la educación primaria, generando retraso académico acumulado y daño a la autoestima. El diagnóstico formal requiere evaluación psicopedagógica especializada con costo de 3,000-8,000 pesos, inaccesible para la mayoría de familias. Un sistema de screening digital puede identificar niños en riesgo y activar apoyos tempranos sin costo.

## Objetivo General
Desarrollar una plataforma digital de screening de dislexia para niños de 6 a 10 años que aplique pruebas cognitivas validadas de forma gamificada, genere reportes diagnósticos preliminares e implemente ejercicios de intervención fonológica y visual adaptados al perfil individual de cada niño.

## Objetivos Específicos
- Digitalizar e implementar las pruebas PROLEC-R (Procesos Lectores - Revisado) en formato de minijuegos accesibles para niños de 6-10 años.
- Desarrollar algoritmo de clasificación de riesgo de dislexia basado en tiempos de respuesta, patrones de error y consistencia en pruebas de conciencia fonológica.
- Crear biblioteca de ejercicios de intervención fonológica, visual y ortográfica con generación procedural infinita de estímulos.
- Implementar seguimiento longitudinal del progreso con visualización de curvas de aprendizaje para maestros y padres.
- Diseñar sistema de alertas automáticas que notifique al maestro cuando un alumno supere el umbral de riesgo recomendando derivación a especialista.

## Justificación
La intervención temprana en dislexia entre los 6 y 8 años tiene una efectividad dramáticamente mayor que las intervenciones tardías. Cada año de retraso en el diagnóstico se traduce en rezago académico acumulado y mayor resistencia a la intervención terapéutica. Un sistema de screening masivo y gratuito puede transformar la trayectoria académica de miles de niños.

## Metodología
Investigación y desarrollo con validación psicométrica. Las pruebas digitalizadas se calibrarán con una muestra normativa de 300 niños sin dislexia y 50 niños con diagnóstico confirmado de dislexia fonológica. La validez de criterio se establecerá comparando las clasificaciones del sistema contra diagnósticos de psicólogos educativos certificados.

## Stack Tecnológico
- Frontend: React, Howler.js (audio), Framer Motion (animaciones lúdicas)
- Backend: Django, PostgreSQL
- ML: scikit-learn (Random Forest para clasificación de riesgo), análisis de tiempo de respuesta
- Audio: Web Speech API para síntesis de voz y reconocimiento de lectura oral
- Reportes: ReportLab (PDF) para informes para maestros y padres

## Alcance
La plataforma cubre el screening de dislexia fonológica y visual para primero a cuarto grado de primaria. Requiere supervisión de un adulto durante la aplicación. No constituye diagnóstico clínico formal y no reemplaza la evaluación psicopedagógica especializada.

## Conclusión
La detección temprana masiva de dislexia mediante tecnología puede cambiar radicalmente las trayectorias educativas de miles de niños mexicanos, convirtiendo lo que hoy es un obstáculo oculto y silencioso en una condición identificada y atendida oportunamente.
