from uma_ai.career.actions import TrainingType
from uma_ai.scenarios.ura import URAScenario


def test_ura_calendar_matches_training_period_and_finals() -> None:
    scenario = URAScenario()

    assert len(scenario.turns) == 65
    assert scenario.turns[0].label == "Junior 06 early"
    assert scenario.turns[61].label == "Senior 12 late"
    assert [turn.label for turn in scenario.turns[-3:]] == [
        "URA Finals Preliminary",
        "URA Finals Semifinal",
        "URA Finals Final",
    ]
    assert all(turn.is_ura_race for turn in scenario.turns[-3:])


def test_ura_summer_camp_is_classic_and_senior_july_august() -> None:
    camp_turns = [turn for turn in URAScenario().turns if turn.is_summer_camp]

    assert len(camp_turns) == 8
    assert {(turn.year, turn.month) for turn in camp_turns} == {
        ("Classic", 7),
        ("Classic", 8),
        ("Senior", 7),
        ("Senior", 8),
    }


def test_summer_camp_boosts_training_base_stats() -> None:
    scenario = URAScenario()
    normal_turn = scenario.turns[0]
    camp_turn = next(turn for turn in scenario.turns if turn.is_summer_camp)

    assert scenario.base_training_stats(TrainingType.SPEED, normal_turn).speed == 10
    assert scenario.base_training_stats(TrainingType.SPEED, camp_turn).speed == 12
