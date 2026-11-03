import sys

def patch(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    found = False
    for i, line in enumerate(lines):
        if 'for op_id in wall.get(' in line and 'openingIds' in line:
            indent = ' ' * 12
            new_lines.append(indent + 'op_ids = list(wall.get("openingIds", []))\n')
            new_lines.append(indent + 'for op in model.get("openings", []):\n')
            new_lines.append(indent + '    if op.get("wallId") == wid and op["id"] not in op_ids:\n')
            new_lines.append(indent + '        op_ids.append(op["id"])\n')
            new_lines.append(indent + 'for op_id in op_ids:\n')
            found = True
        else:
            new_lines.append(line)
    
    if not found:
        print(f'ERROR: target line not found in {path}')
        sys.exit(1)
        
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f'Patched {path}')

patch('scripts/drawing_generator.py')
patch('skills/sketch-to-cad/scripts/drawing_generator.py')

