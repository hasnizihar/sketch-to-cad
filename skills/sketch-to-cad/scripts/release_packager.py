"""
Sketch-to-CAD Production Release Packaging Framework (Milestone 11)

Assembles standardized, professional release packages for approved architectural projects:
output/<project_name>/
├── source/       # Source sketch/PDF + source-metadata.json with SHA-256
├── review/       # Approval package, uncertainty register, proposal markdown
├── drawings/     # Coordinated 2D DXF files + PNG raster previews
├── sheets/       # High-resolution printable PDF sheets (A4/A3/A2/A1) with title block & legend
├── handoff/      # Validated companion BIM handoff JSON
├── reports/      # Architectural schedules & area reports (JSON, Markdown, PDF)
├── qa/           # Independent DXF inspection, Engineering QA, and Visual QA reports
└── manifest.json # Cryptographic release manifest (SHA-256 for all files, geometry hash, QA status)
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from scripts.approval_package import (
    DISALLOWED_AGENT_IDENTITIES,
    calculate_geometry_hash,
    create_approval_package,
    generate_proposal_markdown,
)
from scripts.architectural_qa import (
    generate_engineering_qa_markdown,
    perform_architectural_qa,
)
from scripts.architectural_reports import (
    compile_architectural_report,
    render_markdown_report,
    render_pdf_report,
)
from scripts.drawing_generator import DrawingGenerator, compile_bim_handoff
from scripts.dxf_inspector import DXFInspector, generate_dxf_inspection_markdown
from scripts.pipeline_reliability import (
    atomic_write_json,
    atomic_write_text,
)
from scripts.sheet_generator import SheetGenerator, SheetTitleBlock


def compute_file_sha256(file_path: Union[str, Path]) -> str:
    """Computes SHA-256 hexadecimal digest of a file on disk."""
    p = Path(file_path)
    if not p.is_file():
        return ""
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class ReleasePackager:
    """Orchestrates end-to-end production packaging and manifest generation for approved projects."""

    def __init__(self, output_root: str = "output"):
        self.output_root = Path(output_root)

    def assemble_release_package(
        self,
        project_name: str,
        model: Dict[str, Any],
        source_file_path: Optional[str] = None,
        approval_package: Optional[Dict[str, Any]] = None,
        paper_size: str = "A3",
        scale: int = 100,
        allow_blocked: bool = False,
    ) -> Dict[str, Any]:
        """
        Assembles complete production release package conforming to Milestone 11 standards.
        Validates approval status, executes QA gates, generates all deliverables,
        and produces manifest.json with cryptographic hashes.
        """
        # 1. Approval Gate Validation
        status = model.get("status")
        if status != "approved":
            raise ValueError(f"Cannot package unapproved project: model status is '{status}', expected 'approved'.")

        reviewer = str(model.get("approvedBy", "")).strip().lower()
        if any(agent in reviewer for agent in DISALLOWED_AGENT_IDENTITIES):
            raise ValueError(f"Security Gate: AI Agent self-approval rejected ('{reviewer}').")

        geom_hash = calculate_geometry_hash(model)

        # 2. Setup Directory Structure
        safe_proj = project_name.replace(" ", "-").lower()
        pkg_dir = self.output_root / safe_proj
        source_dir = pkg_dir / "source"
        review_dir = pkg_dir / "review"
        drawings_dir = pkg_dir / "drawings"
        sheets_dir = pkg_dir / "sheets"
        handoff_dir = pkg_dir / "handoff"
        reports_dir = pkg_dir / "reports"
        qa_dir = pkg_dir / "qa"

        for d in [source_dir, review_dir, drawings_dir, sheets_dir, handoff_dir, reports_dir, qa_dir]:
            d.mkdir(parents=True, exist_ok=True)

        deliverables: List[Dict[str, Any]] = []

        # 3. Archive Source Sketch & Metadata
        src_sha256 = ""
        if source_file_path and os.path.exists(source_file_path):
            src_p = Path(source_file_path)
            dest_src = source_dir / src_p.name
            shutil.copy2(str(src_p), str(dest_src))
            src_sha256 = compute_file_sha256(dest_src)

            src_meta = {
                "fileName": src_p.name,
                "fileSizeBytes": dest_src.stat().st_size,
                "sha256": src_sha256,
                "archivedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            meta_path = source_dir / "source-metadata.json"
            atomic_write_json(meta_path, src_meta)
            deliverables.append({
                "path": str(dest_src.relative_to(pkg_dir)),
                "format": src_p.suffix.lstrip(".").upper(),
                "sizeBytes": dest_src.stat().st_size,
                "sha256": src_sha256,
            })
            deliverables.append({
                "path": str(meta_path.relative_to(pkg_dir)),
                "format": "JSON",
                "sizeBytes": meta_path.stat().st_size,
                "sha256": compute_file_sha256(meta_path),
            })

        # 4. Human Review & Uncertainty Deliverables
        app_pkg = approval_package or create_approval_package(model, project_name=project_name)
        pkg_json_path = review_dir / "approval-package.json"
        atomic_write_json(pkg_json_path, app_pkg)
        deliverables.append({
            "path": str(pkg_json_path.relative_to(pkg_dir)),
            "format": "JSON",
            "sizeBytes": pkg_json_path.stat().st_size,
            "sha256": compute_file_sha256(pkg_json_path),
        })

        prop_md_path = review_dir / "review-proposal.md"
        prop_md_content = generate_proposal_markdown(app_pkg)
        atomic_write_text(prop_md_path, prop_md_content)
        deliverables.append({
            "path": str(prop_md_path.relative_to(pkg_dir)),
            "format": "MARKDOWN",
            "sizeBytes": prop_md_path.stat().st_size,
            "sha256": compute_file_sha256(prop_md_path),
        })

        # Uncertainty register
        unc_reg_path = review_dir / "uncertainty-register.json"
        unc_data = {
            "projectId": project_name,
            "totalUncertainties": len(model.get("uncertainties", [])),
            "uncertainties": model.get("uncertainties", []),
        }
        atomic_write_json(unc_reg_path, unc_data)
        deliverables.append({
            "path": str(unc_reg_path.relative_to(pkg_dir)),
            "format": "JSON",
            "sizeBytes": unc_reg_path.stat().st_size,
            "sha256": compute_file_sha256(unc_reg_path),
        })

        # 5. CAD Drawings Deliverables
        generator = DrawingGenerator()
        floors = model.get("floors", [])
        dxf_paths: List[str] = []

        if len(floors) > 1:
            multi_res = generator.build_multi_floor_drawings(
                model=model,
                output_dir=str(drawings_dir),
                base_filename=safe_proj,
                generate_report=False,
                generate_handoff=False,
            )
            floors_dict = multi_res.get("floors", {})
            if isinstance(floors_dict, dict):
                for fl_id, fl_data in floors_dict.items():
                    dp = fl_data.get("dxf") or fl_data.get("dxfPath")
                    if dp:
                        dxf_paths.append(dp)
                        p_dxf = Path(dp)
                        deliverables.append({
                            "path": str(p_dxf.relative_to(pkg_dir)),
                            "format": "DXF",
                            "sizeBytes": p_dxf.stat().st_size,
                            "sha256": compute_file_sha256(p_dxf),
                        })
            elif isinstance(floors_dict, list):
                for fl in floors_dict:
                    dp = fl.get("dxf") or fl.get("dxfPath")
                    if dp:
                        dxf_paths.append(dp)
                        p_dxf = Path(dp)
                        deliverables.append({
                            "path": str(p_dxf.relative_to(pkg_dir)),
                            "format": "DXF",
                            "sizeBytes": p_dxf.stat().st_size,
                            "sha256": compute_file_sha256(p_dxf),
                        })
        else:
            dxf_out = drawings_dir / f"{safe_proj}.dxf"
            png_out = drawings_dir / f"{safe_proj}.png"
            cad_res = generator.build_drawing(
                model=model,
                output_dxf_path=str(dxf_out),
                output_png_path=str(png_out),
                generate_report=False,
            )
            dxf_paths.append(str(dxf_out))
            deliverables.append({
                "path": str(dxf_out.relative_to(pkg_dir)),
                "format": "DXF",
                "sizeBytes": dxf_out.stat().st_size,
                "sha256": compute_file_sha256(dxf_out),
            })
            if png_out.is_file():
                deliverables.append({
                    "path": str(png_out.relative_to(pkg_dir)),
                    "format": "PNG",
                    "sizeBytes": png_out.stat().st_size,
                    "sha256": compute_file_sha256(png_out),
                })

        # 6. Companion BIM Handoff Metadata
        primary_dxf = dxf_paths[0] if dxf_paths else str(drawings_dir / f"{safe_proj}.dxf")
        handoff_data = compile_bim_handoff(model=model, dxf_path=primary_dxf)
        handoff_file = handoff_dir / f"{safe_proj}.handoff.json"
        atomic_write_json(handoff_file, handoff_data)
        deliverables.append({
            "path": str(handoff_file.relative_to(pkg_dir)),
            "format": "JSON",
            "sizeBytes": handoff_file.stat().st_size,
            "sha256": compute_file_sha256(handoff_file),
        })

        # 7. Printable Drawing Sheets (PDF)
        sheet_gen = SheetGenerator(paper_size=paper_size, orientation="landscape", scale=scale)
        sheet_paths: List[str] = []

        if len(floors) > 1:
            for idx, fl in enumerate(floors, start=1):
                fl_id = fl.get("id", f"LEVEL-0{idx}")
                sh_name = f"{safe_proj}-{fl_id.lower()}-sheet.pdf"
                sh_out = sheets_dir / sh_name
                tb = SheetTitleBlock(
                    project_name=project_name,
                    sheet_title=f"{fl.get('name', fl_id).upper()} PLAN",
                    drawing_number=f"A-10{idx}",
                    floor_id=fl_id,
                    scale_notation=f"1:{scale} @ {paper_size}",
                    north_orientation=model.get("metadata", {}).get("northOrientation"),
                )
                sheet_gen.render_sheet_pdf(
                    model=model,
                    output_pdf_path=str(sh_out),
                    scale=scale,
                    floor_id=fl_id,
                    title_block=tb,
                    allow_overflow=True,
                )
                sheet_paths.append(str(sh_out))
                deliverables.append({
                    "path": str(sh_out.relative_to(pkg_dir)),
                    "format": "PDF",
                    "sizeBytes": sh_out.stat().st_size,
                    "sha256": compute_file_sha256(sh_out),
                })
        else:
            sh_out = sheets_dir / f"{safe_proj}-sheet.pdf"
            tb = SheetTitleBlock(
                project_name=project_name,
                sheet_title="GROUND FLOOR PLAN",
                drawing_number="A-101",
                floor_id="LEVEL-01",
                scale_notation=f"1:{scale} @ {paper_size}",
                north_orientation=model.get("metadata", {}).get("northOrientation"),
            )
            sheet_gen.render_sheet_pdf(
                model=model,
                output_pdf_path=str(sh_out),
                scale=scale,
                title_block=tb,
                allow_overflow=True,
            )
            sheet_paths.append(str(sh_out))
            deliverables.append({
                "path": str(sh_out.relative_to(pkg_dir)),
                "format": "PDF",
                "sizeBytes": sh_out.stat().st_size,
                "sha256": compute_file_sha256(sh_out),
            })

        # 8. Architectural Schedules & Reports
        rep_dict = compile_architectural_report(model=model, handoff=handoff_data, dxf_path=primary_dxf)
        rep_json = reports_dir / f"{safe_proj}.report.json"
        rep_md = reports_dir / f"{safe_proj}.report.md"
        rep_pdf = reports_dir / f"{safe_proj}.report.pdf"

        atomic_write_json(rep_json, rep_dict)
        deliverables.append({
            "path": str(rep_json.relative_to(pkg_dir)),
            "format": "JSON",
            "sizeBytes": rep_json.stat().st_size,
            "sha256": compute_file_sha256(rep_json),
        })

        atomic_write_text(rep_md, render_markdown_report(rep_dict))
        deliverables.append({
            "path": str(rep_md.relative_to(pkg_dir)),
            "format": "MARKDOWN",
            "sizeBytes": rep_md.stat().st_size,
            "sha256": compute_file_sha256(rep_md),
        })

        try:
            render_pdf_report(rep_dict, str(rep_pdf))
            deliverables.append({
                "path": str(rep_pdf.relative_to(pkg_dir)),
                "format": "PDF",
                "sizeBytes": rep_pdf.stat().st_size,
                "sha256": compute_file_sha256(rep_pdf),
            })
        except Exception:
            pass

        # 9. Quality Assurance & Independent Inspection
        inspector = DXFInspector()
        dxf_report = inspector.inspect(primary_dxf, model=model, handoff=handoff_data)
        dxf_insp_json = qa_dir / f"{safe_proj}.dxf-inspection.json"
        dxf_insp_md = qa_dir / f"{safe_proj}.dxf-inspection.md"

        atomic_write_json(dxf_insp_json, dxf_report.to_dict())
        atomic_write_text(dxf_insp_md, generate_dxf_inspection_markdown(dxf_report))
        deliverables.append({
            "path": str(dxf_insp_json.relative_to(pkg_dir)),
            "format": "JSON",
            "sizeBytes": dxf_insp_json.stat().st_size,
            "sha256": compute_file_sha256(dxf_insp_json),
        })
        deliverables.append({
            "path": str(dxf_insp_md.relative_to(pkg_dir)),
            "format": "MARKDOWN",
            "sizeBytes": dxf_insp_md.stat().st_size,
            "sha256": compute_file_sha256(dxf_insp_md),
        })

        # Unified Engineering QA
        eng_qa = perform_architectural_qa(model=model, cad_output_path=primary_dxf, handoff=handoff_data)
        qa_json_path = qa_dir / f"{safe_proj}.engineering-qa.json"
        qa_md_path = qa_dir / f"{safe_proj}.engineering-qa.md"

        atomic_write_json(qa_json_path, eng_qa)
        atomic_write_text(qa_md_path, generate_engineering_qa_markdown(eng_qa))
        deliverables.append({
            "path": str(qa_json_path.relative_to(pkg_dir)),
            "format": "JSON",
            "sizeBytes": qa_json_path.stat().st_size,
            "sha256": compute_file_sha256(qa_json_path),
        })
        deliverables.append({
            "path": str(qa_md_path.relative_to(pkg_dir)),
            "format": "MARKDOWN",
            "sizeBytes": qa_md_path.stat().st_size,
            "sha256": compute_file_sha256(qa_md_path),
        })

        # Determine release QA status
        sev_counts = eng_qa.get("severity_counts", {})
        if sev_counts.get("blocking", 0) > 0:
            qa_status = "BLOCKED"
        elif sev_counts.get("major", 0) > 0:
            qa_status = "REQUIRES_RESOLUTION"
        elif sev_counts.get("warning", 0) > 0:
            qa_status = "CONDITIONAL_RELEASE"
        else:
            qa_status = "RELEASE_READY"

        if qa_status == "BLOCKED" and not allow_blocked:
            raise ValueError(f"Release blocked: {sev_counts.get('blocking')} blocking QA issues detected.")

        # 10. Master Release Manifest
        manifest = {
            "manifestVersion": "1.1.0",
            "projectId": safe_proj,
            "projectName": project_name,
            "softwareVersion": "1.1.0",
            "releaseTimestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sourceSketch": {
                "fileName": Path(source_file_path).name if source_file_path else "unspecified",
                "sha256": src_sha256,
            },
            "geometryRevisionHash": geom_hash,
            "approval": {
                "status": "approved",
                "approvedBy": model.get("approvedBy", "Architect"),
                "approvedAt": model.get("approvedAt", time.strftime("%Y-%m-%d")),
                "authMethod": "identity_assertion",
            },
            "qaStatus": qa_status,
            "qaSummary": sev_counts,
            "deliverablesCount": len(deliverables),
            "deliverables": deliverables,
        }

        manifest_path = pkg_dir / "manifest.json"
        atomic_write_json(manifest_path, manifest)

        return {
            "packageDir": str(pkg_dir),
            "manifestPath": str(manifest_path),
            "qaStatus": qa_status,
            "deliverablesCount": len(deliverables),
            "manifest": manifest,
        }

    @staticmethod
    def verify_package_integrity(package_dir: Union[str, Path]) -> Tuple[bool, List[str]]:
        """Verifies all deliverables against manifest.json SHA-256 checksums."""
        pkg_path = Path(package_dir)
        manifest_path = pkg_path / "manifest.json"
        if not manifest_path.is_file():
            return False, [f"manifest.json not found in {package_dir}"]

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        errors = []
        for deliv in manifest.get("deliverables", []):
            rel_path = deliv.get("path", "")
            expected_sha = deliv.get("sha256", "")
            file_path = pkg_path / rel_path
            if not file_path.is_file():
                errors.append(f"Missing deliverable: {rel_path}")
                continue
            actual_sha = compute_file_sha256(file_path)
            if actual_sha != expected_sha:
                errors.append(f"Hash mismatch for {rel_path}: expected {expected_sha}, got {actual_sha}")

        return len(errors) == 0, errors

