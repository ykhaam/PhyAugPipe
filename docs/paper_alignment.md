# Paper Alignment: PhyAugPipe-style Stages

## Stage mapping
1. **Element Parsing** -> `src/pipeline/stage3_element_parsing.py`
2. **Vision Checking** -> `src/pipeline/stage4_vision_checking.py`
3. **Physics Reasoning** -> `src/pipeline/stage5_physics_reasoning.py`
4. **Data Scoring** -> `src/pipeline/stage6_scoring.py`
5. **Prompt Extending** -> `src/pipeline/stage7_prompt_extending.py`

## Directly specified by paper/project concept
- Multi-stage decomposition from parse to scoring and prompt improvement.
- Emphasis on physics-grounded causal understanding.
- Preference for dynamic, physically informative samples.

## Approximated / inferred in this implementation
- Exact numerical scoring weights and penalties.
- Exact threshold values for pass/fail.
- Keyword shortlist heuristics for metadata prefiltering.
- Practical metadata-only fallback behavior.
- Deterministic shard strategy for commodity multi-GPU environments.

## Intentional scope restriction
- No loser generation.
- No DPO training.
- No full-dataset downloader.
