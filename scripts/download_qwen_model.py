import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse

from huggingface_hub import snapshot_download


def main() -> None:
    ap = argparse.ArgumentParser(description="Download/cache Qwen model with skip-if-exists behavior")
    ap.add_argument("--model-id", default="Qwen/Qwen2.5-3B-Instruct")
    ap.add_argument("--local-dir", default="models/Qwen2.5-3B-Instruct")
    ap.add_argument("--revision", default=None)
    args = ap.parse_args()

    local_dir = Path(args.local_dir)
    if local_dir.exists() and any(local_dir.iterdir()):
        print({"status": "skipped_existing", "local_dir": str(local_dir), "model_id": args.model_id})
        return

    local_dir.mkdir(parents=True, exist_ok=True)
    resolved = snapshot_download(
        repo_id=args.model_id,
        local_dir=str(local_dir),
        local_dir_use_symlinks=False,
        revision=args.revision,
    )
    print({"status": "downloaded", "model_id": args.model_id, "local_dir": str(local_dir), "resolved": resolved})


if __name__ == "__main__":
    main()
