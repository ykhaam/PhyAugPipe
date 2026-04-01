# Assumptions and Defaults

## Model defaults
- Default VLM: `Qwen/Qwen2.5-VL-7B-Instruct`.
- Reason: scope requests avoiding 72B and enabling feasible local execution.

## Prefilter defaults (metadata-first)
- desirable-only: enabled.
- single-shot-only: enabled.
- duration: 1s to 20s.
- keyword shortlist: sports/dynamics motion words.

These are configurable in `configs/panda70m.yaml`.

## Scoring formula defaults
- Components:
  - entity/interaction richness
  - force/outcome visibility
  - causal clarity
- Weights default to 0.35 / 0.30 / 0.35.

Rationale:
- Balanced emphasis between structured content and causality.
- Slightly prioritizes interpretable dynamics and reasoning coherence.

## Penalties
- heavy camera motion: 0.15
- stylized/non-natural visuals: 0.20
- static aftermath/weak dynamic event: 0.20

Rationale:
- Penalties suppress low-value samples for physics-grounded supervision.
- Stylization penalty stronger to prefer real-world videos.

## Selection defaults
- Default mode: threshold.
- Default threshold: 0.55.
- Alternative mode: top-N.

Important: threshold is intentionally configurable and should be tuned after reviewing `score_distribution.json` and representative bins.

## Alternatives and tradeoffs
- Higher threshold -> precision up, recall down.
- top-N -> stable output size, can drift by corpus quality.
- Larger penalties -> stricter realism, may remove borderline useful data.
