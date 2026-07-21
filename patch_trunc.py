import re

with open("app/api/routes.py", "r") as f:
    content = f.read()

# 1. Truncate similar projects more aggressively (800 chars)
content = content.replace(
    'p["content"][:1500] + "..." if len(p["content"]) > 1500 else p["content"]',
    'p["content"][:800] + "..." if len(p["content"]) > 800 else p["content"]'
)

# 2. Truncate proposal text more aggressively (8000 chars)
content = content.replace(
    'proposal_text = full_proposal_text[:12000] if len(full_proposal_text) > 12000 else full_proposal_text',
    'proposal_text = full_proposal_text[:8000] if len(full_proposal_text) > 8000 else full_proposal_text'
)

with open("app/api/routes.py", "w") as f:
    f.write(content)
