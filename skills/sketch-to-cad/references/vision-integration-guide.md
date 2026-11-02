# Vision Integration & Setup Guide

This guide provides instructions for configuring, authenticating, and running genuine multimodal vision models with the Sketch-to-CAD pipeline.

---

## 1. Quick Setup

Sketch-to-CAD supports multimodal vision via standard REST endpoints and agent-native interfaces, requiring zero external SDK compilation.

### Option A: Google Gemini Multimodal Vision (Recommended)
1. Obtain an API key from Google AI Studio.
2. Set the environment variable:
   ```bash
   # Windows PowerShell
   $env:GEMINI_API_KEY = "AIzaSy..."

   # Linux / macOS
   export GEMINI_API_KEY="AIzaSy..."
   ```
3. Optional model override (defaults to `gemini-2.5-flash`):
   ```bash
   $env:GEMINI_MODEL = "gemini-1.5-pro"
   ```

### Option B: OpenAI Multimodal Vision
1. Obtain an API key from OpenAI Platform.
2. Set the environment variable:
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY = "sk-..."

   # Linux / macOS
   export OPENAI_API_KEY="sk-..."
   ```
3. Optional model override (defaults to `gpt-4o`):
   ```bash
   $env:OPENAI_MODEL = "gpt-4o"
   ```

### Option C: Antigravity Agent Native Multimodal Bridge
When running inside an interactive Google Antigravity coding environment:
- The agent natively inspects uploaded sketch images.
- Observations are piped directly into the pipeline with `execution_type: "agent_native"`.

### Option D: Deterministic Mock Provider (Offline / CI Testing)
No credentials required. Automatically selected when API keys are absent and `allow_mock_fallback=True`.
```bash
python scripts/evaluate_vision.py --provider mock
```

---

## 2. Running the Full Pipeline with Vision

```python
from scripts.sketch_to_cad_pipeline import SketchToCADPipeline
from scripts.vision_config import resolve_vision_config
from scripts.vision_provider import create_vision_provider

# 1. Resolve configuration (auto-detects keys from environment)
config = resolve_vision_config()
provider = create_vision_provider(config)

pipeline = SketchToCADPipeline(vision_provider=provider)

# 2. Run Step 1: Vision extraction & proposal generation (stops at approval gate)
res = pipeline.run_pipeline(
    source_sketch_path="sketches/my-house-plan.jpg",
    output_dir="output/project_01",
    approval_decision=None,
    project_name="My House Plan",
)

print(f"Status: {res['status']}")  # 'awaiting_approval'
print(f"Review Proposal: {res['proposal_path']}")
print(f"Vision Execution Record: {res['vision_execution_path']}")

# 3. Human Review & Approval
human_approval = {
    "reviewer_name": "Marcus Vance, Principal Architect",
    "action": "approve",
    "details": {"notes": "Approved for CAD drafting."},
}

approved_res = pipeline.run_pipeline(
    source_sketch_path="sketches/my-house-plan.jpg",
    output_dir="output/project_01",
    approval_decision=human_approval,
    project_name="My House Plan",
    allow_demo_identities=False,
)

print(f"Status: {approved_res['status']}")  # 'completed'
print(f"DXF Deliverable: {approved_res['dxf_path']}")
print(f"Visual QA Report: {approved_res['visual_qa_md_path']}")
```

---

## 3. Verifying Vision Execution Records

Every run writes `<project>.vision-execution.json`. Inspect the file to confirm genuine vision execution:
```bash
# Verify execution type is 'real_api' or 'agent_native', NOT 'mocked'
python -c "
import json
with open('output/project_01/my-house-plan.vision-execution.json') as f:
    rec = json.load(f)
print('Execution Type:', rec['execution_type'])
print('Provider:', rec['provider_name'])
print('Model:', rec['model_identifier'])
print('Duration (ms):', rec['processing_duration_ms'])
"
```
