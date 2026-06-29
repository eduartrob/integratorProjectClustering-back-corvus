import sys
import os
sys.path.append('/home/eduartrob/Documentos/project9no/back/integratorProjectClustering-back-corvus')
from app.services.chroma_service import chroma_service

def test():
    niches = []
    results = chroma_service.collection.get(include=["metadatas"])
    
    unique_projects = {}
    if results and results.get('metadatas'):
        for meta in results['metadatas']:
            if meta and meta.get('is_blue_ocean'):
                p_id = meta.get('project_id')
                if p_id and p_id not in unique_projects:
                    unique_projects[p_id] = meta
    
    for p_id, meta in unique_projects.items():
        name = p_id.replace('proyecto_', '').replace('.md', '').replace('.pdf', '').replace('_', ' ').title()
        niches.append({"title": name})
    
    print("Niches:", niches)

test()
