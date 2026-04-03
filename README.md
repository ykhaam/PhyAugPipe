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
### 0) Build test subset from Panda-70M `train_2m.csv` (sports-focused, <=30k prompts)
```bash
python scripts/build_prompt_subset.py \
  --input-csv data/panda70m_meta/train_2m.csv \
  --output-csv data/panda70m_meta/train_2m_sports_30k.csv \
  --max-samples 30000 \
  --seed 42
```

> Note: to avoid duplicate downsampling, default `configs/default.yaml` keeps
> `shortlist.max_samples: null`. The 30k cap is applied in this step only.

### 0.5) Download Qwen once (skip if already exists)
```bash
python scripts/download_qwen_model.py \
  --model-id Qwen/Qwen2.5-3B-Instruct \
  --local-dir models/Qwen2.5-3B-Instruct
```

### 0.6) Download videos for subset (skip existing files)
```bash
python scripts/download_videos_subset.py \
  --input-csv data/panda70m_meta/train_2m_sports_30k.csv \
  --raw-video-dir data/videos_raw \
  --clip-dir data/videos
```

### Metadata inspection
```bash
python scripts/inspect_metadata.py --csv data/panda70m_meta/train_2m_sports_30k.csv
```

### (Optional) Convert raw `train_2m.csv` directly to pipeline schema + first 10 rows
```bash
python scripts/prepare_pipeline_csv.py \
  --input-csv data/panda70m_meta/train_2m.csv \
  --output-csv data/panda70m_meta/train_2m_top10_pipeline.csv \
  --top-n 10
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

### 3) Action clustering via semantics matching
```bash
python scripts/cluster_actions_semantic.py \
  --input-csv outputs/default_run/final_exports/passed_winners.csv \
  --output-json outputs/default_run/final_exports/action_clusters.json
```

### 4) Data sampling with physics rewarding
```bash
python scripts/sample_physics_rewarded.py \
  --input-csv outputs/default_run/final_exports/all_scored_samples.csv \
  --output-csv outputs/default_run/final_exports/physics_rewarded_sample.csv \
  --sample-size 5000 \
  --alpha 2.0
```

## Resumability
- Per-sample JSON artifacts are written at each stage.
- Existing stage outputs are skipped unless `modes.overwrite: true`.
- Crash-safe reruns process only missing items.

## Metadata-only mode
Set `modes.metadata_only: true` to run pipeline without requiring local videos.
Missing local videos are logged and skipped (non-fatal).
