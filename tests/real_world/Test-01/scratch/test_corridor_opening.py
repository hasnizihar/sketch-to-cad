import json
import shutil
from pathlib import Path

BASE_DIR = Path(r"d:\Agent Skills\sketch-to-cad-main")
TEST_DIR = BASE_DIR / "tests" / "real_world" / "Test-01"

import sys
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(TEST_DIR / "scripts"))
from scripts.drawing_generator import DrawingGenerator
from render_test01_sheet import render_monochrome_dxf_preview

# Load draft_model.json
with open(TEST_DIR / "draft_model.json", "r", encoding="utf-8") as f:
    model = json.load(f)

# Update W-INT-CORR-WEST end to [9000.0, 12400.0]
for w in model["walls"]:
    if w["id"] == "W-INT-CORR-WEST":
        print("Old W-INT-CORR-WEST:", w)
        w["end"] = [9000.0, 12400.0]
        print("New W-INT-CORR-WEST:", w)

out_dxf = TEST_DIR / "scratch" / "test_corridor_opening.dxf"
out_png = TEST_DIR / "scratch" / "test_corridor_opening.png"
out_mono_png = TEST_DIR / "scratch" / "test_corridor_opening_monochrome.png"

gen = DrawingGenerator()
res = gen.build_drawing(model, str(out_dxf), str(out_png))
print("Build result:", res["status"], "entities:", res["entityCount"])

render_monochrome_dxf_preview(str(out_dxf), str(out_mono_png), dpi=300)
print("Monochrome preview rendered!")
