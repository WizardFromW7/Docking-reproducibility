# Molecular Docking Reproducibility — BSc Pharmacology Dissertation

**University of Reading, School of Pharmacy | 2025–26**  
**Benjamin Kamya**

> Docking reproducibility is not an intrinsic property of a software engine — it depends on the structural and energetic landscape of the target protein.

---

## Objective

Systematic evaluation of docking reproducibility across AutoDock Vina, Smina, and GOLD using three crystallographic benchmark systems. Parameters swept: exhaustiveness, grid size, stochastic seed, ligand flexibility, and ligand preparation.

---

## Systems

| PDB  | Target         | Ligand                       |
|------|----------------|------------------------------|
| 1HVR | HIV-1 Protease | XK2 (cyclic urea inhibitor)  |
| 4PH9 | COX-2          | Ibuprofen (IBP)              |
| 3PTB | β-Trypsin      | Benzamidine                  |

---

## Tools

| Tool           | Version     | Role                       |
|----------------|-------------|----------------------------|
| AutoDock Vina  | 1.2.5       | Primary docking engine     |
| Smina          | 2020.12.10  | Vina fork, Vinardo scoring |
| GOLD           | CCDC        | Commercial comparator      |
| AutoDockTools  | 1.5.7       | File preparation           |
| ChimeraX       | 1.x         | Interaction analysis       |
| PyMOL          | 2.x         | Structural visualisation   |
| Python         | 3.11        | Sweep automation           |

---

## Workflow

```
1. Prepare receptor + ligand (.pdbqt) via AutoDockTools
2. Run rigid redocking baseline
3. Run flexible docking baseline
4. Parameter sweep (exhaustiveness / grid size / seed)
5. Ligand modification experiments
6. Parse binding energies + compute RMSD (ADT)
7. Interaction profiling (ChimeraX / PyMOL)
```

---

## Parameter Sweep Grid

| Parameter      | Values tested       |
|----------------|---------------------|
| Exhaustiveness | 8, 16, 32           |
| Grid size (Å)  | 18, 22, 26          |
| Random seed    | 12345, 54321, 99999 |
| Flexibility    | Rigid, Flexible     |
| Software       | Vina, Smina         |

Total runs per system: 27 (3×3×3 parameter combinations × 2 engines)



## Key Results

### Rigid vs Flexible

Rigid redocking consistently outperformed flexible across all three systems.

| System | Protocol | Engine | RMSD (Å) | Binding Energy (kcal/mol) |
|--------|----------|--------|----------|--------------------------|
| 1HVR   | Rigid    | Vina   | 0.607    | −20.5 |
| 1HVR   | Flexible | Vina   | 1.782    | −14.2 |
| 1HVR   | Rigid    | Smina  | 0.101    | −14.1 |
| 1HVR   | Flexible | Smina  | 2.244    | −9.3  |
| 3PTB   | Rigid    | Vina   | 0.205    | −17.3 |
| 3PTB   | Flexible | Vina   | 1.045    | −14.5 |
| 3PTB   | Rigid    | Smina  | 0.132    | −19.8 |
| 3PTB   | Flexible | Smina  | 1.988    | −16.2 |
| 4PH9   | Rigid    | Vina   | ~0.000   | −9.3  |
| 4PH9   | Flexible | Vina   | 1.146    | −7.7  |

### Parameter Sensitivity (Flexible Docking)

| System | Engine | SD (kcal/mol) | Key finding |
|--------|--------|--------------|-------------|
| 1HVR   | Vina   | 1.63 | 8/9 runs at −14.2; seed 54321 outlier (−9.3) |
| 1HVR   | Smina  | 2.72 | Range −8.2 to −14.2; exhaustiveness-dependent |
| 3PTB   | Vina   | 4.63 | Grid 22 Å → −1.9 kcal/mol (ligand displacement) |
| 3PTB   | Smina  | 4.06 | Range −7.5 to −20.1; highest variability in study |
| 4PH9   | Vina   | 0.32 | Most stable system; grid 18 Å minor deviation only |

### Ligand Modification

| Complex | Modification           | Engine | RMSD (Å) | Binding Energy (kcal/mol) |
|---------|------------------------|--------|----------|--------------------------|
| 3PTB    | Energy-minimised       | Vina   | 1.204    | −14.1 |
| 3PTB    | Reprotonated           | Smina  | 0.523    | −14.8 |
| 1HVR    | Extra proton           | Vina   | 0.422    | −14.6 |
| 1HVR    | Extra proton           | Smina  | 2.755    | −9.5  |
| 1HVR    | Aromatic ring deletion | Vina   | 5.405    | −5.6  |
| 1HVR    | Aromatic ring deletion | Smina  | 5.176    | −5.6  |

---

## Conclusions

- Rigid docking is a stable convergence baseline; flexible docking amplifies stochastic effects
- 3PTB (shallow, open binding site) is substantially less reproducible than 1HVR (deep, enclosed pocket)
- Random seed is the primary source of outlier results in Vina; exhaustiveness drives variability in Smina
- Grid size matters most for 3PTB — 22 Å displaced the ligand entirely
- Ligand preparation sensitivity is engine- and target-dependent, not universal

**Reproducibility is a property of the system, not the software.**


