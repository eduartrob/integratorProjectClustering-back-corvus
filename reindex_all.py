"""
Script de Re-Indexación Completa
Vacía ChromaDB y vuelve a indexar todos los proyectos de la carpeta test/
con los vectores limpios (sin estructura de plantilla).
"""
import os
import glob
import chromadb
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.services.nlp_service import nlp_service
from app.services.chroma_service import chroma_service

TEST_DIR = "/home/eduartrob/Descargas/test"

def main():
    # 1. Vaciar la colección directamente
    print("🗑️  Vaciando ChromaDB...")
    try:
        from app.core.config import settings
        client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        try:
            client.delete_collection("integrator_projects")
            print("✅ Colección eliminada.")
        except Exception:
            print("ℹ️  La colección no existía, se creará nueva.")
        # Re-crear la colección limpia
        collection = client.get_or_create_collection(
            name="integrator_projects",
            metadata={"hnsw:space": "cosine"}
        )
    except Exception as e:
        print(f"❌ Error al inicializar ChromaDB: {e}")
        return

    # 2. Re-indexar todos los .md de la carpeta test
    md_files = sorted(glob.glob(os.path.join(TEST_DIR, "*.md")) + glob.glob(os.path.join(TEST_DIR, "*.MD")))
    print(f"\n📂 Encontrados {len(md_files)} archivos en {TEST_DIR}")

    success = 0
    failed = 0
    for filepath in md_files:
        project_id = os.path.splitext(os.path.basename(filepath))[0].lower()
        
        # Saltar archivos README y de documentación que no son proyectos
        if project_id.startswith('readme') or project_id.startswith('_'):
            print(f"  ⏭️  Skipped (no es proyecto): {project_id}")
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()

            # Validación básica
            if not nlp_service.is_valid_project(raw_text):
                print(f"  ⚠️  Skipped (no válido): {project_id}")
                continue

            # Pipeline correcto: strip_structure PRIMERO (antes de que los nombres
            # se conviertan en [ALUMNO_ANONIMO] y rompan los regex de sección)
            clean_text = nlp_service.strip_structure(raw_text)
            safe_text = nlp_service.anonymize_pii(clean_text)
            chunks = nlp_service.chunk_text(safe_text)
            if not chunks:
                print(f"  ⚠️  Skipped (sin chunks): {project_id}")
                continue

            embeddings = nlp_service.vectorize(chunks)
            ids = [f"{project_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{"project_id": project_id, "url": "local://reindex", "chunk_index": i} for i in range(len(chunks))]
            collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
            print(f"  ✅ {project_id} → {len(chunks)} chunks")
            success += 1

        except Exception as e:
            print(f"  ❌ Error en {project_id}: {e}")
            failed += 1

    print(f"\n🎉 Re-indexación completa: {success} proyectos, {failed} errores.")
    print(f"   Los vectores ya son 100% CONTENIDO PURO (sin estructura de plantilla).")

if __name__ == "__main__":
    main()
