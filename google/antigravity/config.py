from __future__ import annotations
import os
from typing import Dict, List, Optional


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(key, default)


class Config:
    """Safe configuration accessor for Antigravity CLI and helpers.

    Loads from environment first. Designed to avoid any network/model calls at import.
    """

    def __init__(self):
        # Model routing: comma-separated list (primary,fallback...)
        models = get_env("ANTIGRAVITY_MODELS")
        self.models: List[str] = [m.strip() for m in models.split(",")] if models else ["gemini-pro", "gemini-2.1"]

        # API keys (must be provided via env or secrets)
        self.gemini_key = get_env("GEMINI_API_KEY")
        self.google_api_key = get_env("GOOGLE_API_KEY")
        self.mcp_endpoint = get_env("MCP_ENDPOINT")

        # Control flags
        self.model_test_enabled = get_env("ANTIGRAVITY_MODEL_TEST_ENABLED", "false").lower() in ("1", "true", "yes")
        # Build command default (can be overridden when invoking ag site)
        self.default_build_cmd = get_env("ANTIGRAVITY_SITE_BUILD_CMD", "echo 'No build command configured'")

    def as_dict(self) -> Dict[str, object]:
        return {
            "models": self.models,
            "gemini_key_present": bool(self.gemini_key),
            "google_api_key_present": bool(self.google_api_key),
            "mcp_endpoint": self.mcp_endpoint,
            "model_test_enabled": self.model_test_enabled,
        }


# Convenience module-level config instance (lazy import safe)
_config: Optional[Config] = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config
