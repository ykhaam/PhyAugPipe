# Design Decisions

## Why metadata-first
Panda-70M is large; full local availability is unrealistic for many users. Metadata-first filtering reduces compute/storage cost and supports incremental subset curation.

## Why full download is not required
Pipeline only requires metadata + optional local subset videos. Missing files are skipped non-fatally and logged.

## Local-subset-only operation
`video_locator` resolves local files from user-provided directories. Stage 2 writes resolution outcomes regardless of availability.

## Multi-GPU design
- One process per GPU.
- Deterministic hash-based sharding by `sample_id`.
- Stage-specific shard runs + deterministic merge in export stage.

## Resume-safe artifacts
Every stage writes per-sample JSON artifacts. Reruns skip completed outputs unless overwrite is set.

## Data-side vs prompt-side separation
- Data-side: metadata/frame/parse records
- Prompt-side: prompt records
- Final exports combine both without collapsing intermediate provenance.
