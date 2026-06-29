import fitz
import pymupdf4llm
from app.services.nlp_service import nlp_service

doc = fitz.open("/home/eduartrob/Documentos/project9no/documentos/PropuestasPI.docx.pdf")
text = pymupdf4llm.to_markdown(doc)

is_valid = nlp_service.is_valid_project(text)
print("\nIs Valid Project?", is_valid)
