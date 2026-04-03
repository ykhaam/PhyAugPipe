import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import csv
import json


def load_shortlist_ids(run_dir: Path) -> set[str]:
    p = run_dir / "metadata_records" / "shortlist.csv"
    if not p.exists():
        return set()
    out: set[str] = set()
    with p.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sid = str(row.get("sample_id", "")).strip()
            if sid:
                out.add(sid)
    return out


def load_json_ids(folder: Path) -> set[str]:
    if not folder.exists():
        return set()
    return {p.stem for p in folder.glob("*.json")}


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate artifact linkage across pipeline stages")
    ap.add_argument("--run-dir", default="outputs/default_run")
    ap.add_argument("--check-local-video-path", action="store_true", help="Also verify local_video_path files in frame_records")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    shortlist_ids = load_shortlist_ids(run_dir)
    frame_ids = load_json_ids(run_dir / "frame_records")
    parse_ids = load_json_ids(run_dir / "parse_records")
    prompt_ids = load_json_ids(run_dir / "prompt_records")

    errors: list[str] = []
    warnings: list[str] = []

    if not shortlist_ids:
        errors.append("shortlist is empty or missing: metadata_records/shortlist.csv")

    missing_frame = shortlist_ids - frame_ids
    if missing_frame:
        errors.append(f"missing frame_records for {len(missing_frame)} shortlist samples")

    missing_parse = frame_ids - parse_ids
    if missing_parse:
        warnings.append(f"missing parse_records for {len(missing_parse)} frame samples (stage3+ not run yet)")

    missing_prompt = parse_ids - prompt_ids
    if missing_prompt:
        warnings.append(f"missing prompt_records for {len(missing_prompt)} parse samples (stage7 not run yet)")

    final_all = run_dir / "final_exports" / "all_scored_samples.csv"
    if final_all.exists():
        with final_all.open("r", encoding="utf-8") as f:
            export_ids = {str(r.get("sample_id", "")).strip() for r in csv.DictReader(f) if str(r.get("sample_id", "")).strip()}
        missing_export = parse_ids - export_ids
        if missing_export:
            warnings.append(f"missing exported rows for {len(missing_export)} parsed samples")

    if args.check_local_video_path and (run_dir / "frame_records").exists():
        missing_local_paths = 0
        for p in (run_dir / "frame_records").glob("*.json"):
            row = json.loads(p.read_text(encoding="utf-8"))
            lp = str(row.get("local_video_path", "")).strip()
            if lp and not Path(lp).exists():
                missing_local_paths += 1
        if missing_local_paths:
            warnings.append(f"frame_records with non-existing local_video_path: {missing_local_paths}")

    result = {
        "run_dir": str(run_dir),
        "counts": {
            "shortlist": len(shortlist_ids),
            "frame_records": len(frame_ids),
            "parse_records": len(parse_ids),
            "prompt_records": len(prompt_ids),
        },
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
