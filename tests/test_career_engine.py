from random import Random

from uma_ai.cards.manual import manual_support_card
from uma_ai.career.actions import RaceAction, RestAction, TrainAction, TrainingType
from uma_ai.career.engine import CareerEngine
from uma_ai.career.models import CareerState, Motivation, Stats
from uma_ai.scenarios.ura import URAScenario


def test_training_applies_stats_energy_motivation_support_and_bond() -> None:
    support = manual_support_card(
        name="Manual Speed SSR",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={TrainingType.SPEED: Stats(speed=4, power=2, skill_points=1)},
        initial_bond=40,
    )
    state = CareerState.new(Stats(speed=100, stamina=100, power=100, guts=100, wisdom=100), [support])
    state.motivation = Motivation.GREAT
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, TrainAction(TrainingType.SPEED))

    assert state.stats.speed == 117
    assert state.stats.power == 108
    assert state.stats.skill_points == 4
    assert state.energy == 79
    assert state.supports[0].bond == 47
    assert state.logs[-1].action == "train"


def test_friendship_bonus_applies_after_bond_threshold() -> None:
    support = manual_support_card(
        name="Manual Speed SSR",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={TrainingType.SPEED: Stats(speed=8)},
        initial_bond=80,
    )
    state = CareerState.new(Stats(), [support])
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, TrainAction(TrainingType.SPEED))

    assert state.stats.speed == 20
    assert state.supports[0].bond == 87


def test_wisdom_training_recovers_energy_and_cannot_fail() -> None:
    state = CareerState.new(Stats())
    state.energy = 1
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, TrainAction(TrainingType.WISDOM))

    assert state.energy == 6
    assert state.logs[-1].action == "train"


def test_rest_caps_energy_at_maximum() -> None:
    state = CareerState.new(Stats())
    state.energy = 90
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RestAction())

    assert state.energy == 100


def test_race_probability_is_bounded_and_race_logs_result() -> None:
    state = CareerState.new(Stats(speed=1200, stamina=1200, power=1200, guts=1200, wisdom=1200))
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RaceAction(name="Debut"))

    assert state.race_results[0].win_probability == 0.95
    assert state.race_results[0].won is True
    assert state.energy == 85
    assert state.stats.skill_points == 45


def test_ura_finals_force_race_action() -> None:
    state = CareerState.new(Stats(speed=1200, stamina=1200, power=1200, guts=1200, wisdom=1200))
    state.turn_index = 62
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, TrainAction(TrainingType.SPEED))

    assert state.race_results[0].race_name == "URA Finals Preliminary"
    assert state.stats.speed == 1200
    assert state.stats.skill_points == 40
