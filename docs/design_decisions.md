# Design Decisions

## Metadata-first architecture
The pipeline starts from Panda-70M metadata to avoid requiring full video availability. This enables rapid shortlist and scoring preparation before heavy video IO.

## No full Panda-70M download assumption
Only user-provided metadata CSV is required initially. Local videos are optional and can be partial.

## Local-subset operation
`video_locator` resolves shortlist IDs against one or more local roots. Missing videos are logged and skipped without terminating the run.

## Multi-GPU strategy
VLM-heavy stages are sharded by deterministic index modulo (`idx % num_shards == shard_id`). This avoids cross-process locking and enables one process per GPU.

## Resume-safe artifacts
Every stage writes per-sample JSON outputs in stage-specific directories. Existing artifacts are skipped by default, which supports crash-safe reruns.

## Separation of concerns
Data artifacts (`metadata_records`, `frame_records`, `parse_records`) are separate from prompt artifacts (`prompt_records`). Final exports are materialized independently.
