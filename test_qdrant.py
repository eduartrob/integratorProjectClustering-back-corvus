import sys
import os
sys.path.append("/home/eduartrob/Documentos/project9no/back/integratorProjectClustering-back-corvus")
from app.services.qdrant_service import qdrant_service
_, payloads = qdrant_service.get_all_embeddings()
if payloads:
    print("Example payload:", payloads[0])
    # check how many have university_id
    with_uni = [p for p in payloads if "university_id" in p and p["university_id"]]
    print(f"Total: {len(payloads)}, With university_id: {len(with_uni)}")
else:
    print("No payloads found")
