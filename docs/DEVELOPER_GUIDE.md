# Developer Guide: Sketch-to-CAD

**Repository:** `https://github.com/hasnizihar/sketch-to-cad`  
**Branch:** `Skill-test-1.0.1`  
**Python Version:** 3.10–3.12  
**Test Harness:** `unittest`  

---

## 1. Repository Directory Structure

```
sketch-to-cad/
├── docs/                        # Project & architectural documentation
├── scripts/                     # Master production pipeline scripts
│   ├── architectural_qa.py      # 4-tier discrepancy analyzer
│   ├── architectural_reports.py # Markdown, PDF, and JSON report generator
│   ├── benchmark_engine.py      # Bipartite geometric accuracy evaluator
│   ├── bim_integration_validator.py # Downstream 3D BIM validator
│   ├── dimension_engine.py      # 3-tier dimensioning with collision avoidance
│   ├── drawing_generator.py     # CADCraft MCP vector drafting engine
│   ├── dxf_inspector.py         # Structural DXF audit & Layer 0 inspector
│   ├── performance_profiler.py  # Phase latency & resource profiling
│   ├── pilot_benchmark_runner.py# Decoupled 22-sample pilot benchmark runner
│   ├── pipeline_reliability.py  # Atomic writes, rollback, retry backoff
│   ├── release_packager.py      # Isolated deliverable packager & SHA-256 manifest
│   ├── run_vision_pilot.py      # Vision inference CLI runner with dry-run
│   ├── sheet_generator.py       # A4–A1 PDF drawing sheet generator
│   ├── sketch_interpreter.py    # Geometry reconstruction & opening projection
│   ├── sketch_to_cad_pipeline.py# End-to-end pipeline orchestrator
│   ├── vision_config.py         # Provider configuration & secret masking
│   └── vision_provider.py       # Multimodal provider interfaces
├── skills/
│   └── sketch-to-cad/           # Antigravity skill payload
│       ├── SKILL.md             # Skill frontmatter & prompt instructions
│       ├── schemas/             # 7 canonical Draft-07 JSON Schemas
│       ├── scripts/             # Mirrored copies of production scripts
│       ├── references/          # 28 architectural reference specifications
│       └── workflows/           # 3 core phase workflows
└── tests/                       # Exhaustive automated test suites
    ├── benchmark/pilot_dataset/ # 22-sample benchmark dataset & ground truth
    ├── fixtures/                # Canonical test models & sample sketches
    └── test_*.py                # 240 automated unit & regression tests
```

---

## 2. Mandatory Script Mirroring Rule

The Antigravity skill payload resides in `skills/sketch-to-cad/scripts/`, while root execution scripts reside in `scripts/`.

> [!CRITICAL]
> **Bi-Directional Mirroring Integrity**: Every script modified in `scripts/` MUST be mirrored identically into `skills/sketch-to-cad/scripts/`. Running `scripts/validate-skill.ps1` checks for file existence and consistency.

To synchronize scripts automatically:
```powershell
Copy-Item -Path scripts\*.py -Destination skills\sketch-to-cad\scripts\ -Force
```

---

## 3. JSON Schemas (`skills/sketch-to-cad/schemas/`)

All system interfaces communicate through Draft-07 JSON Schemas:
1. **`floor-plan-model.json`**: Intermediate coordinate representation of envelopes, walls, openings, rooms, elements, and finishes.
2. **`bim-handoff.schema.json`**: Coordinate handoff contract consumed by downstream 3D BIM pipelines (`dxf-to-3d-bim`).
3. **`architectural-report.schema.json`**: Architectural schedules, Shoelace room areas, finishes, and uncertainty audit.
4. **`sketch-observations.schema.json`**: Structured visual observations with `source_evidence`, `review_status`, and `revision_history`.
5. **`approval-package.schema.json`**: Human review proposal, uncertainty register, and cryptographic revision hash.
6. **`vision-execution-record.schema.json`**: Auditable vision execution log capturing model ID, SHA-256 fingerprint, duration, and schema validation.
7. **`vision-benchmark-result.schema.json`**: Bipartite evaluation metrics (precision, recall, F1, IoU, dimension error).

---

## 4. Vision Provider Interface (`BaseVisionProvider`)

To implement a new multimodal vision provider, subclass `BaseVisionProvider` in `scripts/vision_provider.py`:

```python
from scripts.vision_provider import BaseVisionProvider, VisionResult
from scripts.vision_config import VisionConfig
from typing import Dict, Any, Optional

class CustomVisionProvider(BaseVisionProvider):
    def __init__(self, config: VisionConfig):
        super().__init__(config)
        self.config = config

    def interpret_sketch(
        self,
        source_path: str,
        page_number: int = 1,
        source_metadata: Optional[Dict[str, Any]] = None,
    ) -> VisionResult:
        # 1. Load image and compute SHA-256
        # 2. Execute inference using self.config.model_identifier
        # 3. Format observations adhering to sketch-observations.schema.json
        # 4. Return VisionResult(status="success", observations=obs, execution_record=rec)
        pass
```

---

## 5. Running the Test Suite & Quality Validator

### Running Unit Tests (240 tests)
```powershell
python -m unittest discover tests
```

### Running the Skill Validator (19 checks)
The repository includes an automated PowerShell validator checking schema validity, fixture health, unit test execution, and zero machine-specific path leaks:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/validate-skill.ps1
```

---

## 6. Installed Skill Synchronization

To test the skill live inside the active Antigravity IDE:
1. Ensure the skill is copied to the user's Antigravity config directory:
   `<user_config_dir>\skills\sketch-to-cad\`
2. Verify that `SKILL.md` frontmatter contains `name: sketch-to-cad` and a descriptive prompt overview.
