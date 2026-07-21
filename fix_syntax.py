import re

with open("app/api/routes.py", "r") as f:
    content = f.read()

target = """async def _run_analysis_background(user_id: str, draft_path: str):
    import sys, traceback
    try:

    try:"""

replacement = """async def _run_analysis_background(user_id: str, draft_path: str):
    import sys, traceback
    try:"""

content = content.replace(target, replacement)

with open("app/api/routes.py", "w") as f:
    f.write(content)
