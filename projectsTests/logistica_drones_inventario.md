# Automatización de Inventario en Almacenes con Drones y Visión Artificial

## Resumen
Plataforma que utiliza drones autónomos equipados con cámaras de alta resolución y software de reconocimiento de imágenes para realizar inventarios cíclicos en grandes centros de distribución. Los drones navegan por los pasillos leyendo códigos de barras, QR y etiquetas RFID, procesando las imágenes mediante IA para actualizar el software de gestión de almacenes (WMS) de forma automática.

## Introducción
Los inventarios físicos manuales son procesos lentos, costosos y propensos a errores humanos. Además, el conteo en estanterías altas representa un riesgo de seguridad laboral significativo para los operarios que deben usar montacargas o plataformas elevadoras. La automatización del conteo mediante vehículos aéreos no tripulados permite realizar inventarios con mayor frecuencia sin detener las operaciones del centro logístico.

## Objetivo General
Automatizar el proceso de toma de inventario físico en almacenes verticales mediante el uso de drones autónomos y visión por computadora, reduciendo el tiempo de conteo en un 80% y eliminando los riesgos de trabajo en altura.

## Objetivos Específicos
- Implementar un sistema de navegación indoor sin GPS para que los drones se ubiquen utilizando odometría visual y marcadores fiduciales en los pasillos.
- Entrenar un modelo de Deep Learning (YOLO) para la detección y lectura de múltiples códigos de barras y etiquetas alfanuméricas bajo condiciones de iluminación variable.
- Desarrollar un planificador de vuelos que asigne automáticamente rutas de escaneo a una flota de múltiples drones en base al layout del almacén.
- Crear una API de integración para sincronizar las lecturas capturadas por los drones con los sistemas ERP/WMS (como SAP o Manhattan) existentes en la empresa.
- Implementar un sistema de carga automática donde los drones aterricen en bases inductivas para recargar batería de forma autónoma.

## Justificación
Un centro de distribución promedio invierte semanas de trabajo hombre cada año en realizar auditorías de inventario, lo que a menudo requiere detener la recepción y despacho de mercancía. Utilizar drones permite realizar "inventarios cíclicos continuos" durante las noches o fines de semana sin supervisión humana, asegurando una precisión del stock del 99.9% y evitando roturas de stock.

## Metodología
Desarrollo experimental. Integración de drones comerciales de código abierto (Pixhawk/PX4) con computadoras de acompañamiento (Raspberry Pi 4) para el procesamiento de imágenes en el borde (Edge Computing). Validación del sistema en un almacén de pruebas de 500 metros cuadrados con estanterías de 3 niveles, comparando la precisión de lectura y el tiempo empleado contra un equipo humano.

## Stack Tecnológico
- Robótica Aérea: ROS (Robot Operating System), MAVROS, PX4 Autopilot
- Visión por Computadora: OpenCV, PyTorch, YOLOv8 (detección de etiquetas), ZBar (decodificación)
- Navegación Indoor: SLAM (Simultaneous Localization and Mapping), ArUco markers
- Backend Control: Python, FastAPI, WebSockets para telemetría
- Frontend Dashboard: React, Three.js para visualización 3D del almacén

## Alcance
El proyecto se enfoca en almacenes techados con estanterías estandarizadas y pasillos rectos. El dron requiere línea de vista hacia las etiquetas; no puede contabilizar artículos ocultos detrás de otros. La capacidad operativa está limitada por la autonomía de vuelo actual (aproximadamente 20 minutos por carga).

## Conclusión
La robótica aérea combinada con la inteligencia artificial transforma la gestión logística, convirtiendo el inventario físico de una obligación tediosa y riesgosa a un flujo de datos constante y automatizado, otorgando a las empresas visibilidad absoluta de sus activos en tiempo real.
