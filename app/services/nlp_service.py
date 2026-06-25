import spacy
import re
import torch
from sentence_transformers import SentenceTransformer
import logging

# Limitar PyTorch a 1 hilo de CPU para no "ahorcar" al servidor AWS
# y permitir que FastAPI responda rápidamente al polling de progreso del celular.
torch.set_num_threads(1)

logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        logger.info("Cargando modelo SentenceTransformer: all-MiniLM-L6-v2...")
        # Este modelo pesa ~90MB y generará vectores de 384 dimensiones
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        logger.info("Cargando modelo de Spacy para español...")
        try:
            self.nlp = spacy.load("es_core_news_sm")
        except OSError:
            logger.warning("No se encontró el modelo 'es_core_news_sm'. Ejecuta: python -m spacy download es_core_news_sm")
            self.nlp = None

    def is_valid_project(self, text: str) -> bool:
        """
        Filtro Heurístico para detectar si el documento es basura (currículums, manuales, etc.)
        """
        text_lower = text.lower()
        
        # Palabras comunes en documentos que NO queremos procesar
        black_list = ["currículum", "curriculum vitae", "experiencia laboral", "autoevaluación", "manual de usuario", "manual de mantenimiento"]
        for word in black_list:
            # Buscamos en los primeros 2000 caracteres (portada/intro)
            if word in text_lower[:2000]:
                logger.warning(f"Documento rechazado por contener palabra bloqueada: {word}")
                return False
                
        # Palabras requeridas en un proyecto de investigación o software
        white_list = [
            "resumen", "abstract", "introducción", "conclusión", "objetivo", "metodología", "proyecto", "investigación",
            "sistema", "plataforma", "aplicación", "software", "desarrollo", "base de datos", "ecommerce", "web", "app"
        ]
        match_count = sum(1 for word in white_list if word in text_lower)
        
        # Debe tener al menos 1 palabra clave académica o técnica
        if match_count < 1:
            logger.warning("Documento rechazado por falta de vocabulario académico o técnico.")
            return False
            
        return True

    def anonymize_pii(self, text: str) -> str:
        """
        Detecta y censura nombres de personas (PII) usando Spacy NER.
        Reemplaza los nombres propios con [ALUMNO_ANONIMO].
        """
        if self.nlp is None or not text:
            return text
            
        # Spacy tiene un límite de longitud de texto por defecto (1,000,000 caracteres).
        # Lo procesaremos completo.
        doc = self.nlp(text)
        anonymized_text = text
        
        # Procesamos las entidades en reversa para no desfasar los índices al reemplazar
        for ent in reversed(doc.ents):
            if ent.label_ == "PER":
                start, end = ent.start_char, ent.end_char
                anonymized_text = anonymized_text[:start] + "[ALUMNO_ANONIMO]" + anonymized_text[end:]
                
        return anonymized_text

    def strip_structure(self, text: str) -> str:
        """
        Elimina los encabezados y etiquetas de estructura de la plantilla institucional
        antes de vectorizar. Garantiza que el modelo neuronal compare CONTENIDO
        puro — sin secciones boilerplate idénticas en todos los proyectos.

        CRÍTICO: Llamar ANTES de anonymize_pii() para que los regex de bibliografía
        y nombres de sección funcionen sobre el texto original.
        """
        if not text:
            return text

        # 1. Eliminar SECCIONES COMPLETAS de boilerplate (header + su contenido).
        #    Estas secciones son idénticas en TODOS los proyectos — son ruido puro.
        sections_to_remove = [
            r'##\s*¿Por qué elegir este proyecto\?.*?(?=\n##|\Z)',   # Párrafo de marketing idéntico
            r'##\s*Por qué elegir este proyecto.*?(?=\n##|\Z)',
            r'##\s*Informaci[oó]n del Equipo.*?(?=\n##|\Z)',          # Nombres y matrículas
            r'##\s*Información de la Propuesta.*?(?=\n##|\Z)',
            r'##\s*(Bibliograf[ií]a|Referencias|Bibliography).*?(?=\n##|\Z)',  # Bibliografía
        ]
        for pattern in sections_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

        # 2. Eliminar encabezados Markdown en MAYÚSCULAS (## TÍTULO COMPLETO)
        text = re.sub(r'^#{1,4}\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s/()\-]+$', '', text, flags=re.MULTILINE)

        # 3. Eliminar los labels de sección genéricos de la plantilla (mixed-case)
        #    Solo el header label, el contenido debajo se preserva.
        #    NOTA: 'Stack Tecnológico' NO se elimina — es la sección más discriminativa
        #    y el TF-IDF necesita esas palabras técnicas únicas para separar proyectos.
        generic_headers = [
            r'^#{1,4}\s+Descripci[oó]n del Proyecto\s*$',
            r'^#{1,4}\s+Caracter[ií]sticas Principales\s*$',
        ]
        for pattern in generic_headers:
            text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)

        # 3b. Eliminar el título H1 principal del documento (# Título del proyecto)
        #     El título suele tener palabras genéricas ('Memoria', 'Gestión', 'Sistema')
        #     que contaminan la comparación semántica con proyectos distintos.
        text = re.sub(r'^#\s+.+$', '', text, flags=re.MULTILINE)

        # 3c. Limpieza específica para PDFs extraídos de plantillas institucionales de Word
        #     Eliminar bloque de información del equipo
        text = re.sub(r'INFORMACI[OÓ]N DEL EQUIPO DE TRABAJO.*?INFORMACI[OÓ]N DE LA PROPUESTA.*?\n', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Eliminar restos de tablas de PDF con saltos de línea irregulares
        anomalias = [
            r'NOMBRE DEL\s*\n\s*PROYECTO',
            r'Corvus: Aplicación Móvil de Gestión de Memoria Histórica.*?\.', # Elimina el título específico para evitar anclaje a "Memoria"
            r'CATEGOR[IÍ]A.*?PROBLEM[AÁ]TICA',
            r'OBJETIVO\s*\n?\s*GENERAL',
            r'OBJETIVOS\s*\n?\s*ESPEC[IÍ]FICOS',
            r'USUARIOS\s*\n?\s*FINALES',
            r'LISTA DE\s*\n?\s*FUNCIONALIDADES\s*\n?\s*POR TIPO DE\s*\n?\s*USUARIO',
            r'LISTA DE\s*\n?\s*TECNOLOG[IÍ]AS\s*\n?\s*A\s*\n?\s*APLICAR',
            r'BIBLIOGRAF[IÍ]A\s*\n?\s*CONSULTADA.*'
        ]
        for patron in anomalias:
            text = re.sub(patron, '', text, flags=re.IGNORECASE | re.DOTALL)

        # 4. Eliminar etiquetas de metadatos en negrita (**Categoría:** Videojuegos)
        text = re.sub(r'\*\*(Categoría|Grupo de Similitud|Nivel de Dificultad).*?\n', '\n', text, flags=re.IGNORECASE)

        # 5. Eliminar separadores horizontales (--- o ===)
        text = re.sub(r'^[-=]{3,}$', '', text, flags=re.MULTILINE)

        # 6. Eliminar líneas de datos administrativos (matrículas)
        text = re.sub(r'^.*[Mm]atrícula:.*\d+.*$', '', text, flags=re.MULTILINE)

        # 7. Colapsar líneas en blanco excesivas
        text = re.sub(r'\n{3,}', '\n\n', text)

        logger.debug(f"[strip_structure] Texto limpiado: {len(text)} chars")
        return text.strip()

    def chunk_text(self, text: str, max_words: int = 150) -> list[str]:
        """
        Divide un texto largo en pequeños fragmentos (chunks) con sentido semántico.
        Usa Spacy para detectar las oraciones.
        """
        if not text or not text.strip():
            return []

        if self.nlp is None:
            # Fallback muy básico si Spacy falla
            return [text[i:i+500] for i in range(0, len(text), 500)]

        doc = self.nlp(text)
        chunks = []
        current_chunk = []
        current_word_count = 0

        for sent in doc.sents:
            words_in_sent = len(sent)
            # Si añadir esta oración supera el límite, guardamos el chunk actual y empezamos otro
            if current_word_count + words_in_sent > max_words and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_word_count = 0
            
            current_chunk.append(sent.text.strip())
            current_word_count += words_in_sent
        
        # Guardar el sobrante
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

    def vectorize(self, texts: list[str]) -> list[list[float]]:
        """
        Convierte una lista de textos (chunks) en una lista de vectores (embeddings).
        Aplica limpieza de estructura antes de vectorizar para que la IA compare
        solo el contenido técnico, no los títulos de la plantilla.
        """
        if not texts:
            return []
        
        # Limpiamos la estructura antes de vectorizar
        clean_texts = [self.strip_structure(t) for t in texts]
        
        # encode() devuelve un array de numpy o tensores, lo pasamos a lista nativa
        embeddings = self.encoder.encode(clean_texts, convert_to_numpy=True)
        return embeddings.tolist()

# Instancia global (Singleton) para no recargar la IA en cada petición
nlp_service = NLPService()
