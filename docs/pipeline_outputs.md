# Pipeline Outputs

## 1) `metadata_records/`
Contains:
- original metadata references
- shortlist pass/fail tags
- local path resolution result

## 2) `frame_records/`
Contains:
- extracted frame paths
- frame extraction metadata (fps, indices, counts)
- sampling strategy used

## 3) `parse_records/`
Contains:
- raw element parse
- vision-checked parse
- physics reasoning
- score components
- penalties and final physics richness

## 4) `prompt_records/`
Contains:
- original caption
- cleaned prompt
- extended prompt
- revision notes

## 5) `final_exports/`
Contains:
- `all_scored_samples` (CSV + JSONL)
- `passed_winners` (CSV + JSONL)
- `rejected_samples` (CSV + JSONL)
- `score_distribution.json`

## Data-side vs prompt-side separation
- Data-side: metadata/frame/parse directories.
- Prompt-side: prompt_records.
- Export layer joins these artifacts without collapsing provenance.

## Use for later winner-loser construction
The winner list already includes score, reasoning, parse, and prompt fields. Later loser sampling can be done by selecting low-score or rejected samples while preserving traceable artifacts.
