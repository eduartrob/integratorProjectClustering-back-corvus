# Brazo Robótico para Clasificación Automática de Paquetería

## Resumen
Sistema robótico industrial basado en el framework ROS (Robot Operating System) que clasifica automáticamente paquetes y sobres en centros de distribución. Utiliza un brazo articulado acoplado a una cámara RGB-D que detecta la forma del paquete, escanea el código de envío al vuelo, y desvía la caja hacia la rampa correspondiente a su código postal o ruta de entrega de última milla.

## Introducción
El auge imparable del comercio electrónico ha llevado al límite la capacidad humana de clasificación de paquetes. Los centros de distribución modernos reciben decenas de miles de paquetes por turno que deben ser clasificados hacia cientos de rutas diferentes. La clasificación manual genera cuellos de botella severos, errores de enrutamiento y fatiga física extrema para los operarios.

## Objetivo General
Diseñar e implementar una celda robótica de clasificación de paquetería impulsada por visión artificial, capaz de identificar, agarrar y enrutar paquetes de diferentes dimensiones hacia contenedores específicos con una cadencia superior a 1,200 paquetes por hora.

## Objetivos Específicos
- Modelar y ensamblar un brazo robótico de 4 grados de libertad (SCARA o Delta) optimizado para operaciones de "pick and place" de alta velocidad en un plano 2D.
- Implementar un sistema de visión estéreo para la detección del contorno, centro de masa y orientación espacial de cajas y sobres en movimiento sobre una banda transportadora.
- Desarrollar un algoritmo de reconocimiento óptico de caracteres (OCR) y lectura de códigos de barras capaz de funcionar en milisegundos para identificar el destino del paquete.
- Diseñar y manufacturar un efector final (gripper) neumático basado en ventosas capaz de sujetar superficies irregulares (cartón corrugado, bolsas plásticas).
- Programar la cinemática inversa y la planificación de trayectorias libres de colisiones en ROS utilizando MoveIt.

## Justificación
La automatización de la clasificación "sortation" es el diferenciador clave entre un operador logístico local y empresas de talla mundial como Amazon o DHL. Un sistema robótico no sufre fatiga, reduce la tasa de errores de enrutamiento (que cuestan tiempo y dinero en re-envíos) y permite reubicar a los trabajadores humanos en tareas de mayor valor agregado o supervisión técnica.

## Metodología
Desarrollo mecatrónico iterativo. Modelado CAD en SolidWorks, seguido de simulación física en Gazebo para ajustar controladores PID y trayectorias. Construcción del prototipo físico utilizando perfiles de aluminio estructural, motores stepper/servo de lazo cerrado y bombas de vacío. Pruebas de validación de velocidad de ciclo y tasa de éxito de sujeción con cajas de tamaños y pesos variables (0.1 kg a 5 kg).

## Stack Tecnológico
- Software Robótico: Ubuntu Linux, ROS Noetic, MoveIt, Gazebo
- Visión Artificial: OpenCV, tesseract-ocr, ZBar (sobre una cámara Intel RealSense)
- Hardware de Control: PLC Siemens o microcontrolador embebido (STM32/Teensy)
- Comunicaciones: protocolo Modbus TCP/IP para integrar la banda transportadora
- Diseño Mecánico: SolidWorks, piezas impresas en 3D PETG para montajes

## Alcance
El prototipo físico clasificará paquetes de dimensiones máximas de 30x30x30 cm y un peso no mayor a 3 kg. La demostración contempla la separación en 4 rampas de salida distintas. El proyecto no abarca el empaquetado de productos, solo la clasificación de cajas ya selladas y etiquetadas.

## Conclusión
La integración de robótica ágil con visión por computadora democratiza el acceso a la automatización logística de alto nivel, demostrando que sistemas de clasificación eficientes pueden ser desarrollados localmente sin depender exclusivamente de integradores extranjeros de alto costo.
