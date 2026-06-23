# Control de Acceso Biométrico mediante Reconocimiento Facial Anti-Spoofing

## Resumen
Sistema avanzado de control de acceso físico para edificios corporativos que utiliza cámaras de profundidad y modelos de Deep Learning para identificar a los empleados en tiempo real. A diferencia de los sistemas faciales básicos, este proyecto incorpora tecnología anti-spoofing (liveness detection) mediante visión estéreo e infrarroja para evitar que el sistema sea engañado mediante fotografías de alta resolución, videos en tablets o máscaras de silicona 3D.

## Introducción
Los sistemas de acceso tradicionales basados en tarjetas RFID o pines numéricos son inherentemente vulnerables; las credenciales pueden ser prestadas, robadas o clonadas. Aunque la biometría facial resuelve el problema de la transferencia de credenciales, los algoritmos 2D estándar son fácilmente engañados (ataques de presentación). En entornos corporativos de alta seguridad, es indispensable garantizar que la persona intentando acceder está físicamente presente y viva.

## Objetivo General
Desarrollar un sistema de control de acceso biométrico facial seguro y sin fricción, capaz de identificar a usuarios registrados en menos de 1 segundo, incorporando algoritmos de detección de vida (anti-spoofing) para prevenir el 99.9% de los ataques de suplantación.

## Objetivos Específicos
- Entrenar una red neuronal convolucional (CNN) sobre un conjunto de imágenes estéreo e infrarrojas para clasificar rostros vivos frente a reproducciones artificiales (fotos, pantallas, máscaras).
- Implementar un pipeline de reconocimiento facial que extraiga embeddings vectoriales del rostro y los compare contra la base de datos de empleados usando búsqueda por similitud de coseno.
- Desarrollar un dispositivo de borde (edge device) utilizando hardware embebido para realizar inferencia local sin depender de la nube, garantizando funcionamiento sin conexión a internet y menor latencia.
- Diseñar un módulo de integración por relé seguro para la apertura de puertas, torniquetes y plumas de estacionamiento.
- Construir un panel de administración web para el registro (enrolamiento) de nuevos empleados, revocación de accesos y visualización de registros de entrada.

## Justificación
La seguridad física es la primera línea de defensa para la seguridad de la información. Un intruso en las oficinas puede instalar hardware malicioso o acceder a terminales desbloqueadas. Este sistema elimina el costo recurrente de reposición de tarjetas RFID, mejora la experiencia del usuario (ingreso "hands-free", higiénico post-pandemia) y provee una capa de seguridad criptográficamente ligada a la identidad física inmutable del empleado.

## Metodología
Desarrollo de hardware y software concurrente. Se creará un corpus propio de ataque grabando a 50 voluntarios bajo diferentes escenarios de spoofing (fotos en papel, pantallas OLED). El modelo de liveness se evaluará mediante métricas de seguridad estandarizadas (APCER, BPCER). El hardware se probará instalando un prototipo en los torniquetes de entrada del campus universitario durante 1 mes para evaluar la tasa de falsos rechazos en condiciones reales de iluminación.

## Stack Tecnológico
- IA & Computer Vision: PyTorch, OpenCV, Dlib (alineación facial), ArcFace (extracción de features)
- Hardware Embebido: NVIDIA Jetson Nano / Raspberry Pi 4 con acelerador Coral TPU, cámara Intel RealSense Depth
- Backend & Panel: FastAPI, Vue.js, PostgreSQL
- Edge Deployment: TensorRT, ONNX para optimización de inferencia
- Comunicación: MQTT para sincronización de logs al servidor central

## Alcance
El sistema final está diseñado para manejar bases de datos de hasta 5,000 empleados concurrentes con inferencia local en el dispositivo. Soporta variaciones en la iluminación natural y uso de accesorios (lentes de vista, sombreros). No garantiza detección absoluta contra gemelos idénticos ni cirugías reconstructivas avanzadas.

## Conclusión
La biometría facial combinada con la evaluación de profundidad infrarroja cierra la brecha de vulnerabilidad más crítica en la seguridad física corporativa, ofreciendo una experiencia de acceso fluida mientras blinda las instalaciones contra tácticas de infiltración de ingeniería social.
