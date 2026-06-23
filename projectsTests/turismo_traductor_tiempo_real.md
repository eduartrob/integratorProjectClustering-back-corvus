# Dispositivo Wearable de Traducción Simultánea para Turistas

## Resumen
Desarrollo de un dispositivo de hardware embebido de bajo costo (wearable) que se acopla magnéticamente a la ropa del turista y realiza traducción bidireccional en tiempo real. El dispositivo cuenta con un arreglo de micrófonos direccionales y un pequeño altavoz, conectándose vía Bluetooth al smartphone del usuario para procesar las traducciones de voz a voz en milisegundos, rompiendo la barrera del idioma de forma natural y sin tener que interponer un teléfono entre los conversadores.

## Introducción
La barrera lingüística sigue siendo el mayor obstáculo para los viajeros internacionales que desean explorar fuera de las zonas turísticas altamente comercializadas. Si bien existen aplicaciones de traducción en los teléfonos móviles, obligan a los usuarios a compartir pantallas, esperar turnos largos y rompen completamente la naturalidad del contacto visual y el lenguaje corporal. Una traducción verdaderamente fluida requiere que la tecnología desaparezca en el fondo de la interacción humana.

## Objetivo General
Diseñar y construir un prototipo de dispositivo wearable para traducción conversacional simultánea de voz a voz, logrando una latencia inferior a 1.5 segundos entre la frase original y el audio traducido, facilitando la interacción fluida entre turistas y proveedores de servicios locales.

## Objetivos Específicos
- Diseñar la electrónica del dispositivo basándose en un microcontrolador Bluetooth Low Energy (BLE) y un codec de audio de alta fidelidad para captura de voz en ambientes ruidosos.
- Implementar un arreglo de micrófonos (beamforming) con algoritmos de cancelación de eco acústico (AEC) y reducción de ruido de fondo para captar nítidamente a la persona que habla a un metro de distancia.
- Desarrollar la aplicación compañera en iOS/Android que gestione el flujo de audio y se conecte con los motores de traducción neuronal en la nube.
- Integrar APIs de reconocimiento de voz (ASR), traducción automática neuronal (NMT) y síntesis de voz (TTS) para ejecutar el pipeline de traducción en tiempo real.
- Optimizar el consumo energético del hardware para garantizar una autonomía operativa de al menos 12 horas de uso intermitente en el viaje.

## Justificación
Facilitar la comunicación empodera a los turistas a viajar de manera más inmersiva, a comprar en mercados locales, interactuar con comunidades y gestionar emergencias médicas o logísticas sin estrés. Un dispositivo dedicado que permita el contacto visual continuo transforma la dinámica comercial y cultural, beneficiando económicamente a los pequeños comerciantes que normalmente quedan excluidos del turismo internacional por no hablar inglés.

## Metodología
Diseño mecatrónico y de software embebido. El hardware se prototipará usando módulos de desarrollo (como el ESP32-S3) y carcasas impresas en 3D. Se realizarán pruebas de inteligibilidad del habla (evaluación MOS - Mean Opinion Score) en ambientes controlados y ruidosos (ej. mercados, calles concurridas). La latencia del pipeline ASR-NMT-TTS se optimizará implementando streaming de audio fragmentado.

## Stack Tecnológico
- Hardware: ESP32-S3 (SoC con soporte de IA embebida), micrófonos MEMS I2S, amplificadores clase D
- Firmware: C/C++, FreeRTOS, Bluetooth Classic (HFP/A2DP) y BLE
- App Móvil: Kotlin (Android) / Swift (iOS)
- IA en Nube: Google Cloud Speech-to-Text (streaming), DeepL API para traducción semántica superior, Amazon Polly para voces neurales
- Procesamiento de Audio Local: Algoritmos DSP para supresión de ruido (SpeexDSP)

## Alcance
El prototipo inicial funcionará dependiente de la conexión a internet 4G/5G del smartphone del usuario (no realiza la traducción offline). Se limitará inicialmente a la traducción bidireccional fluido entre Español, Inglés, Francés, Alemán y Mandarín. El proyecto engloba el desarrollo de un (1) prototipo funcional.

## Conclusión
La tecnología de traducción simultánea integrada en dispositivos wearables es la clave para la verdadera globalización turística. Eliminar la fricción de la pantalla del teléfono celular en las interacciones personales devuelve la humanidad a los viajes, construyendo puentes culturales inmediatos y abriendo nuevas oportunidades económicas a nivel local.
