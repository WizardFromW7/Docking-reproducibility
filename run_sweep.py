"""
run_sweep.py
------------
Automates the molecular docking parameter sweep described in:
  "Does Molecular Docking Reproducibility Depend on the Target Protein?"
  Benjamin Kamya, University of Reading, 2025-26

Iterates through all combinations of exhaustiveness, grid size, and random seed
using itertools.product, calling Vina or Smina via subprocess.run().

Usage:
    python scripts/run_sweep.py --system 1hvr --software vina
    python scripts/run_sweep.py --system 3ptb --software smina
    python scripts/run_sweep.py --system all  --software all

Note: Vina runs on Windows directly. Smina runs via WSL on Windows.
      On Linux/Mac, remove 'wsl' from build_smina_cmd().
"""

import argparse
import itertools
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# System configurations
# Grid centres derived from crystallographic ligand coordinates
# ---------------------------------------------------------------------------
SYSTEMS = {
    "1hvr": {
        "receptor":    "data/receptor/1hvr_prepared.pdbqt",
        "ligand":      "data/ligand/xk2_prepared.pdbqt",
        "center_x":    -8.715,
        "center_y":    15.544,
        "center_z":    27.900,
        "description": "HIV-1 Protease / XK2 (cyclic urea inhibitor)",
    },
    "4ph9": {
        "receptor":    "data/receptor/4ph9_prepared.pdbqt",
        "ligand":      "data/ligand/ibp_prepared.pdbqt",
        "center_x":    0.0,   # replace with your grid centre
        "center_y":    0.0,
        "center_z":    0.0,
        "description": "COX-2 / Ibuprofen (IBP)",
    },
    "3ptb": {
        "receptor":    "data/receptor/3ptb_prepared.pdbqt",
        "ligand":      "data/ligand/bzm_prepared.pdbqt",
        "center_x":    0.0,   # replace with your grid centre
        "center_y":    0.0,
        "center_z":    0.0,
        "description": "beta-Trypsin / Benzamidine",
    },
}

# ---------------------------------------------------------------------------
# Parameter sweep grid — 27 combinations per system per engine
# ---------------------------------------------------------------------------
EXHAUSTIVENESS_VALUES = [8, 16, 32]
GRID_SIZES            = [18, 22, 26]
RANDOM_SEEDS          = [12345, 54321, 99999]

NUM_MODES    = 9
ENERGY_RANGE = 3

RAW_DIR = Path("results/raw")


def to_wsl_path(path: str) -> str:
    """Convert Windows relative path to WSL-compatible format."""
    return path.replace("\\", "/")


def build_vina_cmd(system, exhaustiveness, grid_size, seed, out_path, log_path):
    """Build AutoDock Vina command list."""
    return [
        "vina",
        "--receptor",       system["receptor"],
        "--ligand",         system["ligand"],
        "--center_x",       str(system["center_x"]),
        "--center_y",       str(system["center_y"]),
        "--center_z",       str(system["center_z"]),
        "--size_x",         str(grid_size),
        "--size_y",         str(grid_size),
        "--size_z",         str(grid_size),
        "--exhaustiveness", str(exhaustiveness),
        "--seed",           str(seed),
        "--num_modes",      str(NUM_MODES),
        "--energy_range",   str(ENERGY_RANGE),
        "--out",            str(out_path),
        "--log",            str(log_path),
    ]


def build_smina_cmd(system, exhaustiveness, grid_size, seed, out_path, log_path):
    """
    Build Smina command list.
    Smina was run via WSL (Windows Subsystem for Linux).
    Remove 'wsl' from the command if running natively on Linux or Mac.
    """
    return [
        "wsl", "smina",
        "-r",               to_wsl_path(system["receptor"]),
        "-l",               to_wsl_path(system["ligand"]),
        "--center_x",       str(system["center_x"]),
        "--center_y",       str(system["center_y"]),
        "--center_z",       str(system["center_z"]),
        "--size_x",         str(grid_size),
        "--size_y",         str(grid_size),
        "--size_z",         str(grid_size),
        "--exhaustiveness", str(exhaustiveness),
        "--seed",           str(seed),
        "--num_modes",      str(NUM_MODES),
        "--energy_range",   str(ENERGY_RANGE),
        "--scoring",        "vinardo",
        "-o",               to_wsl_path(str(out_path)),
        "--log",            to_wsl_path(str(log_path)),
    ]


def run_sweep(system_keys, software_list):
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Generate all 27 parameter combinations per system per engine
    combos = list(itertools.product(
        system_keys,
        software_list,
        EXHAUSTIVENESS_VALUES,
        GRID_SIZES,
        RANDOM_SEEDS,
    ))
    total = len(combos)
    print(f"Total runs: {total}\n")

    for i, (sys_key, sw, ex, gs, seed) in enumerate(combos, 1):
        system   = SYSTEMS[sys_key]
        tag      = f"{sys_key}_{sw}_{ex}_{gs}_{seed}"
        out_path = RAW_DIR / f"{tag}_out.pdbqt"
        log_path = RAW_DIR / f"{tag}_log.txt"

        if out_path.exists():
            print(f"[{i}/{total}] SKIP  {tag}")
            continue

        cmd = build_vina_cmd(system, ex, gs, seed, out_path, log_path) \
              if sw == "vina" \
              else build_smina_cmd(system, ex, gs, seed, out_path, log_path)

        print(f"[{i}/{total}] RUN   {tag}  ({system['description']})")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                print(f"  ERROR: {result.stderr.strip()}", file=sys.stderr)
            else:
                print(f"  OK -> {out_path.name}")
        except FileNotFoundError:
            print(f"  ERROR: '{sw}' not found. Is it installed and on PATH?",
                  file=sys.stderr)
            sys.exit(1)
        except subprocess.TimeoutExpired:
            print(f"  ERROR: {tag} timed out", file=sys.stderr)


def parse_args():
    p = argparse.ArgumentParser(description="Molecular docking parameter sweep.")
    p.add_argument("--system",   nargs="+",
                   choices=list(SYSTEMS.keys()) + ["all"], default=["all"])
    p.add_argument("--software", nargs="+",
                   choices=["vina", "smina", "all"],       default=["all"])
    return p.parse_args()


if __name__ == "__main__":
    args     = parse_args()
    systems  = list(SYSTEMS.keys()) if "all" in args.system   else args.system
    software = ["vina", "smina"]    if "all" in args.software else args.software
    run_sweep(systems, software)
