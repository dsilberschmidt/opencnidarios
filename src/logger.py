"""Minimal logger for OpenCnidarios v0.1.

Writes:
- per-tick aggregates to CSV
- optional event stream to JSONL (placeholder)

This is intentionally minimal.
"""

from __future__ import annotations

from dataclasses import asdict
import csv
from pathlib import Path
from typing import Optional


class Logger:
    def __init__(self, out_dir: str = "runs/latest"):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.csv_path = self.out_dir / "ticks.csv"
        self._csv_file = self.csv_path.open("w", newline="", encoding="utf-8")
        self._csv = None

    def log_tick(self, tick_stats) -> None:
        row = asdict(tick_stats)
        if self._csv is None:
            self._csv = csv.DictWriter(self._csv_file, fieldnames=list(row.keys()))
            self._csv.writeheader()
        self._csv.writerow(row)
        self._csv_file.flush()

    def close(self) -> None:
        if self._csv_file:
            self._csv_file.close()
