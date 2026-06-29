import spacy
import re
import torch
import unicodedata
from sentence_transformers import SentenceTransformer
import logging

torch.set_num_threads(1)

logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        logger.info("Cargando modelo SentenceTransformer: paraphrase-multilingual-MiniLM-L12-v2...")
        self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        logger.info("Cargando modelo de Spacy para español...")
        try:
            self.nlp = spacy.load("es_core_news_sm")
        except OSError:
            logger.warning("No se encontró el modelo 'es_core_news_sm'. Ejecuta: python -m spacy download es_core_news_sm")
            self.nlp = None

    def is_valid_project(self, text: str) -> bool:
        
        text_lower = text.lower()
        
        black_list = ["currículum", "curriculum vitae", "experiencia laboral", "autoevaluación", "manual de usuario", "manual de mantenimiento"]
        for word in black_list:
            if word in text_lower[:2000]:
                logger.warning(f"Documento rechazado por contener palabra bloqueada: {word}")
                return False
                
        white_list = [
            "resumen", "abstract", "introducción", "conclusión", "objetivo", "metodología", "proyecto", "investigación",
            "sistema", "plataforma", "aplicación", "software", "desarrollo", "base de datos", "ecommerce", "web", "app"
        ]
        match_count = sum(1 for word in white_list if word in text_lower)
        
        if match_count < 1:
            logger.warning("Documento rechazado por falta de vocabulario académico o técnico.")
            return False
            
        return True

    def anonymize_pii(self, text: str) -> str:
        
        if self.nlp is None or not text:
            return text
            
        doc = self.nlp(text)
        anonymized_text = text
        
        for ent in reversed(doc.ents):
            if ent.label_ == "PER":
                start, end = ent.start_char, ent.end_char
                anonymized_text = anonymized_text[:start] + "[ALUMNO_ANONIMO]" + anonymized_text[end:]
                
        return anonymized_text

    def strip_structure(self, text: str) -> str:
        
        if not text:
            return text

        sections_to_remove = [
            r'##\s*¿Por qué elegir este proyecto\?.*?(?=\n##|\Z)',
            r'##\s*Por qué elegir este proyecto.*?(?=\n##|\Z)',
            r'##\s*Informaci[oó]n del Equipo.*?(?=\n##|\Z)',
            r'##\s*Información de la Propuesta.*?(?=\n##|\Z)',
            r'##\s*(Bibliograf[ií]a|Referencias|Bibliography).*?(?=\n##|\Z)',
        ]
        for pattern in sections_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

        text = re.sub(r'^#{1,4}\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s/()\-]+$', '', text, flags=re.MULTILINE)

        generic_headers = [
            r'^#{1,4}\s+Descripci[oó]n del Proyecto\s*$',
            r'^#{1,4}\s+Caracter[ií]sticas Principales\s*$',
        ]
        for pattern in generic_headers:
            text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)

        text = re.sub(r'^#\s+.+$', '', text, flags=re.MULTILINE)

        text = re.sub(r'INFORMACI[OÓ]N DEL EQUIPO DE TRABAJO.*?INFORMACI[OÓ]N DE LA PROPUESTA.*?\n', '', text, flags=re.IGNORECASE | re.DOTALL)
        
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

        text = re.sub(r'\*\*(Categoría|Grupo de Similitud|Nivel de Dificultad).*?\n', '\n', text, flags=re.IGNORECASE)

        text = re.sub(r'^[-=]{3,}$', '', text, flags=re.MULTILINE)

        text = re.sub(r'^.*[Mm]atrícula:.*\d+.*$', '', text, flags=re.MULTILINE)

        text = re.sub(r'\n{3,}', '\n\n', text)

        logger.debug(f"[strip_structure] Texto limpiado: {len(text)} chars")
        return text.strip()

    def detect_prompt_injection(self, text: str) -> bool:
        
        text_lower = text.lower()
        patterns = [
            r"ignora.*instrucciones",
            r"olvida.*anterior",
            r"(?i)\b(act[uú]a como|eres un bot)\b(?!\s+(sinodal|sistema|plataforma|herramienta))",
            r"innovation_index",
            r"approved:\s*true",
            r"system prompt"
        ]
        for p in patterns:
            if re.search(p, text_lower):
                logger.warning(f"¡Alerta de Seguridad! Posible inyección de prompt detectada por patrón: {p}")
                return True
        return False

    def normalize_homoglyphs(self, text: str) -> str:
        
        if not text:
            return ""
        normalized = unicodedata.normalize('NFKD', text)
        clean_text = re.sub(r'[\u0400-\u04FF\u0500-\u052F\u2D00-\u2D2F\uA640-\uA69F]', '', normalized)
        return clean_text

    def chunk_text(self, text: str, max_words: int = 150) -> list[str]:
        
        if not text or not text.strip():
            return []

        chunks = []
        sections = re.split(r'\n(?=#+ )', text)

        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            words = section.split()
            if len(words) <= max_words:
                chunks.append(section)
            else:
                if self.nlp is None:
                    for i in range(0, len(words), max_words):
                        chunks.append(" ".join(words[i:i+max_words]))
                else:
                    doc = self.nlp(section)
                    current_chunk = []
                    current_count = 0
                    for sent in doc.sents:
                        w_count = len(sent)
                        if current_count + w_count > max_words and current_chunk:
                            chunks.append(" ".join(current_chunk))
                            current_chunk = []
                            current_count = 0
                        current_chunk.append(sent.text.strip())
                        current_count += w_count
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))

        return chunks

    def vectorize(self, texts: list[str]) -> list[list[float]]:
        
        if not texts:
            return []
        
        clean_texts = [self.strip_structure(t) for t in texts]
        
        embeddings = self.encoder.encode(clean_texts, convert_to_numpy=True)
        return embeddings.tolist()

nlp_service = NLPService()
