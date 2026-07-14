import re

text = """
# 1. Introducción
Este es un proyecto.
## 2. problemática
La falta de comida.
Una introducción al tema es necesaria.
3. OBJETIVO GENERAL
Hacer cosas.
Objetivos Específicos:
- A
- B
"""

kws = ["introducción", "problemática", "objetivo general", "objetivos específicos"]

t = text.lower()
for kw in kws:
    # regex to match start of line, optional #, optional numbers/letters with dots/dashes, then the keyword
    pattern = r'(?m)^(?:#+\s*)?(?:(?:[0-9]+|[a-z])[\.\-\)]\s*)*' + re.escape(kw) + r'\b'
    match = re.search(pattern, t)
    print(f"Keyword: {kw}, Match: {match is not None}")

