# Assumptions and Defaults

## Model defaults
- Default VLM: `Qwen/Qwen2.5-VL-7B-Instruct` (project requirement).
- Temperature 0.1 for stable structured outputs.

## Shortlist heuristics (metadata-first)
- desirable-only: `true`
- single-shot-only: `true`
- sports/dynamics keyword filter: `true`
- duration range: `1s` to `30s`

Rationale: prioritizes concise, dynamic, physically rich events likely useful for winner selection.

## Scoring defaults (configurable)
- entity/interaction: 0.35
- force/outcome: 0.35
- causal clarity: 0.30

Penalties:
- heavy_camera_motion: 0.15
- stylization_non_natural: 0.20
- static_aftermath_weak_event: 0.10

Rationale: preserves interpretability while allowing user tuning after score distribution inspection.

## Selection defaults
- Default export mode: `threshold`
- Threshold fallback: `0.62`
- Alternative: `top_n` with configurable N.

## Tradeoffs
- Placeholder detectors maximize resumable architecture completeness but may underfit quality filtering until upgraded.
- Metadata-only mode enables immediate dry-runs before local subset videos are available.
