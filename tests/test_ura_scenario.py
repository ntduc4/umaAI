from uma_ai.career.actions import TrainingType
from uma_ai.career.models import RaceGrade
from uma_ai.scenarios.ura import URAScenario


def test_ura_calendar_matches_training_period_and_finals() -> None:
    scenario = URAScenario()

    assert len(scenario.turns) == 78
    assert scenario.turns[10].label == "Junior 06 early"
    assert scenario.turns[71].label == "Senior 12 late"
    assert [turn.label for turn in scenario.turns[-6:]] == [
        "URA Finals Preliminary Training",
        "URA Finals Preliminary Race",
        "URA Finals Semifinal Training",
        "URA Finals Semifinal Race",
        "URA Finals Final Training",
        "URA Finals Final Race",
    ]
    assert [turn.is_ura_race for turn in scenario.turns[-6:]] == [False, True, False, True, False, True]


def test_ura_summer_camp_is_classic_and_senior_july_august() -> None:
    camp_turns = [turn for turn in URAScenario().turns if turn.is_summer_camp]

    assert len(camp_turns) == 8
    assert {(turn.year, turn.month) for turn in camp_turns} == {
        ("Classic", 7),
        ("Classic", 8),
        ("Senior", 7),
        ("Senior", 8),
    }


def test_summer_camp_is_calendar_only_until_sourced_rule_is_added() -> None:
    scenario = URAScenario()
    normal_turn = scenario.turns[0]
    camp_turn = next(turn for turn in scenario.turns if turn.is_summer_camp)

    assert scenario.base_training_stats(TrainingType.SPEED, normal_turn).speed == 10
    assert scenario.base_training_stats(TrainingType.SPEED, camp_turn).speed == 10


def test_training_facility_level_changes_base_stats() -> None:
    scenario = URAScenario()

    assert scenario.base_training_stats(TrainingType.SPEED, scenario.turns[0], facility_level=1).speed == 10
    assert scenario.base_training_stats(TrainingType.SPEED, scenario.turns[0], facility_level=5).speed == 14
    assert scenario.base_training_stats(TrainingType.SPEED, scenario.turns[0], facility_level=5).power == 7
    assert scenario.training_energy_delta(TrainingType.SPEED, scenario.turns[0], facility_level=5) == -27


def test_ura_has_common_race_schedule_entries() -> None:
    scenario = URAScenario()
    race = scenario.race_by_id("japanese_derby")

    assert race is not None
    assert race.name == "Japanese Derby"
    assert race.grade == RaceGrade.G1
    assert race.month == 5
    assert race.half == "late"


def test_ura_available_races_filter_by_turn_and_fans() -> None:
    scenario = URAScenario()
    junior_debut_turn = scenario.turns[11]
    asahi_turn = scenario.turns[22]

    assert [race.id for race in scenario.available_races(junior_debut_turn, fans=0)] == ["junior_debut"]
    assert scenario.available_races(asahi_turn, fans=0) == []
    assert [race.id for race in scenario.available_races(asahi_turn, fans=7000)] == ["asahi_hai_fs"]


def test_ura_fixed_scenario_events_are_exposed_by_turn() -> None:
    scenario = URAScenario()

    assert scenario.scenario_events_for_turn(scenario.turns[29]) == []
    assert [event.id for event in scenario.scenario_events_for_turn(scenario.turns[44])] == ["aoi_three_legged_race"]
    assert [event.id for event in scenario.scenario_events_for_turn(scenario.turns[47])] == ["classic_100k_fans"]
    assert [event.id for event in scenario.scenario_events_for_turn(scenario.turns[54])] == ["senior_early_april_fan_meeting"]
    assert [event.id for event in scenario.scenario_events_for_turn(scenario.turns[71])] == ["senior_240k_fans"]
