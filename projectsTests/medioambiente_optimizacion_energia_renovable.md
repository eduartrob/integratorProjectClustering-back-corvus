# Sistema de Gestión de Microrredes de Energía Renovable con Blockchain

## Resumen
Plataforma de software para la gestión de energía distribuida y transacciones directas (Peer-to-Peer, P2P) entre usuarios de una comunidad o parque industrial. Utiliza medidores inteligentes (smart meters) conectados a una red blockchain privada para que los prosumidores (productores que también consumen) con paneles solares puedan vender automáticamente sus excedentes de energía a vecinos cercanos a precios dinámicos, eliminando al distribuidor central como intermediario forzoso en cada transacción financiera.

## Introducción
El modelo eléctrico tradicional es centralizado, unidireccional y propenso a fallas catastróficas en cascada (apagones masivos). La proliferación de paneles solares residenciales permite generar energía de forma distribuida, pero cuando un techo produce más energía de la que consume la casa, el excedente se inyecta a la red pública, a menudo mal compensado por la empresa estatal. Las microrredes (microgrids) locales requieren un sistema confiable, automatizado y auditable para medir y compensar justicieramente los flujos bidireccionales de electrones entre vecinos.

## Objetivo General
Crear una plataforma descentralizada basada en blockchain y contratos inteligentes que habilite y audite mercados locales de energía Peer-to-Peer, incentivando económicamente la adopción de generación solar distribuida al mejorar el retorno de inversión para el propietario del panel y abaratar la energía para el consumidor.

## Objetivos Específicos
- Diseñar e instalar nodos IoT en los medidores bidireccionales de los hogares capaces de leer el flujo eléctrico neto cada 5 minutos y firmar criptográficamente el paquete de datos.
- Desplegar una red blockchain permisionada que registre inmutablemente la generación y el consumo de cada participante de la comunidad.
- Desarrollar un contrato inteligente (Smart Contract) de mercado que case automáticamente las ofertas de venta de energía solar excedente con la demanda de los vecinos cercanos mediante un algoritmo de subasta continua.
- Implementar un sistema de facturación o tokenización ("Energy Tokens") donde las liquidaciones financieras de la energía intercambiada ocurran automáticamente al final del ciclo de facturación.
- Desarrollar una aplicación móvil para el usuario final que visualice su consumo, su generación, las ganancias obtenidas por vender a la red y el origen (verde o fósil) de la energía que consumió.

## Justificación
Un mercado P2P de energía descentraliza no solo la generación de electricidad, sino también la economía subyacente. Maximiza la eficiencia de la red física, ya que la energía se consume a unos pocos metros de donde se generó, minimizando las pérdidas masivas por transmisión térmica a través de cientos de kilómetros de cables de alta tensión. La blockchain es indispensable aquí para crear un registro único, confiable y auditable de transacciones automatizadas en las que participan múltiples propietarios sin depender de una compañía central con fines monopolísticos.

## Metodología
Investigación aplicada en infraestructuras de tecnología distribuida (DLT). Desarrollo de software y simulación arquitectónica. Puesto que las restricciones regulatorias nacionales actuales pueden prohibir el intercambio comercial directo de energía física a través del cableado estatal, el proyecto funcionará como una prueba de concepto tecnológica utilizando un esquema de "facturación neta virtual" simulada entre 5 hogares e instalaciones universitarias reales instrumentadas con los medidores IoT desarrollados ad-hoc.

## Stack Tecnológico
- Blockchain: Ethereum (usando una red de pruebas L2 local o Hyperledger Besu para eliminar costos de gas)
- Smart Contracts: Solidity, Truffle suite, Web3.js / Ethers.js
- Hardware IoT de Medición: Sensores de corriente no invasivos (SCT-013), ESP32 para lectura de potencia real, factor de potencia y cifrado TLS
- Backend Orquestador: Node.js, Express, PostgreSQL (para datos off-chain de configuración de usuario)
- Frontend App: React Native (móvil) con gráficos de series temporales dinámicos

## Alcance
El sistema medirá flujos de energía reales mediante los medidores IoT propios. Las transacciones financieras se realizarán mediante tokens de prueba (criptomonedas locales sin valor fiat inmediato) a manera de validación contable inmutable. No implica la modificación física de la infraestructura eléctrica pública (postes o transformadores de CFE/distribuidor local).

## Conclusión
La intersección de la energía solar descentralizada con infraestructuras de confianza automatizada (blockchain) transformará a las comunidades residenciales de consumidores pasivos a participantes activos de un mercado energético democratizado, resiliente y 100% renovable.
