import re

with open("app/api/routes.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith("async def _run_analysis_background("):
        start_idx = i
        break

# Insert try/except around the whole content of the function
new_lines = lines[:start_idx+1]
new_lines.append("    import traceback\n")
new_lines.append("    import sys\n")
new_lines.append("    try:\n")

for line in lines[start_idx+1:]:
    if line.startswith("async def ") or line.startswith("@router"):
        # We reached the next function
        end_idx = lines.index(line)
        break

for line in lines[start_idx+1:end_idx]:
    # indent the body
    if line == "\n":
        new_lines.append("\n")
    else:
        new_lines.append("    " + line)

new_lines.append("    except Exception as e:\n")
new_lines.append("        print(f'CRITICAL ERROR IN _run_analysis_background: {e}', file=sys.stderr)\n")
new_lines.append("        traceback.print_exc(file=sys.stderr)\n")
new_lines.append("        analysis_progress_store[user_id] = {'phase': -1, 'message': f'Fallo critico: {e}'}\n")

new_lines.extend(lines[end_idx:])

with open("app/api/routes.py", "w") as f:
    f.writelines(new_lines)
