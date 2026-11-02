"""
Vision Configuration for Sketch-to-CAD Multimodal Providers.

Manages provider selection, environment variable credential resolution,
model parameters, and configuration validation without exposing sensitive secrets.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


SUPPORTED_PROVIDERS = ("google_gemini", "openai", "antigravity_agent", "mock")

# Standard documented multimodal models
SUPPORTED_GEMINI_MODELS = (
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
)

SUPPORTED_OPENAI_MODELS = (
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
)


@dataclass
class VisionConfig:
    """Configuration for multimodal vision providers."""
    provider_name: str = "mock"
    model_identifier: str = "mock-architectural-v1"
    api_key: Optional[str] = None
    endpoint_url: Optional[str] = None
    timeout_seconds: float = 60.0
    max_retries: int = 3
    temperature: float = 0.1
    prompt_version: str = "arch-interpret-v1.0"
    allow_mock_fallback: bool = True
    config_version: str = "1.0.0"

    def __repr__(self) -> str:
        # Mask API key in representation to prevent credential leaks
        masked_key = "***" if self.api_key else None
        return (
            f"VisionConfig(provider={self.provider_name}, model={self.model_identifier}, "
            f"api_key={masked_key}, timeout={self.timeout_seconds}s, prompt_v={self.prompt_version})"
        )


def mask_secret(secret: Optional[str]) -> str:
    """Safely mask a secret for logging or inspection."""
    if not secret:
        return "[NOT SET]"
    if len(secret) <= 8:
        return "***"
    return f"{secret[:3]}...{secret[-4:]}"


def resolve_vision_config(
    provider_name: Optional[str] = None,
    model_identifier: Optional[str] = None,
    api_key: Optional[str] = None,
    allow_mock_fallback: bool = True,
) -> VisionConfig:
    """
    Resolve vision configuration from parameters or environment variables.
    
    Priority:
    1. Explicit arguments.
    2. Environment variables (GEMINI_API_KEY, OPENAI_API_KEY, SKETCH_TO_CAD_VISION_PROVIDER).
    3. Antigravity Agent native bridge or mock provider.
    """
    prov = provider_name or os.environ.get("SKETCH_TO_CAD_VISION_PROVIDER")
    resolved_key = api_key

    if not prov:
        # Auto-detect available provider from environment keys
        if "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"].strip():
            prov = "google_gemini"
            resolved_key = resolved_key or os.environ["GEMINI_API_KEY"].strip()
        elif "OPENAI_API_KEY" in os.environ and os.environ["OPENAI_API_KEY"].strip():
            prov = "openai"
            resolved_key = resolved_key or os.environ["OPENAI_API_KEY"].strip()
        elif "ANTIGRAVITY_AGENTAPI_EXE" in os.environ:
            prov = "antigravity_agent"
        else:
            prov = "mock" if allow_mock_fallback else "google_gemini"

    prov = prov.lower()

    # Model default resolution
    model = model_identifier
    endpoint = None

    if prov == "google_gemini":
        model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        resolved_key = resolved_key or os.environ.get("GEMINI_API_KEY")
        endpoint = "https://generativelanguage.googleapis.com/v1beta/models"

    elif prov == "openai":
        model = model or os.environ.get("OPENAI_MODEL", "gpt-4o")
        resolved_key = resolved_key or os.environ.get("OPENAI_API_KEY")
        endpoint = "https://api.openai.com/v1/chat/completions"

    elif prov == "antigravity_agent":
        model = model or "antigravity-native-vision-v1"

    else:
        prov = "mock"
        model = model or "mock-architectural-v1"

    return VisionConfig(
        provider_name=prov,
        model_identifier=model,
        api_key=resolved_key,
        endpoint_url=endpoint,
        allow_mock_fallback=allow_mock_fallback,
    )


def validate_vision_config(config: VisionConfig) -> Tuple[bool, List[str]]:
    """
    Validate vision provider configuration.
    Returns (is_valid, list_of_errors).
    """
    errors: List[str] = []

    if config.provider_name not in SUPPORTED_PROVIDERS:
        errors.append(
            f"Unsupported provider '{config.provider_name}'. Supported providers: {list(SUPPORTED_PROVIDERS)}"
        )

    if config.timeout_seconds <= 0:
        errors.append(f"timeout_seconds must be positive, got {config.timeout_seconds}")

    if config.max_retries < 0:
        errors.append(f"max_retries must be non-negative, got {config.max_retries}")

    if config.provider_name in ("google_gemini", "openai"):
        if not config.api_key:
            errors.append(
                f"Missing API key for provider '{config.provider_name}'. "
                f"Set {config.provider_name.upper()}_API_KEY in environment or pass explicitly."
            )

        if config.provider_name == "google_gemini":
            if config.model_identifier not in SUPPORTED_GEMINI_MODELS and not config.model_identifier.startswith("gemini-"):
                errors.append(
                    f"Unrecognized Gemini model identifier '{config.model_identifier}'. "
                    f"Recommended: {list(SUPPORTED_GEMINI_MODELS)}"
                )

        if config.provider_name == "openai":
            if config.model_identifier not in SUPPORTED_OPENAI_MODELS and not config.model_identifier.startswith("gpt-"):
                errors.append(
                    f"Unrecognized OpenAI model identifier '{config.model_identifier}'. "
                    f"Recommended: {list(SUPPORTED_OPENAI_MODELS)}"
                )

    return (len(errors) == 0, errors)
