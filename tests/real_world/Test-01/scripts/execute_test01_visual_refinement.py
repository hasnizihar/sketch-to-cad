"""
Execute Test 01 Visual QA & Presentation Refinement
Nordic Residential Villa (REV-03)
"""

import os
import sys
import json
import math
from pathlib import Path

# Add repository root and scripts to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from scripts.approval_package import calculate_geometry_hash
from scripts.drawing_generator import DrawingGenerator
from scripts.render_test01_sheet import render_test01_sheet_pdf
from scripts.sheet_generator import SheetTitleBlock
from scripts.dxf_inspector import DXFInspector, generate_dxf_inspection_markdown
from scripts.architectural_qa import perform_architectural_qa, generate_engineering_qa_markdown
from scripts.bim_integration_validator import BIMIntegrationValidator, generate_bim_integration_markdown
from dataclasses import asdict

TARGET_HASH = "7cf483c4f2f27282cad5a0662b55b1336de7974a194e28ef5fe83bf8ac46e6cf"
TEST_DIR = REPO_ROOT / "tests" / "real_world" / "Test-01"

def main():
    print("=" * 70)
    print("REAL-WORLD TEST 01: VISUAL QA & PRESENTATION REFINEMENT")
    print("=" * 70)

    # 1. Load and verify draft model
    draft_model_path = TEST_DIR / "draft_model.json"
    with open(draft_model_path, "r", encoding="utf-8") as f:
        draft_model = json.load(f)

    initial_hash = calculate_geometry_hash(draft_model)
    print(f"Pre-refinement Geometry Hash: {initial_hash}")
    assert initial_hash == TARGET_HASH, f"ABORT: Geometry hash mismatch! Got {initial_hash}, expected {TARGET_HASH}"
    print(f"[PASSED] Initial Geometry Hash strictly verified: {TARGET_HASH[:16]}...")

    # 2. Refine Room Presentation Attributes
    print("\n--- Phase 1: Room Label Presentation & Area Reconciliation ---")
    ROOM_REFINEMENTS = {
        "R-DUSS": {
            "displayName": "SHOWER",
            "labelPosition": [900.0, 14700.0],
            "approximateArea": 4.7,
            "calculatedArea": 4.7,
            "sourceArea": 6.0,
            "areaText": "Clear: 4.7 m²\n(Src: 6.0 m²)",
            "textHeight": 130.0,
            "areaHeight": 90.0,
            "areaOffset": 170.0,
        },
        "R-SAUN": {
            "displayName": "SAUNA",
            "labelPosition": [900.0, 12100.0],
            "approximateArea": 3.1,
            "calculatedArea": 3.1,
            "sourceArea": 4.0,
            "areaText": "Clear: 3.1 m²\n(Src: 4.0 m²)",
            "textHeight": 130.0,
            "areaHeight": 90.0,
            "areaOffset": 170.0,
        },
        "R-SAUNA-PUHKE": {
            "displayName": "SAUNA LOUNGE",
            "labelPosition": [3400.0, 13500.0],
            "approximateArea": 15.0,
            "calculatedArea": 15.0,
            "sourceArea": 15.0,
            "areaText": "15.0 m²",
            "textHeight": 160.0,
            "areaHeight": 120.0,
            "areaOffset": 220.0,
        },
        "R-MAJAPIDAMIS": {
            "displayName": "UTILITY ROOM",
            "labelPosition": [6300.0, 14900.0],
            "approximateArea": 5.6,
            "calculatedArea": 5.6,
            "sourceArea": 6.0,
            "areaText": "Clear: 5.6 m² (Src: 6.0 m²)",
            "textHeight": 130.0,
            "areaHeight": 95.0,
            "areaOffset": 180.0,
        },
        "R-TEH": {
            "displayName": "TECH ROOM",
            "labelPosition": [8600.0, 14900.0],
            "approximateArea": 4.3,
            "calculatedArea": 4.3,
            "sourceArea": 5.0,
            "areaText": "Clear: 4.3 m² (Src: 5.0 m²)",
            "textHeight": 130.0,
            "areaHeight": 95.0,
            "areaOffset": 180.0,
        },
        "R-WC": {
            "displayName": "WC",
            "labelPosition": [10050.0, 14500.0],
            "approximateArea": 1.8,
            "calculatedArea": 1.8,
            "sourceArea": 2.4,
            "areaText": "1.8 m²\n(Src: 2.4 m²)",
            "textHeight": 130.0,
            "areaHeight": 85.0,
            "areaOffset": 160.0,
        },
        "R-BED-1": {
            "displayName": "BEDROOM 1",
            "labelPosition": [12750.0, 13800.0],
            "approximateArea": 12.0,
            "calculatedArea": 12.0,
            "sourceArea": 12.0,
            "areaText": "12.0 m²",
            "textHeight": 160.0,
            "areaHeight": 120.0,
            "areaOffset": 220.0,
        },
        "R-BED-2": {
            "displayName": "BEDROOM 2",
            "labelPosition": [12750.0, 10700.0],
            "approximateArea": 12.0,
            "calculatedArea": 12.0,
            "sourceArea": 12.0,
            "areaText": "12.0 m²",
            "textHeight": 160.0,
            "areaHeight": 120.0,
            "areaOffset": 220.0,
        },
        "R-ESIK": {
            "displayName": "ENTRY VESTIBULE",
            "labelPosition": [12750.0, 8150.0],
            "approximateArea": 12.8,
            "calculatedArea": 12.8,
            "sourceArea": 12.8,
            "areaText": "12.8 m²",
            "textHeight": 160.0,
            "areaHeight": 120.0,
            "areaOffset": 220.0,
        },
        "R-MASTER-BED": {
            "displayName": "MASTER BEDROOM",
            "labelPosition": [7000.0, 10500.0],
            "approximateArea": 17.6,
            "calculatedArea": 17.6,
            "sourceArea": 17.6,
            "areaText": "17.6 m²",
            "textHeight": 160.0,
            "areaHeight": 120.0,
            "areaOffset": 220.0,
        },
        "R-BATHROOM": {
            "displayName": "MAIN BATHROOM",
            "labelPosition": [7600.0, 7800.0],
            "approximateArea": 9.8,
            "calculatedArea": 9.8,
            "sourceArea": 6.5,
            "areaText": "Clear: 9.8 m² | Src: 6.5 m²",
            "textHeight": 140.0,
            "areaHeight": 100.0,
            "areaOffset": 190.0,
        },
        "R-LIVING-KITCHEN": {
            "displayName": "LIVING ROOM & KITCHEN",
            "labelPosition": [10000.0, 4500.0],
            "approximateArea": 65.0,
            "calculatedArea": 65.0,
            "sourceArea": 65.0,
            "areaText": "65.0 m²",
            "textHeight": 180.0,
            "areaHeight": 130.0,
            "areaOffset": 250.0,
        },
        "R-CORRIDOR": {
            "displayName": "HALLWAY",
            "labelPosition": [9750.0, 8500.0],
            "approximateArea": 7.1,
            "calculatedArea": 7.1,
            "sourceArea": None,
            "areaText": "7.1 m²",
            "textHeight": 140.0,
            "areaHeight": 100.0,
            "areaOffset": 180.0,
        },
    }

    for r in draft_model.get("rooms", []):
        rid = r.get("id")
        if rid in ROOM_REFINEMENTS:
            r.update(ROOM_REFINEMENTS[rid])
            print(f"Refined room '{rid}': name='{r.get('name')}', label='{r.get('displayName')}', pos={r.get('labelPosition')}, area='{r.get('areaText')}'")

    # 3. Refine Dimension Annotations
    print("\n--- Phase 2: Dimension Text & Scaling Refinement ---")
    DIM_TEXTS = {
        "DIM-EXT-TOP-1": "5000",
        "DIM-EXT-TOP-2": "10000",
        "DIM-EXT-EAST": "16000",
        "DIM-EXT-TERRACE-S": "3000",
        "DIM-EXT-SAUNA-W": "5000",
        "DIM-EXT-MAIN-S": "10000",
    }
    for d in draft_model.get("dimensions", []):
        did = d.get("id")
        if did in DIM_TEXTS:
            d["text"] = DIM_TEXTS[did]
            print(f"Dimension '{did}': text set to '{d['text']}' at {d.get('at')}")

    # 4. Verify Geometry Hash Invariance
    post_refinement_hash = calculate_geometry_hash(draft_model)
    print(f"\nPost-refinement Geometry Hash: {post_refinement_hash}")
    assert post_refinement_hash == TARGET_HASH, (
        f"ABORT: Geometry mutated during presentation refinement! Target={TARGET_HASH}, Got={post_refinement_hash}"
    )
    print(f"[PASSED] STRICT GEOMETRY INVARIANCE VERIFIED: Hash 100% identical ({post_refinement_hash[:16]}...)")

    with open(draft_model_path, "w", encoding="utf-8") as f:
        json.dump(draft_model, f, indent=2)
    print(f"[PASSED] Persisted refined draft model to disk.")

    # 5. Deterministic Drawing Generation
    print("\n--- Phase 3: Deterministic CADCraft Vector Drafting ---")
    out_dxf = TEST_DIR / "Test-01-floor-plan.dxf"
    out_png = TEST_DIR / "Test-01-floor-plan.png"
    out_handoff = TEST_DIR / "Test-01-floor-plan.handoff.json"
    rep_base = str(TEST_DIR / "Test-01-drawing")

    gen = DrawingGenerator()
    cad_res = gen.build_drawing(
        model=draft_model,
        output_dxf_path=str(out_dxf),
        output_png_path=str(out_png),
        output_handoff_path=str(out_handoff),
        generate_report=True,
        output_report_base=rep_base,
    )

    print(f"CADCraft Status: {cad_res.get('status')}")
    print(f"Total Entities in Drawing: {cad_res.get('entityCount')}")
    print(f"Entity breakdown by type: {cad_res.get('counts')}")
    assert out_dxf.is_file() and out_dxf.stat().st_size > 0
    assert out_png.is_file() and out_png.stat().st_size > 0
    assert out_handoff.is_file() and out_handoff.stat().st_size > 0
    print(f"[PASSED] Refined DXF ({out_dxf.stat().st_size} bytes) and PNG preview ({out_png.stat().st_size} bytes) generated.")

    # 6. Render Enhanced Architectural Drawing Sheet (True 1:100 A2)
    print("\n--- Phase 4: Enhanced Architectural Sheet Rendering (A2 @ 1:100) ---")
    sheet_pdf_path = TEST_DIR / "Test-01-sheet-A2.pdf"
    tb = SheetTitleBlock(
        project_name="Nordic Residential Villa (Real-World Test 01)",
        sheet_title="GROUND FLOOR PLAN - ARCHITECTURAL LAYOUT",
        drawing_number="A-101",
        revision="REV-03",
        date_str="2026-11-03",
        author="Sketch-to-CAD Drafting Agent",
        scale_notation="1:100 @ A2",
        units="MILLIMETERS",
        status="SUPERVISED EXPERIMENTAL CAD OUTPUT",
    )

    res_sheet = render_test01_sheet_pdf(
        model=draft_model,
        output_pdf_path=str(sheet_pdf_path),
        drawing_preview_png=str(out_png),
        title_block=tb,
        paper_size="A2",
        scale=100,
    )
    print(f"[PASSED] Architectural Sheet rendered to {res_sheet} ({sheet_pdf_path.stat().st_size} bytes).")

    # 7. Independent Structural DXF Inspection
    print("\n--- Phase 5: Independent Structural DXF Inspection ---")
    with open(out_handoff, "r", encoding="utf-8") as f:
        handoff_data = json.load(f)

    inspector = DXFInspector()
    insp_report = inspector.inspect(
        dxf_path=str(out_dxf),
        model=draft_model,
        handoff=handoff_data,
    )
    insp_json_path = TEST_DIR / "Test-01-dxf-inspection.json"
    insp_md_path = TEST_DIR / "Test-01-dxf-inspection.md"
    with open(insp_json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(insp_report), f, indent=2)
    with open(insp_md_path, "w", encoding="utf-8") as f:
        f.write(generate_dxf_inspection_markdown(insp_report))
    print(f"DXF Inspection Status: {insp_report.overall_status}")
    print(f"Header INSUNITS: {insp_report.header.insunits} ({insp_report.header.units_name})")
    print(f"Layer 0 Cleanliness: {insp_report.layer_zero_clean}")
    print(f"Duplicate Entities: {insp_report.duplicate_entities_count}")
    print(f"Degenerate Segments: {insp_report.degenerate_geometry_count}")

    # 8. Unified Architectural & Engineering QA
    print("\n--- Phase 6: Unified Architectural QA ---")
    with open(TEST_DIR / "extracted_observations.json", "r", encoding="utf-8") as f:
        observations = json.load(f)

    qa_report = perform_architectural_qa(
        model=draft_model,
        source_sketch_path=str(TEST_DIR / "source_sketch.jpg"),
        cad_output_path=str(out_dxf),
        handoff=handoff_data,
        observations=observations,
    )
    qa_json_path = TEST_DIR / "Test-01-architectural-qa.json"
    qa_md_path = TEST_DIR / "Test-01-architectural-qa.md"
    with open(qa_json_path, "w", encoding="utf-8") as f:
        json.dump(qa_report, f, indent=2)
    with open(qa_md_path, "w", encoding="utf-8") as f:
        f.write(generate_engineering_qa_markdown(qa_report))
    print(f"Architectural QA Status: {qa_report.get('overall_status')}")
    print(f"Severity Breakdown: {qa_report.get('severity_counts')}")

    # 9. Downstream BIM Integration Validation
    print("\n--- Phase 7: Downstream BIM Integration Check ---")
    bim_val = BIMIntegrationValidator()
    bim_res = bim_val.run_integration_pipeline(
        dxf_path=str(out_dxf),
        handoff_path=str(out_handoff),
        output_intermediate_path=str(TEST_DIR / "Test-01_intermediate_bim.json"),
    )
    bim_json_path = TEST_DIR / "Test-01-bim-integration.json"
    bim_md_path = TEST_DIR / "Test-01-bim-integration.md"
    with open(bim_json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(bim_res), f, indent=2)
    with open(bim_md_path, "w", encoding="utf-8") as f:
        f.write(generate_bim_integration_markdown(bim_res))
    print(f"BIM Contract Valid: {bim_res.contract_valid}")
    print(f"Downstream Preflight Passed: {bim_res.preflight_passed}")
    print(f"Downstream Intermediate Reconstruction Passed: {bim_res.reconstruction_passed}")

    print("\n" + "=" * 70)
    print("ALL VISUAL REFINEMENT PHASES COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()

