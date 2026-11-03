import os
import sys

new_code = '''    def _draw_walls_and_openings(self, c: CADCraftClient, model: Dict[str, Any], floor_id: Optional[str] = None):
        """Generates double-line walls following architectural hierarchy:
        1. Exterior envelope (A-WALL-EXTR) walls are completed first, mitering at all building corners
           to form a continuous, unbroken outer envelope.
        2. Interior walls (A-WALL-INTR) connect to the completed outer walls, terminating cleanly at
           the inner faces of host exterior walls without penetrating wall cavities.
        3. Interior partitions connect and miter with each other at internal corners and T-junctions.
        """
        default_floor = model.get("floors", [{}])[0].get("id", "LEVEL-01") if model.get("floors") else model.get("floorId", "LEVEL-01")
        openings_by_id = {op["id"]: op for op in model.get("openings", [])}
        walls = [w for w in model.get("walls", []) if _matches_floor(w, floor_id, default_floor)]

        def line_intersect(p1, v1, p2, v2):
            denom = v1[0] * v2[1] - v1[1] * v2[0]
            if abs(denom) < 1e-6:
                return None
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            t = (dx * v2[1] - dy * v2[0]) / denom
            u = (dx * v1[1] - dy * v1[0]) / denom
            return t, u

        wall_info = {}
        for w in walls:
            wid = w["id"]
            s = [float(w["start"][0]), float(w["start"][1])]
            e = [float(w["end"][0]), float(w["end"][1])]
            th = float(w.get("thickness", 200.0))
            dx = e[0] - s[0]
            dy = e[1] - s[1]
            L = math.hypot(dx, dy)
            if L < 1e-4:
                continue
            ux = dx / L
            uy = dy / L
            nx = -uy * (th / 2.0)
            ny = ux * (th / 2.0)
            wall_info[wid] = {
                "wall": w,
                "layer": w.get("layer", "A-WALL-EXTR"),
                "s": s, "e": e, "th": th, "L": L,
                "ux": ux, "uy": uy, "nx": nx, "ny": ny,
                "t0_start": 0.0, "t0_end": L,
                "t1_start": 0.0, "t1_end": L,
                "step_lines": []
            }

        extr_info = {wid: info for wid, info in wall_info.items() if info["layer"] == "A-WALL-EXTR"}
        intr_info = {wid: info for wid, info in wall_info.items() if info["layer"] != "A-WALL-EXTR"}

        # -------------------------------------------------------------
        # PASS 1: Complete the Exterior Wall Envelope (A-WALL-EXTR)
        # Outer walls have priority and form continuous perimeter corners
        # -------------------------------------------------------------
        for w1_id, w1 in extr_info.items():
            s1, e1 = w1["s"], w1["e"]
            u1, n1 = [w1["ux"], w1["uy"]], [w1["nx"], w1["ny"]]
            L1, th1 = w1["L"], w1["th"]

            for end1_name, end1_pt in [("start", s1), ("end", e1)]:
                dir1 = [u1[0] if end1_name == "start" else -u1[0],
                        u1[1] if end1_name == "start" else -u1[1]]

                for sgn1, face1_key in [(+1, "t0"), (-1, "t1")]:
                    norm1 = [sgn1 * n1[0], sgn1 * n1[1]]
                    p1_face = [end1_pt[0] + norm1[0], end1_pt[1] + norm1[1]]

                    best_t = None
                    for w2_id, w2 in extr_info.items():
                        if w2_id == w1_id:
                            continue
                        s2, e2 = w2["s"], w2["e"]
                        u2, n2 = [w2["ux"], w2["uy"]], [w2["nx"], w2["ny"]]
                        th2 = w2["th"]

                        for end2_name, end2_pt in [("start", s2), ("end", e2)]:
                            dist = math.hypot(end1_pt[0] - end2_pt[0], end1_pt[1] - end2_pt[1])
                            if dist <= 25.0:
                                dir2 = [u2[0] if end2_name == "start" else -u2[0],
                                        u2[1] if end2_name == "start" else -u2[1]]
                                cross_z = dir1[0] * dir2[1] - dir1[1] * dir2[0]

                                if abs(cross_z) < 0.1:
                                    # Collinear continuation of exterior wall
                                    dot = dir1[0] * dir2[0] + dir1[1] * dir2[1]
                                    if dot < -0.9:
                                        best_t = 0.0 if end1_name == "start" else L1
                                    continue

                                # Corner bisector
                                bx = dir1[0] + dir2[0]
                                by = dir1[1] + dir2[1]
                                b_len = math.hypot(bx, by)
                                if b_len < 1e-4:
                                    continue
                                bx /= b_len
                                by /= b_len

                                dot1 = norm1[0] * bx + norm1[1] * by
                                is_inner1 = (dot1 > 0.05)
                                is_outer1 = (dot1 < -0.05)

                                for sgn2 in [+1, -1]:
                                    norm2 = [sgn2 * n2[0], sgn2 * n2[1]]
                                    dot2 = norm2[0] * bx + norm2[1] * by
                                    is_inner2 = (dot2 > 0.05)
                                    is_outer2 = (dot2 < -0.05)

                                    if (is_inner1 and is_inner2) or (is_outer1 and is_outer2):
                                        p2_face = [end2_pt[0] + norm2[0], end2_pt[1] + norm2[1]]
                                        sol = line_intersect(p1_face, u1, p2_face, u2)
                                        if sol is not None:
                                            t1_sol, t2_sol = sol
                                            abs_t = t1_sol if end1_name == "start" else L1 + t1_sol
                                            if abs(t1_sol) <= max(th1, th2) * 1.5:
                                                best_t = abs_t
                                                break
                                if best_t is not None:
                                    break
                        if best_t is not None:
                            break
                    if best_t is not None:
                        w1[f"{face1_key}_{end1_name}"] = best_t

        # -------------------------------------------------------------
        # PASS 2: Connect Interior Walls (A-WALL-INTR) to Outer & Inner Walls
        # Inner walls terminate at the inner face of completed outer walls
        # -------------------------------------------------------------
        for w1_id, w1 in intr_info.items():
            s1, e1 = w1["s"], w1["e"]
            L1, th1 = w1["L"], w1["th"]
            u1, n1 = [w1["ux"], w1["uy"]], [w1["nx"], w1["ny"]]

            for end1_name, end1_pt in [("start", s1), ("end", e1)]:
                dir1 = [u1[0] if end1_name == "start" else -u1[0],
                        u1[1] if end1_name == "start" else -u1[1]]

                # Check connection to an EXTERIOR wall (body or endpoint)
                connected_to_extr = False
                for w_ext_id, w_ext in extr_info.items():
                    s_ext, e_ext = w_ext["s"], w_ext["e"]
                    dx_ext, dy_ext = e_ext[0] - s_ext[0], e_ext[1] - s_ext[1]
                    l_ext_sq = dx_ext * dx_ext + dy_ext * dy_ext
                    t_proj = ((end1_pt[0] - s_ext[0]) * dx_ext + (end1_pt[1] - s_ext[1]) * dy_ext) / l_ext_sq
                    if -0.05 <= t_proj <= 1.05:
                        proj = [s_ext[0] + t_proj * dx_ext, s_ext[1] + t_proj * dy_ext]
                        dist = math.hypot(end1_pt[0] - proj[0], end1_pt[1] - proj[1])
                        if dist <= 35.0:
                            trim = w_ext["th"] / 2.0
                            sin_a = abs(u1[0] * (dy_ext / math.sqrt(l_ext_sq)) - u1[1] * (dx_ext / math.sqrt(l_ext_sq)))
                            if sin_a > 0.1:
                                trim = (w_ext["th"] / 2.0) / sin_a
                            if end1_name == "start":
                                w1["t0_start"] = max(w1["t0_start"], trim)
                                w1["t1_start"] = max(w1["t1_start"], trim)
                            else:
                                w1["t0_end"] = min(w1["t0_end"], L1 - trim)
                                w1["t1_end"] = min(w1["t1_end"], L1 - trim)
                            connected_to_extr = True
                            break

                if connected_to_extr:
                    continue

                # Check T-junction with other INTERIOR walls:
                for w2_id, w2 in intr_info.items():
                    if w1_id == w2_id:
                        continue
                    s2, e2 = w2["s"], w2["e"]
                    dx2, dy2 = e2[0] - s2[0], e2[1] - s2[1]
                    l2_sq = dx2 * dx2 + dy2 * dy2
                    t2_proj = ((end1_pt[0] - s2[0]) * dx2 + (end1_pt[1] - s2[1]) * dy2) / l2_sq
                    if 0.01 < t2_proj < 0.99:
                        proj = [s2[0] + t2_proj * dx2, s2[1] + t2_proj * dy2]
                        dist = math.hypot(end1_pt[0] - proj[0], end1_pt[1] - proj[1])
                        if dist <= 35.0:
                            trim = w2["th"] / 2.0
                            if end1_name == "start":
                                w1["t0_start"] = max(w1["t0_start"], trim)
                                w1["t1_start"] = max(w1["t1_start"], trim)
                            else:
                                w1["t0_end"] = min(w1["t0_end"], L1 - trim)
                                w1["t1_end"] = min(w1["t1_end"], L1 - trim)
                            break

                # Check L-corners with other INTERIOR walls:
                for sgn1, face1_key in [(+1, "t0"), (-1, "t1")]:
                    norm1 = [sgn1 * n1[0], sgn1 * n1[1]]
                    p1_face = [end1_pt[0] + norm1[0], end1_pt[1] + norm1[1]]
                    best_t = None
                    for w2_id, w2 in intr_info.items():
                        if w2_id == w1_id:
                            continue
                        s2, e2 = w2["s"], w2["e"]
                        u2, n2 = [w2["ux"], w2["uy"]], [w2["nx"], w2["ny"]]
                        th2 = w2["th"]
                        for end2_name, end2_pt in [("start", s2), ("end", e2)]:
                            dist = math.hypot(end1_pt[0] - end2_pt[0], end1_pt[1] - end2_pt[1])
                            if dist <= 25.0:
                                dir2 = [u2[0] if end2_name == "start" else -u2[0],
                                        u2[1] if end2_name == "start" else -u2[1]]
                                cross_z = dir1[0] * dir2[1] - dir1[1] * dir2[0]
                                if abs(cross_z) < 0.1:
                                    continue
                                bx = dir1[0] + dir2[0]
                                by = dir1[1] + dir2[1]
                                b_len = math.hypot(bx, by)
                                if b_len < 1e-4:
                                    continue
                                bx /= b_len
                                by /= b_len
                                dot1 = norm1[0] * bx + norm1[1] * by
                                is_inner1 = (dot1 > 0.05)
                                is_outer1 = (dot1 < -0.05)
                                for sgn2 in [+1, -1]:
                                    norm2 = [sgn2 * n2[0], sgn2 * n2[1]]
                                    dot2 = norm2[0] * bx + norm2[1] * by
                                    is_inner2 = (dot2 > 0.05)
                                    is_outer2 = (dot2 < -0.05)
                                    if (is_inner1 and is_inner2) or (is_outer1 and is_outer2):
                                        p2_face = [end2_pt[0] + norm2[0], end2_pt[1] + norm2[1]]
                                        sol = line_intersect(p1_face, u1, p2_face, u2)
                                        if sol is not None:
                                            t1_sol, _ = sol
                                            abs_t = t1_sol if end1_name == "start" else L1 + t1_sol
                                            if abs(t1_sol) <= max(th1, th2) * 1.5:
                                                best_t = abs_t
                                                break
                                if best_t is not None:
                                    break
                        if best_t is not None:
                            break
                    if best_t is not None:
                        w1[f"{face1_key}_{end1_name}"] = best_t

        for wid, info in wall_info.items():
            wall = info["wall"]
            layer = wall.get("layer", "A-WALL-EXTR")
            c.execute("layer.current", {"name": layer})

            start = info["s"]
            ux, uy = info["ux"], info["uy"]
            nx, ny = info["nx"], info["ny"]
            t0_s, t0_e = info["t0_start"], info["t0_end"]
            t1_s, t1_e = info["t1_start"], info["t1_end"]

            wall_openings = []
            for op_id in wall.get("openingIds", []):
                if op_id in openings_by_id:
                    op = openings_by_id[op_id]
                    op_center = op["center"]
                    op_t = (op_center[0] - start[0]) * ux + (op_center[1] - start[1]) * uy
                    op_w = float(op.get("width", 900.0))
                    wall_openings.append({
                        "id": op_id,
                        "t1": op_t - op_w / 2.0,
                        "t2": op_t + op_w / 2.0,
                        "type": op.get("type", "door")
                    })

            wall_openings.sort(key=lambda o: o["t1"])

            # Draw Face 0 (left-hand normal: +n)
            curr_0 = t0_s
            for op in wall_openings:
                op_cut1 = max(t0_s, min(t0_e, op["t1"]))
                op_cut2 = max(t0_s, min(t0_e, op["t2"]))
                if op_cut1 > curr_0:
                    p1 = [start[0] + curr_0 * ux + nx, start[1] + curr_0 * uy + ny]
                    p2 = [start[0] + op_cut1 * ux + nx, start[1] + op_cut1 * uy + ny]
                    c.execute("line", {"points": [p1, p2]})
                curr_0 = max(curr_0, op_cut2)
            if curr_0 < t0_e:
                p1 = [start[0] + curr_0 * ux + nx, start[1] + curr_0 * uy + ny]
                p2 = [start[0] + t0_e * ux + nx, start[1] + t0_e * uy + ny]
                c.execute("line", {"points": [p1, p2]})

            # Draw Face 1 (right-hand normal: -n)
            curr_1 = t1_s
            for op in wall_openings:
                op_cut1 = max(t1_s, min(t1_e, op["t1"]))
                op_cut2 = max(t1_s, min(t1_e, op["t2"]))
                if op_cut1 > curr_1:
                    p1 = [start[0] + curr_1 * ux - nx, start[1] + curr_1 * uy - ny]
                    p2 = [start[0] + op_cut1 * ux - nx, start[1] + op_cut1 * uy - ny]
                    c.execute("line", {"points": [p1, p2]})
                curr_1 = max(curr_1, op_cut2)
            if curr_1 < t1_e:
                p1 = [start[0] + curr_1 * ux - nx, start[1] + curr_1 * uy - ny]
                p2 = [start[0] + t1_e * ux - nx, start[1] + t1_e * uy - ny]
                c.execute("line", {"points": [p1, p2]})

            # Transverse jamb end-caps sealing the wall cavity at openings
            for op in wall_openings:
                p1_out = [start[0] + op["t1"] * ux + nx, start[1] + op["t1"] * uy + ny]
                p1_in = [start[0] + op["t1"] * ux - nx, start[1] + op["t1"] * uy - ny]
                p2_out = [start[0] + op["t2"] * ux + nx, start[1] + op["t2"] * uy + ny]
                p2_in = [start[0] + op["t2"] * ux - nx, start[1] + op["t2"] * uy - ny]
                c.execute("line", {"points": [p1_out, p1_in]})
                c.execute("line", {"points": [p2_out, p2_in]})

            # Draw step lines sealing collinear thickness transitions
            for p_step1, p_step2, step_layer in info["step_lines"]:
                c.execute("layer.current", {"name": step_layer})
                c.execute("line", {"points": [p_step1, p_step2]})

    def _draw_wall_segment(self, c: CADCraftClient, start, ux, uy, nx, ny, t1, t2):
        p1_out = [start[0] + t1 * ux + nx, start[1] + t1 * uy + ny]
        p2_out = [start[0] + t2 * ux + nx, start[1] + t2 * uy + ny]
        p1_in = [start[0] + t1 * ux - nx, start[1] + t1 * uy - ny]
        p2_in = [start[0] + t2 * ux - nx, start[1] + t2 * uy - ny]
        c.execute("line", {"points": [p1_out, p2_out]})
        c.execute("line", {"points": [p1_in, p2_in]})

'''

for path in ['scripts/drawing_generator.py', 'skills/sketch-to-cad/scripts/drawing_generator.py']:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    s_marker = '    def _draw_walls_and_openings(self, c: CADCraftClient, model: Dict[str, Any], floor_id: Optional[str] = None):'
    e_marker = '    def _draw_doors_and_windows(self, c: CADCraftClient, model: Dict[str, Any], floor_id: Optional[str] = None):'
    s_idx = content.find(s_marker)
    e_idx = content.find(e_marker)
    if s_idx == -1 or e_idx == -1:
        print(f'ERROR: Markers not found in {path}')
        sys.exit(1)
    updated = content[:s_idx] + new_code + content[e_idx:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(updated)
    print(f'Successfully updated {path}')
