import requests
import json
import logging

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self, host="http://localhost:11434"):
        self.host = host
        self.model = "phi3:mini"
        
    def check_health(self) -> bool:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=3)
            return response.status_code == 200
        except:
            return False

    def analyze_originality(self, proposal_text: str, similar_projects: list[dict]) -> dict:
        """
        Fase 5: Evalúa la originalidad de la propuesta contrastándola con los K-NN más cercanos.
        Retorna un diccionario JSON estructurado para la app móvil.
        """
        context_text = ""
        for i, proj in enumerate(similar_projects):
            sim_pct = proj.get('similarity_pct', 0)
            context_text += f"\n--- Proyecto Existente {i+1} ---\nTítulo: {proj.get('title', 'Desconocido')}\nSimilitud Matemática (ChromaDB): {sim_pct:.1f}%\nContenido: {proj.get('content', '')}\n"

        prompt = f"""Eres un estricto comité evaluador de proyectos universitarios en un sistema de IA avanzado (AcadeRAG).
Tu tarea PRINCIPAL es EVALUAR EXCLUSIVAMENTE la "NUEVA PROPUESTA". 
El "HISTORIAL DE PROYECTOS SIMILARES" se te proporciona ÚNICAMENTE como referencia para que busques si hay plagio o colisión semántica. ¡NO evalúes ni des recomendaciones sobre el historial!

REGLAS DE ANÁLISIS DE COLISIÓN (HISTORIAL): 
- Si un proyecto del historial tiene una Similitud Matemática (ChromaDB) > 50% y la idea central es idéntica, emite una "Alerta Roja".
- Si la similitud matemática es moderada (20-50%) pero aplican la tecnología a sectores distintos o con diferenciadores claros, emite una "Falsa Alarma". Si les falta diferenciarse, emite "Alerta Amarilla".
- Si un proyecto supera el 90% de similitud, asúmelo como plagio/copia, asigna un innovation_index score de 0 y Rechaza (approved: false).

--- INICIO DE LA NUEVA PROPUESTA A EVALUAR (CONCÉNTRATE EN ESTO) ---
{proposal_text}
--- FIN DE LA NUEVA PROPUESTA ---

--- INICIO DEL HISTORIAL DE PROYECTOS SIMILARES (SOLO REFERENCIA PARA PLAGIO) ---
{context_text}
--- FIN DEL HISTORIAL ---

INSTRUCCIONES FINALES DE ESTRUCTURA JSON:
Tu salida debe ser ÚNICA y EXCLUSIVAMENTE un documento JSON válido, sin ningún texto Markdown ni comentarios fuera de él. El JSON llenará un Dashboard UI.
Respeta EXACTAMENTE esta estructura y sigue las reglas para cada campo:
{{
  "innovation_index": {{
    "score": <número 0-100>,
    "label": "<Usa exactamente una de estas: Excepcional | Muy Bueno | Aceptable | Tradicional>"
  }},
  "quality_metrics": {{
    "academic_rigor": <número 0-100 evaluando citas y referencias>,
    "technical_relevance": <número 0-100 evaluando la modernidad de la tecnología propuesta>,
    "structural_clarity": <número 0-100 evaluando la redacción y organización>
  }},
  "semantic_collision_risk": {{
    "alert_type": "<Usa exactamente una de estas: Alerta Roja | Alerta Amarilla | Falsa Alarma>",
    "explanation": "<Análisis humano leyendo ambos proyectos. Explica a detalle por qué chocan o por qué es original. Si no hay historial similar, indica originalidad alta.>"
  }},
  "recommendations": [
    {{
      "icon": "<Usa exactamente uno de estos identificadores de Material Symbols: code, lock, fact_check, architecture, library_books>",
      "title": "<Título accionable (ej. Actualizar stack tecnológico)>",
      "description": "<Instrucción experta, técnica y específica sobre cómo mejorar (entre 2 y 3 oraciones).>"
    }}
  ],
  "verdict": "<Breve resumen del dictamen>",
  "approved": <booleano true o false>
}}
"""

        try:
            logger.info(f"Enviando prompt a Ollama ({self.model}) en modo JSON...")
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.2
                    }
                },
                timeout=900
            )
            response.raise_for_status()
            data = response.json()
            
            # Convertir el string JSON de Ollama a un diccionario de Python
            respuesta_texto = data.get("response", "{}")
            return json.loads(respuesta_texto)
        except Exception as e:
            logger.error(f"Error comunicando con Ollama: {e}")
            return {
                "innovation_index": 0,
                "error": str(e),
                "verdict": "Error de Inferencia"
            }

ollama_service = OllamaService()
