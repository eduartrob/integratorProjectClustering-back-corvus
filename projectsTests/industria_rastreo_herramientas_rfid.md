# Sistema de Rastreo de Herramentales y Calibración mediante RFID UHF

## Resumen
Solución integral de seguimiento de activos basada en Identificación por Radiofrecuencia (RFID) de Ultra Alta Frecuencia para el control de inventario y la gestión del ciclo de vida de herramentales, moldes y troqueles de precisión en la industria manufacturera. El sistema automatiza el registro de entrada/salida (Check-in/Check-out) y bloquea operaciones de manufactura en la maquinaria principal si detecta que la herramienta insertada ha superado su fecha de calibración obligatoria o ciclo de vida por impacto.

## Introducción
En la manufactura de precisión (aeroespacial, médica, mecanizado CNC), una broca desafilada o un micrómetro descalibrado se traducen directamente en piezas que incumplen las tolerancias ISO y deben desecharse (scrap). El control manual de la calibración de miles de herramientas mediante libretas o planillas de Excel y la pérdida física de herramientas (herramienta extraviada en la línea) causan el 20% de las paradas menores de las máquinas y representan un costo oculto significativo en retrabajos y recompras.

## Objetivo General
Eliminar la pérdida de herramentales críticos y asegurar el 100% del cumplimiento de calibración metrológica (ISO 9001) mediante la implementación de un sistema de identificación RFID y bloqueo automático en máquina-herramienta.

## Objetivos Específicos
- Seleccionar e instalar etiquetas RFID (Tags) cerámicas o metálicas de alta resistencia al calor, vibración y fluidos de corte (Taladrina) en el inventario base de 5,000 herramientas.
- Implementar arcos de lectura RFID en la entrada del almacén central (Crib) y antenas direccionales en los centros de mecanizado CNC para identificar la herramienta colocada en el husillo.
- Desarrollar un sistema de base de datos relacional para el seguimiento individual del ciclo de vida: número de cortes realizados, operario responsable, fecha de mantenimiento y certificado de calibración escaneado.
- Diseñar la integración electrónica a nivel de máquina: si la antena RFID detecta una herramienta vencida introducida en la fresadora CNC, se interrumpe la señal del circuito de seguridad, impidiendo el arranque del programa G-Code.
- Construir un dashboard web de alertas para el gerente de calidad, mostrando el inventario perdido, el estado de vida de las herramientas de alta rotación y pronosticando automáticamente las órdenes de afilado.

## Justificación
La trazabilidad inteligente de activos (Asset Tracking) elimina el tiempo que los maquinistas invierten "buscando la herramienta adecuada". Garantizar que ninguna herramienta defectuosa toque una pieza de producción protege las certificaciones de calidad internacionales requeridas para ser proveedores Tier-1 de compañías aeronáuticas y automotrices, donde la calidad innegociable del proceso de manufactura justifica de sobra la inversión en infraestructura RFID.

## Metodología
Implementación tecnológica e integración OT. El proyecto inicia con un estudio de campo electromagnético para evitar reflexiones de ondas RFID en el ambiente metálico industrial. Las etiquetas serán sometidas a pruebas de estrés químico sumergiéndolas en refrigerantes y aceites de la planta. El piloto se desplegará en el departamento central de herramientas (Tool Room) y se conectará con el panel de 3 centros de mecanizado CNC HAAS. La eficacia se medirá con la reducción porcentual del tiempo de "set-up" de máquina.

## Stack Tecnológico
- Hardware de Identificación: Antenas y Lectores RFID UHF EPC Gen2 (ej. Impinj o Zebra), Tags on-metal de alta durabilidad (Xerafy/Omni-ID)
- Middleware de Recolección: LLRP (Low Level Reader Protocol), Edge Gateway (Raspberry Pi / IPC local)
- Backend de Software: Java Spring Boot / Python, API REST
- Base de Datos: Microsoft SQL Server o PostgreSQL
- Panel de Control Web: Angular, Bootstrap, integración con Active Directory del cliente

## Alcance
El sistema rastrea el herramental dentro del perímetro de la planta productiva. La precisión espacial (localización exacta dentro de un pasillo) usando RFID pasivo UHF no es sub-métrica (típicamente 1-3 metros de zona de lectura), por lo que rastrea "qué salió, cuándo y a qué máquina llegó", no funciona como un GPS interno para objetos pequeños escondidos. El proyecto no abarca modificaciones de programación (G-Code) del CNC en sí.

## Conclusión
Aplicar el Internet de las Cosas industriales (IIoT) a los objetos más simples y fundamentales de la manufactura —las herramientas— transforma los talleres mecánicos caóticos en operaciones orquestadas, digitales y blindadas contra errores metrológicos, asegurando la calidad del producto final desde el nivel más básico del proceso de arranque de viruta.
