"""
calc_rmsd.py
------------
Computes heavy-atom RMSD between top docking poses across all runs.

In the original study, RMSD was calculated manually using AutoDockTools (ADT)
by superimposing the crystallographic and docked ligands (heavy atoms only).
This script automates equivalent pairwise RMSD calculations using MDAnalysis.

Usage:
    python scripts/calc_rmsd.py \
        --poses  results/raw/ \
        --output results/summary/rmsd_matrix.csv
"""

import argparse
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import MDAnalysis as mda
except ImportError:
    raise SystemExit("MDAnalysis not found. Run: conda install -c conda-forge mdanalysis")


def load_top_pose(pdbqt_path: Path) -> mda.Universe:
    """Load only MODEL 1 (top pose) from a multi-model .pdbqt output file."""
    lines = []
    in_model = False
    with open(pdbqt_path) as f:
        for line in f:
            if line.startswith("MODEL") and not in_model:
                in_model = True
            if in_model:
                lines.append(line)
            if line.startswith("ENDMDL") and in_model:
                break

    tmp = Path("/tmp") / (pdbqt_path.stem + "_top.pdbqt")
    tmp.write_text("".join(lines))
    return mda.Universe(str(tmp))


def heavy_atom_rmsd(u1: mda.Universe, u2: mda.Universe) -> float:
    """Calculate heavy-atom RMSD between two poses."""
    sel  = "not name H*"
    pos1 = u1.select_atoms(sel).positions
    pos2 = u2.select_atoms(sel).positions
    if pos1.shape != pos2.shape:
        return float("nan")
    diff = pos1 - pos2
    return float(np.sqrt((diff ** 2).sum(axis=1).mean()))


def main(poses_dir: Path, output_path: Path):
    poses = sorted(poses_dir.glob("*_out.pdbqt"))
    if not poses:
        print(f"No pose files found in {poses_dir}")
        return

    print(f"Found {len(poses)} pose files. Computing pairwise RMSD...")
    names     = [p.stem.replace("_out", "") for p in poses]
    universes = [load_top_pose(p) for p in poses]

    matrix = pd.DataFrame(np.nan, index=names, columns=names)
    for i, j in combinations(range(len(poses)), 2):
        r = heavy_atom_rmsd(universes[i], universes[j])
        matrix.iloc[i, j] = r
        matrix.iloc[j, i] = r
    for i in range(len(poses)):
        matrix.iloc[i, i] = 0.0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(output_path)
    print(f"RMSD matrix ({len(names)} x {len(names)}) saved -> {output_path}")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--poses",  type=Path, default=Path("results/raw"))
    p.add_argument("--output", type=Path,
                   default=Path("results/summary/rmsd_matrix.csv"))
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.poses, args.output)
