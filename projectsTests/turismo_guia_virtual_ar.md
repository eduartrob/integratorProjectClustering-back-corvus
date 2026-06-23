# Guía Turístico Virtual con Realidad Aumentada para Zonas Arqueológicas

## Resumen
Aplicación móvil innovadora que utiliza realidad aumentada (AR) inmersiva para superponer reconstrucciones históricas tridimensionales sobre las ruinas actuales, acompañado de un avatar interactivo generado por Inteligencia Artificial que actúa como guía turístico políglota. Los visitantes pueden ver cómo lucían los palacios y templos en su máximo esplendor, caminar alrededor de ellos y hacer preguntas sobre la historia y arquitectura en tiempo real.

## Introducción
La experiencia de visitar zonas arqueológicas (como Teotihuacán o Chichén Itzá) a menudo carece de un contexto visual vívido. Para el turista promedio, un conjunto de rocas erosionadas es difícil de imaginar como las majestuosas estructuras pintadas que fueron originalmente. Los guías humanos son costosos, no siempre dominan el idioma del visitante, y los folletos estáticos no ofrecen una experiencia inmersiva que conecte emocionalmente a las nuevas generaciones con el patrimonio cultural.

## Objetivo General
Enriquecer la experiencia turística y educativa en sitios del patrimonio cultural mediante la reconstrucción arquitectónica in-situ usando realidad aumentada y un guía conversacional IA, aumentando el tiempo de permanencia y el nivel de satisfacción del visitante en un 40%.

## Objetivos Específicos
- Crear reconstrucciones 3D fotorrealistas optimizadas para móviles de 10 estructuras clave de una zona arqueológica mexicana, basadas estrictamente en evidencia antropológica validada por el INAH.
- Implementar un motor de anclaje espacial AR que utilice las características visuales de las ruinas reales para superponer y alinear milimétricamente el modelo 3D digital, garantizando la persistencia espacial al moverse.
- Desarrollar un agente conversacional basado en Modelos de Lenguaje Grande (LLMs) especializado en la historia del sitio, capaz de responder preguntas contextuales del usuario por voz en más de 20 idiomas.
- Diseñar la interfaz de usuario con mecánicas de gamificación ligeras (recolección de "artefactos virtuales" esparcidos por la zona) para incentivar la exploración de áreas menos visitadas del sitio.
- Construir un backend analítico para la secretaría de turismo que recolecte datos de calor (heatmaps) sobre las rutas más populares y el tiempo de permanencia de los usuarios en la zona.

## Justificación
La digitalización inmersiva del patrimonio cultural es el futuro del turismo histórico. Al proveer una experiencia de "viaje en el tiempo", los sitios arqueológicos pueden atraer a un público más joven, incrementar los ingresos por venta de entradas y posicionar el destino en la vanguardia tecnológica del turismo global, todo sin tocar o dañar físicamente ni una sola piedra de las estructuras originales.

## Metodología
Investigación y desarrollo de software de entretenimiento educativo (Edutainment). Los modelos 3D se desarrollarán bajo la supervisión de arqueólogos usando fotogrametría base y modelado procedural. Las pruebas de usabilidad del anclaje espacial se realizarán in-situ bajo condiciones extremas de luz solar. Se evaluará el impacto del sistema mediante encuestas de satisfacción y retención de información histórica (A/B testing con turistas tradicionales).

## Stack Tecnológico
- Desarrollo AR: Unity 3D, AR Foundation (ARCore para Android, ARKit para iOS)
- Anclaje Espacial: Niantic Lightship VPS o Azure Spatial Anchors
- Agente Conversacional: OpenAI GPT-4 API con prompt de personalidad histórica
- Interfaz de Voz: Google Cloud Speech-to-Text y Text-to-Speech (Voces neurales)
- Backend y Analíticas: Firebase, BigQuery

## Alcance
La aplicación se desarrollará para un piloto inicial en una única zona arqueológica delimitada. Requiere que el usuario disponga de un smartphone moderno compatible con ARCore/ARKit. No incluye la provisión de red WiFi in-situ, por lo que los modelos 3D pesados deberán descargarse antes de llegar a la zona, mientras que el módulo de voz operará con consumo mínimo de datos celulares.

## Conclusión
La combinación de la Realidad Aumentada y la IA Conversacional no solo rescata visualmente civilizaciones perdidas, sino que transforma profundamente el turismo cultural: pasando de ser espectadores pasivos de ruinas a ser exploradores activos de la historia viva.
