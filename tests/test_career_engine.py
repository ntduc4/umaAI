from random import Random

from uma_ai.cards.manual import manual_support_card
from uma_ai.career.actions import RaceAction, RaceEnergyChoice, RecreationAction, RestAction, TrainAction, TrainingType
from uma_ai.career.engine import CareerEngine
from uma_ai.career.models import CareerObjective, CareerState, Motivation, ObjectiveType, Stats
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
    assert state.stats.skill_points == 3
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
        friendship_bonus_percent=20,
    )
    state = CareerState.new(Stats(), [support])
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, TrainAction(TrainingType.SPEED))

    assert state.stats.speed == 22
    assert state.supports[0].bond == 87


def test_support_training_uses_mood_training_effect_and_energy_reduction() -> None:
    support = manual_support_card(
        name="Manual Speed SSR",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={TrainingType.SPEED: Stats(speed=4)},
        initial_bond=80,
        friendship_bonus_percent=20,
        mood_effect_percent=20,
        training_effectiveness_percent=10,
        energy_cost_reduction_percent=10,
    )
    state = CareerState.new(Stats(), [support])
    state.motivation = Motivation.GREAT
    state.event_history.add("ura_opening")
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, TrainAction(TrainingType.SPEED))

    assert state.stats.speed == 24
    assert state.stats.power == 8
    assert state.stats.skill_points == 3
    assert state.energy == 82


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


def test_rest_uses_sourced_discrete_recovery_values() -> None:
    recovered_values = set()

    for seed in range(50):
        state = CareerState.new(Stats())
        state.energy = 0
        engine = CareerEngine(URAScenario(), rng=Random(seed))
        engine.step(state, RestAction())
        recovered_values.add(state.logs[-1].details["energy_recovered"])

    assert recovered_values == {30, 50, 70}


def test_race_probability_is_bounded_and_race_logs_result() -> None:
    state = CareerState.new(Stats(speed=1200, stamina=1200, power=1200, guts=1200, wisdom=1200))
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RaceAction(name="Debut"))

    assert state.race_results[0].win_probability == 0.95
    assert state.race_results[0].won is True
    assert state.energy == 85
    assert state.stats.skill_points == 45


def test_ura_finals_training_turn_allows_normal_actions() -> None:
    state = CareerState.new(Stats(speed=1200, stamina=1200, power=1200, guts=1200, wisdom=1200))
    state.turn_index = 62
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, TrainAction(TrainingType.SPEED))

    assert state.race_results == []
    assert state.stats.speed == 1200
    assert state.stats.power == 1200


def test_ura_finals_race_turn_forces_race_action() -> None:
    state = CareerState.new(Stats(speed=1200, stamina=1200, power=1200, guts=1200, wisdom=1200))
    state.turn_index = 63
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, TrainAction(TrainingType.SPEED))

    assert state.race_results[0].race_name == "URA Finals Preliminary"
    assert state.race_results[0].race_id == "ura_preliminary"
    assert state.stats.speed == 1200
    assert state.stats.skill_points == 40


def test_legal_actions_include_training_rest_recreation_and_available_races() -> None:
    state = CareerState.new(Stats())
    state.turn_index = 1
    engine = CareerEngine(URAScenario(), rng=Random(1))

    actions = engine.legal_actions(state)

    assert TrainAction(TrainingType.SPEED) in actions
    assert RestAction() in actions
    assert any(isinstance(action, RaceAction) and action.race_id == "junior_debut" for action in actions)


def test_legal_actions_hide_races_when_fans_are_too_low() -> None:
    state = CareerState.new(Stats())
    state.turn_index = 12
    engine = CareerEngine(URAScenario(), rng=Random(1))

    actions = engine.legal_actions(state)

    assert not any(isinstance(action, RaceAction) and action.race_id == "asahi_hai_fs" for action in actions)


def test_race_action_uses_schedule_rewards_and_fans() -> None:
    state = CareerState.new(Stats(speed=1200, stamina=1200, power=1200, guts=1200, wisdom=1200))
    state.turn_index = 1
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RaceAction(name="Junior Debut", race_id="junior_debut"))

    assert state.fans == 700
    assert state.race_results[0].fans_gained == 700
    assert state.race_results[0].race_id == "junior_debut"
    assert state.stats.skill_points == 45


def test_g1_race_rewards_apply_race_and_fan_bonus() -> None:
    support = manual_support_card(
        name="Manual Race Bonus SSR",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={},
        race_bonus_percent=35,
        fan_bonus_percent=10,
    )
    state = CareerState.new(Stats(speed=1200, stamina=1200, power=1200, guts=1200, wisdom=1200), [support])
    state.turn_index = 12
    state.fans = 7000
    state.event_history.add("ura_opening")
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RaceAction(name="Asahi Hai Futurity Stakes", race_id="asahi_hai_fs"))

    assert state.stats.skill_points == 60
    assert state.race_results[0].stats_gained.speed == 13
    assert state.race_results[0].stats_gained.total_without_skill_points == 13
    assert state.race_results[0].fans_gained == 7700
    assert state.energy == 85


def test_recreation_uses_reference_outcome_table() -> None:
    outcomes = set()

    for seed in range(50):
        state = CareerState.new(Stats())
        state.energy = 50
        engine = CareerEngine(URAScenario(), rng=Random(seed))
        engine.step(state, RecreationAction())
        outcomes.add(state.logs[-1].details["outcome"])

    assert outcomes == {"karaoke", "stroll", "shrine_10", "shrine_20", "shrine_30"}


def test_summer_camp_rest_raises_motivation() -> None:
    state = CareerState.new(Stats())
    state.energy = 0
    state.turn_index = 26
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RestAction())

    assert state.motivation == Motivation.GOOD
    assert state.logs[-1].details["motivation_delta"] == 1


def test_reference_ura_fan_events_require_fans() -> None:
    state = CareerState.new(Stats())
    state.turn_index = 34
    state.fans = 50_000
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RestAction())

    assert "aoi_three_legged_race" in state.event_history
    assert state.stats.wisdom == 20
    assert state.stats.skill_points == 20


def test_senior_early_april_fan_meeting_requires_fans_and_director_bond() -> None:
    state = CareerState.new(Stats())
    state.turn_index = 44
    state.fans = 70_000
    state.director_bond = 60
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RestAction())

    assert state.motivation == Motivation.GOOD
    assert "senior_early_april_fan_meeting" in state.event_history


def test_senior_early_april_fan_meeting_has_lower_urara_falcon_threshold() -> None:
    state = CareerState.new(Stats())
    state.turn_index = 44
    state.fans = 60_000
    state.director_bond = 60
    state.trainee_id = "haru_urara"
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RestAction())

    assert "senior_early_april_fan_meeting" in state.event_history


def test_senior_early_april_fan_meeting_does_not_trigger_without_director_bond() -> None:
    state = CareerState.new(Stats())
    state.turn_index = 44
    state.fans = 70_000
    state.director_bond = 59
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RestAction())

    assert "senior_early_april_fan_meeting" not in state.event_history


def test_optional_race_penalty_applies_on_third_consecutive_race() -> None:
    state = CareerState.new(Stats(speed=1200, stamina=1200, power=1200, guts=1200, wisdom=1200))
    state.turn_index = 1
    state.consecutive_races = 2
    state.motivation = Motivation.GREAT
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RaceAction(name="Junior Debut", race_id="junior_debut"))

    assert state.consecutive_races == 3
    assert state.logs[-1].details["race_penalty"]["consecutive_races"] == 3


def test_optional_race_win_stat_reward_uses_random_stat() -> None:
    rewarded_stats = set()

    for seed in range(20):
        state = CareerState.new(Stats(speed=1000, stamina=1000, power=1000, guts=1000, wisdom=1000))
        state.turn_index = 12
        state.fans = 7000
        engine = CareerEngine(URAScenario(), rng=Random(seed))
        engine.step(state, RaceAction(name="Asahi Hai Futurity Stakes", race_id="asahi_hai_fs"))
        gained = state.race_results[0].stats_gained
        for stat_name in ("speed", "stamina", "power", "guts", "wisdom"):
            if getattr(gained, stat_name):
                rewarded_stats.add(stat_name)

    assert len(rewarded_stats) > 1


def test_failure_protection_reduces_fail_rate() -> None:
    support = manual_support_card(
        name="Manual Failure Protection",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={},
        failure_protection_percent=35,
    )
    state = CareerState.new(Stats(), [support])
    engine = CareerEngine(URAScenario(), rng=Random(1))

    assert engine.training_fail_rate(state.energy, TrainingType.SPEED, state) == 0.0
    state.energy = 50
    assert engine.training_fail_rate(state.energy, TrainingType.SPEED, state) == 0.03


def test_ura_scenario_race_rewards_are_affected_by_race_bonus() -> None:
    support = manual_support_card(
        name="Manual Race Bonus SSR",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={},
        race_bonus_percent=35,
    )
    state = CareerState.new(Stats(speed=100, stamina=100, power=100, guts=100, wisdom=100), [support])
    state.turn_index = 63
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RaceAction(name="URA Finals Preliminary", race_id="ura_preliminary"))

    assert state.race_results[0].stats_gained.speed == 13
    assert state.race_results[0].stats_gained.skill_points == 54


def test_ura_scenario_race_rewards_use_stage_specific_skill_points() -> None:
    scenario = URAScenario()

    assert scenario.race_stats(won=True, is_ura_race=True, race_id="ura_preliminary").skill_points == 40
    assert scenario.race_stats(won=True, is_ura_race=True, race_id="ura_semifinal").skill_points == 60
    assert scenario.race_stats(won=True, is_ura_race=True, race_id="ura_final").skill_points == 80


def test_ura_races_ignore_mant_twinkle_star_energy_choices() -> None:
    state = CareerState.new(Stats(speed=1200, stamina=1200, power=1200, guts=1200, wisdom=1200))
    state.turn_index = 1
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, RaceAction(name="Junior Debut", race_id="junior_debut", energy_choice=RaceEnergyChoice.GAMBLE))

    assert state.race_results[0].won is True
    assert state.energy == 85


def test_facility_level_increases_after_repeated_training() -> None:
    state = CareerState.new(Stats())
    state.event_history.add("ura_opening")
    engine = CareerEngine(URAScenario(), rng=Random(1))

    for _ in range(4):
        engine.step(state, TrainAction(TrainingType.SPEED))

    assert state.training_counts[TrainingType.SPEED] == 4
    assert state.facility_levels[TrainingType.SPEED] == 2


def test_mandatory_objective_forces_race_and_marks_complete() -> None:
    state = CareerState.new(Stats(speed=1200, stamina=1200, power=1200, guts=1200, wisdom=1200))
    state.turn_index = 1
    state.objectives.append(
        CareerObjective(
            id="debut",
            description="Run debut race",
            objective_type=ObjectiveType.RACE,
            deadline_turn_index=2,
            race_id="junior_debut",
            required_place=1,
        )
    )
    engine = CareerEngine(URAScenario(), rng=Random(1))

    actions = engine.legal_actions(state)
    engine.step(state, TrainAction(TrainingType.SPEED))

    assert actions == [RaceAction(name="Junior Debut", race_id="junior_debut")]
    assert state.completed_objective_ids == {"debut"}
    assert state.failed is False


def test_support_card_specialty_rate_defaults_to_zero() -> None:
    from uma_ai.career.models import SupportCard

    card = SupportCard(name="Test", card_type=TrainingType.SPEED, level=1, training_stats={})
    assert card.specialty_rate == 0


def test_support_card_specialty_rate_can_be_set() -> None:
    support = manual_support_card(
        name="Kitasan Black",
        card_type=TrainingType.SPEED,
        level=45,
        training_stats={TrainingType.SPEED: Stats(speed=6, power=2)},
        initial_bond=25,
        friendship_bonus_percent=20,
        training_effectiveness_percent=5,
        race_bonus_percent=5,
        fan_bonus_percent=10,
        mood_effect_percent=20,
        specialty_rate=20,
    )
    assert support.specialty_rate == 20


def test_support_always_placed_on_matching_type_with_high_specialty_rate() -> None:
    support = manual_support_card(
        name="High Priority Speed",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={},
        specialty_rate=80,
    )
    state = CareerState.new(Stats(), [support])
    engine = CareerEngine(URAScenario(), rng=Random(0))

    placed = engine._placed_supports(state, TrainingType.SPEED)
    assert len(placed) == 1
    assert placed[0].card.name == "High Priority Speed"


def test_support_can_be_absent_on_non_matching_type() -> None:
    support = manual_support_card(
        name="Speed Only",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={TrainingType.SPEED: Stats(speed=10)},
        specialty_rate=0,
    )
    state = CareerState.new(Stats(), [support])
    engine = CareerEngine(URAScenario(), rng=Random(0))

    placed = engine._placed_supports(state, TrainingType.STAMINA)
    assert len(placed) == 0


def test_training_only_counts_placed_supports() -> None:
    support = manual_support_card(
        name="Speed Card",
        card_type=TrainingType.SPEED,
        level=50,
        training_stats={TrainingType.SPEED: Stats(speed=10)},
        specialty_rate=0,
    )
    state = CareerState.new(Stats(), [support])
    state.event_history.add("ura_opening")
    engine = CareerEngine(URAScenario(), rng=Random(1))

    engine.step(state, TrainAction(TrainingType.STAMINA))
    assert state.stats.stamina == 9
    assert state.stats.speed == 0
