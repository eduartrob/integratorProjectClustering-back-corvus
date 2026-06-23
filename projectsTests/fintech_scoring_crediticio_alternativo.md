# Sistema de Scoring Crediticio Alternativo para Personas sin Historial Bancario

## Resumen
Sistema de evaluación crediticia que construye un perfil de riesgo para personas sin historial bancario formal (población no bancarizada) utilizando fuentes de datos alternativas: historial de pagos de servicios (luz, agua, teléfono), comportamiento de compra en tiendas de barrio mediante CODI, patrones de movilidad georreferenciada y actividad en redes sociales. El modelo predice la probabilidad de incumplimiento con precisión equivalente al scoring FICO tradicional.

## Introducción
El 54% de los adultos mexicanos no tiene acceso al crédito formal por carecer de historial crediticio. Esto crea un círculo vicioso: sin crédito no se construye historial, sin historial no se accede a crédito. Los datos alternativos tienen el potencial de romper este ciclo y ampliar el acceso al crédito responsable a millones de mexicanos excluidos del sistema financiero formal.

## Objetivo General
Desarrollar un modelo de scoring crediticio alternativo para población no bancarizada que use datos no tradicionales para predecir la capacidad y voluntad de pago, con precisión estadística equivalente al scoring convencional y con mayor inclusión de la población marginada.

## Objetivos Específicos
- Construir un pipeline de ingestión y normalización de datos de pagos de servicios básicos mediante convenios con CFE, TELMEX y organismos de agua municipales.
- Desarrollar modelos de machine learning (Gradient Boosting, XGBoost, LightGBM) para predicción de default crediticio con validación por curva ROC-AUC.
- Implementar técnicas de explicabilidad (SHAP values) para cumplir con la regulación de la CNBV sobre transparencia algorítmica en decisiones de crédito.
- Crear API REST para que fintechs y cooperativas de ahorro integren el scoring como servicio.
- Diseñar pipeline de actualización mensual del modelo con drift detection para mantener la precisión predictiva en el tiempo.

## Justificación
El modelo de negocio de las fintechs de crédito en México depende de su capacidad de evaluar riesgo en segmentos no atendidos por la banca. Un scoring alternativo preciso y explicable es la infraestructura que habilita el crédito responsable en la base de la pirámide económica, contribuyendo a la inclusión financiera sin sacrificar la salud del portafolio de la institución crediticia.

## Metodología
Investigación aplicada con metodología de ciencia de datos. Dataset de entrenamiento: 50,000 créditos de una cooperativa de ahorro con 24 meses de seguimiento. Variables alternativas a probar: 47 features derivadas de pagos de servicios, movilidad y comportamiento digital. Validación temporal con hold-out del último año.

## Stack Tecnológico
- ML: XGBoost, LightGBM, sklearn Pipeline, SHAP
- Backend: FastAPI, PostgreSQL, Celery para scoring por lotes
- Monitoreo: MLflow, Evidently AI para drift detection
- API: REST + OAuth 2.0 para clientes B2B
- Cumplimiento regulatorio: auditría de sesgo con Fairlearn

## Alcance
El modelo se entrenará con datos de una cooperativa de ahorro del Estado de México con 50,000 socios. El scoring se limita a créditos de consumo de hasta 50,000 pesos a 24 meses. No incluye créditos hipotecarios ni empresariales.

## Conclusión
El scoring crediticio alternativo es la clave para extender el crédito responsable a la mayoría de mexicanos excluidos del sistema financiero, transformando datos de comportamiento cotidiano en el capital social que abre las puertas del crédito formal.
