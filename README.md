# PhyAugPipe-Style Panda-70M Winner Selection Pipeline

This repository implements a **clean, reproducible, resumable, metadata-first** pipeline for selecting **winning real-world videos** from Panda-70M for later preference-learning dataset construction.

> Scope: data pipeline only (no loser generation, no DPO/PhyGDPO training).

## Pre-implementation proposal (as requested)

### Files created
- `requirements.txt`
- `configs/{default,models,scoring,panda70m}.yaml`
- `src/metadata/{panda70m_index,shortlist_builder}.py`
- `src/video/{video_locator,frame_sampler,frame_cache}.py`
- `src/vlm/{qwen_vl_runner,prompt_templates,parser}.py`
- `src/scoring/{richness,penalties,thresholds}.py`
- `src/storage/{schemas,writers,readers}.py`
- `src/pipeline/{stage1_prefilter,stage2_extract_frames,stage3_element_parsing,stage4_vision_checking,stage5_physics_reasoning,stage6_scoring,stage7_prompt_extending,stage8_export,runner}.py`
- `src/utils/{io,logging,distributed,progress,hashing,jsonl}.py`
- `scripts/{run_pipeline,inspect_metadata,build_shortlist,extract_subset_frames,run_vlm_stage,export_winners}.py`
- docs files in `docs/`

### Config schema
- `default.yaml`: runtime paths, stage order, overwrite, smoke test, sharding
- `models.yaml`: default VLM model (Qwen2.5-VL-7B-Instruct), generation controls
- `scoring.yaml`: weights, penalties, score bins, threshold/top-N selection
- `panda70m.yaml`: metadata fields + prefilter rules + local video roots + frame sampling

### Multi-GPU sharding
- One process per GPU/shard.
- Set `--num-shards N --shard-id i`.
- VLM stages process only records where `index % N == i`.
- Shard logs are written separately.
- Final export merges deterministically by reading persisted per-sample JSON records.

### Resume strategy
- Every stage writes per-sample JSON to its stage-specific directory.
- Reruns skip existing per-sample artifacts unless `overwrite=true`.
- Crash recovery: rerun the same command; remaining samples continue.

### Metadata-only mode
- Pipeline still runs without local videos.
- Missing local files are logged and non-fatal.
- VLM uses metadata/caption fallback parsing so scoring/export can proceed.

### Artifact separation
- `metadata_records/`: metadata + shortlist decisions + local path resolution
- `frame_records/`: frame extraction outputs only
- `parse_records/`: parse/check/reason/score outputs
- `prompt_records/`: prompt-clean + prompt-extend outputs
- `final_exports/`: merged CSV/JSONL + pass/reject + score distribution

### Paper-direct vs inferred defaults
- Directly aligned stage order: parse -> vision check -> reasoning -> scoring -> prompt extending
- Inferred defaults: numerical weights, penalties, keyword shortlist heuristics, thresholds/top-N behavior
- All inferred choices documented in `docs/assumptions_and_defaults.md`

---

## Installation

```bash
pip install -r requirements.txt
```

## Expected input

Provide Panda-70M metadata CSV at path configured in `configs/panda70m.yaml`:
- required columns: `sample_id`, `split`, `caption`
- optional columns used for filtering: `desirability`, `shot_count`, `duration_sec`, `video_path`

## Commands

### 1) Inspect metadata
```bash
python scripts/inspect_metadata.py
```

### 2) Build metadata-first shortlist
```bash
python scripts/build_shortlist.py
```
Outputs:
- `artifacts/metadata_records/shortlist.jsonl`
- `artifacts/metadata_records/shortlist.csv`
- per-sample JSON in `artifacts/metadata_records/*.json`

### 3) Extract frames from local subset only
```bash
python scripts/extract_subset_frames.py
```
Missing videos are logged and skipped.

### 4) Run VLM stages (single shard)
```bash
python scripts/run_vlm_stage.py --stage all
```

### 5) Run VLM stages (multi-GPU / multi-process shards)
GPU 0:
```bash
CUDA_VISIBLE_DEVICES=0 python scripts/run_vlm_stage.py --stage all --num-shards 2 --shard-id 0
```
GPU 1:
```bash
CUDA_VISIBLE_DEVICES=1 python scripts/run_vlm_stage.py --stage all --num-shards 2 --shard-id 1
```

### 6) Export winners
```bash
python scripts/export_winners.py
```

### 7) End-to-end pipeline
```bash
python scripts/run_pipeline.py
```
Smoke mode (10 samples):
```bash
python scripts/run_pipeline.py --smoke-test
```

## Selection modes
In `configs/scoring.yaml`:
- threshold mode: `selection.mode: threshold`, use `selection.threshold`
- top-N mode: `selection.mode: top_n`, use `selection.top_n`

The pipeline always exports score distribution first (`score_distribution.json`) to support threshold tuning.

## Final winning list fields
`passed_winners.{jsonl,csv}` includes:
- `sample_id`, `source_split`, `source_metadata_reference`, `local_video_path`
- `original_caption`, `cleaned_prompt`, `extended_prompt`
- `parsed_entities`, `parsed_actions`, `parsed_forces`, `parsed_outcomes`
- `physics_reasoning`, `physics_richness`, `physics_label`
- `penalty_breakdown`, `pass_fail_decision`, `shortlist_stage_tags`
- `notes_for_later_pairing`

## Notes
- Default VLM model config is Qwen2.5-VL-7B-Instruct.
- Current implementation supports a robust fallback mode for metadata-only operation and smoke testing.
- To enable full model inference, extend `src/vlm/qwen_vl_runner.py` runtime loading for your environment.
