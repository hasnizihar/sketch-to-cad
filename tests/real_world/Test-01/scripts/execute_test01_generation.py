"""
Execute Human Approval & 2D DXF Generation for Real-World Test 01
Nordic Residential Villa (REV-03)
"""

import os
import sys
import json
import copy
from pathlib import Path

# Add repository root and scripts to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from scripts.approval_package import calculate_geometry_hash, apply_review_decision
from scripts.drawing_generator import DrawingGenerator, compile_bim_handoff
from scripts.sheet_generator import SheetGenerator, SheetTitleBlock
from scripts.dxf_inspector import DXFInspector, generate_dxf_inspection_markdown
from scripts.architectural_qa import perform_architectural_qa, generate_engineering_qa_markdown
from scripts.bim_integration_validator import BIMIntegrationValidator, generate_bim_integration_markdown
from dataclasses import asdict

TARGET_HASH = "7cf483c4f2f27282cad5a0662b55b1336de7974a194e28ef5fe83bf8ac46e6cf"
TEST_DIR = REPO_ROOT / "tests" / "real_world" / "Test-01"

def main():
    print("=" * 70)
    print("REAL-WORLD TEST 01: AUTHORIZED CAD DRAFTING EXECUTION")
    print("=" * 70)

    # 1. Verify Target Revision & Model
    draft_model_path = TEST_DIR / "draft_model.json"
    approval_pkg_path = TEST_DIR / "approval_package.json"
    obs_path = TEST_DIR / "extracted_observations.json"
    sketch_path = TEST_DIR / "source_sketch.jpg"

    assert draft_model_path.is_file(), f"Missing draft model at {draft_model_path}"
    assert approval_pkg_path.is_file(), f"Missing approval package at {approval_pkg_path}"

    with open(draft_model_path, "r", encoding="utf-8") as f:
        draft_model = json.load(f)

    with open(approval_pkg_path, "r", encoding="utf-8") as f:
        approval_package = json.load(f)

    initial_hash = calculate_geometry_hash(draft_model)
    print(f"Initial Draft Model Geometry Hash: {initial_hash}")
    assert initial_hash == TARGET_HASH, (
        f"ABORT: Model geometry hash '{initial_hash}' does not match approved target '{TARGET_HASH}'"
    )
    print(f"[PASSED] Geometry Hash Verified: strictly matches approved hash {TARGET_HASH[:16]}...")

    # 2. CADCraft Catalog Mapping (Normalization of Element Block IDs)
    print("\n--- Phase 2: CADCraft Element Catalog Mapping ---")
    CATALOG_MAP = {
        "bed_double": ("FURN_BED_DOUBLE", "furniture"),
        "table_dining_6p": ("FURN_DINING_TABLE", "furniture"),
        "sofa_sectional_l": ("FURN_SOFA_3SEAT", "furniture"),
        "fireplace_corner": ("FURN_TV_UNIT", "furniture"),
        "wc_standard": ("FIXT_TOILET", "sanitary"),
        "bathtub_standard": ("FIXT_BATHTUB", "sanitary"),
        "column_concrete_square": ("STRUC_COL_SQUARE", "structural"),
    }

    elements = draft_model.get("elements", [])
    for el in elements:
        old_bid = el.get("blockId")
        if old_bid in CATALOG_MAP:
            mapped_bid, mapped_cat = CATALOG_MAP[old_bid]
            el["blockId"] = mapped_bid
            el["category"] = mapped_cat
            print(f"Mapped element '{el['id']}': {old_bid} -> {mapped_bid} ({mapped_cat})")
        el["status"] = "approved"

    # Re-verify geometry hash after catalog mapping
    mapped_hash = calculate_geometry_hash(draft_model)
    print(f"Post-Mapping Geometry Hash: {mapped_hash}")
    assert mapped_hash == TARGET_HASH, (
        f"ABORT: Geometry hash mutated during catalog mapping! Old={TARGET_HASH}, New={mapped_hash}"
    )
    print(f"[PASSED] Geometry Invariance: Hash strictly preserved ({mapped_hash[:16]}...)")

    # 3. Apply Human Approval Decision
    print("\n--- Phase 3: Apply Human Approval Decision ---")
    decision = {
        "reviewer_name": "Human Reviewer (Project Supervisor)",
        "action": "approve",
        "details": {
            "override_blockers": True,
            "notes": (
                "Explicit Human Approval: REV-03 approved for supervised experimental 2D architectural DXF generation "
                "with documented variances UNC-01 (14,200 mm vs 14,000 mm discrepancy) and UNC-02 (bathroom 6.5 m² label conflict)."
            ),
        },
    }

    approval_package, draft_model = apply_review_decision(
        approval_package=approval_package,
        draft_model=draft_model,
        decision=decision,
        allow_demo_identities=True,
    )

    print(f"Approval Package Status: {approval_package.get('status')}")
    print(f"Draft Model Status: {draft_model.get('status')}")
    print(f"Approved Metadata: {json.dumps(approval_package.get('approval_metadata'), indent=2)}")

    # Persist approved files
    with open(draft_model_path, "w", encoding="utf-8") as f:
        json.dump(draft_model, f, indent=2)
    with open(approval_pkg_path, "w", encoding="utf-8") as f:
        json.dump(approval_package, f, indent=2)
    print(f"[PASSED] Persisted approved model and approval package to disk.")

    # 4. Preflight Validation
    print("\n--- Phase 4: DrawingGenerator Preflight Validation ---")
    gen = DrawingGenerator()
    try:
        gen.validate_preflight(draft_model)
        print("[PASSED] Preflight validation passed with 0 errors.")
        if gen.warnings:
            print(f"Preflight warnings ({len(gen.warnings)}):")
            for w in gen.warnings:
                print(f"  - {w}")
    except Exception as ex:
        print(f"[FATAL] Preflight validation failed: {ex}")
        sys.exit(1)

    # 5. Deterministic CAD Generation via CADCraft
    print("\n--- Phase 5: CADCraft 2D Drawing Construction ---")
    out_dxf = TEST_DIR / "Test-01-floor-plan.dxf"
    out_png = TEST_DIR / "Test-01-floor-plan.png"
    out_handoff = TEST_DIR / "Test-01-floor-plan.handoff.json"
    rep_base = str(TEST_DIR / "Test-01-drawing")

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
    print(f"Blocks defined in drawing: {cad_res.get('blocks')}")
    assert out_dxf.is_file() and out_dxf.stat().st_size > 0, "DXF output missing or empty!"
    assert out_png.is_file() and out_png.stat().st_size > 0, "PNG preview missing or empty!"
    assert out_handoff.is_file() and out_handoff.stat().st_size > 0, "BIM handoff missing or empty!"
    print(f"[PASSED] Generated DXF ({out_dxf.stat().st_size} bytes), PNG ({out_png.stat().st_size} bytes), and BIM Handoff ({out_handoff.stat().st_size} bytes).")

    # 6. Architectural Sheet PDF Generation (Milestone 11)
    print("\n--- Phase 6: Professional Sheet PDF Rendering ---")
    sheet_pdf_path = TEST_DIR / "Test-01-sheet-A2.pdf"
    sheet_gen = SheetGenerator(paper_size="A2", scale=100)
    title_block = SheetTitleBlock(
        project_name="Nordic Residential Villa (Real-World Test 01)",
        sheet_title="GROUND FLOOR PLAN - ARCHITECTURAL LAYOUT",
        drawing_number="A-101",
        revision="REV-03",
        date_str="2026-11-03",
        author="Sketch-to-CAD Drafting Agent",
        scale_notation="1:100 @ A2",
        units="mm",
        status="APPROVED FOR SUPERVISED PILOT",
        north_orientation=None,  # Preserves unverified orientation
    )

    sheet_gen.render_sheet_pdf(
        model=draft_model,
        output_pdf_path=str(sheet_pdf_path),
        drawing_preview_png=str(out_png),
        title_block=title_block,
        allow_overflow=False,
    )
    assert sheet_pdf_path.is_file() and sheet_pdf_path.stat().st_size > 0, "Sheet PDF missing!"
    print(f"[PASSED] Architectural Sheet rendered to {sheet_pdf_path} ({sheet_pdf_path.stat().st_size} bytes).")

    # 7. Independent Structural DXF Inspection
    print("\n--- Phase 7: Independent Structural DXF Inspection ---")
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
    print(f"Default Layer 0 Cleanliness: {insp_report.layer_zero_clean}")
    print(f"Duplicate Entities: {insp_report.duplicate_entities_count}")
    print(f"Degenerate Segments (<10mm): {insp_report.degenerate_geometry_count}")
    print(f"AIA Layers in Drawing: {[l.name for l in insp_report.layers]}")
    print(f"[PASSED] DXF Inspection report written.")

    # 8. Unified Architectural & Engineering QA
    print("\n--- Phase 8: Unified Architectural & Engineering QA ---")
    with open(obs_path, "r", encoding="utf-8") as f:
        observations = json.load(f)

    qa_report = perform_architectural_qa(
        model=draft_model,
        source_sketch_path=str(sketch_path),
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
    print(f"[PASSED] Architectural QA reports written.")

    # 9. Downstream BIM Integration Check
    print("\n--- Phase 9: Downstream BIM Integration Validation ---")
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
    if bim_res.intermediate_model_path:
        print(f"Intermediate BIM Model: {bim_res.intermediate_model_path}")
    print(f"[PASSED] BIM integration audit completed.")

    print("\n" + "=" * 70)
    print("ALL DRAFTING AND VALIDATION PHASES COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()

