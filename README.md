# PhyAugPipe-style Panda-70M Winner Selection Pipeline

This project implements a **metadata-first, resumable, sharded pipeline** for selecting high-quality real-world winning videos from Panda-70M, aligned to PhyAugPipe stages:
1. Element Parsing
2. Vision Checking
3. Physics Reasoning
4. Data Scoring
5. Prompt Extending

## Install
```bash
pip install -r requirements.txt
```

## Quickstart (Smoke Test on 10 samples)
1) Prepare a small metadata CSV at `data/panda70m_metadata.csv` with columns:
`sample_id,split,caption,desirability,shot_count,duration_sec,video_path`

2) Enable smoke mode in `configs/default.yaml`:
- `modes.smoke_test: true`
- `modes.smoke_test_n: 10`

3) Run full pipeline:
```bash
python scripts/run_pipeline.py
```

## Exact Commands
### Metadata inspection
```bash
python scripts/inspect_metadata.py --csv data/panda70m_metadata.csv
```

### Shortlist building (prefilter + artifacts)
```bash
python scripts/run_pipeline.py
```
(Shortlist outputs in `outputs/<run_name>/metadata_records/`)

### Frame extraction for local subset
```bash
python scripts/extract_subset_frames.py
```

### Multi-GPU VLM execution (one process per GPU)
```bash
CUDA_VISIBLE_DEVICES=0 python scripts/run_vlm_stage.py --stage element_parsing --shard-id 0 --num-shards 4
CUDA_VISIBLE_DEVICES=1 python scripts/run_vlm_stage.py --stage element_parsing --shard-id 1 --num-shards 4
CUDA_VISIBLE_DEVICES=2 python scripts/run_vlm_stage.py --stage element_parsing --shard-id 2 --num-shards 4
CUDA_VISIBLE_DEVICES=3 python scripts/run_vlm_stage.py --stage element_parsing --shard-id 3 --num-shards 4
```
Repeat for `vision_checking`, `physics_reasoning`, and `prompt_extending`.

### Export final winners
```bash
python scripts/export_winners.py
```

## Resumability
- Per-sample JSON artifacts are written at each stage.
- Existing stage outputs are skipped unless `modes.overwrite: true`.
- Crash-safe reruns process only missing items.

## Metadata-only mode
Set `modes.metadata_only: true` to run pipeline without requiring local videos.
Missing local videos are logged and skipped (non-fatal).
