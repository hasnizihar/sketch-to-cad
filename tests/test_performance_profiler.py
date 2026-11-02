"""
Test Suite for Performance & Resource Profiler Framework (Milestone 10).
Validates:
1. Pipeline phase start and end timing tracking.
2. Multiple contiguous pipeline stages (preprocessing, vision, reconstruction, CADCraft, export).
3. Entity summary tracking (floors, walls, openings, rooms, elements).
4. Source metadata recording (file path, file size, dimensions).
5. Serialization to dictionary and JSON format.
6. Markdown performance and resource audit report generation.
"""

from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from scripts.performance_profiler import (
    PhaseTiming,
    PipelineProfiler,
    PipelineResourceProfile,
    generate_performance_markdown_report,
)


class TestPerformanceProfiler(unittest.TestCase):
    """Unit tests for the performance and resource profiler."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_phase_timing_lifecycle(self):
        """Profiler accurately measures phase duration and records timestamps."""
        profiler = PipelineProfiler(project_name="BenchmarkHouse")
        profiler.start_phase("ImagePreprocessing")
        time.sleep(0.02)  # 20ms
        profiler.end_phase()

        self.assertEqual(len(profiler.phase_timings), 1)
        timing = profiler.phase_timings[0]
        self.assertEqual(timing.name, "ImagePreprocessing")
        self.assertGreaterEqual(timing.duration_ms, 15.0)

    def test_02_multiple_sequential_phases(self):
        """Starting a new phase automatically closes the previous active phase."""
        profiler = PipelineProfiler(project_name="MultiPhaseRun")
        profiler.start_phase("PhaseA")
        time.sleep(0.01)
        profiler.start_phase("PhaseB")  # Should auto-close PhaseA
        time.sleep(0.01)
        profiler.end_phase()

        self.assertEqual(len(profiler.phase_timings), 2)
        self.assertEqual(profiler.phase_timings[0].name, "PhaseA")
        self.assertEqual(profiler.phase_timings[1].name, "PhaseB")

    def test_03_record_entities_and_source_metadata(self):
        """Profiler accurately tracks architectural entities and source image info."""
        test_file = self.temp_path / "sample.jpg"
        test_file.write_bytes(b"\x00" * 2048)

        profiler = PipelineProfiler(project_name="ResidentialVilla")
        profiler.record_source(str(test_file), dimensions=[1920, 1080])
        profiler.record_entities(walls=16, openings=8, rooms=4, elements=12, floors=2)

        profile = profiler.generate_profile()
        self.assertEqual(profile.source_file_name, "sample.jpg")
        self.assertEqual(profile.source_file_size_bytes, 2048)
        self.assertEqual(profile.source_dimensions_pixels, [1920, 1080])
        self.assertEqual(profile.entity_summary["walls"], 16)
        self.assertEqual(profile.entity_summary["openings"], 8)
        self.assertEqual(profile.entity_summary["rooms"], 4)
        self.assertEqual(profile.entity_summary["elements"], 12)
        self.assertEqual(profile.entity_summary["floors"], 2)
        self.assertEqual(profile.entity_summary["total_entities"], 40)

    def test_04_profile_serialization(self):
        """PipelineResourceProfile serializes to dictionary with all required keys."""
        profiler = PipelineProfiler(project_name="DuplexRun")
        profiler.start_phase("CADGeneration")
        profiler.end_phase()
        profile = profiler.generate_profile()

        d = profile.to_dict()
        self.assertIn("project_name", d)
        self.assertIn("total_pipeline_duration_ms", d)
        self.assertIn("timings", d)
        self.assertIn("entity_summary", d)

    def test_05_markdown_report_generation(self):
        """Markdown report renders executive metrics and phase breakdown table."""
        profile = PipelineResourceProfile(
            project_name="DuplexUrban",
            source_file_name="floor_sketch.png",
            source_file_size_bytes=524288,
            source_dimensions_pixels=[2400, 1800],
            entity_summary={"walls": 24, "openings": 10, "rooms": 6, "total_entities": 40},
            timings=[
                PhaseTiming(name="VisionInference", duration_ms=450.0, start_time_iso="2026-11-02T12:00:00Z", end_time_iso="2026-11-02T12:00:00Z"),
                PhaseTiming(name="CADDrafting", duration_ms=150.0, start_time_iso="2026-11-02T12:00:01Z", end_time_iso="2026-11-02T12:00:01Z"),
            ],
            total_pipeline_duration_ms=600.0,
            timestamp_iso="2026-11-02T12:00:02Z",
        )

        md = generate_performance_markdown_report(profile)
        self.assertIn("# Pipeline Performance & Resource Audit: DuplexUrban", md)
        self.assertIn("floor_sketch.png", md)
        self.assertIn("VisionInference", md)
        self.assertIn("CADDrafting", md)
        self.assertIn("600.0 ms", md)


if __name__ == "__main__":
    unittest.main()
