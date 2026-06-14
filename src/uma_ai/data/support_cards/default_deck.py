from uma_ai.career.actions import TrainingType
from uma_ai.career.models import Stats, SupportCard

# Default test deck for URA simulation.
# Data from GT-SUPPORT compare tool:
# https://gametora.com/umamusume/compare?s=30028-30020-30010-30097_2-20012-30056
# All values at MLB (level 50) unless noted.

DEFAULT_DECK: list[SupportCard] = [
    # -- Kitasan Black SSR Speed MLB (30028) --
    # Friendship 25, Mood 30, Training 15, Race 5, Fan 15
    # Specialty 100, Hint Lv 2, Hint Freq 30
    # Speed Bonus +1, Power Bonus +1, Init Speed 35, Init Bond 35
    # Stat gain: Speed +6, Power +2
    SupportCard(
        name="Kitasan Black SSR",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={TrainingType.SPEED: Stats(speed=6, power=2)},
        bonus_stats=Stats(power=1),
        initial_bond=35,
        initial_stats=Stats(speed=35),
        friendship_bonus_percent=25,
        mood_effect_percent=30,
        training_effectiveness_percent=15,
        race_bonus_percent=5,
        fan_bonus_percent=15,
        specialty_rate=100,
    ),
    # -- Biko Pegasus SSR Speed MLB (30020) --
    # Friendship 25, Training 20, Race 10, Fan 20
    # Specialty 55, Hint Lv 2, Hint Freq 36
    # Init Bond 30
    # Stat gain: Speed +6, Power +2
    SupportCard(
        name="Biko Pegasus SSR",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={TrainingType.SPEED: Stats(speed=6, power=2)},
        initial_bond=30,
        friendship_bonus_percent=25,
        training_effectiveness_percent=20,
        race_bonus_percent=10,
        fan_bonus_percent=20,
        specialty_rate=55,
    ),
    # -- Fine Motion SSR Wit MLB (30010) --
    # Friendship 37.5, Mood 30, Training 15, Race 10, Fan 20
    # Specialty 35, WFR 5
    # Wit Bonus +1, Init Wit 35, Init Bond 15
    # Stat gain: Wit +6, SP +5
    SupportCard(
        name="Fine Motion SSR",
        card_type=TrainingType.WISDOM,
        level=50,
        training_stats={TrainingType.WISDOM: Stats(wisdom=6, skill_points=5)},
        bonus_stats=Stats(wisdom=1),
        initial_bond=15,
        initial_stats=Stats(wisdom=35),
        friendship_bonus_percent=37,
        mood_effect_percent=30,
        training_effectiveness_percent=15,
        race_bonus_percent=10,
        fan_bonus_percent=20,
        wisdom_friendship_recovery=5,
        specialty_rate=35,
    ),
    # -- Mr. C.B. SSR Wit 2LB/level 40 (30097_2) --
    # Friendship 27, Training 5, Race 5, Fan 13
    # Specialty 45, WFR 4, Hint Lv 3, Hint Freq 20
    # Speed +1, Wit +2, SP +1, Init Bond 18
    # Stat gain: Wit +6, SP +5
    SupportCard(
        name="Mr. C.B. SSR",
        card_type=TrainingType.WISDOM,
        level=40,
        training_stats={TrainingType.WISDOM: Stats(wisdom=6, skill_points=5)},
        bonus_stats=Stats(speed=1, wisdom=2, skill_points=1),
        initial_bond=18,
        friendship_bonus_percent=27,
        training_effectiveness_percent=5,
        race_bonus_percent=5,
        fan_bonus_percent=13,
        wisdom_friendship_recovery=4,
        specialty_rate=45,
    ),
    # -- Agnes Tachyon SR Wit MLB (20012) --
    # Friendship 20, Mood 40, Training 5, Race 10, Fan 20
    # Specialty 50, WFR 4
    # Wit +1, SP +1, Init Wit 20, Init Bond 25
    # Stat gain: Wit +6, SP +5
    SupportCard(
        name="Agnes Tachyon SR",
        card_type=TrainingType.WISDOM,
        level=50,
        training_stats={TrainingType.WISDOM: Stats(wisdom=6, skill_points=5)},
        bonus_stats=Stats(wisdom=1, skill_points=1),
        initial_bond=25,
        initial_stats=Stats(wisdom=20),
        friendship_bonus_percent=20,
        mood_effect_percent=40,
        training_effectiveness_percent=5,
        race_bonus_percent=10,
        fan_bonus_percent=20,
        wisdom_friendship_recovery=4,
        specialty_rate=50,
    ),
    # -- King Halo SSR Power MLB (30056) --
    # Friendship 43, Training 10
    # Specialty 70, Hint Lv 2, Hint Freq 50
    # Power +1, Init Power 30, Init Bond 20
    # Stat gain: Stamina +2, Power +6
    SupportCard(
        name="King Halo SSR",
        card_type=TrainingType.POWER,
        level=50,
        training_stats={TrainingType.POWER: Stats(stamina=2, power=6)},
        bonus_stats=Stats(power=1),
        initial_bond=20,
        initial_stats=Stats(power=30),
        friendship_bonus_percent=43,
        training_effectiveness_percent=10,
        specialty_rate=70,
    ),
]
