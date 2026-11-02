# Vision Provider Contract

This document defines the formal engineering interface for multimodal vision models integrated into the Sketch-to-CAD pipeline.

---

## 1. Objectives & Principles

1. **Decoupled Architecture**: Multimodal vision models extract architectural observations; deterministic geometry algorithms reconstruct CAD drawings. A vision model never directly outputs raw DXF entities.
2. **Auditability & Traceability**: Every vision request produces an immutable execution record conforming to `schemas/vision-execution-record.schema.json`.
3. **Execution Type Categorization**: Every run is explicitly categorized into one of five execution types:
   - `real_api`: Authenticated call to a commercial multimodal vision endpoint (Google Gemini or OpenAI).
   - `agent_native`: Multimodal inspection performed natively by the hosting AI agent.
   - `manual_override`: Explicitly supplied ground-truth observations for regression testing.
   - `mocked`: Offline test stub for simulated failures or offline validation.
   - `deterministic_heuristic`: Fallback geometric heuristics.
4. **No Secret Storage**: API keys, bearer tokens, and authentication headers are never written to execution records, logs, or reports.

---

## 2. Supported Multimodal Providers

| Provider Identifier | Supported Models | Transport Protocol | Environment Variable |
| :--- | :--- | :--- | :--- |
| **`google_gemini`** | `gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-pro` | REST (`generateContent`) | `GEMINI_API_KEY` |
| **`openai`** | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` | REST (`chat/completions`) | `OPENAI_API_KEY` |
| **`antigravity_agent`** | `antigravity-native-vision-v1` | Direct Agent Bridge | Native Session Context |
| **`mock`** | `mock-architectural-v1` | Local Deterministic Simulator | None required |

---

## 3. Interface Specification (`BaseVisionProvider`)

All providers implement the abstract base class in `scripts/vision_provider.py`:

```python
class BaseVisionProvider(ABC):
    def __init__(self, config: VisionConfig):
        self.config = config

    @abstractmethod
    def interpret_sketch(
        self,
        source_path: str,
        page_number: int = 1,
        source_metadata: Optional[Dict[str, Any]] = None,
    ) -> VisionResult:
        """Submit sketch image to multimodal model and return structured VisionResult."""
        pass
```

### `VisionResult` Data Object:
- `status`: `"success" | "schema_validation_failed" | "api_error" | "timeout" | "rate_limited" | "invalid_response"`
- `execution_record`: Dictionary adhering to `vision-execution-record.schema.json`.
- `observations`: Dictionary adhering to `sketch-observations.schema.json` (populated on success).
- `raw_response`: Verbatim response string from provider endpoint.
- `error_message`: Detailed description if status is not `"success"`.

---

## 4. Structured Vision Execution Record Schema

Saved automatically to `<output-dir>/<project>.vision-execution.json`.

```json
{
  "$schema": "./vision-execution-record.schema.json",
  "record_id": "VR-GEMINI-1793634000",
  "execution_type": "real_api",
  "provider_name": "google_gemini",
  "model_identifier": "gemini-2.5-flash",
  "provider_config_version": "1.0.0",
  "source_image": {
    "file_name": "sketch-before.jpg",
    "page_number": 1,
    "total_pages": 1,
    "sha256": "8683c2cd307c28ca22a9bcb1790a66e7dfc9bb8a3e923cbf32c022cebbe6ea60",
    "dimensions_pixels": {"width": 1200, "height": 849},
    "dpi": 300.0
  },
  "timestamp": "2026-11-02T15:30:00Z",
  "prompt_version": "arch-interpret-v1.0",
  "status": "success",
  "validation_result": {
    "is_valid": true,
    "error_count": 0,
    "errors": []
  },
  "processing_duration_ms": 1420.5
}
```

---

## 5. Error & Failure Handling

Providers must implement graceful degradation without halting the surrounding application:
1. **Timeout**: HTTP calls exceed `config.timeout_seconds` (default: 60s). Status logged as `timeout`.
2. **Rate Limit (HTTP 429)**: Status logged as `rate_limited` with retry-after hint if provided.
3. **Malformed JSON**: When model returns invalid JSON syntax or truncated text, status is logged as `invalid_response`.
4. **Schema Violation**: If model returns JSON missing required architectural keys (`walls`, `rooms`, `dimensions`), status is logged as `schema_validation_failed`.
