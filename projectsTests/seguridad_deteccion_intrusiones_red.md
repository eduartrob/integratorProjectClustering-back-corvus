# Sistema de Detección de Intrusiones (IDS) basado en Análisis de Comportamiento

## Resumen
Monitor de tráfico de red de próxima generación que utiliza técnicas de Machine Learning no supervisado para establecer una línea base de comportamiento "normal" en la red corporativa. En lugar de buscar firmas de virus conocidos, el sistema alerta sobre desviaciones estadísticas en el tráfico (como transferencias masivas de datos a horas inusuales o escaneos de puertos silenciosos), detectando ataques de día cero antes de que se liberen parches de seguridad.

## Introducción
Los firewalls y los antivirus tradicionales funcionan mediante listas negras (firmas): solo bloquean lo que ya saben que es malo. Esto deja a las organizaciones indefensas frente a vulnerabilidades recién descubiertas (Zero-Days) y ataques dirigidos avanzados (APTs). Cuando un atacante vulnera un equipo internamente, su comportamiento lateral en la red deja huellas estadísticas sutiles que las reglas estáticas no pueden detectar.

## Objetivo General
Implementar un Sistema de Detección de Intrusiones de Red (NIDS) basado en inteligencia artificial que reduzca el tiempo de descubrimiento de brechas de seguridad identificando anomalías de red con una tasa de falsos positivos menor al 2%.

## Objetivos Específicos
- Desarrollar un motor de captura y procesamiento de paquetes (PCAP) capaz de extraer metadatos de flujo de red (NetFlow/IPFIX) a velocidad de Gigabit sin inspeccionar la carga útil cifrada.
- Aplicar ingeniería de características (feature engineering) para modelar comportamientos como: proporción de bytes enviados/recibidos, entropía de los puertos, y frecuencias de conexión por dispositivo.
- Implementar algoritmos de clustering (K-Means, DBSCAN) y algoritmos de aislamiento (Isolation Forest, Autoencoders) para detectar flujos estadísticamente improbables.
- Construir un dashboard SOC (Security Operations Center) que clasifique las anomalías detectadas por nivel de severidad y visualice el grafo de comunicaciones del atacante.
- Diseñar un módulo de integración con firewalls perimetrales (API REST) para aislar automáticamente la IP del host comprometido al detectar comportamiento tipo ransomware.

## Justificación
El tiempo promedio que un atacante pasa oculto dentro de una red corporativa antes de ser detectado es de más de 200 días. Un IDS basado en anomalías actúa como una cámara de seguridad interna, alertando no sobre quién entra, sino sobre quién se comporta de manera sospechosa una vez dentro, salvando a la empresa de la exfiltración masiva de datos o el cifrado destructivo.

## Metodología
Investigación aplicada utilizando el dataset académico CICIDS2017/2019, que contiene capturas de red reales de ataques modernos (DDoS, Brute Force, XSS, Infiltración). Se entrenarán los modelos usando ventanas de tiempo de 5 minutos para evaluar el tráfico. Se comparará el rendimiento del modelo frente a sistemas basados en reglas open-source como Snort o Suricata en un entorno de red de pruebas.

## Stack Tecnológico
- Procesamiento de Red: Zeek (anteriormente Bro) para extracción de flujos, Scapy
- Machine Learning: PySpark para procesamiento distribuido, Scikit-learn (Isolation Forest), PyTorch (Autoencoders)
- Backend y Streaming: Apache Kafka para ingesta de logs en tiempo real, Elasticsearch, Logstash
- Frontend Visualización: Kibana / Grafana, D3.js para grafos de red
- Lenguajes: Python y Go (Golang) para alto rendimiento de captura

## Alcance
El sistema opera a nivel de Capa 3 y Capa 4 del modelo OSI (flujos IP y puertos TCP/UDP); no realiza inspección profunda de paquetes (DPI) para evitar violaciones de privacidad y cuellos de botella con tráfico TLS/SSL cifrado. Está diseñado para monitorear redes de área local (LAN) de hasta 1,000 hosts.

## Conclusión
El análisis de comportamiento mediante aprendizaje automático es el cambio de paradigma necesario en la ciberseguridad defensiva, permitiendo pasar de una postura reactiva (esperando a que el ataque sea conocido) a una postura proactiva (detectando la técnica del ataque sin importar el malware específico).
