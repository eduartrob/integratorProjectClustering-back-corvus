import re

with open('app/api/routes.py', 'r') as f:
    content = f.read()

dummy_logic = """
    if not niches and page == 1:
        niches = [
            {
                "category": "MÉTRICA VACÍA",
"""
content = re.sub(r'\s+if not niches:\n\s+niches = \[\n\s+{\n\s+"category": "MÉTRICA VACÍA",', dummy_logic, content)

with open('app/api/routes.py', 'w') as f:
    f.write(content)
