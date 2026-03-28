"""
parse_results.py
----------------
Extracts top-ranked binding energies from AutoDock Vina / Smina log files.

Vina/Smina log format:
  mode | affinity (kcal/mol) | rmsd l.b. | rmsd u.b.
  -----+---------------------+-----------+----------
     1 |       -14.2         |   0.000   |   0.000

Usage:
    python scripts/parse_results.py \
        --input  results/raw/ \
        --output results/summary/binding_energies.csv
"""

import argparse
import re
from pathlib import Path

import pandas as pd


def parse_top_energy(log_path: Path) -> float | None:
    """Return binding energy of mode 1 (top pose) from a Vina/Smina log."""
    pattern = re.compile(r"^\s*1\s+([-\d.]+)")
    with open(log_path) as f:
        for line in f:
            m = pattern.match(line)
            if m:
                return float(m.group(1))
    return None


def parse_tag(stem: str) -> dict:
    """
    Parse filename stem into parameter components.
    Format: {system}_{software}_{exhaustiveness}_{gridsize}_{seed}_log
    e.g.  : 1hvr_vina_8_18_12345_log
    """
    parts = stem.replace("_log", "").split("_")
    return {
        "system":         parts[0],
        "software":       parts[1],
        "exhaustiveness": int(parts[2]),
        "grid_size":      int(parts[3]),
        "seed":           int(parts[4]),
    }


def main(input_dir: Path, output_path: Path):
    logs = sorted(input_dir.glob("*_log.txt"))
    if not logs:
        print(f"No log files found in {input_dir}")
        return

    rows = []
    for log in logs:
        energy = parse_top_energy(log)
        if energy is None:
            print(f"  WARN: could not parse {log.name}")
            continue
        row = parse_tag(log.stem)
        row["top_energy_kcal_mol"] = energy
        rows.append(row)

    df = pd.DataFrame(rows).sort_values(
        ["system", "software", "exhaustiveness", "grid_size", "seed"]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows -> {output_path}")
    print(df.groupby(["system", "software"])["top_energy_kcal_mol"]
            .agg(["mean", "std", "min", "max"]).round(2))


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input",  type=Path, default=Path("results/raw"))
    p.add_argument("--output", type=Path,
                   default=Path("results/summary/binding_energies.csv"))
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.input, args.output)
