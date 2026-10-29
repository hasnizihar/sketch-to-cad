"""
Approval Package and Human Review Gate for Sketch-to-CAD.

Creates structured human review packages and enforces revision-aware approval
governance without requiring a graphical user interface. AI agents are strictly
prohibited from self-approving their own proposals.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import jsonschema
except ImportError:
    jsonschema = None


# Schema paths
SCHEMA_DIR = Path(__file__).resolve().parent.parent / "skills" / "sketch-to-cad" / "schemas"
APPROVAL_SCHEMA_PATH = SCHEMA_DIR / "approval-package.schema.json"


# Disallowed self-approval identities
DISALLOWED_AGENT_IDENTITIES = {
    "agent",
    "antigravity",
    "ai",
    "assistant",
    "system",
    "llm",
    "bot",
    "auto",
    "self",
    "automated",
    "sketch-to-cad",
}


def get_approval_package_schema() -> Dict[str, Any]:
    """Load the approval-package JSON schema."""
    if not APPROVAL_SCHEMA_PATH.is_file():
        raise FileNotFoundError(f"Approval package schema not found at {APPROVAL_SCHEMA_PATH}")
    with open(APPROVAL_SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_geometry_hash(model: Dict[str, Any]) -> str:
    """
    Calculate a deterministic SHA-256 revision hash of the model's geometry.
    
    Any material change to envelope, walls, openings, rooms, stairs, columns,
    furnishings, or levels changes this hash and invalidates prior approvals.
    """
    def _clean_geom(obj: Any) -> Any:
        if isinstance(obj, dict):
            # Only keep structural geometric properties
            keys = [
                "envelope", "walls", "openings", "rooms", "dimensions",
                "staircases", "columns", "elements", "finishes", "levels",
                "width", "depth", "start", "end", "thickness", "type",
                "wallId", "center", "swing", "id", "name", "p1", "p2", "at",
                "levelId", "levelNumber", "elevation_mm", "height_mm"
            ]
            return {k: _clean_geom(v) for k, v in sorted(obj.items()) if k in keys}
        elif isinstance(obj, list):
            return [_clean_geom(elem) for elem in obj]
        elif isinstance(obj, float):
            return round(obj, 2)
        return obj

    geom_subset = {
        "envelope": _clean_geom(model.get("envelope", {})),
        "walls": _clean_geom(model.get("walls", [])),
        "openings": _clean_geom(model.get("openings", [])),
        "rooms": _clean_geom(model.get("rooms", [])),
        "dimensions": _clean_geom(model.get("dimensions", [])),
        "staircases": _clean_geom(model.get("staircases", [])),
        "columns": _clean_geom(model.get("columns", [])),
        "elements": _clean_geom(model.get("elements", [])),
        "levels": _clean_geom(model.get("levels", [])),
    }

    canonical_json = json.dumps(geom_subset, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def generate_proposal_markdown(package: Dict[str, Any]) -> str:
    """Generate a clean, professional human-readable Markdown proposal for review."""
    summary = package["draft_model_summary"]
    env = summary["envelope"]
    proj = package["project_name"]
    rev = package["revision_hash"][:12]
    sketch = package["source_sketch"]

    lines = [
        f"# Architectural Floor Plan Proposal: {proj}",
        "",
        f"> **Model Revision:** `{rev}` | **Status:** `{package['status'].upper()}` | **Source:** `{sketch.get('source_file', 'unknown')}`",
        "",
        "## 1. Footprint & Envelope Summary",
        "",
        f"- **Overall Width:** {env.get('width_mm', 0):.0f} mm",
        f"- **Overall Depth:** {env.get('depth_mm', 0):.0f} mm",
        f"- **Gross Footprint Area:** {(env.get('width_mm', 0) * env.get('depth_mm', 0)) / 1_000_000:.2f} m²",
        f"- **Levels Count:** {summary.get('levels_count', 1)}",
        f"- **Total Rooms:** {summary.get('rooms_count', 0)}",
        f"- **Total Walls:** {summary.get('walls_count', 0)} ({summary.get('walls_count', 0)} segments)",
        f"- **Total Openings:** {summary.get('openings_count', 0)} doors & windows",
        "",
        "## 2. Extracted Dimensions & Provenance",
        "",
        "| Dimension ID | Source Text | Value (mm) | Category | Target |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for d in package.get("extracted_dimensions", []):
        lines.append(
            f"| `{d['id']}` | `{d['source_text']}` | {d['value_mm']:.0f} mm | `{d['category']}` | {d.get('target_description', '-')} |"
        )

    lines.extend([
        "",
        "## 3. Detected Conflicts & Critical Uncertainties",
        "",
    ])

    conflicts = package.get("detected_conflicts", [])
    if conflicts:
        for c in conflicts:
            sev_badge = "🔴 **BLOCKER**" if c["severity"] == "blocker" else "🟡 **WARNING**"
            lines.append(f"- {sev_badge}: {c['description']} *(Type: `{c['conflict_type']}`)*")
    else:
        lines.append("✅ No geometric or arithmetic conflicts detected.")

    lines.extend([
        "",
        "## 4. Unannotated Information & Defaults",
        "",
    ])

    unknowns = package.get("unknowns", [])
    if unknowns:
        for u in unknowns:
            lines.append(f"- `{u['field']}`: {u['description']} *(Default: `{u.get('default_if_approved', 'Standard')}`)*")
    else:
        lines.append("✅ All required architectural dimensions and parameters are fully defined.")

    lines.extend([
        "",
        "## 5. Required Approval Actions",
        "",
    ])

    actions = package.get("approval_actions_required", [])
    for idx, act in enumerate(actions, start=1):
        lines.append(f"### Action {idx}: {act['question']}")
        lines.append(f"- **Options:** {', '.join(act['options'])}")
        lines.append(f"- **Current Status:** `{act.get('status', 'pending')}`")
        if act.get("resolved_choice"):
            lines.append(f"- **Resolved As:** `{act['resolved_choice']}`")
        lines.append("")

    lines.extend([
        "---",
        "",
        "### How to Approve or Correct (Headless Protocol)",
        "",
        "To approve this proposal, execute the approval command with a human reviewer name:",
        "```json",
        "{\"reviewer_name\": \"Jane Doe, Architect\", \"action\": \"approve\", \"details\": {\"notes\": \"Approved as drafted.\"}}",
        "```",
        "*Note: AI agents cannot self-approve. CAD generation will halt until valid human approval is recorded.*",
    ])

    return "\n".join(lines)


def create_approval_package(
    draft_model: Dict[str, Any],
    observations: Optional[Dict[str, Any]] = None,
    project_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Construct a structured approval package and Markdown proposal for human review.
    
    Calculates the exact SHA-256 geometry hash.
    Validates output against approval-package.schema.json.
    """
    proj_name = project_name or draft_model.get("metadata", {}).get("projectName", "Residential Floor Plan")
    rev_hash = calculate_geometry_hash(draft_model)

    env = draft_model.get("envelope", {})
    walls = draft_model.get("walls", [])
    openings = draft_model.get("openings", [])
    rooms = draft_model.get("rooms", [])
    dims = draft_model.get("dimensions", [])
    uncs = draft_model.get("uncertainties", [])

    src_sketch_info = {
        "source_file": "unknown.png",
        "file_type": "png",
        "page_number": 1,
        "dimensions_pixels": None,
    }
    if observations and "source_metadata" in observations:
        sm = observations["source_metadata"]
        src_sketch_info = {
            "source_file": sm.get("source_file", "unknown"),
            "file_type": sm.get("file_type", "png"),
            "page_number": sm.get("page_number", 1),
            "dimensions_pixels": sm.get("dimensions_pixels"),
        }

    # Extract dimensions summary
    extracted_dims: List[Dict[str, Any]] = []
    if observations and "dimensions" in observations:
        for d in observations["dimensions"]:
            extracted_dims.append({
                "id": d["id"],
                "source_text": d.get("source_text", f"{d.get('value_mm', 0)} mm"),
                "value_mm": float(d.get("value_mm", 0)),
                "category": d.get("category", "explicit"),
                "target_description": d.get("target_entity_type", "architectural_dimension"),
            })
    else:
        for d in dims:
            p1 = d.get("p1", [0, 0])
            p2 = d.get("p2", [0, 0])
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            extracted_dims.append({
                "id": d.get("id", "dim"),
                "source_text": f"{dist:.0f} mm",
                "value_mm": round(dist, 1),
                "category": d.get("source", "explicit"),
                "target_description": "model_dimension",
            })

    # Conflicts
    detected_conflicts: List[Dict[str, Any]] = []
    unknowns: List[Dict[str, Any]] = []
    suggested_corrections: List[Dict[str, Any]] = []
    actions_required: List[Dict[str, Any]] = []

    for u in uncs:
        target = u.get("target", "parameter")
        desc = u.get("description", "")
        if "conflict" in desc.lower() or "contradict" in desc.lower() or "exceeds" in desc.lower():
            detected_conflicts.append({
                "id": f"conflict-{len(detected_conflicts)+1}",
                "conflict_type": "arithmetic_mismatch",
                "severity": "blocker",
                "description": desc,
                "involved_elements": [target],
            })
            actions_required.append({
                "action_id": f"act-resolve-{len(actions_required)+1}",
                "question": f"Conflict detected on '{target}': {desc}. Which value should be prioritized?",
                "options": ["Prioritize overall building envelope", "Prioritize room dimensions chain", "Input custom dimension"],
                "status": "pending",
                "resolved_choice": None,
            })
        elif "missing" in desc.lower() or "not annotated" in desc.lower() or "estimated" in desc.lower():
            unknowns.append({
                "id": f"unk-{len(unknowns)+1}",
                "field": target,
                "description": desc,
                "default_if_approved": "Standard Residential Practice",
            })

    # If no blockers, standard approval action
    if not actions_required:
        actions_required.append({
            "action_id": "act-approve-proposal",
            "question": f"Approve floor plan layout ({env.get('width', 0):.0f} x {env.get('depth', 0):.0f} mm, {len(rooms)} rooms) for CAD generation?",
            "options": ["Approve without changes", "Reject proposal", "Request specific dimension changes"],
            "status": "pending",
            "resolved_choice": None,
        })

    package: Dict[str, Any] = {
        "package_id": f"AP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        "project_name": proj_name,
        "revision_hash": rev_hash,
        "status": "awaiting_approval",
        "source_sketch": src_sketch_info,
        "draft_model_summary": {
            "envelope": {
                "width_mm": float(env.get("width", 8000.0)),
                "depth_mm": float(env.get("depth", 8700.0)),
            },
            "levels_count": len(draft_model.get("levels", [])) or 1,
            "rooms_count": len(rooms),
            "walls_count": len(walls),
            "openings_count": len(openings),
            "staircases_count": len(draft_model.get("staircases", [])),
            "columns_count": len(draft_model.get("columns", [])),
            "furnishings_count": len(draft_model.get("elements", [])),
        },
        "extracted_dimensions": extracted_dims,
        "detected_conflicts": detected_conflicts,
        "unknowns": unknowns,
        "suggested_corrections": suggested_corrections,
        "approval_actions_required": actions_required,
        "decisions_log": [],
    }

    # Validate against schema
    if jsonschema is not None:
        schema = get_approval_package_schema()
        validator = jsonschema.Draft7Validator(schema)
        errors = [e.message for e in validator.iter_errors(package)]
        if errors:
            raise ValueError(f"Approval package schema validation error: {errors}")

    return package


def apply_review_decision(
    approval_package: Dict[str, Any],
    draft_model: Dict[str, Any],
    decision: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Apply a human review decision to an approval package and draft model.
    
    Enforces:
    1. AI agents cannot self-approve.
    2. Model geometry hash must match the approved package hash.
    3. Any geometry changes invalidate prior approval.
    """
    reviewer_name = str(decision.get("reviewer_name", "")).strip()
    action = str(decision.get("action", "")).strip().lower()
    details = decision.get("details", {})

    if not reviewer_name:
        raise ValueError("Missing reviewer_name: A verified reviewer identity is required.")

    # Prevent agent self-approval
    clean_name = reviewer_name.lower().replace(" ", "")
    for disallowed in DISALLOWED_AGENT_IDENTITIES:
        if disallowed in clean_name:
            raise PermissionError(
                f"Self-approval rejected: Reviewer identity '{reviewer_name}' appears to be an automated agent or AI. "
                "The approval gate strictly mandates human review before CAD generation."
            )

    # Verify geometry revision hash
    current_hash = calculate_geometry_hash(draft_model)
    expected_hash = approval_package.get("revision_hash")

    if current_hash != expected_hash:
        approval_package["status"] = "invalidated_by_revision"
        draft_model["status"] = "rejected"
        raise ValueError(
            f"Approval invalidated: Model geometry has been altered (hash {current_hash[:12]}) "
            f"since approval package was generated (hash {expected_hash[:12]}). A new approval package must be reviewed."
        )

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if action == "reject":
        approval_package["status"] = "rejected"
        draft_model["status"] = "rejected"
        approval_package["decisions_log"].append({
            "timestamp": timestamp,
            "reviewer_name": reviewer_name,
            "action": "reject",
            "details": details,
        })
        return approval_package, draft_model

    elif action == "correct_dimension":
        target_id = details.get("target_id")
        new_value = float(details.get("new_value_mm", 0))
        if new_value <= 0:
            raise ValueError(f"Invalid dimension value: {new_value}")

        # Update dimension in model
        updated = False
        for d in draft_model.get("dimensions", []):
            if d.get("id") == target_id:
                # Update dimension
                p1 = d.get("p1", [0, 0])
                d["p2"] = [p1[0] + new_value, p1[1]]
                d["source"] = "explicit"
                updated = True
                break

        if not updated:
            # Update envelope width or depth
            if target_id == "overall_width" or target_id == "DIM-OVERALL-WIDTH":
                draft_model["envelope"]["width"] = new_value
                draft_model["envelope"]["widthSource"] = "explicit"
                updated = True
            elif target_id == "overall_depth" or target_id == "DIM-OVERALL-DEPTH":
                draft_model["envelope"]["depth"] = new_value
                draft_model["envelope"]["depthSource"] = "explicit"
                updated = True

        # Recalculate revision hash after modification
        new_rev = calculate_geometry_hash(draft_model)
        approval_package["revision_hash"] = new_rev
        approval_package["status"] = "awaiting_approval"  # Requires renewal of approval
        approval_package["decisions_log"].append({
            "timestamp": timestamp,
            "reviewer_name": reviewer_name,
            "action": "correct_dimension",
            "details": details,
        })
        return approval_package, draft_model

    elif action == "correct_room_label":
        room_id = details.get("room_id")
        new_label = str(details.get("new_label", "")).strip()
        for r in draft_model.get("rooms", []):
            if r.get("id") == room_id:
                r["name"] = new_label
                break
        new_rev = calculate_geometry_hash(draft_model)
        approval_package["revision_hash"] = new_rev
        approval_package["decisions_log"].append({
            "timestamp": timestamp,
            "reviewer_name": reviewer_name,
            "action": "correct_room_label",
            "details": details,
        })
        return approval_package, draft_model

    elif action == "approve":
        # Check if there are unresolved blockers
        blockers = [c for c in approval_package.get("detected_conflicts", []) if c.get("severity") == "blocker"]
        if blockers and not details.get("override_blockers", False):
            raise ValueError(
                f"Cannot approve proposal with {len(blockers)} unresolved blocker conflict(s): "
                f"{[b['description'] for b in blockers]}. Blockers must be resolved or explicitly overridden."
            )

        approval_package["status"] = "approved"
        draft_model["status"] = "approved"

        approval_package["approval_metadata"] = {
            "approved_by": reviewer_name,
            "approval_timestamp": timestamp,
            "approved_revision_hash": current_hash,
            "notes": str(details.get("notes", "Approved for drafting")),
        }

        # Mark actions as resolved
        for act in approval_package.get("approval_actions_required", []):
            act["status"] = "resolved"
            act["resolved_choice"] = "Approved by human reviewer"

        approval_package["decisions_log"].append({
            "timestamp": timestamp,
            "reviewer_name": reviewer_name,
            "action": "approve",
            "details": details,
        })
        return approval_package, draft_model

    else:
        raise ValueError(f"Unknown review action '{action}'. Supported: approve, reject, correct_dimension, correct_room_label.")
