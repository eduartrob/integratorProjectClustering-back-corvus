from app.services.nlp_service import NLPService
nlp_service = NLPService()

text = """
# 1. Desarrollo
Este es un proyecto.
## 2. problemática
La falta de comida.
Una introducción al tema es necesaria.
3. OBJETIVO GENERAL
Hacer cosas.
Objetivos Específicos:
- A
- B
"""

# Let's test section validation
# We need to mock config_manager since it requires DB or files
from app.core.config_manager import ConfigManager
import app.core.config_manager
class MockConfigManager:
    def get_project_sections(self):
        return [
            {"nombre": "Introducción", "keywords": ["introducción", "introduccion"], "obligatoria": True},
            {"nombre": "Problemática", "keywords": ["problemática", "problematica"], "obligatoria": True},
            {"nombre": "Objetivo General", "keywords": ["objetivo general"], "obligatoria": True}
        ]

app.services.nlp_service.config_manager = MockConfigManager()

print(nlp_service.validar_secciones_profesor(text))
