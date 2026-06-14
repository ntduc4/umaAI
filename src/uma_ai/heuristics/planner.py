from __future__ import annotations

from random import Random

from uma_ai.career.actions import CareerAction, RaceAction
from uma_ai.career.engine import CareerEngine
from uma_ai.career.models import CareerState
from uma_ai.heuristics.scoring import ActionScorer


class RolloutPlanner:
    def __init__(
        self,
        engine: CareerEngine,
        rng: Random | None = None,
        *,
        rollouts: int = 10,
        depth: int = 8,
    ) -> None:
        self.engine = engine
        self.scorer = ActionScorer(engine)
        self.rng = rng or Random()
        self.rollout_count = rollouts
        self.depth = depth

    def run(self, state: CareerState) -> CareerState:
        while not self.engine.is_complete(state) and not state.failed:
            actions = self.engine.legal_actions(state)
            if not actions:
                break
            if len(actions) == 1:
                best = actions[0]
            else:
                best = self._best_action(state, actions)
            self.engine.step(state, best)
        return state

    def _best_action(self, state: CareerState, actions: list[CareerAction]) -> CareerAction:
        scores = {action: 0.0 for action in actions}
        for action in actions:
            total = 0.0
            for _ in range(self.rollout_count):
                clone = state.clone()
                try:
                    self.engine.step(clone, action)
                except (ValueError, Exception):
                    total -= 100
                    continue
                if self.engine.is_complete(clone) or clone.failed:
                    total += self._terminal_score(clone)
                else:
                    total += self._rollout(clone)
            scores[action] = total / self.rollout_count
        return max(actions, key=lambda a: scores[a])

    def _rollout(self, state: CareerState) -> float:
        for _ in range(self.depth):
            if self.engine.is_complete(state) or state.failed:
                break
            actions = self.engine.legal_actions(state)
            if not actions:
                break
            best = max(actions, key=lambda a: self.scorer.score(state, a))
            try:
                self.engine.step(state, best)
            except (ValueError, Exception):
                return -50
        return self._terminal_score(state)

    def _terminal_score(self, state: CareerState) -> float:
        if state.failed:
            return -200
        st = state.stats
        score = st.total_without_skill_points + st.skill_points * 0.25
        completed = len(state.completed_objective_ids)
        total = len(state.objectives) or 1
        score += completed / total * 200
        return score
