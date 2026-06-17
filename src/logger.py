"""Minimal logger for OpenCnidarios v0.1.

Writes:
- per-tick aggregates to CSV
- optional event stream to JSONL (birth, death, discovery, movement)

This is intentionally minimal.
"""

from __future__ import annotations

from dataclasses import asdict
import csv
import json
from pathlib import Path
from typing import Any


class Logger:
    def __init__(
        self,
        out_dir: str = "runs/latest",
        run_id: str | None = None,
        event_logging: bool = False,
        interview_logging: bool = False,
        ruminate_logging: bool = False,
    ):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        filename = f"ticks_{run_id}.csv" if run_id else "ticks.csv"
        self.csv_path = self.out_dir / filename
        self._csv_file = self.csv_path.open("w", newline="", encoding="utf-8")
        self._csv = None

        self._jsonl_file = None
        if event_logging:
            ev_filename = f"events_{run_id}.jsonl" if run_id else "events.jsonl"
            self._jsonl_file = (self.out_dir / ev_filename).open("w", encoding="utf-8")

        self._ruminate_file = None
        if ruminate_logging:
            rum_filename = f"ruminate_{run_id}.jsonl" if run_id else "ruminate.jsonl"
            self._ruminate_file = (self.out_dir / rum_filename).open("w", encoding="utf-8")

        self.interview_logging = interview_logging
        self._interviews_dir: Path | None = None

    def log_tick(self, tick_stats) -> None:
        row = asdict(tick_stats)
        if self._csv is None:
            self._csv = csv.DictWriter(self._csv_file, fieldnames=list(row.keys()))
            self._csv.writeheader()
        self._csv.writerow(row)
        self._csv_file.flush()

    def log_event(
        self,
        tick: int,
        event_type: str,
        organism_id: str,
        **payload: Any,
    ) -> None:
        if self._jsonl_file is None:
            return
        record = {"tick": tick, "event": event_type, "organism_id": organism_id}
        record.update(payload)
        self._jsonl_file.write(json.dumps(record) + "\n")
        self._jsonl_file.flush()

    def log_ruminate(
        self,
        tick: int,
        organism_id: str,
        output_raw: str,
        action_parsed: str | None,
    ) -> None:
        if self._ruminate_file is None:
            return
        record = {
            "tick": tick,
            "organism_id": organism_id,
            "output_raw": output_raw,
            "action_parsed": action_parsed,
        }
        self._ruminate_file.write(json.dumps(record) + "\n")
        self._ruminate_file.flush()

    def write_interview_clone(
        self,
        tick: int,
        organism_id: str,
        discovery_action: str,
        ruminant_snapshot: dict,
        adapter_state: dict,
        interview_qa: list,
    ) -> None:
        if not self.interview_logging:
            return
        if self._interviews_dir is None:
            self._interviews_dir = self.out_dir / "interviews"
            self._interviews_dir.mkdir(exist_ok=True)
        data = {
            **ruminant_snapshot,
            "adapter_state": adapter_state,
            "discovery_action": discovery_action,
            "interview": interview_qa,
        }
        fname = f"tick{tick:06d}_{organism_id[:8]}_{discovery_action}.json"
        (self._interviews_dir / fname).write_text(json.dumps(data, indent=2), encoding="utf-8")

    def close(self) -> None:
        if self._csv_file:
            self._csv_file.close()
        if self._jsonl_file:
            self._jsonl_file.close()
        if self._ruminate_file:
            self._ruminate_file.close()
