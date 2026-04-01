from __future__ import annotations


def compute_richness(entities_n: int, actions_n: int, forces_n: int, outcomes_n: int, causal_clarity: float, weights: dict) -> tuple[float, dict[str, float]]:
    entity_interaction = min((entities_n + actions_n) / 8.0, 1.0)
    force_outcome = min((forces_n + outcomes_n) / 6.0, 1.0)
    causal = max(0.0, min(causal_clarity, 1.0))
    score = (
        weights["entity_interaction_richness_weight"] * entity_interaction
        + weights["force_outcome_visibility_weight"] * force_outcome
        + weights["causal_clarity_weight"] * causal
    )
    return score, {
        "entity_interaction": entity_interaction,
        "force_outcome": force_outcome,
        "causal_clarity": causal,
    }
