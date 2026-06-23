# Billetera Digital con IA para Control de Gastos Personales en Jóvenes Universitarios

## Resumen
Aplicación de billetera digital con inteligencia artificial que analiza automáticamente los patrones de gasto de jóvenes universitarios, categoriza transacciones usando NLP, detecta comportamientos de riesgo financiero y genera recomendaciones personalizadas de ahorro. Integra con CoDi/SPEI para pagos instantáneos y ofrece micro-inversiones automáticas con reglas configurables del tipo "ahorra el 5% de cada transacción".

## Introducción
El 78% de los universitarios mexicanos no lleva ningún registro de sus gastos y el 65% reporta quedarse sin dinero antes de que termine el mes. La educación financiera formal prácticamente no existe en el bachillerato ni en la universidad. Una aplicación que automatice el análisis de gastos y entregue retroalimentación en tiempo real puede construir hábitos financieros saludables desde la juventud.

## Objetivo General
Desarrollar una aplicación móvil de gestión financiera personal con inteligencia artificial para jóvenes universitarios que categorice automáticamente sus gastos, detecte patrones de riesgo financiero, genere metas de ahorro personalizadas y facilite pagos digitales mediante integración con la infraestructura bancaria nacional.

## Objetivos Específicos
- Implementar OCR para lectura automática de recibos y tickets mediante la cámara del smartphone con clasificación automática de categoría de gasto.
- Desarrollar modelo de NLP para clasificación de transacciones bancarias importadas por Open Banking o CSV en 15 categorías de gasto.
- Crear motor de reglas de ahorro automático tipo "round-up" (redondeo al peso superior enviado a fondo de ahorro) y reglas personalizadas.
- Integrar con CoDi y SPEI para envío y recepción de pagos sin comisión entre usuarios.
- Implementar análisis predictivo de saldo al fin de mes basado en patrones históricos con alertas tempranas de riesgo de quedar en saldo negativo.

## Justificación
Las aplicaciones financieras existentes en México están diseñadas para adultos con ingresos estables. Los universitarios tienen patrones de ingreso irregulares (becas, mesadas, trabajos part-time) y gastos impulsivos. Un producto diseñado específicamente para este segmento con gamificación y lenguaje generacional puede generar adopción masiva y construir hábitos financieros que persistan toda la vida.

## Metodología
Design thinking centrado en el usuario universitario. Investigación cualitativa con 20 entrevistas a universitarios de diferentes estratos. Prototipado y prueba de usabilidad. Lanzamiento piloto con 100 usuarios beta en campus universitario durante 3 meses. Métricas de éxito: promedio de ahorro mensual, frecuencia de uso diario, retención a 30 días.

## Stack Tecnológico
- Móvil: Flutter (Android + iOS), Bloc state management
- Backend: FastAPI, PostgreSQL, Plaid API / Open Banking México
- OCR: Google Vision API, Tesseract para offline
- NLP: BERT fine-tuneado para clasificación de transacciones en español
- Pagos: CoDi API (BANXICO), SPEI REST

## Alcance
La aplicación soporta cuentas bancarias de los principales bancos mexicanos que soporten Open Banking (BBVA, Banamex, Santander, Banorte). El módulo de inversión se limita a CETES Directo. No incluye créditos, préstamos ni seguros.

## Conclusión
Una billetera digital inteligente diseñada para el universitario mexicano puede ser el primer contacto transformador con la educación financiera práctica, estableciendo hábitos de ahorro e inversión que construyan patrimonio a lo largo de toda la vida adulta.
