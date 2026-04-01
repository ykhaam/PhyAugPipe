# Paper Alignment (PhyAugPipe vs This Implementation)

## Directly aligned stages
- Element Parsing -> `src/pipeline/stage3_element_parsing.py`
- Vision Checking -> `src/pipeline/stage4_vision_checking.py`
- Physics Reasoning -> `src/pipeline/stage5_physics_reasoning.py`
- Data Scoring -> `src/pipeline/stage6_scoring.py`
- Prompt Extending -> `src/pipeline/stage7_prompt_extending.py`

## Directly specified by paper (high-level)
- Multi-stage filtering with parsing + checking + reasoning + scoring + prompt refinement.
- Emphasis on physics-grounded, real-world dynamic content.

## Approximated/inferred in this implementation
- Numeric scoring weights and penalties are configurable defaults (`configs/scoring.yaml`).
- Penalty detectors are currently conservative placeholders, intended for replacement by stronger vision signals.
- Qwen2.5-VL-7B-Instruct is used by default (scope requirement), instead of larger model variants.

## Scope exclusions
- No loser generation.
- No DPO training.
- No full Panda-70M dataset downloader.
