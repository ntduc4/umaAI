#!/usr/bin/env python3
"""Automatic career simulation with overridable parameters.

Usage:
  .venv/bin/python scripts/auto_sim.py                          # default Oguri + deck
  .venv/bin/python scripts/auto_sim.py --seed 42                # specific seed
  .venv/bin/python scripts/auto_sim.py --energy 80 --motivation great  # override
  .venv/bin/python scripts/auto_sim.py --speed 200 --stamina 200   # custom stats

Or edit the CONFIG dict below and run:
  .venv/bin/python scripts/auto_sim.py
"""

from __future__ import annotations

import argparse
import sys
from random import Random

from uma_ai.career.actions import TrainingType
from uma_ai.career.engine import CareerEngine
from uma_ai.career.loader import oguri_cap_ura_state
from uma_ai.career.models import Motivation, Stats
from uma_ai.heuristics.planner import RolloutPlanner
from uma_ai.scenarios.ura import URAScenario


def main() -> None:
    p = argparse.ArgumentParser(description="Auto-simulate a URA career")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--rollouts", type=int, default=8, help="rollouts per action")
    p.add_argument("--depth", type=int, default=6, help="lookahead depth")
    p.add_argument("--speed", type=int, help="starting speed")
    p.add_argument("--stamina", type=int, help="starting stamina")
    p.add_argument("--power", type=int, help="starting power")
    p.add_argument("--guts", type=int, help="starting guts")
    p.add_argument("--wisdom", type=int, help="starting wisdom")
    p.add_argument("--energy", type=int, default=100, help="starting energy")
    p.add_argument("--motivation", type=str, default="normal",
                   choices=["awful", "bad", "normal", "good", "great"])
    p.add_argument("--fans", type=int, default=0, help="starting fans")
    args = p.parse_args()

    state = oguri_cap_ura_state()

    if any([args.speed, args.stamina, args.power, args.guts, args.wisdom]):
        state.stats = Stats(
            speed=args.speed or state.stats.speed,
            stamina=args.stamina or state.stats.stamina,
            power=args.power or state.stats.power,
            guts=args.guts or state.stats.guts,
            wisdom=args.wisdom or state.stats.wisdom,
            skill_points=state.stats.skill_points,
        )
    state.energy = args.energy
    state.motivation = Motivation[args.motivation.upper()]
    state.fans = args.fans

    rng = Random(args.seed)
    engine = CareerEngine(URAScenario(), rng=rng)
    planner = RolloutPlanner(engine, rng=rng, rollouts=args.rollouts, depth=args.depth)

    print(f"Seed: {args.seed}  Rollouts: {args.rollouts}  Depth: {args.depth}")
    st = state.stats
    print(f"Start:  SPD={st.speed} STA={st.stamina} PWR={st.power} "
          f"GUT={st.guts} WIT={st.wisdom}  SP={st.skill_points}")
    print(f"Energy: {state.energy}  Mood: {state.motivation.name}  "
          f"Fans: {state.fans:,}")
    print(f"Objectives: {len(state.objectives)}")
    print(f"Supports: {len(state.supports)} cards")

    import time
    t0 = time.monotonic()
    final = planner.run(state)
    elapsed = time.monotonic() - t0

    print(f"\n{'='*60}")
    if final.failed:
        print(f"FAILED at turn {final.turn_index} ({elapsed:.1f}s)")
    else:
        print(f"COMPLETED in {final.turn_index} turns ({elapsed:.1f}s)")

    if planner.timing:
        times = sorted(planner.timing.values())
        avg = sum(times) / len(times)
        print(f"Decision time: avg={avg*1000:.0f}ms max={times[-1]*1000:.0f}ms "
              f"min={times[0]*1000:.0f}ms")
    st = final.stats
    print(f"Final:  SPD={st.speed} STA={st.stamina} PWR={st.power} "
          f"GUT={st.guts} WIT={st.wisdom}  SP={st.skill_points}")
    print(f"Total:  {st.total_without_skill_points} stats + {st.skill_points} SP")
    print(f"Energy: {final.energy}  Mood: {final.motivation.name}  "
          f"Fans: {final.fans:,}")
    conditions = ', '.join(c.value for c in final.conditions) or 'none'
    print(f"Conditions: {conditions}")
    print(f"Races won: {sum(1 for r in final.race_results if r.won)} / "
          f"{len(final.race_results)}")
    print(f"Objectives: {len(final.completed_objective_ids)} / "
          f"{len(final.objectives)} complete")
    if final.failed:
        pending = [o.description for o in final.objectives
                   if o.id not in final.completed_objective_ids]
        print(f"Failed objectives: {', '.join(pending[:3])}")
    print()

    from collections import Counter
    from uma_ai.career.actions import RaceAction, RecreationAction, RestAction, TrainAction
    counts: dict[str, int] = Counter()
    for log in final.logs:
        if log.action == "train":
            counts["train"] += 1
        elif log.action == "rest":
            counts["rest"] += 1
        elif log.action == "race":
            counts["race"] += 1
        elif log.action == "recreation":
            counts["recreation"] += 1
        elif log.action == "train_failed":
            counts["fail"] += 1
    total = sum(counts.values()) or 1
    print(f"Actions: train={counts.get('train',0)} ({counts.get('train',0)*100//total}%)",
          f"rest={counts.get('rest',0)} race={counts.get('race',0)}",
          f"rec={counts.get('recreation',0)} fail={counts.get('fail',0)}")


if __name__ == "__main__":
    main()
