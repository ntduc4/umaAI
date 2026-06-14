from __future__ import annotations

from uma_ai.career.actions import TrainingType
from uma_ai.career.models import Stats, SupportCard


def manual_support_card(
    name: str,
    card_type: TrainingType,
    level: int,
    training_stats: dict[TrainingType, Stats],
    initial_bond: int = 0,
) -> SupportCard:
    """Create a support card from exact user-provided values."""

    return SupportCard(
        name=name,
        card_type=card_type,
        level=level,
        training_stats=training_stats,
        initial_bond=initial_bond,
    )
