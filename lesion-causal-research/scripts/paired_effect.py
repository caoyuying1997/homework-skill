"""Compute a paired edit effect for one fixed model/class/intervention configuration."""
import argparse
import csv
import json
import math
from statistics import mean


def summarize(path):
    effects = []
    seen = set()
    with open(path, encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"image_id", "p_original", "p_edited"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Required columns: image_id,p_original,p_edited")
        for line, row in enumerate(reader, 2):
            key = row["image_id"].strip()
            if not key or key in seen:
                raise ValueError(f"Line {line}: missing or duplicate image_id")
            seen.add(key)
            original, edited = float(row["p_original"]), float(row["p_edited"])
            if not all(math.isfinite(p) and 0 <= p <= 1 for p in (original, edited)):
                raise ValueError(f"Line {line}: probabilities must be finite and within [0,1]")
            effects.append(edited - original)
    if not effects:
        raise ValueError("Input contains no observations")
    ate = mean(effects)
    return {"n_images": len(effects), "ate": ate, "deletion_loss": -ate,
            "change_percentage_points": ate * 100,
            "mean_absolute_change": mean(map(abs, effects))}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", help="One row per image, one fixed configuration only")
    args = parser.parse_args()
    try:
        print(json.dumps(summarize(args.csv), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Error: {exc}\n")
