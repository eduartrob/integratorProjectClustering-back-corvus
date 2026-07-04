import pandas as pd
import re

def limpiar_texto_transformer(texto):
    """
    Limpieza mínima ideal para modelos basados en Transformers (Embeddings).
    Mantiene el contexto, las palabras conectoras y la estructura natural.
    """
    # Convertir a string
    texto = str(texto)
    
    # 1. Pasar a minúsculas
    texto = texto.lower()
    
    # 2. Reemplazar múltiples espacios o saltos de línea por un solo espacio
    texto = re.sub(r'\s+', ' ', texto)
    
    # 3. Eliminar caracteres extraños pero MANTENER los puntos, comas y acentos
    # (Mantenemos el punto '.' porque el usuario pidió separar por bloques antes de un punto)
    texto = re.sub(r'[^\w\s\.,áéíóúüñ]', '', texto)
    
    return texto.strip()

def fragmentar_por_oraciones(texto_limpio):
    """
    Divide el texto usando los puntos '.' como separador lógico.
    Esto agrupa "bloques antes de otro punto" como pidió el usuario.
    """
    # Separar por punto
    fragmentos = texto_limpio.split('.')
    
    chunks = []
    for frag in fragmentos:
        frag = frag.strip()
        # Si el fragmento tiene al menos 3 palabras, lo consideramos un chunk válido
        if len(frag.split()) > 3:
            # Le volvemos a poner el punto final para que el Transformer entienda que termina la idea
            chunks.append(frag + ".")
            
    return chunks

if __name__ == "__main__":
    print("--- INICIANDO PRUEBA: LIMPIEZA LIGERA + CHUNKING POR PUNTOS ---")
    
    df = pd.read_csv("proyectos_sinteticos.csv")
    df_prueba = df.iloc[[0, 3]].copy() 
    
    print("\n[INFO] Aplicando limpieza ligera para Transformers...")
    df_prueba['texto_limpio'] = df_prueba['texto_extraido'].apply(limpiar_texto_transformer)
    
    print("[INFO] Fragmentando textos por oraciones (bloques hasta el punto)...\n")
    df_prueba['chunks'] = df_prueba['texto_limpio'].apply(fragmentar_por_oraciones)
    
    for index, row in df_prueba.iterrows():
        print(f"=== {row['id_documento']} ({row['categoria_calidad']}) ===")
        print(f"ORIGINAL (Fragmento): {row['texto_extraido'][:200]}...\n")
        print(f"LIMPIO (Conserva fluidez): {row['texto_limpio']}\n")
        print(f"CHUNKS (Separados por punto):")
        for i, chunk in enumerate(row['chunks']):
            print(f"  Chunk {i+1} [{len(chunk.split())} palabras]: {chunk}")
        print("="*80 + "\n")
