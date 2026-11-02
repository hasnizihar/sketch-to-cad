"""
Sketch-to-CAD Downstream BIM Integration & Interoperability Validator (Milestone 10)

Validates the architectural and metadata handoff to the downstream `dxf-to-3d-bim` skill:
- Checks downstream environment and CLI availability.
- Performs contract-level schema and semantic checks.
- Executes genuine downstream preflight analysis (`dxf-to-3d-bim inspect`) when installed.
- Executes genuine downstream intermediate BIM reconstruction (`dxf-to-3d-bim prepare`) when installed.
- Verifies comprehensive failure handling (missing files, invalid schema, orphan openings).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

DEFAULT_DOWNSTREAM_PYTHON = r"D:\Agent Skills\DXF to 3D-BIM\.venv\Scripts\python.exe"
DEFAULT_DOWNSTREAM_DIR = r"D:\Agent Skills\DXF to 3D-BIM"


@dataclass
class BIMIntegrationResult:
    dxf_path: str
    handoff_path: Optional[str]
    is_downstream_available: bool
    downstream_execution_type: str  # 'genuine_downstream_cli' or 'contract_validation_only'
    contract_valid: bool
    preflight_passed: bool
    reconstruction_passed: bool
    intermediate_model_path: Optional[str]
    contract_errors: List[str] = field(default_factory=list)
    contract_warnings: List[str] = field(default_factory=list)
    downstream_preflight_summary: Optional[Dict[str, Any]] = None
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BIMIntegrationValidator:
    """Validates interoperability between Sketch-to-CAD outputs and dxf-to-3d-bim."""

    def __init__(self, downstream_python: Optional[str] = None):
        self.downstream_py = downstream_python or DEFAULT_DOWNSTREAM_PYTHON
        self.has_downstream = os.path.exists(self.downstream_py)

    def validate_handoff_contract(
        self,
        dxf_path: str,
        handoff_data: Dict[str, Any],
    ) -> Tuple[bool, List[str], List[str]]:
        """Performs strict semantic checks against downstream requirements."""
        errors: List[str] = []
        warnings: List[str] = []

        # 1. DXF existence and size
        if not os.path.exists(dxf_path):
            errors.append(f"DXF file does not exist at {dxf_path}")
        elif os.path.getsize(dxf_path) < 100:
            errors.append(f"DXF file is degenerate / empty ({os.path.getsize(dxf_path)} bytes)")

        # 2. Coordinate System
        coords = handoff_data.get("project", {}).get("coordinateSystem", "")
        if "Cartesian2D" not in coords:
            errors.append(f"Invalid coordinateSystem '{coords}'. Expected Cartesian2D_RightHanded_YUp.")

        # 3. Units
        units = handoff_data.get("project", {}).get("units", "").lower()
        if units not in ("mm", "millimeters", "m", "meters"):
            errors.append(f"Unsupported units '{units}'. Downstream requires mm or m.")

        # 4. Wall IDs and Referential Integrity
        walls = handoff_data.get("walls", [])
        if not walls:
            errors.append("Handoff contains zero defined walls.")
        wall_ids = set()
        for w in walls:
            wid = w.get("id")
            if not wid:
                errors.append("Wall entry missing required 'id'.")
            elif wid in wall_ids:
                errors.append(f"Duplicate wall id '{wid}' in handoff.")
            wall_ids.add(wid)

        # 5. Openings Host Integrity & Sill Height
        openings = handoff_data.get("openings", [])
        for op in openings:
            op_id = op.get("id", "UNKNOWN")
            wid = op.get("wallId")
            if not wid:
                errors.append(f"Opening '{op_id}' has missing 'wallId'.")
            elif wid not in wall_ids:
                errors.append(f"Opening '{op_id}' references non-existent host wall '{wid}'.")

            op_type = op.get("type", "door")
            if op_type == "window":
                sill = op.get("sillHeight")
                if sill is None:
                    warnings.append(
                        f"Window '{op_id}' has null sillHeight. Downstream BIMCraft requires numeric sill."
                    )

        # 6. Floors
        floors = handoff_data.get("floors", [])
        if not floors:
            warnings.append("No explicit floors array. Downstream will default to single Level 1.")

        return len(errors) == 0, errors, warnings

    def run_integration_pipeline(
        self,
        dxf_path: str,
        handoff_path: Optional[str] = None,
        output_intermediate_path: Optional[str] = None,
    ) -> BIMIntegrationResult:
        """Executes full integration verification against downstream skill."""
        contract_valid = True
        contract_errors: List[str] = []
        contract_warnings: List[str] = []
        handoff_data: Dict[str, Any] = {}

        if handoff_path and os.path.exists(handoff_path):
            with open(handoff_path, "r", encoding="utf-8") as f:
                handoff_data = json.load(f)
            contract_valid, contract_errors, contract_warnings = self.validate_handoff_contract(
                dxf_path, handoff_data
            )
        else:
            if not os.path.exists(dxf_path):
                contract_valid = False
                contract_errors.append(f"DXF file does not exist: {dxf_path}")

        # Check genuine downstream CLI availability
        exec_type = "contract_validation_only"
        preflight_passed = False
        reconstruct_passed = False
        preflight_summary = None
        out_inter = None
        notes = []

        if self.has_downstream and contract_valid and os.path.exists(dxf_path):
            exec_type = "genuine_downstream_cli"
            # 1. Run Preflight Inspection via CLI
            try:
                cmd_inspect = [
                    self.downstream_py, "-m", "dxf_to_3d_bim.cli", "inspect", dxf_path
                ]
                res_inspect = subprocess.run(
                    cmd_inspect,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False
                )
                if res_inspect.returncode == 0:
                    preflight_passed = True
                    preflight_summary = {
                        "status": "PASSED",
                        "raw_output": res_inspect.stdout[:500],
                    }
                else:
                    preflight_passed = False
                    contract_errors.append(f"Downstream preflight inspection failed: {res_inspect.stderr[:200]}")
            except Exception as e:
                contract_errors.append(f"Downstream inspection call error: {str(e)}")

            # 2. Run Intermediate Model Preparation via CLI
            if preflight_passed:
                out_inter = output_intermediate_path or str(
                    Path(dxf_path).parent / f"{Path(dxf_path).stem}_intermediate_bim.json"
                )
                try:
                    cmd_prep = [
                        self.downstream_py, "-m", "dxf_to_3d_bim.cli", "prepare", dxf_path,
                        "--out", out_inter
                    ]
                    if handoff_path and os.path.exists(handoff_path):
                        cmd_prep.extend(["--json", handoff_path])

                    res_prep = subprocess.run(
                        cmd_prep,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        check=False
                    )
                    if res_prep.returncode == 0 and os.path.exists(out_inter):
                        reconstruct_passed = True
                        notes.append(f"Successfully generated downstream intermediate BIM model at {out_inter}")
                    else:
                        reconstruct_passed = False
                        contract_errors.append(f"Downstream prepare failed: {res_prep.stderr or res_prep.stdout}")
                except Exception as e:
                    contract_errors.append(f"Downstream prepare call error: {str(e)}")
        else:
            if not self.has_downstream:
                notes.append("Downstream python environment not detected. Validated contract schemas only.")

        return BIMIntegrationResult(
            dxf_path=dxf_path,
            handoff_path=handoff_path,
            is_downstream_available=self.has_downstream,
            downstream_execution_type=exec_type,
            contract_valid=contract_valid,
            preflight_passed=preflight_passed,
            reconstruction_passed=reconstruct_passed,
            intermediate_model_path=out_inter if reconstruct_passed else None,
            contract_errors=contract_errors,
            contract_warnings=contract_warnings,
            downstream_preflight_summary=preflight_summary,
            notes=notes,
        )


def generate_bim_integration_markdown(result: BIMIntegrationResult) -> str:
    """Renders a comprehensive downstream integration report in Markdown."""
    lines = [
        "# Downstream BIM Integration Validation Report",
        "",
        "## Executive Summary",
        f"- **DXF File:** `{result.dxf_path}`",
        f"- **Handoff JSON:** `{result.handoff_path or 'None'}`",
        f"- **Execution Type:** `{result.downstream_execution_type}`",
        f"- **Downstream Skill Present:** {'Yes' if result.is_downstream_available else 'No'}",
        f"- **Handoff Contract Valid:** {'PASSED' if result.contract_valid else 'FAILED'}",
        f"- **Downstream Preflight Inspection:** {'PASSED' if result.preflight_passed else ('FAILED' if result.is_downstream_available else 'N/A')}",
        f"- **BIM Model Reconstruction:** {'PASSED' if result.reconstruction_passed else ('FAILED' if result.is_downstream_available else 'N/A')}",
        f"- **Generated Intermediate Model:** `{result.intermediate_model_path or 'None'}`",
        "",
    ]

    if result.notes:
        lines.append("## Integration Notes")
        for n in result.notes:
            lines.append(f"- {n}")
        lines.append("")

    if result.contract_warnings:
        lines.append("## Contract Warnings")
        for w in result.contract_warnings:
            lines.append(f"- [WARNING] {w}")
        lines.append("")

    if result.contract_errors:
        lines.append("## Blocking Integration Errors")
        for e in result.contract_errors:
            lines.append(f"- [ERROR] {e}")
        lines.append("")

    return "\n".join(lines)
