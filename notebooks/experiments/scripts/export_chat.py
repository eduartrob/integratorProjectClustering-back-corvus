import json
import os
import re

transcript_path = "/home/eduartrob/.gemini/antigravity-ide/brain/1f46a532-218d-4987-951a-4a7321f36926/.system_generated/logs/transcript.jsonl"
output_dir = "/home/eduartrob/Documentos/project9no/chats_ia"
output_path = os.path.join(output_dir, "historial_laboratorio_corvus.md")

os.makedirs(output_dir, exist_ok=True)

def extract_user_content(raw_content):
    match = re.search(r'<USER_REQUEST>(.*?)</USER_REQUEST>', raw_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_content.strip()

try:
    with open(transcript_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    output = "# Historial de Desarrollo: Laboratorio Corvus AI (Fase 0)\n\n"
    output += "Este documento contiene la conversación completa donde desarrollamos desde cero el modelo de Machine Learning, la simulación de caos, y la implementación de NLP.\n\n---\n\n"
    
    for line in lines:
        try:
            data = json.loads(line)
            
            # Mensajes del Usuario
            if data.get('source') == 'USER_EXPLICIT' and data.get('type') == 'USER_INPUT':
                content = data.get('content', '')
                clean_content = extract_user_content(content)
                if clean_content:
                    output += f"### 👤 Usuario\n\n{clean_content}\n\n---\n\n"
                    
            # Mensajes de Gemini
            elif data.get('source') == 'MODEL' and data.get('type') == 'PLANNER_RESPONSE':
                content = data.get('content', '')
                if content.strip():
                    output += f"### 🤖 Gemini\n\n{content.strip()}\n\n---\n\n"
                    
        except Exception as e:
            continue
            
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
        
    print(f"[ÉXITO] Exportación exitosa en: {output_path}")
except FileNotFoundError:
    print(f"[ERROR] No se encontró la transcripción en {transcript_path}")
