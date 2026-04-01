from __future__ import annotations

import json
from typing import Any


class QwenVLRunner:
    """Lightweight runner abstraction.

    Default implementation is a safe deterministic stub for metadata-only and smoke testing.
    Replace `infer_json` with actual transformers inference for production.
    """

    def __init__(self, model_name: str, device: str = "auto"):
        self.model_name = model_name
        self.device = device

    def infer_json(self, prompt: str, image_paths: list[str]) -> dict[str, Any]:
        # Deterministic fallback behavior for reproducible dry runs.
        lower = prompt.lower()
        if "entities" in lower and "forces" in lower:
            return {
                "entities": ["person", "object"],
                "materials": ["metal"],
                "actions": ["move", "impact"],
                "forces": ["gravity", "contact force"],
                "outcomes": ["object changes velocity"],
            }
        if "cleaned_prompt" in lower:
            return {
                "cleaned_prompt": "A real-world dynamic scene with clear physical interaction.",
                "extended_prompt": "A person causes an object to move through visible contact, followed by an observable outcome.",
                "notes": "No hidden causes added.",
            }
        return {"text": "Physics-consistent visible cause-effect sequence."}

    @staticmethod
    def parse_json_text(text: str) -> dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}
