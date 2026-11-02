"""
Sketch-to-CAD Performance & Resource Profiling Framework (Milestone 10)

Captures high-resolution timing, entity counts, memory metrics, and resource utilization
across all architectural pipeline stages:
- Preprocessing & image rasterization
- Vision inference & token processing
- Geometric reconstruction & constraint solving
- Architectural & engineering QA
- CADCraft DXF generation & viewport rendering
- Independent DXF inspection
- Companion BIM handoff compilation
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class PhaseTiming:
    name: str
    duration_ms: float
    start_time_iso: str
    end_time_iso: str


@dataclass
class PipelineResourceProfile:
    project_name: str
    source_file_name: str
    source_file_size_bytes: int
    source_dimensions_pixels: Optional[List[int]]
    entity_summary: Dict[str, int]
    timings: List[PhaseTiming]
    total_pipeline_duration_ms: float
    timestamp_iso: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PipelineProfiler:
    """Collects and reports phase durations and resource metrics for a pipeline run."""

    def __init__(self, project_name: str = "FloorPlanRun"):
        self.project_name = project_name
        self.phase_timings: List[PhaseTiming] = []
        self._active_phase: Optional[str] = None
        self._phase_start: float = 0.0
        self._pipeline_start: float = time.perf_counter()
        self.entity_summary: Dict[str, int] = {}
        self.source_metadata: Dict[str, Any] = {}

    def start_phase(self, phase_name: str):
        """Begins timing a named pipeline phase."""
        if self._active_phase:
            self.end_phase()
        self._active_phase = phase_name
        self._phase_start = time.perf_counter()

    def end_phase(self):
        """Ends timing the currently active pipeline phase."""
        if not self._active_phase:
            return
        elapsed = (time.perf_counter() - self._phase_start) * 1000.0
        now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.phase_timings.append(
            PhaseTiming(
                name=self._active_phase,
                duration_ms=round(elapsed, 2),
                start_time_iso=now_str,
                end_time_iso=now_str,
            )
        )
        self._active_phase = None

    def record_entities(self, walls: int = 0, openings: int = 0, rooms: int = 0, elements: int = 0, floors: int = 1):
        """Records entity counts processed in the pipeline."""
        self.entity_summary = {
            "floors": floors,
            "walls": walls,
            "openings": openings,
            "rooms": rooms,
            "elements": elements,
            "total_entities": walls + openings + rooms + elements,
        }

    def record_source(self, file_path: str, dimensions: Optional[List[int]] = None):
        """Records source file size and dimensions."""
        p = Path(file_path)
        sz = p.stat().st_size if p.is_file() else 0
        self.source_metadata = {
            "name": p.name,
            "size_bytes": sz,
            "dimensions_pixels": dimensions,
        }

    def generate_profile(self) -> PipelineResourceProfile:
        """Finalizes and compiles the complete pipeline profile."""
        if self._active_phase:
            self.end_phase()

        total_ms = (time.perf_counter() - self._pipeline_start) * 1000.0
        return PipelineResourceProfile(
            project_name=self.project_name,
            source_file_name=self.source_metadata.get("name", "unknown"),
            source_file_size_bytes=self.source_metadata.get("size_bytes", 0),
            source_dimensions_pixels=self.source_metadata.get("dimensions_pixels"),
            entity_summary=self.entity_summary,
            timings=self.phase_timings,
            total_pipeline_duration_ms=round(total_ms, 2),
            timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )


def generate_performance_markdown_report(profile: PipelineResourceProfile) -> str:
    """Renders a performance profile into Markdown."""
    lines = [
        f"# Pipeline Performance & Resource Audit: {profile.project_name}",
        "",
        "## Summary Metrics",
        f"- **Source File:** `{profile.source_file_name}` ({profile.source_file_size_bytes:,} bytes)",
        f"- **Source Dimensions:** `{profile.source_dimensions_pixels or 'N/A'}`",
        f"- **Total Pipeline Duration:** **{profile.total_pipeline_duration_ms:.1f} ms** ({profile.total_pipeline_duration_ms/1000.0:.2f} s)",
        f"- **Total Entities Processed:** {profile.entity_summary.get('total_entities', 0)} "
        f"({profile.entity_summary.get('walls', 0)} walls, {profile.entity_summary.get('openings', 0)} openings, {profile.entity_summary.get('rooms', 0)} rooms)",
        "",
        "## Phase Breakdown & Timing",
        "",
        "| Pipeline Stage / Phase | Duration (ms) | % of Total Time |",
        "| :--- | :---: | :---: |",
    ]

    total_ms = max(profile.total_pipeline_duration_ms, 1e-6)
    for t in profile.timings:
        pct = (t.duration_ms / total_ms) * 100.0
        lines.append(f"| `{t.name}` | {t.duration_ms:.1f} ms | {pct:.1f}% |")

    return "\n".join(lines)
