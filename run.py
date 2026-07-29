"""OpenCnidarios – simulation entrypoint.

Usage:
    python run.py --config runs/configs/v01_smoke_test.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
import uuid as _uuid
from datetime import datetime

from src.world import World
from src.ruminant import Ruminant
from src.engine import Engine
from src.llm_adapter.dummy import DummyAdapter
from src.llm_adapter.claude import ClaudeAdapter
from src.llm_adapter.openai_adapter import OpenAIAdapter
from src.logger import Logger
from src.snapshot import write_snapshot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to run config JSON")
    parser.add_argument("--ticks", type=int, default=None, help="Override cfg['ticks']")
    parser.add_argument("--population", type=int, default=None, help="Override cfg['params']['P0']")
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = json.load(f)

    if args.ticks is not None:
        cfg["ticks"] = args.ticks
    if args.population is not None:
        cfg["params"]["P0"] = args.population

    params = cfg["params"]
    seed = cfg["seed"]
    random.seed(seed)

    world = World(n=params["N"], e_max=params.get("E_max", cfg["world_energy_hi"]), regen_rate=params["regen_rate"], cell_energy_hi=cfg["world_energy_hi"])
    world.seed_energy_uniform(cfg["world_energy_lo"], cfg["world_energy_hi"], seed=seed)

    # config type → normalized adapter_type key (matches adapter_type class attribute)
    _TYPE_NORM   = {"dummy": "dummy", "llm": "claude", "openai": "openai"}
    # normalized type → config type (used for resume_from adapter_type lookup)
    _NORM_TO_CFG = {v: k for k, v in _TYPE_NORM.items()}

    def _build_adapter(cfg_type, spec):
        norm = _TYPE_NORM.get(cfg_type, cfg_type)
        if cfg_type == "dummy":
            return norm, DummyAdapter(p_action=spec.get("p_action", 0.05), seed=seed)
        elif cfg_type == "llm":
            return norm, ClaudeAdapter(
                model=spec.get("model", "claude-haiku-4-5-20251001"),
                memory_cost_factor=spec.get("memory_cost_factor", 0.00005),
                compression_interval=spec.get("compression_interval", 20),
                cost_metric=spec.get("cost_metric", "chars"),
            )
        elif cfg_type == "openai":
            return norm, OpenAIAdapter(
                model=spec.get("model", "gpt-5.4-mini"),
                memory_cost_factor=spec.get("memory_cost_factor", 0.00005),
                compression_interval=spec.get("compression_interval", 20),
                cost_metric=spec.get("cost_metric", "chars"),
            )
        else:
            raise ValueError(
                f"Adapter type {cfg_type!r} is not supported. "
                f"Add it to run.py before starting the run."
            )

    adapter_cfg = cfg["adapter"]

    needed_types: set = {adapter_cfg["type"]}

    # Validate resume_from entries and collect their adapter types before building anything.
    resume_snaps = []
    if cfg.get("resume_from"):
        for entry in cfg["resume_from"]:
            path = entry["path"]
            if not os.path.exists(path):
                raise FileNotFoundError(f"resume_from: snapshot not found: {path!r}")
            with open(path) as f:
                snap = json.load(f)
            snap_type = snap["adapter_type"]
            cfg_type_for_snap = _NORM_TO_CFG.get(snap_type)
            if cfg_type_for_snap is None:
                raise ValueError(
                    f"resume_from: adapter_type {snap_type!r} in {path!r} is not supported."
                )
            needed_types.add(cfg_type_for_snap)
            resume_snaps.append((snap, entry))

    adapters: dict = {}
    for cfg_type in needed_types:
        # Primary adapter uses adapter_cfg params; other types (from resume_from) use defaults.
        # TODO: when integrating with the "population" mechanism (branch mixed-population-config),
        # replace the {} fallback with spec_by_cfg_type = {s["type"]: s for s in population_specs}
        # so each adapter type uses its own spec (model, cost_metric, etc.) instead of generics.
        spec = adapter_cfg if cfg_type == adapter_cfg["type"] else {}
        norm, adapter_obj = _build_adapter(cfg_type, spec)
        if norm not in adapters:
            adapters[norm] = adapter_obj

    p0_adapter_type = _TYPE_NORM.get(adapter_cfg["type"], adapter_cfg["type"])

    run_id = f"{cfg['meta']['date']}_{cfg['meta']['name']}"
    out_dir = f"{cfg['out_dir']}_{datetime.now().strftime('%H%M%S')}"
    organisms_dir = "organisms"

    logger = Logger(
        out_dir=out_dir,
        run_id=run_id,
        event_logging=cfg.get("event_logging", False),
        interview_logging=cfg.get("interview_logging", False),
        ruminate_logging=cfg.get("ruminate_logging", False),
    )

    engine = Engine(world=world, adapters=adapters, params=params, logger=logger,
                    organisms_dir=organisms_dir, run_id=run_id)

    # Build P0 organisms from the primary adapter.
    ruminants = []
    for _ in range(params["P0"]):
        x = random.randrange(params["N"])
        y = random.randrange(params["N"])
        r = Ruminant(
            x=x, y=y,
            energy_internal=float(params["e_i0"]),
            constitution_text=cfg["constitution"],
            memory_text=cfg["memory"],
            adapter_type=p0_adapter_type,
        )
        ruminants.append(r)

    # Reconstruct resumed organisms from snapshots.
    for snap, entry in resume_snaps:
        x = entry.get("x", random.randrange(params["N"]))
        y = entry.get("y", random.randrange(params["N"]))
        r = Ruminant(
            x=x, y=y,
            energy_internal=float(snap["energy_internal"]),
            constitution_text=snap["constitution_text"],
            memory_text=snap["memory_text"],
            age=snap["age"],
            id=snap["id"],
            instance_id=str(_uuid.uuid4()),
            forked_from={
                "instance_id": snap["instance_id"],
                "run_id":      snap["run_id"],
                "tick":        snap["tick"],
            },
            adapter_type=snap["adapter_type"],
        )
        adapters[snap["adapter_type"]].restore_state(snap["id"], snap["adapter_state"])
        ruminants.append(r)

    engine.seed_population(ruminants)

    # Log resumed events before the main loop (tick=0 signals pre-run).
    for r in ruminants:
        if r.forked_from is not None and logger is not None:
            logger.log_event(
                0, "resumed", r.id,
                instance_id=r.instance_id,
                forked_from=r.forked_from,
                x=r.x, y=r.y,
                adapter_type=r.adapter_type,
            )

    checkpoint_every = cfg.get("checkpoint_every")

    try:
        for _ in range(cfg["ticks"]):
            stats = engine.step()
            if stats.population == 0:
                break
            if (checkpoint_every is not None
                    and engine.tick % checkpoint_every == 0
                    and engine.tick < cfg["ticks"]):
                print(f"[checkpoint] tick={engine.tick} pop={stats.population} "
                      f"mean_e={stats.mean_internal_energy:.2f}")
                for r in engine.ruminants:
                    write_snapshot(r, cause="checkpoint", run_id=run_id,
                                   tick=engine.tick, adapter=adapters[r.adapter_type],
                                   organisms_dir=organisms_dir)
                break
        else:
            for r in engine.ruminants:
                write_snapshot(r, cause="end_of_run", run_id=run_id,
                               tick=engine.tick, adapter=adapters[r.adapter_type],
                               organisms_dir=organisms_dir)
    except (Exception, KeyboardInterrupt):
        for r in engine.ruminants:
            write_snapshot(r, cause="crash", run_id=run_id,
                           tick=engine.tick, adapter=adapters[r.adapter_type],
                           organisms_dir=organisms_dir)
        raise
    finally:
        logger.close()


if __name__ == "__main__":
    main()
