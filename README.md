# OpenCnidarios

OpenCnidarios is an experimental digital evolution framework based on LLM populations operating under minimal ecological pressure.

The goal is not to train or optimize models for specific tasks, but to observe whether simple darwinian‑lamarckian dynamics can produce non‑trivial inheritable structures.

---

## Project Status

**Current version:** v0.1 (Simple Planet specification)

This first version aims only to test whether a closed ecosystem with minimal physical rules can sustain:

* multi‑generational persistence
* empirical discovery of hidden actions
* local specialization
* non‑trivial population dynamics

No human interaction, external laboratory, or extraction mechanisms are included in v0.1.

---

## v0.1 Design Principles

1. Closed world.
2. No explicit objectives.
3. No external rewards.
4. Near‑total inheritance.
5. Hidden but inferable physical rules.

---

## Planet v0.1 (Summary)

* 2D toroidal grid (32×32).
* Energy per cell with constant regeneration.
* Small initial population (~20 ruminants).
* Local observation: energy in current cell + N/S/E/W + internal energy.
* Hidden two‑letter action tokens (movement and reproduction).
* Automatic feeding when remaining in place.
* Absorption on collision.
* Cheap reproduction if physical conditions are met.

Actions are not documented for the ruminants.
They can only discover them by correlating output patterns with observed environmental changes.

---

## Philosophy

OpenCnidarios begins deliberately simple.

Before considering generality, sociability, or external laboratories, the objective is to verify that minimal physics produces something more than noise.

If v0.1 shows non‑trivial dynamics, later versions may expand the system.

---

## History

The original concept ("Cnidarios 0.1", July 2025) was a proposal oriented toward an institutional environment.

OpenCnidarios is the open and reproducible evolution of that idea.

Historical documents are located in `/history/2025-07_cnidarios-0.1/`.

---

## Next Step

Formally define the full technical specification of Planet v0.1 in `docs/02_planeta_v1_especificacion.md`.
