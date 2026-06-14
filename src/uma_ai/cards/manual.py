from __future__ import annotations

from uma_ai.career.actions import TrainingType
from uma_ai.career.models import Stats, SupportCard


def manual_support_card(
    name: str,
    card_type: TrainingType,
    level: int,
    training_stats: dict[TrainingType, Stats],
    initial_bond: int = 0,
    friendship_bonus_percent: int = 0,
    mood_effect_percent: int = 0,
    training_effectiveness_percent: int = 0,
    energy_cost_reduction_percent: int = 0,
    wisdom_friendship_recovery: int = 0,
    race_bonus_percent: int = 0,
    fan_bonus_percent: int = 0,
    failure_protection_percent: int = 0,
    specialty_rate: int = 0,
    initial_stats: Stats | None = None,
    bonus_stats: Stats | None = None,
) -> SupportCard:
    """Create a support card from exact user-provided values."""

    return SupportCard(
        name=name,
        card_type=card_type,
        level=level,
        training_stats=training_stats,
        initial_bond=initial_bond,
        friendship_bonus_percent=friendship_bonus_percent,
        mood_effect_percent=mood_effect_percent,
        training_effectiveness_percent=training_effectiveness_percent,
        energy_cost_reduction_percent=energy_cost_reduction_percent,
        wisdom_friendship_recovery=wisdom_friendship_recovery,
        race_bonus_percent=race_bonus_percent,
        fan_bonus_percent=fan_bonus_percent,
        failure_protection_percent=failure_protection_percent,
        specialty_rate=specialty_rate,
        initial_stats=initial_stats or Stats(),
        bonus_stats=bonus_stats or Stats(),
    )
