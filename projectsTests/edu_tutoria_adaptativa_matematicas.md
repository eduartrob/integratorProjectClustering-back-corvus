# Sistema de Tutoría Adaptativa con IA para Matemáticas en Bachillerato

## Resumen
Sistema de tutoría inteligente para matemáticas de bachillerato que diagnostica las brechas de conocimiento de cada estudiante mediante pruebas adaptativas y genera rutas de aprendizaje personalizadas con ejercicios progresivos. La IA detecta el tipo de error conceptual (no solo si la respuesta es incorrecta) y provee explicaciones específicas para cada malentendido identificado, reduciendo la deserción escolar por reprobación de matemáticas.

## Introducción
El 45% de los estudiantes de bachillerato en México reprueban al menos una materia de matemáticas durante su trayectoria escolar. La matemática es la principal causa de abandono escolar a nivel medio superior. Los sistemas de tutoría inteligente han demostrado en investigación educativa resultados equivalentes a dos desviaciones estándar de ventaja sobre la instrucción tradicional.

## Objetivo General
Desarrollar un sistema de tutoría inteligente para matemáticas de bachillerato (álgebra, geometría analítica, probabilidad y estadística, cálculo diferencial) que personalice la instrucción mediante diagnóstico continuo, rutas adaptativas y retroalimentación conceptual específica para cada tipo de error.

## Objetivos Específicos
- Implementar un modelo de trazado de conocimiento (knowledge tracing) basado en redes LSTM para predecir el dominio del estudiante en cada concepto matemático.
- Desarrollar clasificador de tipos de error algebraico y geométrico usando modelos de reconocimiento de ecuaciones manuscritas con CNN.
- Crear un motor de selección de ejercicios basado en la Teoría de Respuesta al Ítem (TRI) para maximizar el aprendizaje por unidad de tiempo.
- Diseñar sistema de generación procedural de ejercicios con dificultad graduada y variedad superficial infinita para evitar la memorización de soluciones.
- Implementar simulador de examen tipo EXANI-II con análisis de rendimiento por área temática y predicción de score en el examen real.

## Justificación
Un maestro de matemáticas atiende en promedio 35-40 estudiantes simultáneamente y no puede proveer retroalimentación individualizada. El sistema de tutoría actúa como un maestro personal disponible 24/7 que conoce exactamente dónde está el bloqueo de cada estudiante y adapta su estrategia de enseñanza al perfil cognitivo individual.

## Metodología
Desarrollo de investigación con marco de Learning Analytics. Se utilizarán datos de 10,000 sesiones de práctica anónimas de estudiantes del CETIS como base de entrenamiento. La efectividad se medirá comparando calificaciones en exámenes parciales de dos grupos: uno que usa el sistema y uno de control.

## Stack Tecnológico
- ML: Deep Knowledge Tracing (PyTorch), TRT para reconocimiento de escritura
- Backend: FastAPI, PostgreSQL, Celery para cómputo asíncrono
- Frontend: React, MathJax para renderizado de ecuaciones, Canvas API para escritura táctil
- Generador de ejercicios: sistema de plantillas + SymPy para verificación algebraica

## Alcance
El sistema cubre el currículo de matemáticas del Componente de Formación Básica del bachillerato tecnológico (4 semestres). Diseñado para uso individual y complementario a la clase presencial. No incluye geometría espacial 3D ni cálculo integral.

## Conclusión
Los sistemas de tutoría inteligente representan la frontera más prometedora de la tecnología educativa para reducir la brecha de aprendizaje en matemáticas y disminuir la deserción escolar que fragmenta el futuro de miles de jóvenes mexicanos.
