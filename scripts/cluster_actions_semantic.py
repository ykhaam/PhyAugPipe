import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import ast
import json

import pandas as pd
from sentence_transformers import SentenceTransformer


def parse_actions(value) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                v = ast.literal_eval(s)
                if isinstance(v, list):
                    return [str(x) for x in v]
            except (ValueError, SyntaxError):
                return [s]
        if not s:
            return []
        return [s]
    return []


def main() -> None:
    ap = argparse.ArgumentParser(description="Action clustering via semantic matching")
    ap.add_argument("--input-csv", required=True, help="passed_winners.csv path")
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--sim-threshold", type=float, default=0.72)
    ap.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    args = ap.parse_args()

    df = pd.read_csv(args.input_csv)
    records = []
    for _, row in df.iterrows():
        for a in parse_actions(row.get("parsed_actions", [])):
            records.append({"sample_id": row["sample_id"], "action": a})

    if not records:
        Path(args.output_json).write_text(json.dumps({"clusters": []}, ensure_ascii=False, indent=2), encoding="utf-8")
        print({"clusters": 0, "items": 0})
        return

    model = SentenceTransformer(args.model)
    actions = [r["action"] for r in records]
    emb = model.encode(actions, normalize_embeddings=True)

    clusters: list[dict] = []
    for i, rec in enumerate(records):
        vec = emb[i]
        best_j = -1
        best_sim = -1.0
        for j, c in enumerate(clusters):
            sim = float((vec * c["centroid"]).sum())
            if sim > best_sim:
                best_sim = sim
                best_j = j
        if best_sim >= args.sim_threshold and best_j >= 0:
            c = clusters[best_j]
            c["items"].append({"sample_id": rec["sample_id"], "action": rec["action"]})
            c["centroid"] = (c["centroid"] * (len(c["items"]) - 1) + vec) / len(c["items"])
        else:
            clusters.append({
                "cluster_id": len(clusters),
                "prototype_action": rec["action"],
                "centroid": vec,
                "items": [{"sample_id": rec["sample_id"], "action": rec["action"]}],
            })

    export = []
    for c in clusters:
        export.append({
            "cluster_id": c["cluster_id"],
            "prototype_action": c["prototype_action"],
            "size": len(c["items"]),
            "items": c["items"],
        })

    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps({"clusters": export}, ensure_ascii=False, indent=2), encoding="utf-8")
    print({"clusters": len(export), "items": len(records), "output": args.output_json})


if __name__ == "__main__":
    main()
