from uma_ai.career.actions import TrainingType
from uma_ai.career.models import Stats, SupportCard

# Default test deck for URA simulation.
# Data sources: GT-SUPPORT (GameTora Kitasan Black page), GLOBAL-REF (stat stick passives section).
# Values marked PROJECT ASSUMPTION are approximated from typical card patterns.

DEFAULT_DECK: list[SupportCard] = [
    SupportCard(
        name="Kitasan Black SSR",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={
            TrainingType.SPEED: Stats(speed=6, power=2),
        },
        initial_bond=25,
        bond_gain_on_training=7,
        friendship_bonus_percent=20,
        mood_effect_percent=20,
        training_effectiveness_percent=10,
        race_bonus_percent=5,
        fan_bonus_percent=10,
        specialty_rate=80,
    ),
    SupportCard(
        name="Biko Pegasus SSR",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={
            TrainingType.SPEED: Stats(speed=5, power=1),
        },
        initial_bond=25,
        friendship_bonus_percent=15,
        mood_effect_percent=15,
        training_effectiveness_percent=10,
        race_bonus_percent=10,
        fan_bonus_percent=15,
        specialty_rate=60,
    ),
    SupportCard(
        name="Fine Motion SSR",
        card_type=TrainingType.WISDOM,
        level=50,
        training_stats={
            TrainingType.WISDOM: Stats(speed=2, wisdom=5),
        },
        initial_bond=30,
        friendship_bonus_percent=25,
        mood_effect_percent=20,
        training_effectiveness_percent=10,
        race_bonus_percent=5,
        wisdom_friendship_recovery=5,
        specialty_rate=80,
    ),
    SupportCard(
        name="Agnes Tachyon SR",
        card_type=TrainingType.WISDOM,
        level=50,
        training_stats={
            TrainingType.WISDOM: Stats(speed=1, wisdom=4),
        },
        initial_bond=20,
        friendship_bonus_percent=20,
        training_effectiveness_percent=5,
        race_bonus_percent=10,
        wisdom_friendship_recovery=4,
        specialty_rate=50,
    ),
    SupportCard(
        name="Mr. C.B. SSR",
        card_type=TrainingType.WISDOM,
        level=40,
        training_stats={
            TrainingType.WISDOM: Stats(speed=3, wisdom=4),
        },
        initial_bond=25,
        friendship_bonus_percent=20,
        mood_effect_percent=15,
        training_effectiveness_percent=5,
        race_bonus_percent=10,
        wisdom_friendship_recovery=4,
        specialty_rate=60,
    ),
    SupportCard(
        name="King Halo SSR",
        card_type=TrainingType.POWER,
        level=50,
        training_stats={
            TrainingType.POWER: Stats(stamina=2, power=6),
        },
        initial_bond=25,
        friendship_bonus_percent=20,
        mood_effect_percent=15,
        training_effectiveness_percent=10,
        race_bonus_percent=15,
        fan_bonus_percent=10,
        specialty_rate=70,
    ),
]
