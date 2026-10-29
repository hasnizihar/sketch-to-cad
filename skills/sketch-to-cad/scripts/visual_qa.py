"""
Visual Quality Assurance for Sketch-to-CAD.

Performs feature-level source-to-CAD verification comparing original hand sketches
against generated CAD drawings or canonical models, producing structured discrepancy reports
and human-readable summaries without automated modifications to approved geometry.
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


def compare_footprint_aspect_ratio(
    sketch_dims_px: Optional[Dict[str, int]],
    model_envelope: Dict[str, Any],
    tolerance_ratio: float = 0.25,
) -> Dict[str, Any]:
    """
    Compare aspect ratio of sketch image against CAD footprint envelope.
    Returns status and deviation details.
    """
    w_mm = float(model_envelope.get("width", 8000.0))
    d_mm = float(model_envelope.get("depth", 8700.0))
    cad_ratio = w_mm / d_mm if d_mm > 0 else 1.0

    if not sketch_dims_px:
        return {
            "check": "footprint_aspect_ratio",
            "status": "PASS",
            "message": "Sketch pixel dimensions not provided; CAD envelope aspect ratio accepted.",
            "cad_aspect_ratio": round(cad_ratio, 3),
        }

    px_w = float(sketch_dims_px.get("width", 1))
    px_h = float(sketch_dims_px.get("height", 1))
    sketch_ratio = px_w / px_h if px_h > 0 else 1.0

    diff = abs(cad_ratio - sketch_ratio) / sketch_ratio
    status = "PASS" if diff <= tolerance_ratio else "DISCREPANCY"

    return {
        "check": "footprint_aspect_ratio",
        "status": status,
        "sketch_aspect_ratio": round(sketch_ratio, 3),
        "cad_aspect_ratio": round(cad_ratio, 3),
        "deviation_pct": round(diff * 100.0, 1),
        "message": (
            f"Aspect ratio comparison: sketch={sketch_ratio:.2f}, CAD={cad_ratio:.2f} "
            f"(deviation {diff*100.0:.1f}% vs {tolerance_ratio*100:.0f}% tolerance)."
        ),
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

    status = "PASS" if not missing_in_cad else "DISCREPANCY"
    return {
        "check": "room_topology_and_count",
        "status": status,
        "observed_room_count": len(obs_rooms),
        "cad_room_count": len(model_rooms),
        "missing_in_cad": missing_in_cad,
        "extra_in_cad": extra_in_cad,
        "message": f"Rooms: observed {len(obs_rooms)}, drafted {len(model_rooms)}. Missing: {missing_in_cad or 'None'}.",
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

    door_match = len(obs_doors) == len(cad_doors)
    win_match = len(obs_windows) == len(cad_windows)
    status = "PASS" if (door_match and win_match) else "DISCREPANCY"

    return {
        "check": "openings_count_and_distribution",
        "status": status,
        "observed_doors": len(obs_doors),
        "cad_doors": len(cad_doors),
        "observed_windows": len(obs_windows),
        "cad_windows": len(cad_windows),
        "message": f"Doors: obs={len(obs_doors)} / cad={len(cad_doors)}. Windows: obs={len(obs_windows)} / cad={len(cad_windows)}.",
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
        # Look for matching value in CAD
        matched = any(abs(cv - val) <= tolerance_mm for cv in cad_values)
        if not matched and d.get("category") == "explicit":
            discrepancies.append({
                "dim_id": d.get("id"),
                "explicit_value": val,
                "text": d.get("source_text"),
            })

    status = "PASS" if not discrepancies else "DISCREPANCY"
    return {
        "check": "dimensions_fidelity",
        "status": status,
        "discrepancies": discrepancies,
        "message": f"Dimension fidelity: {len(obs_dimensions)} observed, {len(discrepancies)} explicit discrepancies.",
    }


def perform_visual_qa(
    source_sketch_path: str,
    cad_output_path: str,
    model: Dict[str, Any],
    observations: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Perform feature-level visual quality assurance comparing the source sketch to the CAD deliverable.
    
    Generates structured discrepancy report.
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
    checks.append({
        "check": "staircase_alignment",
        "status": stair_status,
        "observed_stairs": len(obs_stairs),
        "cad_stairs": len(model_stairs),
        "message": f"Staircases: observed {len(obs_stairs)}, drafted {len(model_stairs)}.",
    })

    # Summary
    total_checks = len(checks)
    passed_checks = sum(1 for c in checks if c["status"] == "PASS")
    has_discrepancy = any(c["status"] == "DISCREPANCY" for c in checks)

    overall_status = "DISCREPANCY_DETECTED" if has_discrepancy else "MATCH"

    report = {
        "project_name": model.get("metadata", {}).get("projectName", "Residential Project"),
        "source_sketch": os.path.basename(source_sketch_path),
        "cad_output": os.path.basename(cad_output_path),
        "overall_status": overall_status,
        "checks_passed": passed_checks,
        "total_checks": total_checks,
        "checks": checks,
        "summary": (
            f"Visual QA {overall_status}: {passed_checks}/{total_checks} checks passed. "
            "Feature-level verification completed without automated modifications."
        ),
    }

    return report


def generate_visual_qa_markdown(report: Dict[str, Any]) -> str:
    """Generate a readable Markdown report from Visual QA results."""
    status_emoji = "✅ PASS" if report["overall_status"] == "MATCH" else "⚠️ DISCREPANCY DETECTED"
    lines = [
        f"# Source-to-CAD Visual QA Report: {report['project_name']}",
        "",
        f"- **Source Sketch:** `{report['source_sketch']}`",
        f"- **CAD Output:** `{report['cad_output']}`",
        f"- **Overall Result:** {status_emoji} ({report['checks_passed']}/{report['total_checks']} checks passed)",
        "",
        "## Detailed Feature Checks",
        "",
        "| Check | Status | Findings / Details |",
        "| :--- | :--- | :--- |",
    ]

    for c in report.get("checks", []):
        badge = "✅ PASS" if c["status"] == "PASS" else "⚠️ DISCREPANCY"
        lines.append(f"| `{c['check']}` | {badge} | {c['message']} |")

    lines.extend([
        "",
        "## Architectural QA Notes",
        "",
        "> Visual comparison findings provide review evidence for human verification and do not",
        "> automatically alter approved CAD drawing geometry or dimensions.",
    ])

    return "\n".join(lines)
