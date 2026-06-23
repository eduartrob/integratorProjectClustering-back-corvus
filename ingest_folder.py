import os
import io
import argparse
import logging
import pdfplumber

from app.services.nlp_service import nlp_service
from app.services.chroma_service import chroma_service

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ingest_folder(folder_path: str):
    if not os.path.isdir(folder_path):
        logger.error(f"La ruta proporcionada no es una carpeta válida: {folder_path}")
        return

    # Listamos todos los archivos PDF y MD en la carpeta
    valid_extensions = ('.pdf', '.md', '.txt')
    files_to_process = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]
    
    if not files_to_process:
        logger.warning(f"No se encontraron archivos PDF o MD en la carpeta: {folder_path}")
        return
        
    logger.info(f"Se encontraron {len(files_to_process)} documentos. Iniciando procesamiento por lotes...")

    success_count = 0
    rejected_count = 0

    for file_name in files_to_process:
        file_path = os.path.join(folder_path, file_name)
        # Usamos el nombre del archivo (sin la extensión) como el Project ID
        project_id = os.path.splitext(file_name)[0]
        
        logger.info(f"\n--- Procesando: {file_name} ---")
        
        try:
            # 1. Extraer texto localmente dependiendo de si es PDF o MD
            full_text = ""
            if file_name.lower().endswith('.pdf'):
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            full_text += text + "\n"
            else:
                # Es un archivo de texto plano o markdown
                with open(file_path, 'r', encoding='utf-8') as f:
                    full_text = f.read()
                        
            if not full_text.strip():
                logger.warning(f"❌ {file_name}: El archivo está vacío o es un escaneo de imágenes puro.")
                rejected_count += 1
                continue
                
            # 2. Filtro Anti-Basura
            if not nlp_service.is_valid_project(full_text):
                logger.warning(f"❌ {file_name}: Rechazado por el filtro (Parece basura/currículum/manual).")
                rejected_count += 1
                continue
                
            # 3. Escudo de Privacidad (PII)
            logger.info(f"🛡️ Anonimizando nombres en {file_name}...")
            safe_text = nlp_service.anonymize_pii(full_text)
            
            # 4. Procesamiento de Inteligencia Artificial
            logger.info("🧠 Picando texto y vectorizando con la IA...")
            chunks = nlp_service.chunk_text(safe_text)
            embeddings = nlp_service.vectorize(chunks)
            
            # 5. Guardar en Base de Datos
            chroma_service.add_vectors(
                project_id=project_id,
                texts=chunks,
                embeddings=embeddings,
                url_drive=f"local_folder:{folder_path}"
            )
            
            logger.info(f"✅ {file_name}: Indexado correctamente. ({len(chunks)} fragmentos).")
            success_count += 1
            
        except Exception as e:
            logger.error(f"❌ Error procesando {file_name}: {str(e)}")
            rejected_count += 1

    logger.info(f"\n===== RESUMEN DE INGESTA =====")
    logger.info(f"Total encontrados: {len(files_to_process)}")
    logger.info(f"Indexados con éxito: {success_count}")
    logger.info(f"Rechazados o fallidos: {rejected_count}")
    logger.info(f"¡Base de datos vectorial lista para graficar!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procesa una carpeta entera de PDFs y los mete a ChromaDB.")
    parser.add_argument("folder", help="Ruta absoluta a la carpeta con los PDFs")
    args = parser.parse_args()
    
    ingest_folder(args.folder)
