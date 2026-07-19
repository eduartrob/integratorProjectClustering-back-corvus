import re

with open("app/api/routes.py", "r") as f:
    content = f.read()

# We will wrap the inside of _run_analysis_background with a try-except and print traceback to sys.stderr
target = """async def _run_analysis_background(user_id: str, draft_path: str):

    try:
        active_analysis_tasks[user_id] = asyncio.current_task()"""

replacement = """async def _run_analysis_background(user_id: str, draft_path: str):
    import sys, traceback
    try:

    try:
        active_analysis_tasks[user_id] = asyncio.current_task()"""

content = content.replace(target, replacement)

target2 = """            analysis_progress_store[user_id] = {
                "phase": -1,
                "message": f"Error interno en análisis: {str(e)}"
            }"""

replacement2 = """            analysis_progress_store[user_id] = {
                "phase": -1,
                "message": f"Error interno en análisis: {str(e)}"
            }
    except Exception as outer_e:
        print(f"CRITICAL ERROR in _run_analysis_background: {outer_e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        analysis_progress_store[user_id] = {"phase": -1, "message": "CRITICAL ERROR"}"""

content = content.replace(target2, replacement2)

with open("app/api/routes.py", "w") as f:
    f.write(content)
