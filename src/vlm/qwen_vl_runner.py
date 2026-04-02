from __future__ import annotations

import json
import re
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
        # This path is intentionally heuristic-only and should be replaced by real model inference for production.
        lower = prompt.lower()

        if "previous parse:" in lower:
            prev = self._extract_json_after_label(prompt, "Previous parse:")
            if isinstance(prev, dict):
                return {
                    "entities": prev.get("entities", []),
                    "materials": prev.get("materials", []),
                    "actions": prev.get("actions", []),
                    "forces": prev.get("forces", []),
                    "outcomes": prev.get("outcomes", []),
                }

        if "return json keys: entities, materials, actions, forces, outcomes." in lower:
            caption = self._extract_line(prompt, "Caption:")
            return self._heuristic_parse(caption)

        if "write concise causal physical reasoning" in lower:
            parse_obj = self._extract_json_after_label(prompt, "Parse:")
            entities = parse_obj.get("entities", []) if isinstance(parse_obj, dict) else []
            actions = parse_obj.get("actions", []) if isinstance(parse_obj, dict) else []
            forces = parse_obj.get("forces", []) if isinstance(parse_obj, dict) else []
            outcomes = parse_obj.get("outcomes", []) if isinstance(parse_obj, dict) else []
            return {
                "text": (
                    f"Visible interaction: {', '.join(actions[:2]) or 'motion'}; "
                    f"forces: {', '.join(forces[:2]) or 'gravity/contact'}; "
                    f"outcome: {', '.join(outcomes[:2]) or 'state change'}"
                )
            }

        if "cleaned_prompt" in lower:
            return {
                "cleaned_prompt": "A real-world dynamic scene with clear physical interaction.",
                "extended_prompt": "A person causes an object to move through visible contact, followed by an observable outcome.",
                "notes": "No hidden causes added.",
            }
        return {"text": "Physics-consistent visible cause-effect sequence."}

    @staticmethod
    def _extract_line(prompt: str, label: str) -> str:
        for line in prompt.splitlines():
            if line.strip().startswith(label):
                return line.split(label, 1)[1].strip()
        return ""

    @staticmethod
    def _extract_json_after_label(prompt: str, label: str) -> dict[str, Any] | None:
        idx = prompt.find(label)
        if idx < 0:
            return None
        raw = prompt[idx + len(label):].strip()
        for candidate in [raw, raw.splitlines()[0] if raw else ""]:
            if not candidate:
                continue
            try:
                obj = json.loads(candidate)
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                continue
        return None

    @staticmethod
    def _heuristic_parse(caption: str) -> dict[str, Any]:
        c = caption.lower()

        entities = []
        if re.search(r"\b(person|man|woman|player|athlete|boy|girl)\b", c):
            entities.append("person")
        if re.search(r"\b(ball|frisbee|bat|car|bike|object|box|hurdle|shelf)\b", c):
            entities.append("object")
        if re.search(r"\b(dog|cat|horse|bird)\b", c):
            entities.append("animal")
        if not entities:
            entities = ["object"]

        actions: list[str] = []
        if re.search(r"\bkick(?:s|ed|ing)?\b", c):
            actions.append("kick")
        if re.search(r"\bthrow(?:s|n|ing)?\b", c):
            actions.append("throw")
        if re.search(r"\bjump(?:s|ed|ing)?\b", c):
            actions.append("jump")
        if re.search(r"\brun(?:s|ning)?\b", c):
            actions.append("run")
        if re.search(r"\bbounce(?:s|d|ing)?\b", c):
            actions.append("bounce")
        if re.search(r"\bcollid(?:e|es|ed|ing)?\b|\bcollision\b|\bcrash(?:es|ed|ing)?\b", c):
            actions.append("collision")
        if re.search(r"\bfall(?:s|ing|en)?\b|\bdrop(?:s|ped|ping)?\b", c):
            actions.append("fall")
        if not actions:
            actions = ["move"]

        forces = ["gravity"]
        if any(a in actions for a in ["kick", "throw", "collision", "bounce"]):
            forces.append("contact force")

        outcomes = ["position changes"]
        if "collision" in actions:
            outcomes.append("abrupt velocity change")
        if "bounce" in actions:
            outcomes.append("direction reverses")
        if "fall" in actions:
            outcomes.append("drops downward")

        return {
            "entities": entities,
            "materials": [],
            "actions": actions,
            "forces": forces,
            "outcomes": outcomes,
        }

    @staticmethod
    def parse_json_text(text: str) -> dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}
