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

        prompt = f"""Eres un estricto comité evaluador de proyectos universitarios.
Tu tarea PRINCIPAL es EVALUAR EXCLUSIVAMENTE la "NUEVA PROPUESTA". 
El "HISTORIAL DE PROYECTOS SIMILARES" se te proporciona ÚNICAMENTE como referencia para que busques si hay plagio o colisión. ¡NO evalúes ni des recomendaciones sobre el historial!
ATENCIÓN: Si el historial muestra un proyecto con una Similitud Matemática (ChromaDB) superior al 90%, SIGNIFICA QUE ES UNA COPIA CASI EXACTA O PARÁFRASIS. Debes rechazarlo inmediatamente por colisión y darle un innovation_index de 0.

--- INICIO DE LA NUEVA PROPUESTA A EVALUAR (CONCÉNTRATE EN ESTO) ---
{proposal_text}
--- FIN DE LA NUEVA PROPUESTA ---

--- INICIO DEL HISTORIAL DE PROYECTOS SIMILARES (SOLO REFERENCIA PARA PLAGIO) ---
{context_text}
--- FIN DEL HISTORIAL ---

INSTRUCCIONES FINALES:
Basándote EXCLUSIVAMENTE en la "NUEVA PROPUESTA", y comparándola con el "HISTORIAL" para buscar similitudes, genera tu evaluación.
Tu única salida debe ser un documento JSON estrictamente formateado, sin texto adicional fuera del JSON.
Debes retornar EXACTAMENTE esta estructura JSON:
{{
  "innovation_index": <número del 0 al 100 indicando qué tan original es la NUEVA PROPUESTA>,
  "quality_metrics": {{
    "academic_rigor": <número 0-100>,
    "technical_relevance": <número 0-100>,
    "structural_clarity": <número 0-100>
  }},
  "semantic_collision_risk": "<Texto breve describiendo si la NUEVA PROPUESTA se parece mucho a un proyecto específico del historial>",
  "recommendations": [
    {{
      "title": "<Título corto de qué mejorar en la NUEVA PROPUESTA>",
      "description": "<Explicación detallada de qué mejorar>"
    }}
  ],
  "verdict": "<Aprobado por originalidad / Requiere cambios / Rechazado por colisión>",
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
