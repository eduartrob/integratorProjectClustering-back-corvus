with open("app/services/llm_client.py", "r") as f:
    content = f.read()

content = content.replace(
    'groq_model = current_config.get("groq_model", "llama-3.1-8b-instant")',
    'groq_model = current_config.get("groq_model", "llama-3.3-70b-versatile")'
)

with open("app/services/llm_client.py", "w") as f:
    f.write(content)
