"""
Patch drawing_generator.py to draw standard architectural doors and windows
conforming to the Architectural Symbols Legend quick reference guide:
1. Windows:
   - Outer sill line (connecting outer jamb corners on layer A-GLAZ)
   - Inner sill line (connecting inner jamb corners on layer A-GLAZ)
   - Glazing centerline(s) on layer A-GLAZ:
     - Single panel window (< 1200 mm): central glass line
     - Double panel window (>= 1200 mm or subType='double'): center mullion + dual glass panes
     - Sliding window: dual offset overlapping sash lines
2. Doors:
   - Cased opening / door placement (swing='none'): clean opening with sealed jambs, zero leaf/arc
   - Sliding door: dual offset bypass track panels
   - Single swing: door leaf line + 90-degree swing arc
   - Double leaf: dual symmetric leaves + dual meeting swing arcs
"""

import sys
from pathlib import Path

for target in [
    Path("scripts/drawing_generator.py"),
    Path("skills/sketch-to-cad/scripts/drawing_generator.py")
]:
    with open(target, "r", encoding="utf-8") as f:
        content = f.read()

    # Target window section
    old_window_code = """            elif op_type == "window":
                c.execute("layer.current", {"name": "A-GLAZ"})
                sub_type = str(op.get("sub_type", op.get("subtype", "standard"))).lower()
                half_w = width / 2.0
                p_left = [center[0] - half_w * ux, center[1] - half_w * uy]
                p_right = [center[0] + half_w * ux, center[1] + half_w * uy]

                if "sliding" in sub_type or "sliding" in str(op.get("swing", "")).lower() or "sliding" in op.get("id", "").lower():
                    # Sliding window: dual offset glass panes
                    off = 15.0
                    p1_a = [center[0] - half_w * ux + off * nx, center[1] - half_w * uy + off * ny]
                    p1_b = [center[0] + 50.0 * ux + off * nx, center[1] + 50.0 * uy + off * ny]
                    p2_a = [center[0] - 50.0 * ux - off * nx, center[1] - 50.0 * uy - off * ny]
                    p2_b = [center[0] + half_w * ux - off * nx, center[1] + half_w * uy - off * ny]
                    c.execute("line", {"points": [p1_a, p1_b]})
                    c.execute("line", {"points": [p2_a, p2_b]})
                else:
                    # Standard / Casement / Fixed window
                    c.execute("line", {"points": [p_left, p_right]})"""

    new_window_code = """            elif op_type == "window":
                c.execute("layer.current", {"name": "A-GLAZ"})
                sub_type = str(op.get("sub_type", op.get("subtype", op.get("subType", "standard")))).lower()
                half_w = width / 2.0
                p_left = [center[0] - half_w * ux, center[1] - half_w * uy]
                p_right = [center[0] + half_w * ux, center[1] + half_w * uy]

                wall_th = float(wall.get("thickness", 200.0)) if wall else 200.0
                half_th = wall_th / 2.0

                # Outer sill line (connecting outer jamb corners)
                p_out_1 = [p_left[0] + half_th * nx, p_left[1] + half_th * ny]
                p_out_2 = [p_right[0] + half_th * nx, p_right[1] + half_th * ny]
                c.execute("line", {"points": [p_out_1, p_out_2]})

                # Inner sill line (connecting inner jamb corners)
                p_in_1 = [p_left[0] - half_th * nx, p_left[1] - half_th * ny]
                p_in_2 = [p_right[0] - half_th * nx, p_right[1] - half_th * ny]
                c.execute("line", {"points": [p_in_1, p_in_2]})

                if "sliding" in sub_type or "sliding" in str(op.get("swing", "")).lower() or "sliding" in op.get("id", "").lower():
                    # Sliding window: dual offset glass panes
                    off = 15.0
                    p1_a = [center[0] - half_w * ux + off * nx, center[1] - half_w * uy + off * ny]
                    p1_b = [center[0] + 50.0 * ux + off * nx, center[1] + 50.0 * uy + off * ny]
                    p2_a = [center[0] - 50.0 * ux - off * nx, center[1] - 50.0 * uy - off * ny]
                    p2_b = [center[0] + half_w * ux - off * nx, center[1] + half_w * uy - off * ny]
                    c.execute("line", {"points": [p1_a, p1_b]})
                    c.execute("line", {"points": [p2_a, p2_b]})
                elif "double" in sub_type or width >= 1200.0:
                    # Double panel window: center mullion + dual glass panes (per Architectural Symbols Legend)
                    mullion_p1 = [center[0] + half_th * nx, center[1] + half_th * ny]
                    mullion_p2 = [center[0] - half_th * nx, center[1] - half_th * ny]
                    c.execute("line", {"points": [mullion_p1, mullion_p2]})
                    c.execute("line", {"points": [p_left, center]})
                    c.execute("line", {"points": [center, p_right]})
                else:
                    # Standard single window: central glass pane (per Architectural Symbols Legend)
                    c.execute("line", {"points": [p_left, p_right]})"""

    old_door_cased = """                elif "sliding" in sub_type or "sliding" in swing_dir or "sliding" in op.get("id", "").lower():
                    # Sliding door: 2 parallel offset overlapping panel lines
                    off = 20.0
                    p1_a = [center[0] - (width / 2.0) * ux + off * nx, center[1] - (width / 2.0) * uy + off * ny]
                    p1_b = [center[0] + 50.0 * ux + off * nx, center[1] + 50.0 * uy + off * ny]
                    p2_a = [center[0] - 50.0 * ux - off * nx, center[1] - 50.0 * uy - off * ny]
                    p2_b = [center[0] + (width / 2.0) * ux - off * nx, center[1] + (width / 2.0) * uy - off * ny]
                    c.execute("line", {"points": [p1_a, p1_b]})
                    c.execute("line", {"points": [p2_a, p2_b]})

                else:"""

    new_door_cased = """                elif "sliding" in sub_type or "sliding" in swing_dir or "sliding" in op.get("id", "").lower():
                    # Sliding door: 2 parallel offset overlapping panel lines
                    off = 20.0
                    p1_a = [center[0] - (width / 2.0) * ux + off * nx, center[1] - (width / 2.0) * uy + off * ny]
                    p1_b = [center[0] + 50.0 * ux + off * nx, center[1] + 50.0 * uy + off * ny]
                    p2_a = [center[0] - 50.0 * ux - off * nx, center[1] - 50.0 * uy - off * ny]
                    p2_b = [center[0] + (width / 2.0) * ux - off * nx, center[1] + (width / 2.0) * uy - off * ny]
                    c.execute("line", {"points": [p1_a, p1_b]})
                    c.execute("line", {"points": [p2_a, p2_b]})

                elif "none" in swing_dir or "cased" in swing_dir or "opening" in swing_dir:
                    # Cased opening / door placement without leaf (per Architectural Symbols Legend)
                    pass

                else:"""

    if old_window_code in content:
        content = content.replace(old_window_code, new_window_code)
        print(f"Replaced window code in {target}")
    else:
        print(f"Could not find old window code in {target}")

    if old_door_cased in content:
        content = content.replace(old_door_cased, new_door_cased)
        print(f"Replaced door cased code in {target}")
    else:
        print(f"Could not find old door cased code in {target}")

    with open(target, "w", encoding="utf-8") as f:
        f.write(content)

print("Patching complete.")

