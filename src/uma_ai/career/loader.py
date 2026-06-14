from __future__ import annotations

from uma_ai.data.characters.oguri_cap import OGURI_CAP_APTITUDES, OGURI_CAP_BASE_STATS, OGURI_CAP_GROWTH_BONUS, OGURI_CAP_URA_OBJECTIVES
from uma_ai.data.support_cards.default_deck import DEFAULT_DECK
from uma_ai.career.models import CareerState, SupportCard


def oguri_cap_ura_state(support_cards: list[SupportCard] | None = None) -> CareerState:
    state = CareerState.new(
        base_stats=OGURI_CAP_BASE_STATS,
        support_cards=support_cards or DEFAULT_DECK,
        growth_rates=OGURI_CAP_GROWTH_BONUS,
        aptitudes=OGURI_CAP_APTITUDES,
    )
    state.trainee_id = "oguri_cap"
    state.objectives = list(OGURI_CAP_URA_OBJECTIVES)
    return state
