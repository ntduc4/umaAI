from uma_ai.career.models import CareerObjective, ObjectiveType, Stats

# Oguri Cap (Starlight Beat) - Original 3★
# Source: UMAWIKI-OGURI https://umamusu.wiki/Game:Oguri_Cap_(Starlight_Beat)
# Growth bonus 20% Speed, 10% Power sourced from GLOBAL-REF line 2848.

OGURI_CAP_BASE_STATS: Stats = Stats(
    speed=101,
    stamina=66,
    power=106,
    guts=84,
    wisdom=93,
)

OGURI_CAP_APTITUDES = {
    "turf": "A",
    "dirt": "B",
    "sprint": "E",
    "mile": "A",
    "medium": "A",
    "long": "B",
    "front": "F",
    "pace": "A",
    "late": "A",
    "end": "D",
}

OGURI_CAP_GROWTH_BONUS = {
    "speed": 20,
    "stamina": 0,
    "power": 10,
    "guts": 0,
    "wisdom": 0,
}

# PROJECT ASSUMPTION: exact deadline turn indices need verification.
# Race objectives based on Oguri Cap's URA career goals.
OGURI_CAP_URA_OBJECTIVES: list[CareerObjective] = [
    CareerObjective(
        id="oguri_junior_debut",
        description="Junior Debut",
        objective_type=ObjectiveType.RACE,
        deadline_turn_index=2,
        race_id="junior_debut",
        required_place=1,
    ),
    CareerObjective(
        id="oguri_fans_5000",
        description="Reach 5,000 fans",
        objective_type=ObjectiveType.FAN_COUNT,
        deadline_turn_index=20,
        required_fans=5_000,
    ),
    CareerObjective(
        id="oguri_satsuki_sho",
        description="Satsuki Sho - top 5",
        objective_type=ObjectiveType.RACE,
        deadline_turn_index=31,
        race_id="satsuki_sho",
        required_place=5,
    ),
    CareerObjective(
        id="oguri_japanese_derby",
        description="Japanese Derby - top 5",
        objective_type=ObjectiveType.RACE,
        deadline_turn_index=33,
        race_id="japanese_derby",
        required_place=5,
    ),
    CareerObjective(
        id="oguri_takarazuka_kinen",
        description="Takarazuka Kinen - top 3",
        objective_type=ObjectiveType.RACE,
        deadline_turn_index=35,
        race_id="takarazuka_kinen_classic",
        required_place=3,
    ),
    CareerObjective(
        id="oguri_fans_70000",
        description="Reach 70,000 fans",
        objective_type=ObjectiveType.FAN_COUNT,
        deadline_turn_index=50,
        required_fans=70_000,
    ),
    CareerObjective(
        id="oguri_takarazuka_kinen_senior",
        description="Takarazuka Kinen - top 3",
        objective_type=ObjectiveType.RACE,
        deadline_turn_index=55,
        race_id="takarazuka_kinen_senior",
        required_place=3,
    ),
    CareerObjective(
        id="oguri_fans_120000",
        description="Reach 120,000 fans",
        objective_type=ObjectiveType.FAN_COUNT,
        deadline_turn_index=62,
        required_fans=120_000,
    ),
]
