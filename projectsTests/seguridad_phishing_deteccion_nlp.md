# Detección de Phishing en Correos Electrónicos con Procesamiento de Lenguaje Natural

## Resumen
Sistema de seguridad perimetral para servidores de correo electrónico corporativo que utiliza Modelos de Lenguaje Grande (LLMs) y Procesamiento de Lenguaje Natural (NLP) para identificar ataques de phishing de lanza (Spear Phishing). A diferencia de los filtros anti-spam que analizan dominios o enlaces de listas negras, este sistema analiza la "intención" semántica del texto, detectando el sentido de urgencia, manipulación psicológica y suplantación de identidad de directivos.

## Introducción
El correo electrónico sigue siendo el vector de entrada para el 90% de los ciberataques exitosos, incluyendo el ransomware corporativo. Los atacantes han perfeccionado sus técnicas utilizando dominios recién creados (sin reputación negativa) y evitando adjuntos maliciosos, dependiendo puramente de la ingeniería social (ej. "Transferencia urgente aprobada por el CEO"). Los filtros basados en firmas técnicas son inútiles ante ataques puramente textuales y conversacionales.

## Objetivo General
Desarrollar un filtro semántico de correo electrónico capaz de detectar intentos de ingeniería social y spear phishing analizando el contexto y la intención del texto, protegiendo a las organizaciones de estafas de compromiso de correo empresarial (BEC).

## Objetivos Específicos
- Crear un dataset de correos electrónicos legítimos de corporaciones (ej. corpus de Enron) y correos de phishing moderno recolectados de honeypots y bases de datos públicas.
- Entrenar y ajustar (Fine-tuning) un modelo de lenguaje Transformer (como RoBERTa o BERT) especializado en la comprensión semántica de escenarios de urgencia financiera y solicitudes de credenciales.
- Extraer características lingüísticas clave (Lexical Features) como errores gramaticales deliberados, tiempos verbales impositivos y saludos anómalos para el contexto corporativo.
- Desarrollar un modelo de análisis de anomalías de remitente que detecte suplantación de dominio (Spoofing) comparando el comportamiento habitual de comunicación entre empleados.
- Construir un plugin para Microsoft Outlook y Google Workspace que marque con etiquetas de advertencia los correos que contengan alto riesgo semántico.

## Justificación
El fraude por suplantación de identidad a nivel directivo causa miles de millones en pérdidas globales. La capacitación de los empleados ayuda, pero el estrés diario hace que eventualmente alguien haga clic. Implementar una barrera de seguridad algorítmica que comprenda las tácticas de persuasión psicológica humanas protege al eslabón más débil de la cadena de ciberseguridad: el propio usuario.

## Metodología
Investigación en Deep Learning para clasificación de texto. El entrenamiento se realizará mediante Transfer Learning a partir de un modelo pre-entrenado en español/inglés. Se validará usando validación cruzada y se probará con un set de correos de phishing nunca vistos. Se configurará el umbral de detección favoreciendo un alto "Recall" (no dejar pasar ataques) manteniendo los falsos positivos por debajo del 5% para no frustrar las operaciones de negocio.

## Stack Tecnológico
- NLP y Deep Learning: HuggingFace Transformers, PyTorch, Scikit-learn
- Modelos Base: mBERT, XLM-RoBERTa (para soporte multilingüe)
- Procesamiento de Texto: NLTK, Spacy (para extracción de entidades financieras)
- Backend: FastAPI, Celery (procesamiento asíncrono para no retrasar la entrega de correos)
- Integración: Microsoft Graph API, Google Gmail API

## Alcance
El sistema se enfoca en el análisis de cuerpo de texto y metadatos de las cabeceras (headers) del correo. No realiza sandboxing dinámico de archivos adjuntos (ej. ejecución de macros de Excel), lo cual debe ser cubierto por soluciones antimalware tradicionales que trabajarán en conjunto con este filtro semántico.

## Conclusión
Combatir la ingeniería social requiere herramientas que entiendan la comunicación humana. Aplicar la última generación de Inteligencia Artificial al análisis de la intención del correo provee una defensa cognitiva que cierra las vulnerabilidades psicológicas explotadas por los ciberdelincuentes.
