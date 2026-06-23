# Trazabilidad de Cadena de Suministro Farmacéutica usando Blockchain

## Resumen
Sistema descentralizado basado en tecnología Blockchain para garantizar la procedencia, autenticidad y mantenimiento de la cadena de frío de medicamentos desde el laboratorio fabricante hasta el paciente final. Utiliza contratos inteligentes y sensores IoT dentro de los contenedores refrigerados para registrar inmutablemente la temperatura y ubicación de los lotes farmacéuticos en un ledger distribuido.

## Introducción
El mercado negro, la falsificación de medicamentos y la pérdida de vacunas por rompimiento de la cadena de frío son problemas críticos de salud pública. Según la OMS, el 10% de los medicamentos en países en desarrollo son falsificados. Los sistemas centralizados de trazabilidad son vulnerables a alteraciones de datos por actores maliciosos dentro de la cadena de suministro.

## Objetivo General
Implementar un sistema de trazabilidad de extremo a extremo para la cadena de suministro farmacéutica utilizando tecnología Blockchain y sensores IoT, para prevenir la falsificación y garantizar el cumplimiento estricto de la cadena de frío.

## Objetivos Específicos
- Desarrollar Smart Contracts en una red blockchain permisionada (Hyperledger Fabric) que definan las reglas de transferencia de custodia de lotes médicos.
- Integrar sensores IoT de temperatura y GPS en contenedores de transporte que firmen y envíen telemetría directamente a la blockchain.
- Implementar un mecanismo de consenso que involucre a laboratorios, distribuidores, farmacias y entidades regulatorias como nodos de la red.
- Desarrollar una aplicación móvil para pacientes que permita escanear un código QR en el empaque y verificar todo el historial del medicamento.
- Crear alertas automáticas que revoquen el certificado de calidad de un lote si la telemetría IoT registra temperaturas fuera del rango permitido.

## Justificación
La inmutabilidad criptográfica de la tecnología blockchain proporciona la única solución técnica robusta donde múltiples empresas que no confían entre sí pueden compartir una base de datos auditable. Aplicar esto a la industria farmacéutica salva vidas al asegurar que un medicamento biológico (como la insulina o las vacunas) no fue expuesto a temperaturas degradantes durante su transporte y almacenaje.

## Metodología
Desarrollo de prototipo funcional en red de pruebas. Configuración de la red blockchain usando Hyperledger Fabric con 4 organizaciones simuladas. Integración de hardware con microcontroladores ESP32 y módulos GPS/GPRS. Pruebas de estrés de la red simulando la inyección de 1,000 transacciones IoT por minuto.

## Stack Tecnológico
- Blockchain: Hyperledger Fabric, Chaincode en Go (Golang)
- IoT: ESP32, Sensores DHT22 (temperatura), Módulo SIM800L (GPRS)
- Backend API: Node.js, Express, Hyperledger Fabric SDK
- App Consumidor: Flutter (escáner QR)
- Infraestructura: Docker Compose para despliegue de nodos y ordenadores

## Alcance
El prototipo soporta la trazabilidad de un medicamento desde su empaquetado final hasta la farmacia minorista. El hardware IoT está diseñado a nivel de prueba de concepto y no cuenta aún con certificación de grado médico. No se contempla la integración nativa con sistemas ERP heredados (SAP) de las farmacéuticas en esta fase.

## Conclusión
La convergencia de IoT y Blockchain permite pasar de un sistema logístico basado en papel y confianza ciega a un ecosistema de confianza matemática verificable, protegiendo al consumidor final y reduciendo drásticamente las mermas por mal manejo en la industria farmacéutica.
