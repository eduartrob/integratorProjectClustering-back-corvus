# Chatbot de Salud Mental para Detección y Acompañamiento de Ansiedad en Universitarios

## Resumen
Chatbot conversacional basado en procesamiento de lenguaje natural entrenado con técnicas de terapia cognitivo-conductual (TCC) para brindar acompañamiento psicológico de primer nivel a estudiantes universitarios con ansiedad leve a moderada. El sistema realiza evaluaciones periódicas con escalas validadas (GAD-7, PHQ-9) y refiere proactivamente a servicios de salud mental cuando detecta señales de crisis.

## Introducción
La pandemia de COVID-19 incrementó en un 25% los trastornos de ansiedad y depresión en jóvenes universitarios según la OMS. En México, menos del 30% de las universidades públicas tienen servicios de salud mental suficientes para atender la demanda estudiantil. Un chatbot terapéutico puede ampliar el alcance del servicio de consejería universitaria a bajo costo, operando 24/7 y sin estigma social.

## Objetivo General
Desarrollar un chatbot de salud mental basado en IA conversacional que aplique técnicas de terapia cognitivo-conductual para acompañar a estudiantes universitarios con síntomas de ansiedad leve a moderada, con detección automática de crisis y escalamiento a profesionales de salud mental.

## Objetivos Específicos
- Entrenar un modelo de diálogo terapéutico basado en DialoGPT-medium fine-tuneado con conversaciones de TCC en español.
- Implementar módulo de evaluación psicológica que aplique las escalas GAD-7 y PHQ-9 de forma conversacional cada 2 semanas.
- Desarrollar detector de crisis mediante análisis de sentimientos y palabras clave de riesgo suicida con escalamiento inmediato a línea de crisis.
- Crear sistema de registro longitudinal de estados de ánimo con visualización de tendencias para el usuario y su terapeuta.
- Integrar módulo de técnicas de respiración y mindfulness con ejercicios guiados por voz sintetizada.

## Justificación
El costo de una sesión con psicólogo privado oscila entre 500 y 1,500 pesos, prohibitivo para la mayoría de estudiantes. El chatbot puede funcionar como primer filtro de atención para síntomas leves, liberando la capacidad del servicio psicológico universitario para casos más graves y reduciendo el tiempo de espera a consulta.

## Metodología
Desarrollo con metodología de diseño centrado en el usuario. Co-diseño con estudiantes y psicólogos universitarios en talleres participativos. Validación de efectividad mediante estudio aleatorizado controlado (RCT) comparando un grupo que usa el chatbot vs. un grupo de control en lista de espera durante 8 semanas.

## Stack Tecnológico
- NLP: GPT-3.5 fine-tuning, Sentence-BERT para similaridad semántica
- Backend: FastAPI, PostgreSQL, Redis para sesiones
- Frontend: React PWA, Web Speech API para voz
- Métricas: análisis longitudinal con Prophet
- Seguridad: cifrado E2E de conversaciones, HIPAA-compliant storage

## Alcance
La plataforma se probará con 200 estudiantes universitarios voluntarios con ansiedad leve-moderada (GAD-7 score 5-14). Excluye el tratamiento de trastornos psicóticos, bipolares o ansiedad severa. El chatbot no reemplaza la atención clínica profesional.

## Conclusión
Un chatbot de salud mental accesible y disponible 24/7 puede democratizar el primer nivel de atención psicológica en el ámbito universitario, reduciendo el sufrimiento de miles de estudiantes y previniendo el escalamiento de síntomas manejables a trastornos clínicos más severos.
