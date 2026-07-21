import re

with open("app/api/routes.py", "r") as f:
    content = f.read()

# We need to find where similar_projects are processed before being sent to analyze_originality
# In _run_analysis_background
# similar_projects = draft_data.get("similar_projects", [])

# Let's truncate the content of each similar project to 1500 chars maximum
patch = """
            similar_projects = draft_data.get("similar_projects", [])
            for p in similar_projects:
                if "content" in p and p["content"]:
                    p["content"] = p["content"][:1500] + "..." if len(p["content"]) > 1500 else p["content"]
"""

content = content.replace(
    '            similar_projects = draft_data.get("similar_projects", [])\n            quick_analysis = draft_data.get("quick_analysis", {})',
    patch + '            quick_analysis = draft_data.get("quick_analysis", {})'
)

with open("app/api/routes.py", "w") as f:
    f.write(content)
