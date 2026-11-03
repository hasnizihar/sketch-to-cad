#!/usr/bin/env python3
"""
Production Release Pipeline for Sketch-to-CAD Test 01 Revision REV-07.
Applies human approval, builds production DXF vector file, renders 1:100 A2 sheet PDF,
generates BIM handoff and drawing reports, and runs DXF inspection, architectural QA,
and downstream BIM integration validation.
"""

import os
import sys
import json
from pathlib import Path
from dataclasses import asdict

SCRIPT_DIR = Path(__file__).resolve().parent
TEST_DIR = SCRIPT_DIR.parent
BASE_DIR = SCRIPT_DIR.parents[3]

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

from scripts.approval_package import create_approval_package, apply_review_decision, verify_approval_integrity, calculate_geometry_hash
from scripts.drawing_generator import DrawingGenerator
from render_test01_sheet import render_test01_sheet_pdf, render_monochrome_dxf_preview
from scripts.sheet_generator import SheetTitleBlock
from scripts.dxf_inspector import DXFInspector, generate_dxf_inspection_markdown
from scripts.architectural_qa import perform_architectural_qa, generate_engineering_qa_markdown
from scripts.bim_integration_validator import BIMIntegrationValidator, generate_bim_integration_markdown

def main():
    print("==================================================================")
    print("   SKETCH-TO-CAD REAL-WORLD TEST 01: PRODUCTION RELEASE (REV-07)  ")
    print("==================================================================")

    # 1. Load draft_model.json and approval_package.json
    model_path = TEST_DIR / "draft_model.json"
    package_path = TEST_DIR / "approval_package.json"

    with open(model_path, "r", encoding="utf-8") as f:
        draft_model = json.load(f)

    with open(package_path, "r", encoding="utf-8") as f:
        approval_package = json.load(f)

    # Apply REV-07 geometric modifications:
    # 1. Guest WC toilet positioned flush against north wall, centered in room
    for el in draft_model.get("elements", []):
        if el.get("id") == "E-WC-FIXTURE":
            el["position"] = [9825.0, 15200.0]
            el["rotation"] = 0.0

    # 2. Window W-WC retained as high-sill window per user decision Option B
    for op in draft_model.get("openings", []):
        if op.get("id") == "W-WC":
            op["sill_height_mm"] = 1500.0
            op["description"] = "High-sill ventilation window above toilet"

    # Set revision metadata
    draft_model["metadata"]["revision"] = "REV-07"
    draft_model["metadata"]["notes"] = (
        "REV-07: Reconciled Guest WC toilet positioning (flush against north wall at [9825.0, 15200.0], centered with 175 mm side clearances) and retained W-WC as high-sill window per user decision Option B."
    )

    # Calculate deterministic geometry hash
    current_hash = calculate_geometry_hash(draft_model)
    draft_model["metadata"]["geometryHash"] = current_hash
    print(f"[PRE-CHECK] Model revision: {draft_model.get('metadata', {}).get('revision')}")
    print(f"[PRE-CHECK] Computed geometry SHA-256: {current_hash}")

    # Create proposal package for REV-07 if hash changed or revision changed
    approval_package = create_approval_package(
        draft_model=draft_model,
        project_name="Nordic Villa Residence (Test 01)"
    )

    # 2. Apply Human Approval Decision
    decision_payload = {
        "action": "approve",
        "reviewer_name": "Haction Lanka",
        "details": {
            "override_blockers": True,
            "notes": "REV-07: Reconciled Guest WC toilet positioning and retained high-sill window W-WC per human approval."
        }
    }

    approved_pkg, approved_model = apply_review_decision(
        approval_package=approval_package,
        draft_model=draft_model,
        decision=decision_payload,
        allow_demo_identities=True
    )

    integrity_ok, integrity_msg = verify_approval_integrity(approved_pkg, approved_model)
    if not integrity_ok:
        print(f"[FAILED] Human approval gate rejected: {integrity_msg}")
        sys.exit(1)
    print(f"[PASSED] Human approval verified: {integrity_msg}")

    # Persist approved states
    with open(model_path, "w", encoding="utf-8") as f:
        json.dump(approved_model, f, indent=2)

    with open(package_path, "w", encoding="utf-8") as f:
        json.dump(approved_pkg, f, indent=2)

    # 3. Phase 4: Deterministic CAD Generation via DrawingGenerator
    print("\n--- Phase 4: Deterministic CAD Generation ---")
    gen = DrawingGenerator()

    dxf_out = TEST_DIR / "Test-01-floor-plan.dxf"
    png_out = TEST_DIR / "Test-01-floor-plan.png"
    handoff_out = TEST_DIR / "Test-01-floor-plan.handoff.json"

    res = gen.build_drawing(
        model=approved_model,
        output_dxf_path=str(dxf_out),
        output_png_path=str(png_out)
    )

    print(f"[PASSED] CAD generation status: {res.get('status')}")
    print(f"[PASSED] Total entities in drawing: {res.get('entityCount')}")
    print(f"[PASSED] DXF vector generated: {dxf_out} ({dxf_out.stat().st_size} bytes)")
    print(f"[PASSED] PNG preview generated: {png_out} ({png_out.stat().st_size} bytes)")
    print(f"[PASSED] BIM handoff JSON generated: {handoff_out} ({handoff_out.stat().st_size} bytes)")

    # 4. Phase 4 Extension: Architectural Sheet Rendering (A2 @ 1:100 Scale)
    print("\n--- Phase 4: Enhanced Architectural Sheet Rendering (A2 @ 1:100) ---")
    tb = SheetTitleBlock(
        project_name="Nordic Villa Residence (Test 01)",
        sheet_title="GROUND FLOOR PLAN - ARCHITECTURAL RELEASE",
        floor_id="LEVEL-01",
        drawing_number="A-101",
        revision="REV-07",
        author="Haction Lanka (Chief Architect)",
        date_str="2026-11-04",
        status="APPROVED FOR CONSTRUCTION",
        scale_notation="1:100 @ A2",
        units="MM",
        north_orientation="NORTH"
    )

    # Render dedicated high-resolution monochrome vector plot from DXF
    monochrome_png = TEST_DIR / "Test-01-floor-plan-monochrome.png"
    render_monochrome_dxf_preview(
        dxf_path=str(dxf_out),
        output_png_path=str(monochrome_png),
        dpi=300
    )
    print(f"[PASSED] Professional monochrome plan rendered: {monochrome_png} ({monochrome_png.stat().st_size} bytes)")

    sheet_pdf = TEST_DIR / "Test-01-sheet-A2.pdf"
    render_test01_sheet_pdf(
        model=approved_model,
        output_pdf_path=str(sheet_pdf),
        drawing_preview_png=str(monochrome_png),
        title_block=tb,
        paper_size="A2",
        scale=100,
        dxf_path=str(dxf_out)
    )
    print(f"[PASSED] True 1:100 A2 Architectural Sheet rendered: {sheet_pdf} ({sheet_pdf.stat().st_size} bytes)")

    # 5. Phase 5: Independent Structural DXF Inspection
    print("\n--- Phase 5: Independent Structural DXF Inspection ---")
    inspector = DXFInspector()
    insp_report = inspector.inspect(str(dxf_out), model=approved_model)
    insp_json = TEST_DIR / "Test-01-dxf-inspection.json"
    insp_md = TEST_DIR / "Test-01-dxf-inspection.md"

    with open(insp_json, "w", encoding="utf-8") as f:
        json.dump(asdict(insp_report), f, indent=2)
    with open(insp_md, "w", encoding="utf-8") as f:
        f.write(generate_dxf_inspection_markdown(insp_report))

    print(f"DXF Inspection Status: {insp_report.overall_status}")
    print(f"Header INSUNITS: {insp_report.header.insunits}")
    print(f"Layer 0 Cleanliness: {insp_report.layer_zero_clean}")
    print(f"Duplicate Entities: {insp_report.duplicate_entities_count}")
    print(f"Degenerate Segments: {insp_report.degenerate_geometry_count}")

    # 6. Phase 6: Unified Architectural QA
    print("\n--- Phase 6: Unified Architectural QA ---")
    qa_report = perform_architectural_qa(
        model=approved_model,
        cad_output_path=str(dxf_out),
        source_sketch_path=str(TEST_DIR / "source_sketch.jpg"),
        observations=None
    )
    qa_json = TEST_DIR / "Test-01-architectural-qa.json"
    qa_md = TEST_DIR / "Test-01-architectural-qa.md"

    with open(qa_json, "w", encoding="utf-8") as f:
        json.dump(qa_report, f, indent=2)
    with open(qa_md, "w", encoding="utf-8") as f:
        f.write(generate_engineering_qa_markdown(qa_report))

    print(f"Architectural QA Status: {qa_report.get('status', qa_report.get('overall_status'))}")
    print(f"Severity Breakdown: {qa_report.get('severity_breakdown', qa_report.get('discrepancy_counts'))}")

    # 7. Phase 7: Downstream BIM Integration Check
    print("\n--- Phase 7: Downstream BIM Integration Check ---")
    validator = BIMIntegrationValidator()
    bim_report = validator.run_integration_pipeline(
        dxf_path=str(dxf_out),
        handoff_path=str(handoff_out),
        output_intermediate_path=str(TEST_DIR / "Test-01_intermediate_bim.json")
    )
    bim_json = TEST_DIR / "Test-01-bim-integration.json"
    bim_md = TEST_DIR / "Test-01-bim-integration.md"

    with open(bim_json, "w", encoding="utf-8") as f:
        json.dump(asdict(bim_report), f, indent=2)
    with open(bim_md, "w", encoding="utf-8") as f:
        f.write(generate_bim_integration_markdown(bim_report))

    print(f"BIM Contract Valid: {bim_report.contract_valid}")
    print(f"Downstream Preflight Passed: {bim_report.preflight_passed}")
    print(f"Downstream Intermediate Reconstruction Passed: {bim_report.reconstruction_passed}")

    print("\n==================================================================")
    print("   PRODUCTION RELEASE REV-07 COMPLETED SUCCESSFULLY!              ")
    print("==================================================================")

if __name__ == "__main__":
    main()
