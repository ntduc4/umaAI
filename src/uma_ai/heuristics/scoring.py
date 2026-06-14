from __future__ import annotations

from uma_ai.career.actions import CareerAction
from uma_ai.career.models import CareerState


class ActionScorer:
    """Future manual or trained heuristic for ranking legal actions."""

    def score(self, state: CareerState, action: CareerAction) -> float:
        raise NotImplementedError("action scoring will be implemented after the career engine is stable")
