import fitz
import pymupdf4llm
from app.api.routes import _validate_project_sections
import json

doc = fitz.open("/home/eduartrob/Documentos/project9no/documentos/PropuestasPI.docx.pdf")
text = pymupdf4llm.to_markdown(doc)
print(text[:500])

result = _validate_project_sections(text)
print("\nValidation Result:", result)
