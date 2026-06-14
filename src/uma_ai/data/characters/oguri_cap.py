from uma_ai.career.models import CareerObjective, ObjectiveType, Stats

# Oguri Cap (Starlight Beat) - Original 3★
# Source: UMAWIKI-OGURI https://umamusu.wiki/Game:Oguri_Cap_(Starlight_Beat)
# Objectives: GT-OGURI https://gametora.com/umamusume/characters/100601-oguri-cap
# Growth bonus 20% Speed, 10% Power sourced from GLOBAL-REF line 2848.
#
# Calendar has 10 pre-debut turns (Junior Jan-May) → GameTora turns = our indices.
# Debut at turn 12 matches GameTora numbering exactly.

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

# Real objectives from GameTora: https://gametora.com/umamusume/characters/100601-oguri-cap
# Turn numbers match GameTora (10 pre-debut turns included in our calendar)
OGURI_CAP_URA_OBJECTIVES: list[CareerObjective] = [
    # 1. Junior Debut — Turn 12, Junior Late June
    CareerObjective(
        id="oguri_debut",
        description="Junior Debut",
        objective_type=ObjectiveType.RACE,
        deadline_turn_index=12,
        race_id="junior_debut",
        required_place=1,
    ),
    # 2. 3000 fans — Turn 24, Junior Late December
    CareerObjective(
        id="oguri_fans_3000",
        description="Reach 3,000 fans",
        objective_type=ObjectiveType.FAN_COUNT,
        deadline_turn_index=24,
        required_fans=3_000,
    ),
    # 3. NHK Mile Cup top 5 — Turn 33, Classic Early May
    CareerObjective(
        id="oguri_nhk_mile_cup",
        description="NHK Mile Cup - top 5",
        objective_type=ObjectiveType.RACE,
        deadline_turn_index=33,
        race_id="nhk_mile_cup",
        required_place=5,
    ),
    # 4. Mile Championship top 3 — Turn 46, Classic Late November
    CareerObjective(
        id="oguri_mile_championship",
        description="Mile Championship - top 3",
        objective_type=ObjectiveType.RACE,
        deadline_turn_index=46,
        race_id="mile_championship_classic",
        required_place=3,
    ),
    # 5. Arima Kinen top 3 — Turn 48, Classic Late December
    CareerObjective(
        id="oguri_arima_kinen_classic",
        description="Arima Kinen - top 3",
        objective_type=ObjectiveType.RACE,
        deadline_turn_index=48,
        race_id="arima_kinen_classic",
        required_place=3,
    ),
    # 6. 2 G1 races top 3 — Turn 60, Senior Late June
    CareerObjective(
        id="oguri_2_g1_races",
        description="2 G1 races - top 3",
        objective_type=ObjectiveType.G1_COUNT,
        deadline_turn_index=60,
        required_place=3,
        required_fans=2,
    ),
    # 7. Tenno Sho Autumn 1st — Turn 68, Senior Late October
    CareerObjective(
        id="oguri_tenno_sho_autumn",
        description="Tenno Sho Autumn - 1st",
        objective_type=ObjectiveType.RACE,
        deadline_turn_index=68,
        race_id="tenno_sho_autumn_senior",
        required_place=1,
    ),
    # 8. Arima Kinen 1st — Turn 72, Senior Late December
    CareerObjective(
        id="oguri_arima_kinen_senior",
        description="Arima Kinen - 1st",
        objective_type=ObjectiveType.RACE,
        deadline_turn_index=72,
        race_id="arima_kinen_senior",
        required_place=1,
    ),
]
