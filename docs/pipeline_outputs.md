# Pipeline Outputs

Root: `outputs/<run_name>/`

## 1) metadata_records/
- `shortlist.csv`, `shortlist.jsonl`
- Includes metadata-based shortlist decisions and local path resolution fields.

## 2) frame_records/
- Per-sample JSON with frame paths and extraction strategy.
- Cached frame files in sample-specific subdirectories.

## 3) parse_records/
- Per-sample JSON:
  - raw parse
  - vision-checked parse
  - physics reasoning
  - score components
  - penalties
  - physics richness + label

## 4) prompt_records/
- Per-sample JSON:
  - original caption
  - cleaned prompt
  - extended prompt
  - revision notes

## 5) final_exports/
- `all_scored_samples.(jsonl|csv)`
- `passed_winners.(jsonl|csv)`
- `rejected_samples.(jsonl|csv)`

## Winner-loser future compatibility
Current outputs include rich provenance fields (scores, penalties, reasoning, prompts), enabling later pairing strategies for winner-loser dataset construction without changing this selection pipeline.
