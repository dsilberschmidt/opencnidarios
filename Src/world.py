"""OpenCnidarios v0.1 – world model (toroidal grid + energy).

Spec references:
- docs/02_planeta_v1_specification.md
- docs/04_parameters_v1.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import random


@dataclass
class World:
    n: int
    e_max: float
    regen_rate: float

    def __post_init__(self) -> None:
        # energy grid: list of lists [y][x]
        self.energy = [[0.0 for _ in range(self.n)] for _ in range(self.n)]

    def seed_energy_uniform(self, lo: float, hi: float, seed: int | None = None) -> None:
        if seed is not None:
            random.seed(seed)
        for y in range(self.n):
            row = self.energy[y]
            for x in range(self.n):
                row[x] = float(random.uniform(lo, hi))

    def wrap(self, x: int, y: int) -> Tuple[int, int]:
        return x % self.n, y % self.n

    def energy_at(self, x: int, y: int) -> float:
        x, y = self.wrap(x, y)
        return float(self.energy[y][x])

    def take_energy(self, x: int, y: int, cap: float) -> float:
        """Remove up to `cap` energy from the cell and return the amount taken."""
        x, y = self.wrap(x, y)
        available = float(self.energy[y][x])
        taken = min(float(cap), available)
        self.energy[y][x] = available - taken
        return float(taken)

    def regenerate(self) -> None:
        """Regenerate energy for all cells."""
        r = float(self.regen_rate)
        emax = float(self.e_max)
        for y in range(self.n):
            row = self.energy[y]
            for x in range(self.n):
                v = float(row[x]) + r
                row[x] = v if v < emax else emax
