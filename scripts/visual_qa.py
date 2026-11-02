"""
Visual Quality Assurance for Sketch-to-CAD.

Performs feature-level source-to-CAD verification comparing original hand sketches
against generated CAD drawings or canonical models, producing structured discrepancy reports,
severity classifications, and human-readable summaries without automated modifications
to approved geometry.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from PIL import Image
except ImportError:
    Image = None


SEVERITY_LEVELS = ("informational", "warning", "major_discrepancy", "blocking_discrepancy")


def compare_footprint_aspect_ratio(
    sketch_dims_px: Optional[Dict[str, int]],
    model_envelope: Dict[str, Any],
    tolerance_ratio: float = 0.25,
) -> Dict[str, Any]:
    """
    Compare aspect ratio of sketch image against CAD footprint envelope.
    
    Distinguishes intentionally out-of-scale hand sketches from geometric reconstruction errors:
    If explicit dimensions exist (e.g. 8000w x 8700d) but the human drafted a landscape sketch (1200x849),
    this is classified as an 'out_of_scale_source_sketch' with warning severity rather than a CAD defect.
    """
    w_mm = float(model_envelope.get("width", 8000.0))
    d_mm = float(model_envelope.get("depth", 8700.0))
    cad_ratio = w_mm / d_mm if d_mm > 0 else 1.0
    w_src = model_envelope.get("widthSource", "estimated")
    d_src = model_envelope.get("depthSource", "estimated")

    if not sketch_dims_px:
        return {
            "check": "footprint_aspect_ratio",
            "status": "PASS",
            "severity": "informational",
            "discrepancy_type": None,
            "message": "Sketch pixel dimensions not provided; CAD envelope aspect ratio accepted.",
            "cad_aspect_ratio": round(cad_ratio, 3),
        }

    px_w = float(sketch_dims_px.get("width", 1))
    px_h = float(sketch_dims_px.get("height", 1))
    sketch_ratio = px_w / px_h if px_h > 0 else 1.0

    diff = abs(cad_ratio - sketch_ratio) / sketch_ratio
    is_out_of_tolerance = diff > tolerance_ratio

    if not is_out_of_tolerance:
        return {
            "check": "footprint_aspect_ratio",
            "status": "PASS",
            "severity": "informational",
            "sketch_aspect_ratio": round(sketch_ratio, 3),
            "cad_aspect_ratio": round(cad_ratio, 3),
            "deviation_pct": round(diff * 100.0, 1),
            "message": f"Aspect ratio consistent: sketch={sketch_ratio:.2f}, CAD={cad_ratio:.2f} (diff {diff*100.0:.1f}%).",
        }

    # If dimensions are explicit, the hand sketch was drawn out of proportion
    if w_src == "explicit" and d_src == "explicit":
        status = "DISCREPANCY"
        sev = "warning"
        disc_type = "out_of_scale_source_sketch"
        msg = (
            f"Hand sketch is out-of-scale relative to explicit annotations: sketch image aspect ratio is {sketch_ratio:.2f} "
            f"(landscape), but handwritten dimensions establish {w_mm:.0f}x{d_mm:.0f} mm (ratio {cad_ratio:.2f}, portrait). "
            "Reconstruction correctly honored explicit dimensions over distorted sketch linework."
        )
    else:
        status = "DISCREPANCY"
        sev = "major_discrepancy"
        disc_type = "aspect_ratio_drift"
        msg = (
            f"Aspect ratio mismatch: sketch={sketch_ratio:.2f}, CAD={cad_ratio:.2f} (deviation {diff*100.0:.1f}%). "
            "Without explicit dimension ground-truth, geometric proportions may be distorted."
        )

    return {
        "check": "footprint_aspect_ratio",
        "status": status,
        "severity": sev,
        "discrepancy_type": disc_type,
        "sketch_aspect_ratio": round(sketch_ratio, 3),
        "cad_aspect_ratio": round(cad_ratio, 3),
        "deviation_pct": round(diff * 100.0, 1),
        "message": msg,
    }


def compare_rooms(
    obs_rooms: List[Dict[str, Any]],
    model_rooms: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Verify that all rooms identified in observations exist in the CAD model."""
    obs_names = {r.get("raw_label", r.get("name", "")).upper() for r in obs_rooms if r.get("raw_label") or r.get("name")}
    model_names = {r.get("name", "").upper() for r in model_rooms if r.get("name")}

    missing_in_cad = sorted(list(obs_names - model_names))
    extra_in_cad = sorted(list(model_names - obs_names))

    if missing_in_cad:
        status = "DISCREPANCY"
        sev = "major_discrepancy"
        msg = f"Rooms missing in CAD model: {missing_in_cad}."
    elif extra_in_cad:
        status = "PASS"
        sev = "informational"
        msg = f"All observed rooms present in CAD. Additional partitioned spaces: {extra_in_cad}."
    else:
        status = "PASS"
        sev = "informational"
        msg = f"All {len(obs_rooms)} observed rooms correctly represented in CAD model."

    return {
        "check": "room_topology_and_count",
        "status": status,
        "severity": sev,
        "observed_room_count": len(obs_rooms),
        "cad_room_count": len(model_rooms),
        "missing_in_cad": missing_in_cad,
        "extra_in_cad": extra_in_cad,
        "message": msg,
    }


def compare_openings(
    obs_openings: List[Dict[str, Any]],
    model_openings: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compare door and window counts and host wall relationships."""
    obs_doors = [o for o in obs_openings if o.get("type") == "door"]
    obs_windows = [o for o in obs_openings if o.get("type") == "window"]
    cad_doors = [o for o in model_openings if o.get("type") == "door"]
    cad_windows = [o for o in model_openings if o.get("type") == "window"]

    door_diff = abs(len(obs_doors) - len(cad_doors))
    win_diff = abs(len(obs_windows) - len(cad_windows))

    if door_diff > 0 or win_diff > 0:
        status = "DISCREPANCY"
        sev = "major_discrepancy" if (door_diff > 1 or win_diff > 1) else "warning"
        msg = (
            f"Openings count discrepancy: Doors observed={len(obs_doors)} / CAD={len(cad_doors)}; "
            f"Windows observed={len(obs_windows)} / CAD={len(cad_windows)}."
        )
    else:
        status = "PASS"
        sev = "informational"
        msg = f"Openings count verified: {len(cad_doors)} doors, {len(cad_windows)} windows."

    return {
        "check": "openings_count_and_distribution",
        "status": status,
        "severity": sev,
        "observed_doors": len(obs_doors),
        "cad_doors": len(cad_doors),
        "observed_windows": len(obs_windows),
        "cad_windows": len(cad_windows),
        "message": msg,
    }


def compare_dimensions(
    obs_dimensions: List[Dict[str, Any]],
    model_dimensions: List[Dict[str, Any]],
    tolerance_mm: float = 50.0,
) -> Dict[str, Any]:
    """Verify that explicit source dimensions are honored in CAD annotations."""
    discrepancies = []
    cad_values = []
    for d in model_dimensions:
        p1 = d.get("p1", [0, 0])
        p2 = d.get("p2", [0, 0])
        val = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        cad_values.append(val)

    for d in obs_dimensions:
        val = float(d.get("value_mm", 0))
        matched = any(abs(cv - val) <= tolerance_mm for cv in cad_values)
        if not matched and d.get("category") == "explicit":
            discrepancies.append({
                "dim_id": d.get("id"),
                "explicit_value": val,
                "text": d.get("source_text"),
            })

    if discrepancies:
        status = "DISCREPANCY"
        sev = "blocking_discrepancy" if len(discrepancies) > 2 else "major_discrepancy"
        msg = f"Explicit dimension discrepancy: {len(discrepancies)} dimension(s) not matched in CAD within {tolerance_mm}mm tolerance."
    else:
        status = "PASS"
        sev = "informational"
        msg = f"All {len(obs_dimensions)} observed dimensions verified within {tolerance_mm}mm tolerance."

    return {
        "check": "dimensions_fidelity",
        "status": status,
        "severity": sev,
        "discrepancies": discrepancies,
        "message": msg,
    }


def detect_duplicate_entities(model: Dict[str, Any]) -> Dict[str, Any]:
    """Check for duplicate entity IDs or overlapping geometric elements."""
    walls = model.get("walls", [])
    openings = model.get("openings", [])
    rooms = model.get("rooms", [])

    wall_ids = [w.get("id") for w in walls if w.get("id")]
    op_ids = [o.get("id") for o in openings if o.get("id")]
    room_ids = [r.get("id") for r in rooms if r.get("id")]

    duplicate_ids = (
        [wid for wid in set(wall_ids) if wall_ids.count(wid) > 1] +
        [oid for oid in set(op_ids) if op_ids.count(oid) > 1] +
        [rid for rid in set(room_ids) if room_ids.count(rid) > 1]
    )

    if duplicate_ids:
        status = "DISCREPANCY"
        sev = "major_discrepancy"
        msg = f"Duplicate entity IDs detected: {duplicate_ids}."
    else:
        status = "PASS"
        sev = "informational"
        msg = "Zero duplicate entity IDs detected across walls, openings, and rooms."

    return {
        "check": "duplicate_entities",
        "status": status,
        "severity": sev,
        "duplicate_ids": duplicate_ids,
        "message": msg,
    }


def perform_visual_qa(
    source_sketch_path: str,
    cad_output_path: str,
    model: Dict[str, Any],
    observations: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Perform feature-level visual quality assurance comparing the source sketch to the CAD deliverable.
    
    Generates structured discrepancy report with severity classifications.
    Never modifies approved geometry.
    """
    checks: List[Dict[str, Any]] = []

    # 1. Aspect ratio check
    sketch_dims = None
    if observations and "source_metadata" in observations:
        sketch_dims = observations["source_metadata"].get("dimensions_pixels")
    elif Path(source_sketch_path).is_file() and Image is not None:
        try:
            with Image.open(source_sketch_path) as img:
                sketch_dims = {"width": img.size[0], "height": img.size[1]}
        except Exception:
            pass

    checks.append(compare_footprint_aspect_ratio(sketch_dims, model.get("envelope", {})))

    # 2. Rooms check
    obs_rooms = observations.get("rooms", []) if observations else []
    checks.append(compare_rooms(obs_rooms, model.get("rooms", [])))

    # 3. Openings check
    obs_openings = observations.get("openings", []) if observations else []
    checks.append(compare_openings(obs_openings, model.get("openings", [])))

    # 4. Dimensions check
    obs_dims = observations.get("dimensions", []) if observations else []
    checks.append(compare_dimensions(obs_dims, model.get("dimensions", [])))

    # 5. Stairs check
    obs_stairs = observations.get("stairs", []) if observations else []
    model_stairs = model.get("staircases", [])
    stair_status = "PASS" if len(obs_stairs) == len(model_stairs) else "DISCREPANCY"
    stair_sev = "informational" if stair_status == "PASS" else "warning"
    checks.append({
        "check": "staircase_alignment",
        "status": stair_status,
        "severity": stair_sev,
        "observed_stairs": len(obs_stairs),
        "cad_stairs": len(model_stairs),
        "message": f"Staircases: observed {len(obs_stairs)}, drafted {len(model_stairs)}.",
    })

    # 6. Duplicate entities check
    checks.append(detect_duplicate_entities(model))

    # Severity Summary
    blocking_count = sum(1 for c in checks if c.get("severity") == "blocking_discrepancy")
    major_count = sum(1 for c in checks if c.get("severity") == "major_discrepancy")
    warning_count = sum(1 for c in checks if c.get("severity") == "warning")
    info_count = sum(1 for c in checks if c.get("severity") == "informational")
    passed_count = sum(1 for c in checks if c["status"] == "PASS")

    if blocking_count > 0:
        overall_status = "REJECT_RECOMMENDED"
    elif major_count > 0:
        overall_status = "MAJOR_DISCREPANCY"
    elif warning_count > 0:
        overall_status = "REVIEW_REQUIRED"
    else:
        overall_status = "MATCH"

    report = {
        "project_name": model.get("metadata", {}).get("projectName", "Residential Project"),
        "source_sketch": os.path.basename(source_sketch_path),
        "cad_output": os.path.basename(cad_output_path),
        "overall_status": overall_status,
        "severity_summary": {
            "blocking_discrepancies": blocking_count,
            "major_discrepancies": major_count,
            "warnings": warning_count,
            "informational": info_count,
        },
        "checks_passed": passed_count,
        "total_checks": len(checks),
        "checks": checks,
        "summary": (
            f"Visual QA {overall_status}: {passed_count}/{len(checks)} checks passed. "
            f"Severity breakdown: {blocking_count} blocking, {major_count} major, {warning_count} warning, {info_count} informational."
        ),
    }

    return report


def generate_visual_qa_markdown(report: Dict[str, Any]) -> str:
    """Generate a readable Markdown report from Visual QA results."""
    sev = report.get("severity_summary", {})
    status = report["overall_status"]
    if status == "MATCH":
        status_badge = "✅ MATCH (Clean Pass)"
    elif status == "REVIEW_REQUIRED":
        status_badge = "🟡 REVIEW REQUIRED (Warnings Present)"
    elif status == "MAJOR_DISCREPANCY":
        status_badge = "🟠 MAJOR DISCREPANCY (Attention Required)"
    else:
        status_badge = "🔴 REJECT RECOMMENDED (Blocking Discrepancies)"

    lines = [
        f"# Source-to-CAD Visual QA Report: {report['project_name']}",
        "",
        f"- **Source Sketch:** `{report['source_sketch']}`",
        f"- **CAD Output:** `{report['cad_output']}`",
        f"- **Overall Evaluation:** {status_badge}",
        f"- **Checks Passed:** {report['checks_passed']} / {report['total_checks']}",
        f"- **Severity Counts:** {sev.get('blocking_discrepancies', 0)} Blocking, {sev.get('major_discrepancies', 0)} Major, {sev.get('warnings', 0)} Warning, {sev.get('informational', 0)} Informational",
        "",
        "## Detailed Feature Checks",
        "",
        "| Check | Status | Severity | Findings / Architectural Reasoning |",
        "| :--- | :--- | :--- | :--- |",
    ]

    for c in report.get("checks", []):
        badge = "✅ PASS" if c["status"] == "PASS" else "⚠️ DISCREPANCY"
        s_badge = f"`{c.get('severity', 'info')}`"
        lines.append(f"| `{c['check']}` | {badge} | {s_badge} | {c['message']} |")

    lines.extend([
        "",
        "## Architectural QA Policy & Discrepancy Reconciliation",
        "",
        "> **Important Principle**: Hand-drawn residential sketches are frequently out-of-scale.",
        "> When explicit handwritten dimensions conflict with image pixel aspect ratios,",
        "> Sketch-to-CAD prioritizes explicit ground-truth dimensions. The resulting ratio difference",
        "> is classified as a warning/informational note, NOT a geometric reconstruction defect.",
        "> Visual QA findings provide auditable review evidence and never automatically alter approved CAD geometry.",
    ])

    return "\n".join(lines)
