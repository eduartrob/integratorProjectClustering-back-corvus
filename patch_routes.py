import re

with open("app/api/routes.py", "r") as f:
    content = f.read()

# 1. Add project_id to draft_data in pre_validate_background
# Find:
#         draft_data = {
#             "chunks": chunks,
#             "similar_projects": similar_projects,
#             "quick_analysis": quick_analysis,
#             "uploaded_by": uploaded_by
#         }
content = content.replace(
    '        draft_data = {\n            "chunks": chunks,\n            "similar_projects": similar_projects,\n            "quick_analysis": quick_analysis,\n            "uploaded_by": uploaded_by\n        }',
    '        draft_data = {\n            "chunks": chunks,\n            "similar_projects": similar_projects,\n            "quick_analysis": quick_analysis,\n            "uploaded_by": uploaded_by,\n            "project_id": project_id\n        }'
)

# 2. Extract project_id in _run_analysis_background
# Find:
#             chunks = draft_data.get("chunks", [])
#             similar_projects = draft_data.get("similar_projects", [])
#             quick_analysis = draft_data.get("quick_analysis", {})
content = content.replace(
    '            chunks = draft_data.get("chunks", [])\n            similar_projects = draft_data.get("similar_projects", [])\n            quick_analysis = draft_data.get("quick_analysis", {})',
    '            chunks = draft_data.get("chunks", [])\n            similar_projects = draft_data.get("similar_projects", [])\n            quick_analysis = draft_data.get("quick_analysis", {})\n            project_id = draft_data.get("project_id")'
)

# 3. Pass project_id to analyze_originality
# Find:
#             llm_verdict = await ollama_service.analyze_originality(
#                 proposal_text=proposal_text,
#                 similar_projects=similar_projects,
#                 max_sim_pct=round(max_sim_pct, 1),
#                 risk_level=risk_level,
#                 project_name="PROPUESTA_DEL_ALUMNO",
#                 top_project_name=top_project_name,
#             )
content = content.replace(
    '            llm_verdict = await ollama_service.analyze_originality(\n                proposal_text=proposal_text,\n                similar_projects=similar_projects,\n                max_sim_pct=round(max_sim_pct, 1),\n                risk_level=risk_level,\n                project_name="PROPUESTA_DEL_ALUMNO",\n                top_project_name=top_project_name,\n            )',
    '            llm_verdict = await ollama_service.analyze_originality(\n                proposal_text=proposal_text,\n                similar_projects=similar_projects,\n                max_sim_pct=round(max_sim_pct, 1),\n                risk_level=risk_level,\n                project_name="PROPUESTA_DEL_ALUMNO",\n                top_project_name=top_project_name,\n                project_id=project_id\n            )'
)

with open("app/api/routes.py", "w") as f:
    f.write(content)
