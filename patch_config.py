with open("app/core/config_manager.py", "r") as f:
    content = f.read()

content = content.replace(
    '"llm_provider": "ollama",',
    '"llm_provider": "groq",'
)

with open("app/core/config_manager.py", "w") as f:
    f.write(content)
