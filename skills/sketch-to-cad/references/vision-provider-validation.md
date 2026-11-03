# Vision Provider Validation Report & Multimodal Interface Architecture

**Project:** Sketch-to-CAD  
**Milestone:** Milestone 13  
**Document:** Vision Provider Validation Report  
**Date:** 2026-11-03  
**Status:** VALIDATED  

---

## 1. Provider Architecture Overview

The Sketch-to-CAD vision subsystem is designed as an extensible, pluggable multimodal provider interface (`scripts/vision_provider.py`) governed by strict configuration management (`scripts/vision_config.py`). It connects multimodal vision models to the deterministic geometry reconstruction pipeline while enforcing complete provenance tracking.

```
                    ┌─────────────────────────┐
                    │      VisionConfig       │
                    │  (Credential & Model)   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   BaseVisionProvider    │
                    └────────────┬────────────┘
         ┌───────────────┬───────┴───────┬───────────────┐
         ▼               ▼               ▼               ▼
┌────────────────┐┌─────────────┐┌──────────────┐┌──────────────┐
│  Google Gemini ││ OpenAI GPT  ││ Antigravity  ││ Mock Testing │
│  (REST API v1) ││ (REST v1)   ││ Agent Native ││ (Offline Sim)│
└────────────────┘└─────────────┘└──────────────┘└──────────────┘
```

---

## 2. Supported Multimodal Providers

### 2.1 Google Gemini (`google_gemini`)
* **Supported Models:** `gemini-2.5-flash` (recommended default), `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`.
* **API Specification:** Google AI Studio / Gemini REST API `v1beta/models/{model}:generateContent`.
* **Payload Structure:** Multimodal inline image payload with base64 data and `response_mime_type: "application/json"`.
* **Credential Variable:** `GEMINI_API_KEY` (or `GOOGLE_GEMINI_API_KEY`).
* **Dry-Run Capability:** Pre-flight checks compute source SHA-256, validate dimensions, assemble prompt, and verify configuration without making outbound network requests.

### 2.2 OpenAI (`openai`)
* **Supported Models:** `gpt-4o` (recommended default), `gpt-4o-mini`, `gpt-4-turbo`.
* **API Specification:** OpenAI Chat Completions API `v1/chat/completions`.
* **Payload Structure:** `image_url` data URL base64 object with `response_format: {"type": "json_object"}`.
* **Credential Variable:** `OPENAI_API_KEY`.
* **Dry-Run Capability:** Pre-flight parameter verification and JSON schema preparation.

### 2.3 Antigravity Agent Native (`antigravity_agent`)
* **Supported Models:** `antigravity-native-vision-v1`.
* **Mechanism:** Direct bridge between Google Antigravity Agent multimodal inspection capabilities and the deterministic CAD pipeline.
* **Auditability:** Binds interactive multimodal extractions to source file SHA-256 and records execution as `agent_native`. When pre-saved fixtures are replayed from disk, they are tagged as `replayed`.

### 2.4 Mock Provider (`mock`)
* **Supported Models:** `mock-architectural-v1`.
* **Purpose:** Deterministic offline unit testing, benchmark baselines, and synthetic failure mode verification.
* **Execution Classification:** Strictly tagged as `execution_type: "mocked"`. It is forbidden to claim mock runs as live AI vision accuracy.

---

## 3. Credential Security & Secret Masking

1. **Zero Secret Leakage:** Repr and log strings automatically mask API keys (`mask_secret()`). Keys with $\le 8$ characters display `***`; longer keys show the first 3 and last 4 characters (`AIz...cdef`).
2. **Environment Isolation:** API keys are never written to disk, committed to Git, or included in execution records or reports.
3. **Strict Validation Enforcement:** If an explicit live cloud provider (`google_gemini` or `openai`) is requested and credentials are missing, the factory `create_vision_provider()` immediately raises a descriptive `ValueError`. It **never** silently switches to mock mode when a live provider was requested.

---

## 4. Failure Mode Simulation & Resilience

The `MockVisionProvider` supports simulating realistic network and API failures to test pipeline resilience:

| Simulated Behavior | Simulated Response | Expected Pipeline Action | Verification Status |
| :--- | :--- | :--- | :---: |
| `timeout` | Exceeds timeout threshold ($60.05\text{ s}$). | Return status `timeout`, log `REQUEST_TIMEOUT` in execution record. | **VERIFIED** |
| `rate_limited` | Simulates HTTP 429 quota exhaustion. | Return status `rate_limited`, record `RATE_LIMIT_EXCEEDED`. | **VERIFIED** |
| `malformed_json` | Incomplete or unparseable JSON string. | Return status `invalid_response`, catch `JSONDecodeError`. | **VERIFIED** |
| `schema_mismatch` | Missing mandatory schema keys (`walls`, `rooms`). | Return status `schema_validation_failed`, log Draft-07 errors. | **VERIFIED** |

---

## 5. Architectural Vision Prompt Engineering

The vision prompt (`build_architectural_vision_prompt()`) enforces eight comprehensive architectural extraction domains:

1. **Domain A (Building Envelope & Primary Structure):** Continuous exterior boundary walls, structural perimeter, closed loops.
2. **Domain B (Interior Partitions & Thicknesses):** Dividing walls, partition thicknesses (explicit vs standard $100/150\text{ mm}$).
3. **Domain C (Door Schedule & Clearances):** Swing directions (inward/outward, left/right, sliding), host walls, widths.
4. **Domain D (Window Schedule & Openings):** Glazing locations on exterior/interior walls, sill height notes.
5. **Domain E (Room Identifiers & Zoning):** Room labels, standardized types (`LIVING`, `KITCHEN`, `BEDROOM`, `BATHROOM`, etc.).
6. **Domain F (Handwritten Dimensions):** Exact numerical values ($\text{mm}$), categorized as `explicit`, `estimated`, `inferred`, or `unknown`.
7. **Domain G (Vertical Circulation):** Stairs (direction up/down, step count hints), columns, structural piers.
8. **Domain H (Discrepancy Cataloging):** Catalog all arithmetic contradictions, unclosed boundary lines, and illegible notes.

> [!CAUTION]
> **Strict Anti-Extrapolation Rule:** The prompt explicitly forbids the model from extrapolating or inventing dimensions based on uncalibrated pixel proportions. All missing or ambiguous dimensions must be categorized as `unknown` or `estimated` and logged in the `uncertainties` register.

---

## 6. Execution Record Schema Compliance

All vision runs output a structured execution record conforming to Draft-07 schema `vision-execution-record.schema.json`. Verified required fields include:
- `record_id`: Unique identifier (e.g., `VR-AGENT-1793708574261`).
- `execution_type`: Validated against enum `["real_api", "agent_native", "mocked", "manual_override", "deterministic_heuristic", "replayed"]`.
- `provider_name`: Verified provider name.
- `model_identifier`: Model identifier.
- `source_image`: Sub-object containing `file_name`, `page_number`, `sha256` (64-character hex hash), and `dimensions_pixels`.
- `validation_result`: Structured validation report with boolean `is_valid` and error counts.
