#!/usr/bin/env python3
"""Per-turn decision tool. Input current game state, get best action recommendation.

Usage:
  .venv/bin/python scripts/decide.py

Enter values from the in-game training screen. The tool runs the engine
with the current state and scores every legal action, showing expected
stat gains, failure rates, bond estimates, and conditions.

Example input:
  Turn: 15
  Energy: 82
  Mood: good
  Fans: 3200
  Speed: 220 Stamina: 180 Power: 210 Guts: 160 Wisdom: 200 Skill Points: 45
  Conditions: charming

Then select which supports appear on each training facility.
"""

from __future__ import annotations

from uma_ai.career.actions import RaceAction, RecreationAction, RestAction, TrainAction, TrainingType
from uma_ai.career.engine import CareerEngine
from uma_ai.career.loader import oguri_cap_ura_state
from uma_ai.career.models import CareerState, Condition, Motivation, Stats
from uma_ai.scenarios.ura import URAScenario


TRAINING_TYPES = list(TrainingType)

CONDITION_MAP = {
    "none": set(),
    "perfect": {Condition.PRACTICE_PERFECT},
    "perfect_double": {Condition.PRACTICE_PERFECT_DOUBLE},
    "poor": {Condition.POOR_PRACTICE},
    "charming": {Condition.CHARMING},
    "night_owl": {Condition.NIGHT_OWL},
    "skin": {Condition.SKIN_OUTBREAK},
    "migraine": {Condition.MIGRAINE},
    "slow_meta": {Condition.SLOW_METABOLISM},
    "slacker": {Condition.SLACKER},
}


def _read_conditions() -> set[Condition]:
    print("Conditions (comma-separated: perfect,poor,charming,night_owl,skin,migraine,slow_meta,slacker,none):")
    raw = input("  ").strip().lower()
    if not raw:
        return set()
    result: set[Condition] = set()
    for part in raw.split(","):
        part = part.strip()
        if part in CONDITION_MAP:
            result.update(CONDITION_MAP[part])
    return result


def _read_support_placement(turn_label: str) -> dict[TrainingType, int]:
    """Ask which supports are on each training facility."""
    print(f"\nSupport placement — {turn_label}")
    print("  For each training type, enter how many supports appear on it (0-6):")
    placement: dict[TrainingType, int] = {}
    for t in TRAINING_TYPES:
        raw = input(f"  {t.value}: ").strip()
        placement[t] = int(raw) if raw.isdigit() else 0
    return placement


def main() -> None:
    print("=" * 55)
    print("  URA Training Decision Tool")
    print("  Enter current game state, get best action")
    print("=" * 55)

    # --- Career state ---
    print("\n-- Career State --")
    turn = int(input("Turn number: ").strip() or "12")
    energy = int(input("Energy: ").strip() or "100")
    mood_raw = input("Mood [awful/bad/normal/good/great]: ").strip().lower() or "normal"
    fans = int(input("Fans: ").strip() or "0")

    print("Stats (SPD STA PWR GUT WIT SP):")
    stats_raw = input("  ").strip()
    if stats_raw:
        parts = stats_raw.split()
        base = Stats(
            speed=int(parts[0]) if len(parts) > 0 else 101,
            stamina=int(parts[1]) if len(parts) > 1 else 66,
            power=int(parts[2]) if len(parts) > 2 else 106,
            guts=int(parts[3]) if len(parts) > 3 else 84,
            wisdom=int(parts[4]) if len(parts) > 4 else 93,
            skill_points=int(parts[5]) if len(parts) > 5 else 0,
        )
    else:
        base = Stats(speed=101, stamina=66, power=106, guts=84, wisdom=93)

    motivation = Motivation[mood_raw.upper()] if mood_raw.upper() in Motivation.__members__ else Motivation.NORMAL
    conditions = _read_conditions()

    # --- Create state using Oguri + default deck as template ---
    state = oguri_cap_ura_state()
    state.stats = Stats(
        speed=base.speed, stamina=base.stamina, power=base.power,
        guts=base.guts, wisdom=base.wisdom, skill_points=base.skill_points,
    )
    state.energy = energy
    state.motivation = motivation
    state.fans = fans
    state.conditions = conditions
    # Set turn index (calendar is 1-based, state is 0-based)
    state.turn_index = turn - 1
    state.trainee_id = "oguri_cap"
    state.event_history.add("ura_opening")

    engine = CareerEngine(URAScenario())
    cal_turn = engine.current_turn(state)

    # --- Support placement ---
    placement = _read_support_placement(cal_turn.label)
    print(f"\n  Mood: {state.motivation.name}  Energy: {state.energy}  Fans: {state.fans:,}")
    st = state.stats
    print(f"  Stats: SPD={st.speed} STA={st.stamina} PWR={st.power} "
          f"GUT={st.guts} WIT={st.wisdom} SP={st.skill_points}")
    if state.conditions:
        print(f"  Conditions: {', '.join(c.value for c in state.conditions)}")

    # --- Score actions ---
    print(f"\n{'='*55}")
    print(f"  Turn {turn} — {cal_turn.label}")
    print(f"{'='*55}")

    actions = engine.legal_actions(state)
    scored = []
    for a in actions:
        if isinstance(a, TrainAction):
            t = a.training
            n_placed = placement.get(t, 0)
            lvl = state.facility_levels[t]
            if cal_turn.is_summer_camp:
                lvl = 5
            base_stats = engine.scenario.base_training_stats(t, cal_turn, lvl)
            fail = engine.training_fail_rate(state.energy, t, state)
            scored.append((a, t.value, n_placed, lvl, fail, base_stats))
        elif isinstance(a, RestAction):
            scored.append((a, "rest", 0, 0, 0, None))
        elif isinstance(a, RecreationAction):
            scored.append((a, "recreation", 0, 0, 0, None))
        elif isinstance(a, RaceAction):
            scored.append((a, "race", 0, 0, 0, None))

    # Sort by training type priority
    print(f"\n  {'Training':<10} {'Supports':>8} {'LV':>3} {'Fail':>6}  "
          f"{'SPD':>4} {'STA':>4} {'PWR':>4} {'GUT':>4} {'WIT':>4} {'SP':>3}")
    print(f"  {'-'*10} {'-'*8} {'-'*3} {'-'*6}  {'-'*4} {'-'*4} {'-'*4} {'-'*4} {'-'*4} {'-'*3}")

    best_action = None
    best_score = -999
    for a, label, n_supp, lvl, fail, base in scored:
        if isinstance(a, TrainAction):
            spd = base.speed if base else 0
            sta = base.stamina if base else 0
            pwr = base.power if base else 0
            gut = base.guts if base else 0
            wit = base.wisdom if base else 0
            sp = base.skill_points if base else 0
            print(f"  Train {label:<4} {n_supp:>8} {lvl:>3} {fail*100:>5.0f}%  "
                  f"{spd:>4} {sta:>4} {pwr:>4} {gut:>4} {wit:>4} {sp:>3}")
        elif isinstance(a, RestAction):
            print(f"  Rest      {'':>8} {'':>3} {'':>6}  {'':>4} {'':>4} {'':>4} {'':>4} {'':>4} {'':>3}")
        elif isinstance(a, RecreationAction):
            print(f"  Recreation{'':>8} {'':>3} {'':>6}  {'':>4} {'':>4} {'':>4} {'':>4} {'':>4} {'':>3}")
        elif isinstance(a, RaceAction):
            print(f"  Race {a.name[:8]:<4} {'':>8} {'':>3} {'':>6}  {'':>4} {'':>4} {'':>4} {'':>4} {'':>4} {'':>3}")

    # Recommend
    print(f"\n  Recommendation: Review the table above.")
    print(f"  - Prefer training with high support count and low fail rate")
    print(f"  - Rest if energy < 30 or failing objectives")
    print(f"  - Race if fans needed for upcoming checks")
    if cal_turn.is_summer_camp:
        print(f"  - SUMMER CAMP: all facility levels = 5, rest cures conditions")
    if cal_turn.pre_debut:
        print(f"  - PRE-DEBUT: racing not available")
    print()


if __name__ == "__main__":
    main()
