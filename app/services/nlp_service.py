import spacy
import re
import torch
import unicodedata
import numpy as np
import joblib
from pathlib import Path
from sentence_transformers import SentenceTransformer
from fastembed import TextEmbedding
import logging

from app.core import constants
from app.core.config_manager import config_manager


torch.set_num_threads(1)

logger = logging.getLogger(__name__)

# ── Rutas a artefactos del modelo entrenado ────────────────────────────────
_BASE_DIR    = Path(__file__).resolve().parent.parent.parent
_NOTEBOOKS   = _BASE_DIR / "notebooks"
_MODELO_PKL  = _NOTEBOOKS / "models" / "modelo_clasificacion_embeddings.pkl"
_EMB_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

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

    # ── FILTRO 1: Clasificador ML entrenado ──────────────────────────────────
    def clasificar_propuesta_ml(self, texto_limpio: str) -> dict:
        """
        Carga el modelo entrenado y clasifica el texto.
        Retorna: {etiqueta, probabilidades, es_valido}
        """
        try:
            emb_model = TextEmbedding(model_name=_EMB_MODEL_NAME)
            vector = np.array(list(emb_model.embed([texto_limpio])))[0]
            clf = joblib.load(_MODELO_PKL)
            etiqueta = clf.predict([vector])[0]
            probas = {}
            try:
                for clase, p in zip(clf.classes_, clf.predict_proba([vector])[0]):
                    probas[clase] = round(float(p) * 100, 1)
            except Exception:
                pass
            es_valido = etiqueta in constants.ETIQUETA_VALIDAS
            logger.info(f"[Filtro 1] Clasificación ML: {etiqueta} | {probas}")
            return {"etiqueta": etiqueta, "probabilidades": probas,
                    "es_valido": es_valido, "vector": vector.tolist()}
        except Exception as e:
            logger.error(f"[Filtro 1] Error cargando modelo ML: {e}")
            return {"etiqueta": "Desconocido", "probabilidades": {},
                    "es_valido": True, "vector": []}  # falla abierta

    # ── FILTRO 2A: Blacklist extendida ─────────────────────────────────────
    def validar_blacklist_extendida(self, texto_crudo: str) -> dict:
        """
        Busca en todo el texto crudo palabras que indican
        que el documento nunca es una propuesta.
        Retorna: {ok, palabra_bloqueada}
        """
        t = texto_crudo.lower()
        for palabra in constants.BLACKLIST_DOCS:
            if palabra in t:
                logger.warning(f"[Filtro 2A] Documento bloqueado por: '{palabra}'")
                return {"ok": False, "palabra_bloqueada": palabra}
        return {"ok": True, "palabra_bloqueada": None}

    # ── FILTRO 2B: Secciones del profesor ─────────────────────────────────
    def validar_secciones_profesor(self, texto_crudo: str, project_id: str = None) -> dict:
        """
        Verifica que el documento tenga las secciones que los profesores definen.
        Retorna: {ok, faltantes, encontradas, completitud_pct}
        """
        t = texto_crudo.lower()
        # Limpiar tags HTML y formato Markdown (negritas/italicas) pero conservar nuevas lineas y encabezados (#)
        t = re.sub(r'<br\s*/?>', '\n', t)
        t = re.sub(r'[*_|]', ' ', t)
        # Limpiar múltiples espacios pero conservar saltos de linea
        t = re.sub(r'[ \t]+', ' ', t)
        faltantes, encontradas = [], []
        
        project_sections = config_manager.get_project_sections(project_id)
        
        if not project_sections:
            return {
                "ok": True,
                "faltantes": [],
                "encontradas": [],
                "completitud_pct": 100.0,
            }

        # Construir lookup de keywords por nombre de sección desde constants.py (fallback)
        _constants_lookup = {s["nombre"]: s["keywords"] for s in constants.SECCIONES_PROFESOR}

        obligatorias_total = sum(1 for s in project_sections if s.get("obligatoria", False))

        for seccion in project_sections:
            seccion_nombre = seccion.get("nombre", "")
            kws = seccion.get("keywords", [])

            # Si el profe no definió keywords, buscar en constants.py por nombre similar
            if not kws:
                for const_nombre, const_kws in _constants_lookup.items():
                    if const_nombre.lower() in seccion_nombre.lower() or seccion_nombre.lower() in const_nombre.lower():
                        kws = const_kws
                        logger.debug(f"[Filtro 2B] Sección '{seccion_nombre}' sin keywords → usando fallback de constants: {const_nombre}")
                        break
                        
                # Si tampoco está en constants.py (es una sección totalmente nueva), usamos su propio nombre como keyword
                if not kws and seccion_nombre.strip():
                    base_kw = seccion_nombre.lower().strip()
                    # Generar versión sin tildes
                    no_accents_kw = ''.join(c for c in unicodedata.normalize('NFD', base_kw) if unicodedata.category(c) != 'Mn')
                    
                    kws = [base_kw]
                    if no_accents_kw != base_kw:
                        kws.append(no_accents_kw)
                        
                    logger.debug(f"[Filtro 2B] Sección personalizada '{seccion_nombre}' → usando keywords: {kws}")

            found = False
            for kw in kws:
                kw_escaped = re.escape(kw.lower())
                pattern = r'(?m)^(?:#+\s*)?(?:(?:[0-9]{1,2}(?:\.[0-9]{1,2})*\.?|[a-z]{1,4}[\.\)])\s*)?' + kw_escaped + r'\b'
                if re.search(pattern, t):
                    found = True
                    break

            if found:
                encontradas.append(seccion_nombre)
            elif seccion.get("obligatoria", False):
                faltantes.append(seccion_nombre)

        obligatorias_encontradas = len([s for s in project_sections
                                        if s.get("obligatoria", False) and s.get("nombre", "") in encontradas])
        completitud_pct = round((obligatorias_encontradas / obligatorias_total) * 100, 1) if obligatorias_total > 0 else 100.0

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "encontradas": encontradas,
            "completitud_pct": completitud_pct,
        }

    # ── FILTRO 3: Coherencia semántica entre secciones ─────────────────────
    def validar_coherencia_semantica(self, texto_crudo: str) -> dict:
        """
        Extrae el contenido de las secciones clave, las vectoriza y calcula
        similitud coseno entre Problema, Objetivo y Justificación.
        Retorna: {ok, coherencia_pct, pares_invalidos, detalles}
        """
        t = texto_crudo.lower()
        t = re.sub(r'<br\s*/?>', '\n', t)
        t = re.sub(r'[*_|]', ' ', t)
        t = re.sub(r'[ \t]+', ' ', t)
        
        contenidos = {}

        for nombre_sec, anchors in constants.ANCHORS_COHERENCIA.items():
            inicio = None
            for kw in anchors:
                kw_escaped = re.escape(kw.lower())
                pattern = r'(?m)^(?:#+\s*)?(?:(?:[0-9]{1,2}(?:\.[0-9]{1,2})*\.?|[a-z]{1,4}[\.\)])\s*)?' + kw_escaped + r'\b'
                match = re.search(pattern, t)
                if match:
                    inicio = match.end()
                    break
            if inicio is None:
                continue
            fin = len(t)
            for otro_kw in constants.TODOS_LOS_ANCHORS:
                kw_escaped = re.escape(otro_kw.lower())
                pattern_otro = r'(?m)^(?:#+\s*)?(?:(?:[0-9]{1,2}(?:\.[0-9]{1,2})*\.?|[a-z]{1,4}[\.\)])\s*)?' + kw_escaped + r'\b'
                match_otro = re.search(pattern_otro, t[inicio:])
                if match_otro:
                    pos = inicio + match_otro.start()
                    if pos < fin:
                        fin = pos
            contenido = re.sub(r'\s+', ' ', t[inicio:fin]).strip()
            if len(contenido) >= constants.MIN_CHARS_SECCION:
                contenidos[nombre_sec] = contenido[:800]

        if len(contenidos) < 2:
            return {"ok": True, "coherencia_pct": 100.0,
                    "pares_invalidos": [], "detalles": ["No se extrajo contenido suficiente para evaluar coherencia (se omite)"]}

        try:
            emb_model = TextEmbedding(model_name=_EMB_MODEL_NAME)
            vectores = {}
            for nombre, texto in contenidos.items():
                vectores[nombre] = np.array(list(emb_model.embed([texto])))[0]
        except Exception as e:
            logger.warning(f"[Filtro 3] Error vectorizando secciones: {e}")
            return {"ok": True, "coherencia_pct": 100.0, "pares_invalidos": [], "detalles": []}

        pares = [("Problema", "Objetivo"), ("Problema", "Justificación"), ("Objetivo", "Justificación")]
        pares_invalidos, sims, detalles = [], [], []

        for (sec_a, sec_b) in pares:
            if sec_a not in vectores or sec_b not in vectores:
                detalles.append(f"{sec_a} ↔ {sec_b}: contenido insuficiente (omitido)")
                continue
            v1, v2 = vectores[sec_a], vectores[sec_b]
            den = np.linalg.norm(v1) * np.linalg.norm(v2)
            sim = float(np.dot(v1, v2) / den) if den > 0 else 0.0
            sims.append(sim)
            if sim < constants.COHERENCIA_UMBRAL:
                detalles.append(f"{sec_a} ↔ {sec_b}: {sim:.2f} (INCOHERENTE)")
                pares_invalidos.append({"par": f"{sec_a} ↔ {sec_b}", "similitud": round(sim, 3)})
            else:
                detalles.append(f"{sec_a} ↔ {sec_b}: {sim:.2f} (OK)")

        coherencia_pct = round(float(np.mean(sims)) * 100, 1) if sims else 100.0
        return {
            "ok": len(pares_invalidos) == 0,
            "coherencia_pct": coherencia_pct,
            "pares_invalidos": pares_invalidos,
            "detalles": detalles,
        }

    # ── Mantener compatibilidad con código viejo que llame is_valid_project ─
    def is_valid_project(self, text: str) -> bool:
        """Deprecated: usar validar_blacklist_extendida() + validar_secciones_profesor()."""
        result = self.validar_blacklist_extendida(text)
        return result["ok"]

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

        # Remover formato de tablas Markdown generado por pymupdf4llm
        text = re.sub(r'\|\s*[-:]+\s*\|(\s*[-:]+\s*\|)*', '\n', text)
        text = re.sub(r'\|', ' ', text)

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
