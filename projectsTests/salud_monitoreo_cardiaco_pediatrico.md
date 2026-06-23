# Sistema de Monitoreo Continuo de Pacientes Pediátricos con Cardiopatías Congénitas

## Resumen
Plataforma de monitoreo cardíaco continuo para pacientes pediátricos con cardiopatías congénitas que combina un parche biosensor reutilizable con análisis de ECG en tiempo real mediante inteligencia artificial. El sistema detecta arritmias potencialmente fatales y notifica al cardiólogo pediátrico en menos de 60 segundos, permitiendo intervención temprana fuera del entorno hospitalario.

## Introducción
Las cardiopatías congénitas afectan a 8 de cada 1,000 recién nacidos en México. El seguimiento post-quirúrgico requiere monitoreo frecuente que actualmente solo puede realizarse con equipos Holter de 24 horas que deben llevarse al hospital para análisis. Este proyecto provee monitoreo continuo, análisis automático y comunicación en tiempo real con el médico tratante.

## Objetivo General
Diseñar e implementar un sistema de monitoreo cardíaco continuo portátil para pacientes pediátricos que detecte automáticamente arritmias y variaciones críticas del ritmo cardíaco usando modelos de deep learning, con notificación inmediata al cardiólogo.

## Objetivos Específicos
- Diseñar un parche electrónico flexible con electrodos Ag/AgCl y microcontrolador nRF52840 para captura de ECG de 3 derivaciones.
- Entrenar modelo de clasificación de arritmias con la base de datos PhysioNet MIT-BIH Arrhythmia Database adaptada para ritmos pediátricos.
- Implementar procesamiento edge en el parche para detección local de eventos críticos con consumo menor a 10mW.
- Desarrollar aplicación móvil parental para visualización del ECG en tiempo real y recepción de alertas.
- Crear portal web para cardiólogos con acceso al historial de eventos y tendencias del paciente.

## Justificación
Las arritmias en cardiopatías congénitas pueden ser fatales si no se detectan y tratan en los primeros minutos. El 80% de los eventos arrítmicos ocurren fuera del hospital. Un sistema de monitoreo continuo ambulatorio puede reducir la mortalidad por causas prevenibles en esta población pediátrica.

## Metodología
Diseño de investigación y desarrollo biomédico. Fase de diseño de hardware con simulación en Proteus. Fase de entrenamiento del modelo con datos anonimizados del Instuto Nacional de Cardiología. Prueba piloto con 30 pacientes durante 3 meses con aprobación de comité de ética pediátrica.

## Stack Tecnológico
- Hardware: nRF52840, AD8232 (ECG front-end), electrodos de hidrogel
- Edge ML: TensorFlow Lite Micro, clasificación de arritmias
- Backend: Node.js, MongoDB, WebSockets
- Móvil: Flutter (Android e iOS)
- Alertas: Firebase Cloud Messaging, Twilio

## Alcance
Sistema aprobado para uso en investigación. La validación clínica se realizará bajo protocolo ético en el Instituto Nacional de Cardiología. No constituye dispositivo médico certificado en esta fase. No incluye marcapasos ni desfibriladores.

## Conclusión
El monitoreo cardíaco continuo ambulatorio en pediatría mediante wearables inteligentes puede transformar el seguimiento de cardiopatías congénitas y reducir la mortalidad por arritmias detectables en el hogar.
