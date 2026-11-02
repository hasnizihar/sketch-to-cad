"""
End-to-End Sketch-to-CAD Pipeline Orchestrator.

Orchestrates the entire workflow from hand-drawn floor-plan sketch (JPG, PNG, PDF)
to editable 2D CADCraft DXF, BIM handoff JSON, architectural PDF/Markdown reports,
vision execution records, and source-to-CAD visual QA discrepancy reporting,
strictly enforcing the human approval gate.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from scripts.sketch_interpreter import (
    load_sketch_input,
    validate_observations,
    reconstruct_geometry,
    compile_draft_model,
)
from scripts.approval_package import (
    create_approval_package,
    apply_review_decision,
    generate_proposal_markdown,
    verify_approval_integrity,
)
from scripts.drawing_generator import DrawingGenerator, compile_bim_handoff
from scripts.architectural_reports import (
    compile_architectural_report,
    render_markdown_report,
    render_pdf_report,
)
from scripts.visual_qa import perform_visual_qa, generate_visual_qa_markdown
from scripts.vision_config import VisionConfig, resolve_vision_config
from scripts.vision_provider import (
    BaseVisionProvider,
    VisionResult,
    create_vision_provider,
    save_vision_execution_record,
)


class SketchToCADPipeline:
    """End-to-End Orchestrator for Sketch-to-CAD conversion with multimodal vision integration."""

    def __init__(
        self,
        cadcraft_cli: Optional[str] = None,
        vision_provider: Optional[BaseVisionProvider] = None,
        vision_config: Optional[VisionConfig] = None,
    ):
        self.cadcraft_cli = cadcraft_cli
        if cadcraft_cli:
            from scripts.drawing_generator import CADCraftClient
            client = CADCraftClient(cli_path=cadcraft_cli)
            self.generator = DrawingGenerator(client=client)
        else:
            self.generator = DrawingGenerator()

        if vision_provider is not None:
            self.vision_provider = vision_provider
        else:
            cfg = vision_config or resolve_vision_config()
            self.vision_provider = create_vision_provider(cfg)

    def run_pipeline(
        self,
        source_sketch_path: str,
        output_dir: str,
        approval_decision: Optional[Dict[str, Any]] = None,
        observations_override: Optional[Dict[str, Any]] = None,
        project_name: str = "Residential Floor Plan",
        allow_demo_identities: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute the complete Sketch-to-CAD pipeline.
        
        If approval_decision is omitted or None, the pipeline halts at the approval gate
        after creating the approval package and proposal markdown.
        """
        out_p = Path(output_dir)
        out_p.mkdir(parents=True, exist_ok=True)
        slug = project_name.lower().replace(" ", "-").replace("_", "-")

        # Step 1: Input Sketch Inspection & Metadata
        source_meta = load_sketch_input(source_sketch_path)

        # Step 2: Multimodal Vision Interpretation / Observation Extraction
        vision_rec_path = out_p / f"{slug}.vision-execution.json"

        if observations_override is not None:
            observations = observations_override
            vision_result = VisionResult(
                status="success",
                execution_record={
                    "record_id": f"VR-OVERRIDE-{slug}",
                    "execution_type": "manual_override",
                    "provider_name": "manual_override",
                    "model_identifier": "manual_ground_truth",
                    "provider_config_version": "1.0.0",
                    "source_image": {
                        "file_name": source_meta["source_file"],
                        "page_number": source_meta.get("page_number", 1),
                        "total_pages": source_meta.get("total_pages", 1),
                        "sha256": "0" * 64,
                        "dimensions_pixels": source_meta["dimensions_pixels"],
                        "dpi": source_meta.get("dpi", 72.0),
                    },
                    "timestamp": source_meta.get("timestamp", "2026-11-02T00:00:00Z"),
                    "prompt_version": "manual-override-v1",
                    "status": "success",
                    "raw_response_path": None,
                    "parsed_observation_path": None,
                    "validation_result": {"is_valid": True, "error_count": 0, "errors": []},
                    "processing_duration_ms": 0.0,
                    "token_usage": None,
                    "error_details": None,
                },
                observations=observations,
            )
        else:
            # Execute actual vision provider
            vision_result = self.vision_provider.interpret_sketch(
                source_path=source_sketch_path,
                page_number=source_meta.get("page_number", 1),
                source_metadata=source_meta,
            )
            if vision_result.status != "success" or vision_result.observations is None:
                # Save execution record for debugging and audit
                save_vision_execution_record(vision_result.execution_record, str(vision_rec_path))
                return {
                    "status": "vision_extraction_failed",
                    "vision_status": vision_result.status,
                    "error_message": vision_result.error_message,
                    "vision_execution_path": str(vision_rec_path),
                    "execution_record": vision_result.execution_record,
                    "message": f"Multimodal vision extraction failed with status '{vision_result.status}': {vision_result.error_message}",
                }
            observations = vision_result.observations

        # Save structured vision execution record
        save_vision_execution_record(vision_result.execution_record, str(vision_rec_path))

        # Validate structured observations against schema
        is_valid_obs, obs_errors = validate_observations(observations)
        if not is_valid_obs:
            raise ValueError(f"Observations schema validation failed: {obs_errors}")

        # Step 3: Deterministic Geometric Reconstruction
        geom = reconstruct_geometry(observations)

        # Step 4: Compile Draft Canonical Model
        draft_model = compile_draft_model(observations, geom, project_name=project_name)

        # Step 5: Construct Structured Approval Package & Markdown Proposal
        package = create_approval_package(draft_model, observations, project_name=project_name)
        proposal_md = generate_proposal_markdown(package)

        package_path = out_p / f"{slug}.approval.json"
        proposal_path = out_p / f"{slug}.proposal.md"
        with open(package_path, "w", encoding="utf-8") as f:
            json.dump(package, f, indent=2)
        with open(proposal_path, "w", encoding="utf-8") as f:
            f.write(proposal_md)

        # Step 6: Enforce Mandatory Human Approval Gate
        if approval_decision is None:
            return {
                "status": "awaiting_approval",
                "package_path": str(package_path),
                "proposal_path": str(proposal_path),
                "vision_execution_path": str(vision_rec_path),
                "revision_hash": package["revision_hash"],
                "draft_model": draft_model,
                "approval_package": package,
                "message": (
                    f"Draft model compiled with revision hash {package['revision_hash'][:12]}. "
                    "Mandatory human approval is required before CAD generation. Pipeline paused."
                ),
            }

        # Apply approval decision
        package, approved_model = apply_review_decision(
            package,
            draft_model,
            approval_decision,
            allow_demo_identities=allow_demo_identities,
        )

        # Re-save updated package with approval metadata
        with open(package_path, "w", encoding="utf-8") as f:
            json.dump(package, f, indent=2)

        if approved_model.get("status") != "approved":
            return {
                "status": approved_model.get("status", "rejected"),
                "package_path": str(package_path),
                "proposal_path": str(proposal_path),
                "vision_execution_path": str(vision_rec_path),
                "message": f"Proposal review concluded with status '{approved_model.get('status')}'. CAD generation halted.",
            }

        # Step 7: CADCraft Drawing Generation
        dxf_path = str(out_p / f"{slug}.dxf")
        png_path = str(out_p / f"{slug}.png")
        handoff_path = str(out_p / f"{slug}.handoff.json")
        report_base = str(out_p / slug)

        is_multi_storey = "levels" in approved_model and len(approved_model["levels"]) > 1

        if is_multi_storey:
            cad_result = self.generator.build_multi_floor_drawings(
                approved_model,
                output_dir=str(out_p),
                base_filename=slug,
                generate_report=True,
                generate_handoff=True,
            )
            primary_dxf = cad_result["floors"][0]["dxf_path"] if cad_result.get("floors") else dxf_path
        else:
            cad_result = self.generator.build_drawing(
                approved_model,
                output_dxf_path=dxf_path,
                output_png_path=png_path,
                output_handoff_path=handoff_path,
                generate_report=True,
                output_report_base=report_base,
            )
            primary_dxf = dxf_path

        # Step 8: Visual Quality Assurance
        qa_report = perform_visual_qa(
            source_sketch_path=source_sketch_path,
            cad_output_path=primary_dxf,
            model=approved_model,
            observations=observations,
        )
        qa_md = generate_visual_qa_markdown(qa_report)

        qa_json_path = out_p / f"{slug}.visual-qa.json"
        qa_md_path = out_p / f"{slug}.visual-qa.md"
        with open(qa_json_path, "w", encoding="utf-8") as f:
            json.dump(qa_report, f, indent=2)
        with open(qa_md_path, "w", encoding="utf-8") as f:
            f.write(qa_md)

        return {
            "status": "completed",
            "project_name": project_name,
            "revision_hash": package["approval_metadata"]["approved_revision_hash"],
            "approved_by": package["approval_metadata"]["approved_by"],
            "dxf_path": primary_dxf,
            "handoff_path": handoff_path if not is_multi_storey else cad_result.get("handoff_path"),
            "report_pdf_path": f"{report_base}.report.pdf",
            "report_md_path": f"{report_base}.report.md",
            "approval_package_path": str(package_path),
            "proposal_md_path": str(proposal_path),
            "vision_execution_path": str(vision_rec_path),
            "visual_qa_json_path": str(qa_json_path),
            "visual_qa_md_path": str(qa_md_path),
            "visual_qa_status": qa_report["overall_status"],
            "cad_result": cad_result,
        }
