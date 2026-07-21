with open("app/api/routes.py", "r") as f:
    content = f.read()

target = """            def normalize_kw(text):
                return ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')"""

replacement = """            def normalize_kw(text):
                if not isinstance(text, str): return ''
                return ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')"""

content = content.replace(target, replacement)

with open("app/api/routes.py", "w") as f:
    f.write(content)
