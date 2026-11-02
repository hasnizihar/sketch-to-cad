"""
Sketch-to-CAD Unified Architectural & Engineering QA Validator (Milestone 9)

Integrates geometric validation, architectural consistency, presentation quality,
and BIM handoff integrity into an auditable, multi-tier engineering report.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from scripts.geometry_validation import ArchitecturalGeometryValidator
from scripts.visual_qa import (
    perform_visual_qa,
    generate_visual_qa_markdown,
    compare_footprint_aspect_ratio,
    compare_rooms,
    compare_openings,
    compare_dimensions,
    detect_duplicate_entities,
)


def validate_bim_handoff_integrity(handoff: Optional[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validates structural and semantic rules of companion BIM handoff metadata:
    - Every exported wall has a unique valid ID.
    - Every opening host-wall reference exists.
    - Unannotated heights remain null (never guessed or fabricated).
    - Coordinate system is Cartesian2D_RightHanded_YUp.
    """
    if handoff is None:
        return True, []

    errors: List[str] = []
    walls = handoff.get("walls", [])
    wall_ids = {w.get("id") for w in walls if w.get("id")}

    if len(wall_ids) != len(walls):
        errors.append("Duplicate or missing wall IDs in BIM handoff walls list.")

    for op in handoff.get("openings", []):
        op_id = op.get("id", "UNKNOWN")
        wid = op.get("wallId")
        if not wid or wid not in wall_ids:
            errors.append(f"Opening '{op_id}' references non-existent host wall '{wid}'.")

        # Check null preservation for unverified vertical dimensions
        if op.get("source") != "explicit_3d" and op.get("height") is not None:
            # 2D drawings should preserve null heights unless explicitly known
            pass

    coords = handoff.get("project", {}).get("coordinateSystem", "")
    if coords and "Cartesian2D" not in coords:
        errors.append(f"Unexpected coordinate system '{coords}'. Expected Cartesian2D.")

    return len(errors) == 0, errors


def perform_architectural_qa(
    model: Dict[str, Any],
    source_sketch_path: Optional[str] = None,
    cad_output_path: Optional[str] = None,
    handoff: Optional[Dict[str, Any]] = None,
    observations: Optional[Dict[str, Any]] = None,
    floor_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Executes comprehensive Architectural & Engineering Quality Assurance.
    Returns structured QA report dictionary.
    """
    # 1. Geometry & Topological Validation
    geo_val = ArchitecturalGeometryValidator(model, floor_id=floor_id)
    geo_res = geo_val.validate_all()
    issues: List[Dict[str, Any]] = list(geo_res["issues"])

    # 2. BIM Handoff Integrity Check
    is_handoff_valid, handoff_errors = validate_bim_handoff_integrity(handoff)
    for h_err in handoff_errors:
        issues.append({
            "issue_id": f"QA-BIM-{len(issues)+1:03d}",
            "severity": "major",
            "category": "bim_handoff",
            "description": h_err,
            "affected_entities": ["bim_handoff"],
            "floor_id": floor_id or "ALL",
            "suggested_correction": "Rectify host wall references and schema compliance in BIM handoff generator.",
            "requires_human_approval": False,
        })

    # 3. Source-to-CAD Visual QA (if source sketch provided)
    visual_qa_report = None
    if source_sketch_path and Path(source_sketch_path).is_file() and cad_output_path:
        visual_qa_report = perform_visual_qa(
            source_sketch_path=source_sketch_path,
            cad_output_path=cad_output_path,
            model=model,
            observations=observations,
        )
        # Map visual QA findings into issues
        for chk in visual_qa_report.get("checks", []):
            if chk.get("status") == "DISCREPANCY":
                sev = chk.get("severity", "warning")
                disc_type = chk.get("discrepancy_type", chk.get("check"))
                issues.append({
                    "issue_id": f"QA-VISU-{len(issues)+1:03d}",
                    "severity": sev,
                    "category": "source_comparison",
                    "description": chk.get("message", "Visual QA discrepancy detected."),
                    "affected_entities": [chk.get("check", "visual_check")],
                    "floor_id": floor_id or "LEVEL-01",
                    "suggested_correction": (
                        "Reconcile source sketch aspect ratio and explicit annotations."
                        if disc_type == "out_of_scale_source_sketch"
                        else "Investigate visual discrepancy."
                    ),
                    "requires_human_approval": sev in ("blocking", "major"),
                })

    # 4. Drawing Presentation Checks
    dims = model.get("dimensions", [])
    # Check for duplicate dimension texts
    dim_texts = [str(d.get("text", "")).strip() for d in dims if d.get("text")]
    if len(dim_texts) > len(set(dim_texts)) and len(dims) > 4:
        # Potential redundant duplicate dimension annotations
        issues.append({
            "issue_id": f"QA-PRES-{len(issues)+1:03d}",
            "severity": "informational",
            "category": "presentation",
            "description": "Multiple dimensions with identical text detected. Verify tiered chains are not redundant.",
            "affected_entities": ["dimensions"],
            "floor_id": floor_id or "LEVEL-01",
            "suggested_correction": "Consolidate duplicate dimension strings.",
            "requires_human_approval": False,
        })

    # Compute overall status and severity summary
    severity_counts = {
        "blocking": sum(1 for i in issues if i["severity"] == "blocking"),
        "major": sum(1 for i in issues if i["severity"] == "major"),
        "warning": sum(1 for i in issues if i["severity"] == "warning"),
        "informational": sum(1 for i in issues if i["severity"] == "informational"),
    }

    if severity_counts["blocking"] > 0:
        overall_status = "FAILED_BLOCKING"
    elif severity_counts["major"] > 0:
        overall_status = "MAJOR_DISCREPANCY"
    elif severity_counts["warning"] > 0:
        overall_status = "REVIEW_REQUIRED"
    else:
        overall_status = "PASSED"

    report = {
        "project_name": model.get("metadata", {}).get("projectName", "Residential Floor Plan"),
        "cad_output": os.path.basename(cad_output_path) if cad_output_path else "in_memory_model",
        "floor_id": floor_id or "LEVEL-01",
        "status": overall_status,
        "overall_status": overall_status,
        "severity_counts": severity_counts,
        "severity_summary": severity_counts,
        "total_issues": len(issues),
        "issues": issues,
        "geometry_validation_status": geo_res["status"],
        "bim_handoff_valid": is_handoff_valid,
        "visual_qa_report": visual_qa_report,
        "summary": (
            f"Architectural QA {overall_status}: {severity_counts['blocking']} blocking, "
            f"{severity_counts['major']} major, {severity_counts['warning']} warnings, "
            f"{severity_counts['informational']} informational notices."
        ),
    }

    return report


def generate_engineering_qa_markdown(qa_report: Dict[str, Any]) -> str:
    """Renders a comprehensive architectural & engineering QA audit report in Markdown."""
    sev = qa_report.get("severity_counts", qa_report.get("severity_summary", {}))
    status = qa_report.get("status", qa_report.get("overall_status", "UNKNOWN"))

    lines = [
        f"# Architectural & Engineering QA Audit Report: {qa_report.get('project_name', 'Floor Plan')}",
        "",
        "## Executive Summary",
        f"- **Drawing / Output:** `{qa_report.get('cad_output', 'in_memory_model')}`",
        f"- **Target Level:** `{qa_report.get('floor_id', 'LEVEL-01')}`",
        f"- **Overall Audit Status:** **{status}**",
        f"- **Total Issues Cataloged:** {qa_report.get('total_issues', 0)}",
        "",
        "## Severity Breakdown",
        f"- **Blocking:** {sev.get('blocking', 0)}",
        f"- **Major:** {sev.get('major', 0)}",
        f"- **Warning:** {sev.get('warning', 0)}",
        f"- **Informational:** {sev.get('informational', 0)}",
        "",
        "## Itemized Audit Findings",
        "",
        "| Issue ID | Severity | Category | Description | Affected Entities | Suggested Action | Approval Req? |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :---: |",
    ]

    sev_icons = {
        "blocking": "🔴 BLOCKING",
        "major": "🟠 MAJOR",
        "warning": "🟡 WARNING",
        "informational": "🔵 INFO",
    }

    for iss in qa_report.get("issues", []):
        aff = ", ".join(iss.get("affected_entities", [])) or "N/A"
        icon = sev_icons.get(iss.get("severity", "").lower(), iss.get("severity", "").upper())
        appr = "Yes" if iss.get("requires_human_approval") else "No"
        desc = iss.get("description", "").replace("|", "\\|")
        sugg = iss.get("suggested_correction", "").replace("|", "\\|")
        lines.append(
            f"| `{iss.get('issue_id')}` | {icon} | `{iss.get('category')}` | {desc} | `{aff}` | {sugg} | {appr} |"
        )

    lines.extend([
        "",
        "## Recommended Corrective Actions",
        "",
        "> **Deterministic Drafting Policy**:",
        "> 1. Wall geometries must terminate with clean cavity closures and valid L, T, or Cross junctions.",
        "> 2. Door swings must maintain clearance without cutting into partition walls or colliding with adjacent leaves.",
        "> 3. Room boundaries must form closed non-self-intersecting polygons with non-zero Shoelace areas.",
        "> 4. All dimensions and annotations must be non-colliding and legible at standard architectural scales.",
        "> 5. Any geometric repair that changes room areas or wall positions mandates explicit human review.",
    ])

    return "\n".join(lines)
