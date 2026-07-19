import re

with open('app/api/routes.py', 'r') as f:
    content = f.read()

new_sig = 'async def get_blue_ocean_niches(page: int = 1, limit: int = 10):'
content = re.sub(r'async def get_blue_ocean_niches\(\):', new_sig, content)

pagination_logic = """
        niches.sort(key=lambda x: x['_gravity_score'], reverse=True)
        
        for niche in niches:
            niche.pop('_gravity_score', None)
            
        # Paginación
        total = len(niches)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        niches = niches[start_idx:end_idx]
        
    except Exception as e:
"""
content = re.sub(r'        niches\.sort\(key=lambda x: x\[\'_gravity_score\'\], reverse=True\)\n\s+for niche in niches:\n\s+niche\.pop\(\'_gravity_score\', None\)\n\s+except Exception as e:', pagination_logic, content)

with open('app/api/routes.py', 'w') as f:
    f.write(content)
