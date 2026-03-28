"""
run_sweep_vina.py
-----------------
AutoDock Vina parameter sweep automation.

Iterates through all combinations of exhaustiveness, grid size, and random seed
(27 total) using itertools.product. Each combination is passed to Vina via
subprocess.run(). Output files are named by parameter configuration for
traceability.

Run on Windows with Vina installed and on PATH.

Usage:
    python run_sweep_vina.py

Outputs go to: results/raw/
"""

import itertools
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Input files — update paths to match your system
# ---------------------------------------------------------------------------
RECEPTOR = "data/receptor/1hvr_prepared.pdbqt"
LIGAND   = "data/ligand/xk2_prepared.pdbqt"

# Grid centre derived from crystallographic ligand coordinates (XK2, 1HVR)
CENTER_X = -8.715
CENTER_Y = 15.544
CENTER_Z = 27.900

# ---------------------------------------------------------------------------
# Parameter sweep values
# ---------------------------------------------------------------------------
EXHAUSTIVENESS_VALUES = [8, 16, 32]
GRID_SIZES            = [18, 22, 26]
RANDOM_SEEDS          = [12345, 54321, 99999]

NUM_MODES    = 9
ENERGY_RANGE = 3

OUTPUT_DIR = Path("results/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Run all 27 combinations
# ---------------------------------------------------------------------------
for exhaustiveness, grid_size, seed in itertools.product(
        EXHAUSTIVENESS_VALUES, GRID_SIZES, RANDOM_SEEDS):

    tag      = f"vina_{exhaustiveness}_{grid_size}_{seed}"
    out_file = OUTPUT_DIR / f"{tag}_out.pdbqt"
    log_file = OUTPUT_DIR / f"{tag}_log.txt"

    # Build command list — equivalent to typing this in the terminal
    cmd = [
        "vina",
        "--receptor",       RECEPTOR,
        "--ligand",         LIGAND,
        "--center_x",       str(CENTER_X),
        "--center_y",       str(CENTER_Y),
        "--center_z",       str(CENTER_Z),
        "--size_x",         str(grid_size),
        "--size_y",         str(grid_size),
        "--size_z",         str(grid_size),
        "--exhaustiveness", str(exhaustiveness),
        "--seed",           str(seed),
        "--num_modes",      str(NUM_MODES),
        "--energy_range",   str(ENERGY_RANGE),
        "--out",            str(out_file),
        "--log",            str(log_file),
    ]

    print(f"Running: exhaustiveness={exhaustiveness}, "
          f"grid={grid_size}A, seed={seed}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"  Done -> {out_file.name}")
    else:
        print(f"  ERROR: {result.stderr.strip()}")

print("\nAll Vina runs complete.")
