from __future__ import annotations

import json
import re
from typing import Any


class QwenVLRunner:
    """Runner for either real Transformers text inference or deterministic fallback."""

    def __init__(self, models_cfg: dict[str, Any]):
        self.models_cfg = models_cfg
        self.vlm_cfg = models_cfg.get("vlm", {})
        self.runtime_cfg = models_cfg.get("runtime", {})
        self.model_name = self.vlm_cfg.get("default_model", "Qwen/Qwen2.5-3B-Instruct")
        self.device = self.runtime_cfg.get("device", "auto")
        self.backend = self.vlm_cfg.get("backend", "stub")
        self._pipe = None

    def infer_json(self, prompt: str, image_paths: list[str]) -> dict[str, Any]:
        if self.backend == "transformers_text":
            generated = self._infer_text(prompt)
            parsed = self.parse_json_text(generated)
            if parsed:
                return parsed
        return self._infer_stub(prompt, image_paths)

    def _infer_text(self, prompt: str) -> str:
        if self._pipe is None:
            from transformers import pipeline

            self._pipe = pipeline(
                "text-generation",
                model=self.model_name,
                device_map=self.device,
                trust_remote_code=bool(self.vlm_cfg.get("tokenizer_trust_remote_code", True)),
            )

        out = self._pipe(
            prompt,
            max_new_tokens=int(self.vlm_cfg.get("max_new_tokens", 512)),
            do_sample=False if float(self.vlm_cfg.get("temperature", 0.0)) <= 0 else True,
            temperature=float(self.vlm_cfg.get("temperature", 0.0)),
            top_p=float(self.vlm_cfg.get("top_p", 0.9)),
            return_full_text=False,
        )
        return out[0]["generated_text"] if out else "{}"

    def _infer_stub(self, prompt: str, image_paths: list[str]) -> dict[str, Any]:
        lower = prompt.lower()

        if "previous parse:" in lower:
            prev = self._extract_json_after_label(prompt, "Previous parse:")
            if isinstance(prev, dict):
                parse = prev.get("parse", prev)
                return {
                    "parse": {
                        "entities": parse.get("entities", []),
                        "materials": parse.get("materials", []),
                        "actions": parse.get("actions", []),
                        "forces": parse.get("forces", []),
                        "outcomes": parse.get("outcomes", []),
                    }
                }

        if "step 1: element parsing" in lower:
            caption = self._extract_line(prompt, "Original prompt p:")
            return {"original": caption, "parse": self._heuristic_parse(caption)}

        if "step 3: physics reasoning" in lower:
            parse_obj = self._extract_json_after_label(prompt, "Checked parse:")
            parse = parse_obj.get("parse", parse_obj) if isinstance(parse_obj, dict) else {}
            actions = parse.get("actions", [])
            forces = parse.get("forces", [])
            outcomes = parse.get("outcomes", [])
            return {
                "reason": (
                    f"Actions {', '.join(actions[:2]) or 'motion'} generate "
                    f"{', '.join(forces[:2]) or 'gravity/contact force'}, leading to "
                    f"{', '.join(outcomes[:2]) or 'observable state change'}."
                )
            }

        if "step 5: prompt extending" in lower:
            caption = self._extract_line(prompt, "Original prompt p:")
            reason = self._extract_line(prompt, "Reason:")
            extended = f"{caption} {reason}".strip()
            extended = " ".join(extended.split()[:100])
            return {
                "cleaned_prompt": caption,
                "extended": extended,
                "notes": "Extended using causal details only.",
            }

        return {"text": "Visible cause-effect relation."}

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
        entities: list[str] = []
        if re.search(r"\b(player|athlete|person|man|woman|runner)\b", c):
            entities.append("person")
        if re.search(r"\b(ball|frisbee|car|bike|hurdle|bat|object)\b", c):
            entities.append("object")
        if not entities:
            entities = ["object"]

        actions: list[str] = []
        patterns = {
            "kick": r"\bkick(?:s|ed|ing)?\b",
            "throw": r"\bthrow(?:s|n|ing)?\b",
            "jump": r"\bjump(?:s|ed|ing)?\b",
            "run": r"\brun(?:s|ning)?\b",
            "bounce": r"\bbounce(?:s|d|ing)?\b",
            "collision": r"\bcollision\b|\bcollid(?:e|es|ed|ing)?\b|\bcrash(?:es|ed|ing)?\b",
            "fall": r"\bfall(?:s|ing|en)?\b|\bdrop(?:s|ped|ping)?\b",
            "spin": r"\bspin(?:s|ning)?\b",
            "hit": r"\bhit(?:s|ting)?\b",
        }
        for action, pattern in patterns.items():
            if re.search(pattern, c):
                actions.append(action)
        if not actions:
            actions = ["move"]

        forces = ["gravity"]
        if any(a in actions for a in ["kick", "throw", "collision", "bounce", "hit"]):
            forces.append("contact force")

        outcomes = ["position changes"]
        if "collision" in actions:
            outcomes.append("abrupt velocity change")
        if "bounce" in actions:
            outcomes.append("direction changes")
        if "fall" in actions:
            outcomes.append("downward motion")

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
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    return {}
            return {}
