# Plataforma de Pagos Colectivos para Cooperativas y Tandas Digitales

## Resumen
Aplicación móvil que digitaliza el sistema de tandas mexicano (ROSCAs - Rotating Savings and Credit Associations) con contratos inteligentes en blockchain para garantizar transparencia y cumplimiento automático. La plataforma gestiona grupos de ahorro de 5 a 30 personas, automatiza los pagos periódicos, mantiene el historial de participación y usa el historial de tanda como garantía para acceder a microcréditos.

## Introducción
Las tandas son el mecanismo de ahorro más utilizado por los mexicanos fuera del sistema bancario formal. Se estima que participan en tandas más de 30 millones de personas, moviendo más de 50,000 millones de pesos anuales de forma completamente informal. La digitalización de las tandas puede formalizarlas, eliminar el riesgo de fraude del organizador y generar historial financiero para los participantes.

## Objetivo General
Desarrollar una plataforma móvil que digitalice y formalice el sistema de tandas mexicano mediante contratos inteligentes blockchain para garantizar transparencia, automatizar pagos y generar historial crediticio formal para los participantes.

## Objetivos Específicos
- Implementar contratos inteligentes en Polygon (Ethereum L2 de bajo costo) que gestionen automáticamente la distribución del turno y el cobro de aportaciones.
- Desarrollar sistema de reputación de participantes basado en historial de cumplimiento en tandas anteriores con puntuación exportable.
- Crear mecanismo de garantías colaterales digitales (NFTs de activos tokenizados) para tandas de alto valor.
- Integrar con CoDi y SPEI para que los pagos de tanda operen en pesos digitales sin fricciones.
- Implementar sistema de resolución de disputas mediante árbitros comunitarios elegidos por los propios miembros del grupo.

## Justificación
El principal riesgo de las tandas informales es la desaparición del organizador con el dinero acumulado. Los contratos inteligentes eliminan este riesgo al programar la distribución automática sin intermediario humano. La generación de historial digitalizado puede integrar a millones de personas al sistema financiero formal usando su comportamiento real de ahorro como garantía.

## Metodología
Investigación etnográfica sobre el funcionamiento de las tandas en diferentes contextos socioeconómicos. Prototipado del contrato inteligente en testnet de Polygon. Prueba piloto con 10 grupos de tanda de 10-15 personas durante 6 meses. Evaluación de satisfacción y adopción mediante encuestas y entrevistas.

## Stack Tecnológico
- Blockchain: Polygon (Ethereum L2), Solidity para contratos inteligentes
- Backend: Node.js, MongoDB, Web3.js
- Móvil: React Native, WalletConnect para integración de billeteras
- Pagos fiat: CoDi API, SPEI
- Identidad: verificación de identidad con INE mediante API de Metamap

## Alcance
La plataforma soporta tandas de 5-30 participantes con aportaciones de 100 a 5,000 pesos semanales. El sistema funciona completamente en pesos mexicanos; el blockchain es solo el backend de garantía invisible para el usuario. No incluye tandas internacionales ni en divisas extranjeras.

## Conclusión
La digitalización blockchain de las tandas mexicanas puede transformar la institución de ahorro más popular del país en un puente hacia la inclusión financiera formal, protegiendo el dinero de millones de personas y generando el historial financiero que les abra las puertas del crédito responsable.
