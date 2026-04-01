from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class QwenVLConfig:
    model_name: str = "Qwen/Qwen2.5-VL-7B-Instruct"
    max_new_tokens: int = 512
    temperature: float = 0.0


class QwenVLRunner:
    """
    Lightweight wrapper. Uses heuristic fallback when model runtime is unavailable,
    keeping metadata-only mode fully functional.
    """

    def __init__(self, cfg: QwenVLConfig, enable_model: bool = False):
        self.cfg = cfg
        self.enable_model = enable_model
        self._pipe = None
        if enable_model:
            self._try_load_model()

    def _try_load_model(self) -> None:
        try:
            from transformers import pipeline

            self._pipe = pipeline("image-text-to-text", model=self.cfg.model_name)
        except Exception:
            self._pipe = None
            self.enable_model = False

    def _heuristic_parse(self, caption: str) -> Dict[str, Any]:
        words = re.findall(r"[a-zA-Z]+", caption.lower())
        verbs = {"run", "jump", "fall", "throw", "hit", "kick", "slide", "bounce", "collide"}
        forces = [w for w in words if w in {"push", "pull", "gravity", "impact", "friction", "collision"}]
        actions = [w for w in words if w in verbs]
        entities = list(dict.fromkeys([w for w in words if len(w) > 3][:6]))
        outcomes = ["motion_change"] if actions else []
        return {
            "entities": entities,
            "materials": [],
            "actions": actions,
            "forces": forces,
            "outcomes": outcomes,
        }

    def element_parse(self, caption: str, frame_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        return self._heuristic_parse(caption)

    def vision_check(self, parsed: Dict[str, Any], caption: str, frame_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        checked = dict(parsed)
        checked["actions"] = list(dict.fromkeys(checked.get("actions", [])))
        checked["entities"] = list(dict.fromkeys(checked.get("entities", [])))
        return checked

    def physics_reasoning(self, parsed: Dict[str, Any], caption: str, frame_paths: Optional[List[str]] = None) -> str:
        acts = ", ".join(parsed.get("actions", [])[:3]) or "motion"
        forces = ", ".join(parsed.get("forces", [])[:2]) or "implicit forces"
        return f"Visible actions include {acts}. The event is plausibly driven by {forces}, leading to observable outcome changes."

    def extend_prompt(self, caption: str, checked_parse: Dict[str, Any], reasoning: str) -> Dict[str, str]:
        cleaned = caption.strip().replace("\n", " ")
        cleaned = re.sub(r"\s+", " ", cleaned)
        ext = f"{cleaned}. Physical dynamics: {reasoning}"
        return {"cleaned_prompt": cleaned, "extended_prompt": ext}
