import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import subprocess


def main() -> None:
    ap = argparse.ArgumentParser(description="Download filtered Panda rows using official video2dataset command")
    ap.add_argument("--csv", required=True, help="Filtered CSV (e.g., train_2m_sports_30k.csv)")
    ap.add_argument("--output-folder", required=True)
    ap.add_argument("--config", default="video2dataset/video2dataset/configs/panda70m.yaml")
    ap.add_argument("--extra-columns", default="[matching_score,desirable_filtering,shot_boundary_detection]")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    Path(args.output_folder).mkdir(parents=True, exist_ok=True)

    cmd = [
        "video2dataset",
        f"--url_list={str(csv_path)}",
        "--url_col=url",
        "--caption_col=caption",
        "--clip_col=timestamp",
        f"--output_folder={args.output_folder}",
        f"--save_additional_columns={args.extra_columns}",
        f"--config={args.config}",
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
