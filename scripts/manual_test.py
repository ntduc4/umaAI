#!/usr/bin/env python3
"""Interactive manual test harness for the URA career engine.

Run with:  .venv/bin/python scripts/manual_test.py
Plays Oguri Cap through URA Finals turn-by-turn.
Each turn shows the state, legal actions with heuristic scores,
and lets you pick one by number.

Enter a number to pick an action.
Enter 'p' to use the planner's top pick.
Enter 'q' to quit.
"""

from __future__ import annotations

from random import Random

from uma_ai.career.actions import RaceAction, RecreationAction, RestAction, TrainAction
from uma_ai.career.engine import CareerEngine
from uma_ai.career.loader import oguri_cap_ura_state
from uma_ai.heuristics.planner import RolloutPlanner
from uma_ai.heuristics.scoring import ActionScorer
from uma_ai.scenarios.ura import URAScenario


def _describe_action(action) -> str:
    if isinstance(action, TrainAction):
        return f"Train {action.training.value}"
    if isinstance(action, RestAction):
        return "Rest"
    if isinstance(action, RecreationAction):
        return "Recreation"
    if isinstance(action, RaceAction):
        fans = ""
        if action.race_id is not None:
            from uma_ai.scenarios.ura import URAScenario

            race = URAScenario().race_by_id(action.race_id)
            if race is not None:
                fans = f"  (fans: +{race.fan_gain_first}, req: {race.fan_requirement})"
        return f"Race {action.name}{fans}"
    return str(action)


def _print_state(state, engine, scorer, turn_no):
    turn = engine.current_turn(state)
    st = state.stats
    print(f"\n{'='*60}")
    print(f"Turn {turn_no} — {turn.label}")
    print(f"  Stats:  SPD={st.speed} STA={st.stamina} PWR={st.power} "
          f"GUT={st.guts} WIT={st.wisdom}  SP={st.skill_points}")
    print(f"  Energy: {state.energy}/100  Mood: {state.motivation.name}  "
          f"Fans: {state.fans:,}")
    if state.conditions:
        print(f"  Conditions: {', '.join(c.value for c in state.conditions)}")
    flevs = state.facility_levels
    print(f"  Facility LV: SPD={flevs['speed']} STA={flevs['stamina']} "
          f"PWR={flevs['power']} GUT={flevs['guts']} WIT={flevs['wisdom']}")

    pending = []
    for obj in state.objectives:
        if obj.id in state.completed_objective_ids:
            continue
        pending.append(f"{obj.description} (deadline turn {obj.deadline_turn_index})")
    if pending:
        print(f"  Objectives pending: {', '.join(pending[:3])}")
        if len(pending) > 3:
            print(f"    ... and {len(pending)-3} more")

    actions = engine.legal_actions(state)
    if len(actions) == 1:
        print(f"\n  Forced action: {_describe_action(actions[0])}")
    else:
        print(f"\n  Actions ({len(actions)}):")
        for i, a in enumerate(actions, 1):
            s = scorer.score(state, a)
            print(f"    {i:2d}. [{s:6.1f}] {_describe_action(a)}")


def _pick_action(actions, scorer, state, engine):
    planner = RolloutPlanner(engine, Random(42), rollouts=3, depth=4)
    best = max(actions, key=lambda a: scorer.score(state, a))

    while True:
        try:
            raw = input("\nAction [number/p/q]? ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if raw == "q":
            return None
        if raw == "p":
            print(f"  Using planner pick: {_describe_action(best)}")
            return best
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= len(actions):
                return actions[n - 1]
        print(f"  Enter 1-{len(actions)}, p, or q")


def main() -> None:
    seed = int(input("Random seed [default=0]? ") or "0")
    rng = Random(seed)
    state = oguri_cap_ura_state()
    engine = CareerEngine(URAScenario(), rng=rng)
    scorer = ActionScorer(engine)

    turn_no = 1
    while not engine.is_complete(state) and not state.failed:
        _print_state(state, engine, scorer, turn_no)
        actions = engine.legal_actions(state)
        if not actions:
            break
        if len(actions) == 1:
            action = actions[0]
            print(f"\n  Forced: {_describe_action(action)}")
        else:
            action = _pick_action(actions, scorer, state, engine)
            if action is None:
                print("\nQuit.")
                return

        engine.step(state, action)
        turn_no += 1

    print(f"\n{'='*60}")
    if state.failed:
        print("CAREER FAILED")
    else:
        print("URA FINALS COMPLETE!")
        st = state.stats
        print(f"  Final:  SPD={st.speed} STA={st.stamina} PWR={st.power} "
              f"GUT={st.guts} WIT={st.wisdom}  SP={st.skill_points}")
        print(f"  Fans: {state.fans:,}  Energy: {state.energy}  "
              f"Mood: {state.motivation.name}")
        conditions = ', '.join(c.value for c in state.conditions) or 'none'
        print(f"  Conditions: {conditions}")
        print(f"  Races run: {len(state.race_results)}")
        print(f"  Objectives completed: {len(state.completed_objective_ids)}")


if __name__ == "__main__":
    main()
