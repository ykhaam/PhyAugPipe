from __future__ import annotations

from typing import Dict


def component_scores(checked_parse: Dict, reasoning: str) -> Dict[str, float]:
    entities = min(len(checked_parse.get("entities", [])) / 6.0, 1.0)
    interactions = min(len(checked_parse.get("actions", [])) / 4.0, 1.0)
    force = 1.0 if checked_parse.get("forces") else 0.3
    outcome = 1.0 if checked_parse.get("outcomes") else 0.3
    causal = min(max(len(reasoning.split()) / 24.0, 0.2), 1.0)
    return {
        "entity_interaction_richness": (entities + interactions) / 2.0,
        "force_outcome_visibility": (force + outcome) / 2.0,
        "causal_clarity": causal,
    }


def aggregate_score(components: Dict[str, float], weights: Dict[str, float]) -> float:
    s = 0.0
    for k, w in weights.items():
        s += components.get(k, 0.0) * w
    return max(0.0, min(1.0, s))
