from __future__ import annotations
import os
import time
import threading
from typing import Callable, List, Optional, Dict, Any


class ModelRouter:
    """Lightweight model router with fallback and simple cost-awareness.

    Default behavior: read ANTIGRAVITY_MODELS env var as comma-separated model ids
    (e.g. "gemini-pro,gemini-2.1"). The router does not call models until
    `run_with_fallback` is invoked. This helps avoid unexpected quota usage.
    """

    def __init__(self, models: Optional[List[str]] = None, weights: Optional[List[float]] = None):
        env = os.environ.get("ANTIGRAVITY_MODELS")
        if env and not models:
            models = [m.strip() for m in env.split(",") if m.strip()]
        self.models = models or ["gemini-pro", "gemini-2.1"]
        if weights and len(weights) == len(self.models):
            self.weights = weights
        else:
            self.weights = [1.0 for _ in self.models]
        # Simple in-memory usage stats to prefer cheaper models when asked
        self.usage: Dict[str, int] = {m: 0 for m in self.models}
        self.lock = threading.Lock()

    def _record_usage(self, model: str) -> None:
        with self.lock:
            self.usage[model] = self.usage.get(model, 0) + 1

    def choose_model(self) -> str:
        """Choose a model deterministically by current weights and usage.

        This is intentionally simple to keep behavior observable and safe.
        """
        # Prefer models with lower usage proportionally to their weight
        scores = []
        total_usage = sum(self.usage.values()) or 1
        for m, w in zip(self.models, self.weights):
            usage = self.usage.get(m, 0)
            score = w * (1 - (usage / total_usage))
            scores.append((score, m))
        scores.sort(reverse=True)
        return scores[0][1]

    def run_with_fallback(self, call_fn: Callable[[str, Any], Any], *args, **kwargs) -> Any:
        """Run call_fn(model, *args, **kwargs) trying models in preference order until success.

        call_fn must accept the model name as its first argument and raise on failure.
        Returns the first successful result or re-raises the last exception.
        """
        last_exc = None
        # Try the preferred model first then fallbacks
        # Build a preference order by choose_model then remaining list
        primary = self.choose_model()
        order = [primary] + [m for m in self.models if m != primary]
        for model in order:
            try:
                result = call_fn(model, *args, **kwargs)
                self._record_usage(model)
                return result
            except Exception as e:
                last_exc = e
                # Small backoff to avoid tight loop if external service is down
                time.sleep(0.2)
        # If all models failed, re-raise the last exception
        if last_exc:
            raise last_exc
        raise RuntimeError("No models configured")


# Convenience singleton for simple scripts
_default_router: Optional[ModelRouter] = None


def get_default_router() -> ModelRouter:
    global _default_router
    if _default_router is None:
        _default_router = ModelRouter()
    return _default_router
