from __future__ import annotations

from math import floor
from random import Random

from uma_ai.career.actions import CareerAction, RaceAction, RecreationAction, RestAction, TrainAction, TrainingType
from uma_ai.career.models import CareerState, Condition, Motivation, ObjectiveType, RaceDefinition, RaceResult, Stats, TurnLogEntry
from uma_ai.career.scenario import Scenario


class CareerEngine:
    def __init__(self, scenario: Scenario, rng: Random | None = None) -> None:
        self.scenario = scenario
        self.rng = rng or Random()

    def current_turn(self, state: CareerState):
        return self.scenario.turns[state.turn_index]

    def is_complete(self, state: CareerState) -> bool:
        return state.turn_index >= len(self.scenario.turns)

    def legal_actions(self, state: CareerState) -> list[CareerAction]:
        if self.is_complete(state) or state.failed:
            return []

        turn = self.current_turn(state)
        forced_race = self._forced_race_for_turn(turn.label) if turn.is_ura_race else self._mandatory_race_for_turn(state)
        if forced_race is not None:
            return [RaceAction(name=forced_race.name, race_id=forced_race.id)]

        actions: list[CareerAction] = [TrainAction(training) for training in TrainingType]
        actions.extend([RestAction(), RecreationAction()])
        races = self.scenario.available_races(turn, state.fans)
        actions.extend(RaceAction(name=race.name, race_id=race.id) for race in self._filter_by_aptitude(state, races))
        return actions

    def step(self, state: CareerState, action: CareerAction) -> CareerState:
        if self.is_complete(state):
            raise ValueError("career is already complete")
        if state.failed:
            raise ValueError("career has already failed")

        turn = self.current_turn(state)
        self._apply_scenario_events(state)
        self._apply_condition_effects(state)

        forced_race = self._forced_race_for_turn(turn.label) if turn.is_ura_race else self._mandatory_race_for_turn(state)
        if forced_race is not None:
            action = RaceAction(name=forced_race.name, race_id=forced_race.id)

        if isinstance(action, TrainAction):
            self._train(state, action)
        elif isinstance(action, RestAction):
            self._rest(state)
        elif isinstance(action, RaceAction):
            self._race(state, action)
        elif isinstance(action, RecreationAction):
            self._recreation(state)
        else:
            raise TypeError(f"unsupported action: {action!r}")

        if not isinstance(action, RaceAction):
            state.consecutive_races = 0

        state.turn_index += 1
        self._check_objectives(state)
        return state

    def _train(self, state: CareerState, action: TrainAction) -> None:
        turn = self.current_turn(state)
        fail_rate = self.training_fail_rate(state.energy, action.training, state)
        failed = self.rng.random() < fail_rate
        if failed:
            self._apply_training_failure(state, action.training, fail_rate)
            return

        facility_level = state.facility_levels[action.training]
        if turn.is_summer_camp:
            facility_level = 5
        gains, energy_delta = self._calculate_training(state, action.training, facility_level)
        for support in self._placed_supports(state, action.training):
            bond_gain = support.card.bond_gain_on_training
            if Condition.CHARMING in state.conditions:
                bond_gain = bond_gain + 2
            support.bond = min(100, support.bond + bond_gain)

        state.stats.add(gains)
        state.energy += energy_delta
        state.clamp_energy()
        self._record_training_for_facility_level(state, action.training)
        # Source: GLOBAL-REF line 3770 — Extra Training: Occurrence after successful training: 6% Chance
        #   Top option:    +5 trained stat, -5 energy (20% chance cures a debuff)
        #   Bottom option: +5 energy
        extra_training = None
        if self.rng.random() < 0.06:
            if self.rng.random() < 0.50:
                extra_training = "top"
                growth = state.growth_rates.get(action.training.value, 0)
                bonus = floor(5 * (1 + growth / 100)) if growth else 5
                setattr(state.stats, action.training.value,
                        min(1200, getattr(state.stats, action.training.value) + bonus))
                state.energy -= 5
                if self.rng.random() < 0.20:
                    state.conditions.difference_update({Condition.POOR_PRACTICE, Condition.SKIN_OUTBREAK,
                                                        Condition.NIGHT_OWL, Condition.SLOW_METABOLISM})
            else:
                extra_training = "bottom"
                state.energy += 5
            state.clamp_energy()
        state.logs.append(
            TurnLogEntry(
                turn,
                "train",
                {
                    "training": action.training.value,
                    "facility_level": max(facility_level, state.facility_levels[action.training]),
                    "fail_rate": fail_rate,
                    "gains": gains,
                    "extra_training": extra_training,
                },
            )
        )

    def _rest(self, state: CareerState) -> None:
        turn = self.current_turn(state)
        # Source: GLOBAL-REF "Resting" probabilities
        #   70 Energy Rest: 25% Chance
        #   50 Energy Rest: 62.5% Chance
        #   30 Energy Rest: 10% Chance
        #   30 Energy Rest + Night Owl: 2.5% Chance
        # Weights: [250, 625, 100, 25] for [70, 50, 30, 30_nightowl]
        choice = self.rng.choices(
            ["70", "50", "30", "30_nightowl"],
            weights=[250, 625, 100, 25],
            k=1,
        )[0]
        recovered = 30 if choice.startswith("30") else int(choice)
        state.energy += recovered
        if choice == "30_nightowl":
            state.conditions.add(Condition.NIGHT_OWL)
        # Source: GLOBAL-REF line 2955 — resting in summer cures ailments
        if turn.is_summer_camp:
            state.conditions.difference_update({Condition.POOR_PRACTICE, Condition.SKIN_OUTBREAK, Condition.NIGHT_OWL})
        mood_delta = 1 if turn.is_summer_camp else 0
        if mood_delta:
            self._change_motivation(state, mood_delta)
        state.clamp_energy()
        state.logs.append(TurnLogEntry(turn, "rest", {"energy_recovered": recovered, "motivation_delta": mood_delta}))

    def _race(self, state: CareerState, action: RaceAction) -> None:
        turn = self.current_turn(state)
        race = self._resolve_race(turn.label, action)
        mandatory = turn.is_ura_race or self._mandatory_race_for_turn(state) is not None
        if not mandatory and race is not None and race.fan_requirement > state.fans:
            raise ValueError(f"not enough fans for {race.name}: need {race.fan_requirement}, have {state.fans}")

        starting_energy = state.energy
        probability = self.estimate_win_probability(state.stats)
        won = self.rng.random() < probability
        is_ura_race = turn.is_ura_race or bool(race and race.is_scenario_race)
        gains = self._race_rewards(race, won, is_ura_race, self._race_bonus_percent(state))
        state.stats.add(gains)
        fans_gained = self._fans_gained(race, won, self._fan_bonus_percent(state))
        state.fans += fans_gained
        state.energy += self.scenario.race_energy_delta(won, action.energy_choice)
        state.clamp_energy()
        penalty = self._apply_optional_race_penalty(state, starting_energy, mandatory)
        result = RaceResult(
            race_name=race.name if race is not None else action.name,
            win_probability=probability,
            won=won,
            stats_gained=gains,
            race_id=race.id if race is not None else action.race_id,
            fans_gained=fans_gained,
            placement=1 if won else 2,
        )
        state.race_results.append(result)
        state.logs.append(
            TurnLogEntry(
                turn,
                "race",
                {
                    "result": result,
                    "race_bonus_percent": self._race_bonus_percent(state),
                    "fan_bonus_percent": self._fan_bonus_percent(state),
                    "energy_choice": action.energy_choice.value,
                    "race_penalty": penalty,
                },
            )
        )

    def _recreation(self, state: CareerState) -> None:
        turn = self.current_turn(state)
        # Source: GLOBAL-REF "Recreation" probabilities
        #   Karaoke (+2 Mood): 35% Chance
        #   Stroll (+1 Mood, +10 Energy): 30% Chance
        #   Shrine (+1 Mood, +10 Energy): 20% Chance
        #   Shrine (+1 Mood, +20 Energy): 10% Chance
        #   Shrine (+1 Mood, +30 Energy): 5% Chance
        #   Bonus Crane game event afterwards: 25% Chance (not implemented)
        roll = self.rng.random()
        if roll < 0.35:
            outcome = "karaoke"
            energy_delta = 0
            motivation_delta = 2
        elif roll < 0.65:
            outcome = "stroll"
            energy_delta = 10
            motivation_delta = 1
        elif roll < 0.85:
            outcome = "shrine_10"
            energy_delta = 10
            motivation_delta = 1
        elif roll < 0.95:
            outcome = "shrine_20"
            energy_delta = 20
            motivation_delta = 1
        else:
            outcome = "shrine_30"
            energy_delta = 30
            motivation_delta = 1

        state.energy += energy_delta
        self._change_motivation(state, motivation_delta)
        # Source: GLOBAL-REF line 3740 — Bonus Crane game event afterwards: 25% Chance
        crane = False
        if self.rng.random() < 0.25:
            crane = True
            bonus = self.rng.choices([10, 20, 30], weights=[50, 35, 15], k=1)[0]
            state.energy += bonus
        state.clamp_energy()
        state.logs.append(
            TurnLogEntry(
                turn,
                "recreation",
                {"outcome": outcome, "energy_delta": energy_delta, "motivation_delta": motivation_delta,
                 "motivation": state.motivation.name, "crane_game": crane},
            )
        )

    def estimate_win_probability(self, stats: Stats) -> float:
        # Placeholder race model: enough to make search trade off stat growth vs racing.
        score = stats.total_without_skill_points + stats.skill_points * 0.25
        return max(0.05, min(0.95, score / 3000))

    def training_fail_rate(self, energy: int, training: TrainingType, state: CareerState | None = None) -> float:
        if training == TrainingType.WISDOM:
            return 0.0
        # PROJECT ASSUMPTION: base fail-rate-by-energy curve not yet directly sourced.
        # uma.guide states "scales inversely with Energy"; GLOBAL-REF gives outcome tier thresholds
        # (1-19%, 20-79%, 80-100%) but not the exact energy→rate formula.
        if energy >= 70:
            base = 0.0
        elif energy >= 50:
            base = 0.05
        elif energy >= 30:
            base = 0.15
        else:
            base = 0.30
        if state is None:
            return base
        # Source: GLOBAL-REF "Conditions"
        #   Practice Perfect:     -2% fail chance (line 3929)
        #   Practice Perfect◎:    -4% fail chance (line 3930)
        #   Poor Practice:        +2% fail chance (line 3940)
        #   Failure Protection:   multiplicative reduction from supports (GLOBAL-REF)
        failure_protection = sum(support.card.failure_protection_percent for support in state.supports)
        rate = base * (1 - failure_protection / 100)
        if Condition.PRACTICE_PERFECT in state.conditions:
            rate -= 0.02
        if Condition.PRACTICE_PERFECT_DOUBLE in state.conditions:
            rate -= 0.04
        if Condition.POOR_PRACTICE in state.conditions:
            rate += 0.02
        return round(max(0.0, rate), 2)

    def energy_delta_for_training(self, training: TrainingType) -> int:
        return self.scenario.training_energy_delta(training, self.scenario.turns[0], 1)

    def _calculate_training(self, state: CareerState, training: TrainingType, facility_level: int) -> tuple[Stats, int]:
        turn = self.current_turn(state)
        base = self.scenario.base_training_stats(training, turn, facility_level)
        base_energy = self.scenario.training_energy_delta(training, turn, facility_level)

        stat_bonuses = Stats()
        friendship_multiplier = 1.0
        mood_effect_percent = 0
        training_effectiveness_percent = 0
        energy_cost_reduction_percent = 0
        wisdom_friendship_recovery = 0
        support_count = 0

        placed = self._placed_supports(state, training)
        for support_state in placed:
            support_count += 1
            stat_bonuses.add(support_state.card.stat_bonus_for(training))
            mood_effect_percent += support_state.card.mood_effect_percent
            training_effectiveness_percent += support_state.card.training_effectiveness_percent
            energy_cost_reduction_percent += support_state.card.energy_cost_reduction_percent
            if support_state.card.is_friendship_training(training, support_state.bond):
                friendship_multiplier *= 1 + support_state.card.friendship_bonus_percent / 100
                if training == TrainingType.WISDOM:
                    wisdom_friendship_recovery += support_state.card.wisdom_friendship_recovery

        mood_multiplier = 1 + state.motivation.mood_value * (1 + mood_effect_percent / 100)
        training_effectiveness_multiplier = 1 + training_effectiveness_percent / 100
        character_count_multiplier = 1 + 0.05 * support_count

        def calc(base_value: int, bonus_value: int) -> int:
            if base_value == 0:
                return 0
            return floor(
                (base_value + bonus_value)
                * friendship_multiplier
                * mood_multiplier
                * training_effectiveness_multiplier
                * character_count_multiplier
            )

        gains = Stats(
            speed=calc(base.speed, stat_bonuses.speed),
            stamina=calc(base.stamina, stat_bonuses.stamina),
            power=calc(base.power, stat_bonuses.power),
            guts=calc(base.guts, stat_bonuses.guts),
            wisdom=calc(base.wisdom, stat_bonuses.wisdom),
            skill_points=calc(base.skill_points, stat_bonuses.skill_points),
        )
        growth = state.growth_rates
        if growth:
            gains = Stats(
                speed=floor(gains.speed * (1 + growth.get("speed", 0) / 100)),
                stamina=floor(gains.stamina * (1 + growth.get("stamina", 0) / 100)),
                power=floor(gains.power * (1 + growth.get("power", 0) / 100)),
                guts=floor(gains.guts * (1 + growth.get("guts", 0) / 100)),
                wisdom=floor(gains.wisdom * (1 + growth.get("wisdom", 0) / 100)),
                skill_points=gains.skill_points,
            )
        energy_delta = base_energy + wisdom_friendship_recovery
        if energy_delta < 0 and energy_cost_reduction_percent:
            energy_delta = -floor(abs(energy_delta) * (1 - energy_cost_reduction_percent / 100))
        return gains, energy_delta

    def _placed_supports(self, state: CareerState, training: TrainingType) -> list:
        # Source: GLOBAL-REF "Specialty Priority" (line 4936)
        # Each training type has a base weight of 100.
        # "Not appearing" has a weight of 50.
        # Specialty Priority ADDS to the card's own type weight.
        #   e.g. Kitasan Black with 80 specialty: Speed weight = 100 + 80 = 180
        #   Chance to appear on matching type = 180 / (180 + 100*4 + 50) = 28.6%
        # Non-matching types: 100 / total_weight
        #
        # PROJECT ASSUMPTION: unique-skill specialty multiplier (1.2x for Kitasan)
        #   is not modeled as a separate SupportCard field. Use specialty_rate to
        #   represent the final effective weight.
        placed = []
        all_types = list(TrainingType)
        not_appear_weight = 50
        base_weight = 100

        for support in state.supports:
            weights = []
            for t in all_types:
                w = base_weight
                if t == support.card.card_type:
                    w += support.card.specialty_rate
                weights.append(w)
            weights.append(not_appear_weight)
            chosen_index = self.rng.choices(range(len(weights)), weights=weights, k=1)[0]
            if chosen_index < len(all_types) and all_types[chosen_index] == training:
                placed.append(support)
        return placed

    @staticmethod
    def _filter_by_aptitude(state: CareerState, races: list) -> list:
        aptitudes = state.aptitudes
        if not aptitudes:
            return races
        filtered = []
        for race in races:
            surface_apt = aptitudes.get(race.surface.value, "A")
            dist_apt = aptitudes.get(race.distance_type.value, "A")
            if surface_apt in {"E", "F"} or dist_apt in {"E", "F"}:
                continue
            filtered.append(race)
        return filtered

    def _apply_scenario_events(self, state: CareerState) -> None:
        turn = self.current_turn(state)
        for event in self.scenario.scenario_events_for_turn(turn):
            if event.id in state.event_history:
                continue
            min_fans = event.min_fans
            if state.trainee_id in event.alternate_trainee_ids and event.alternate_min_fans is not None:
                min_fans = event.alternate_min_fans
            if state.fans < min_fans:
                continue
            if state.director_bond < event.min_director_bond:
                continue
            state.stats.add(event.stats)
            state.stats.skill_points += event.skill_points
            state.energy += event.energy_delta
            state.clamp_energy()
            if event.motivation_delta:
                self._change_motivation(state, event.motivation_delta)
            state.event_history.add(event.id)
            state.logs.append(TurnLogEntry(turn, "scenario_event", {"event": event}))

    def _record_training_for_facility_level(self, state: CareerState, training: TrainingType) -> None:
        state.training_counts[training] += 1
        next_level = min(5, state.training_counts[training] // 4 + 1)
        state.facility_levels[training] = max(state.facility_levels[training], next_level)

    def _resolve_race(self, turn_label: str, action: RaceAction) -> RaceDefinition | None:
        if action.race_id is not None:
            return self.scenario.race_by_id(action.race_id)
        return self._forced_race_for_turn(turn_label)

    def _forced_race_for_turn(self, turn_label: str) -> RaceDefinition | None:
        race_id_by_label = {
            "URA Finals Preliminary Race": "ura_preliminary",
            "URA Finals Semifinal Race": "ura_semifinal",
            "URA Finals Final Race": "ura_final",
        }
        race_id = race_id_by_label.get(turn_label)
        return self.scenario.race_by_id(race_id) if race_id else None

    def _mandatory_race_for_turn(self, state: CareerState) -> RaceDefinition | None:
        turn = self.current_turn(state)
        for objective in state.objectives:
            if objective.id in state.completed_objective_ids or objective.objective_type != ObjectiveType.RACE:
                continue
            if objective.deadline_turn_index == turn.index and objective.race_id is not None:
                return self.scenario.race_by_id(objective.race_id)
        return None

    def _check_objectives(self, state: CareerState) -> None:
        for objective in state.objectives:
            if objective.id in state.completed_objective_ids:
                continue
            if objective.objective_type == ObjectiveType.FAN_COUNT and state.fans >= objective.required_fans:
                state.completed_objective_ids.add(objective.id)
                continue
            if objective.objective_type == ObjectiveType.RACE:
                result = next((race for race in reversed(state.race_results) if race.race_id == objective.race_id), None)
                if result is not None and result.placement <= objective.required_place:
                    state.completed_objective_ids.add(objective.id)
                    continue
            if state.turn_index > objective.deadline_turn_index:
                state.failed = True

    def _race_bonus_percent(self, state: CareerState) -> int:
        return sum(support.card.race_bonus_percent for support in state.supports)

    def _fan_bonus_percent(self, state: CareerState) -> int:
        return sum(support.card.fan_bonus_percent for support in state.supports)

    def _race_rewards(self, race: RaceDefinition | None, won: bool, is_scenario_race: bool, race_bonus_percent: int) -> Stats:
        if is_scenario_race:
            base = self.scenario.race_stats(won=won, is_ura_race=True, race_id=race.id if race is not None else None)
        elif race is not None:
            base = race.stats_first if won else race.stats_other
            base = Stats(
                speed=base.speed,
                stamina=base.stamina,
                power=base.power,
                guts=base.guts,
                wisdom=base.wisdom,
                skill_points=race.skill_points_first if won else race.skill_points_other,
            )
            if won and base.total_without_skill_points:
                base = self._randomize_race_stat_reward(base)
        else:
            base = self.scenario.race_stats(won=won, is_ura_race=False, race_id=race.id if race is not None else None)
        return self._apply_race_bonus(base, race_bonus_percent)

    def _randomize_race_stat_reward(self, stats: Stats) -> Stats:
        total = stats.total_without_skill_points
        chosen = self.rng.choice(["speed", "stamina", "power", "guts", "wisdom"])
        return Stats(**{chosen: total}, skill_points=stats.skill_points)

    def _apply_race_bonus(self, stats: Stats, race_bonus_percent: int) -> Stats:
        multiplier = 1 + race_bonus_percent / 100
        return Stats(
            speed=floor(stats.speed * multiplier),
            stamina=floor(stats.stamina * multiplier),
            power=floor(stats.power * multiplier),
            guts=floor(stats.guts * multiplier),
            wisdom=floor(stats.wisdom * multiplier),
            skill_points=floor(stats.skill_points * multiplier),
        )

    def _fans_gained(self, race: RaceDefinition | None, won: bool, fan_bonus_percent: int) -> int:
        if race is None or not won:
            return 0
        return floor(race.fan_gain_first * (1 + fan_bonus_percent / 100))

    def _change_motivation(self, state: CareerState, delta: int) -> None:
        state.motivation = Motivation(max(Motivation.AWFUL, min(Motivation.GREAT, state.motivation + delta)))

    def _apply_optional_race_penalty(self, state: CareerState, starting_energy: int, mandatory: bool) -> dict[str, object]:
        if mandatory:
            return {"applied": False, "reason": "mandatory_race"}

        state.consecutive_races += 1
        streak = min(state.consecutive_races, 4)
        no_energy = starting_energy <= 0
        mood_chance = self._race_penalty_mood_chance(streak, no_energy)
        stat_loss_chance = 0.40 if streak >= 4 else 0.0

        mood_down = self.rng.random() < mood_chance
        stats_lost: list[str] = []
        if mood_down:
            self._change_motivation(state, -1)

        if self.rng.random() < stat_loss_chance:
            stats_lost = self._lose_random_stats(state, amount=10, count=3)

        return {
            "applied": mood_down or bool(stats_lost),
            "consecutive_races": state.consecutive_races,
            "no_energy": no_energy,
            "mood_down": mood_down,
            "stats_lost": stats_lost,
            "condition_effects_omitted": True,
        }

    def _race_penalty_mood_chance(self, streak: int, no_energy: bool) -> float:
        # Source: GLOBAL-REF optional race penalty table
        # Racing with positive energy:
        #   1st consecutive:  0% mood down
        #   2nd consecutive:  0% mood down
        #   3rd consecutive: 60% mood down
        #   4th+ consecutive: 100% mood down
        # Racing from zero energy:
        #   1st consecutive: 20% mood down
        #   2nd consecutive: 33% mood down
        #   3rd consecutive: 95% mood down
        #   4th+ consecutive: 100% mood down
        if no_energy:
            return {1: 0.20, 2: 0.33, 3: 0.95, 4: 1.0}[streak]
        return {1: 0.0, 2: 0.0, 3: 0.60, 4: 1.0}[streak]

    def _lose_random_stats(self, state: CareerState, amount: int, count: int) -> list[str]:
        stat_names = ["speed", "stamina", "power", "guts", "wisdom"]
        chosen = self.rng.sample(stat_names, k=count)
        for name in chosen:
            setattr(state.stats, name, max(0, getattr(state.stats, name) - amount))
        return chosen

    def _apply_training_failure(self, state: CareerState, training: TrainingType, fail_rate: float) -> None:
        turn = self.current_turn(state)
        trained_stat = training.value
        # Source: GLOBAL-REF "Failed trainings that consume energy"
        #   Failure percentages 1-19% → Normal tier (0% Worst)
        #   Failure percentages 20-79% → Mixed tier (~30% Worst, ~70% Normal)
        #   Failure percentages 80-100% → Worst tier (100% Worst)
        #
        # Normal tier (Get Well Soon!):
        #   Top option (92%): -1 mood, -5 trained stat
        #   Top option (8%):  -1 mood, -5 trained stat, Poor Practice
        #   Bottom (~30%):    -1 mood, -10 trained stat
        #   Bottom (~55%):    -1 mood, -10 trained stat, Poor Practice
        #   Bottom (~15%):    Practice Perfect
        #
        # Worst tier (Don't Overdo It!):
        #   Top option (50%):  -3 mood, +10 energy, -10 trained stat, -10 to 2 random stats
        #   Top option (50%):  -3 mood, +10 energy, -10 trained stat, -10 to 2 random stats, Poor Practice
        #   Bottom (~97%):     -3 mood, -10 trained stat, -10 to 2 random stats, Poor Practice
        #   Bottom (~3%):      +10 energy, Practice Perfect

        if fail_rate < 0.20:
            tier = "normal"
            option = "top"
        elif fail_rate < 0.80:
            tier = "normal" if self.rng.random() >= 0.30 else "worst"
            option = "top" if self.rng.random() < 0.50 else "bottom"
        else:
            tier = "worst"
            option = "top" if self.rng.random() < 0.50 else "bottom"

        if tier == "normal" and option == "top":
            if self.rng.random() < 0.08:
                state.conditions.add(Condition.POOR_PRACTICE)
            self._change_motivation(state, -1)
            state.stats = self._reduce_trained_stat(state.stats, trained_stat, 5)
        elif tier == "normal" and option == "bottom":
            roll = self.rng.random()
            if roll < 0.55:
                state.conditions.add(Condition.POOR_PRACTICE)
            elif roll < 0.70:
                state.conditions.add(Condition.PRACTICE_PERFECT)
            self._change_motivation(state, -1)
            state.stats = self._reduce_trained_stat(state.stats, trained_stat, 10)
        elif tier == "worst" and option == "top":
            if self.rng.random() < 0.50:
                state.conditions.add(Condition.POOR_PRACTICE)
            self._change_motivation(state, -3)
            state.energy += 10
            state.stats = self._reduce_trained_stat(state.stats, trained_stat, 10)
            self._lose_random_stats(state, amount=10, count=2)
        else:
            roll = self.rng.random()
            if roll < 0.03:
                state.conditions.add(Condition.PRACTICE_PERFECT)
                state.energy += 10
            else:
                state.conditions.add(Condition.POOR_PRACTICE)
                self._change_motivation(state, -3)
                state.stats = self._reduce_trained_stat(state.stats, trained_stat, 10)
                self._lose_random_stats(state, amount=10, count=2)

        state.clamp_energy()
        state.logs.append(
            TurnLogEntry(
                turn,
                "train_failed",
                {
                    "training": training.value,
                    "fail_rate": fail_rate,
                    "outcome_tier": tier,
                    "outcome_option": option,
                },
            )
        )

    @staticmethod
    def _reduce_trained_stat(stats: Stats, trained_stat: str, amount: int) -> Stats:
        stat_map = {
            "speed": "speed", "stamina": "stamina", "power": "power", "guts": "guts", "wisdom": "wisdom",
        }
        attr = stat_map.get(trained_stat)
        if attr:
            setattr(stats, attr, max(0, getattr(stats, attr) - amount))
        return stats

    def _apply_condition_effects(self, state: CareerState) -> None:
        # Source: GLOBAL-REF "Conditions" section (lines 3764-3766, 3943-3944)
        # Night Owl: acquired via 2.5% rest outcome (see _rest).
        #   Once active: 25% chance of -10 energy per turn; 23% chance of -1 mood when energy drains.
        # Skin Outbreak: mood randomly lowers regularly (rate is PROJECT ASSUMPTION: 25% per turn)
        # Slacker: 25% chance to skip training per turn; 23% chance of -1 mood when skipping occurs
        if Condition.NIGHT_OWL in state.conditions and self.rng.random() < 0.25:
            state.energy -= 10
            if self.rng.random() < 0.23:
                self._change_motivation(state, -1)
            state.clamp_energy()
        if Condition.SKIN_OUTBREAK in state.conditions and self.rng.random() < 0.25:
            self._change_motivation(state, -1)
        if Condition.SLACKER in state.conditions and self.rng.random() < 0.25:
            state.logs.append(
                TurnLogEntry(
                    self.current_turn(state), "slacker_skip", {"training_skipped": True}
                )
            )
