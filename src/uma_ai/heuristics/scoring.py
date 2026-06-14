from __future__ import annotations

from math import floor

from uma_ai.career.actions import CareerAction, RaceAction, RecreationAction, RestAction, TrainAction, TrainingType
from uma_ai.career.engine import CareerEngine
from uma_ai.career.models import CareerState, Motivation, ObjectiveType, Stats


class ActionScorer:
    def __init__(self, engine: CareerEngine) -> None:
        self.engine = engine

    def score(self, state: CareerState, action: CareerAction) -> float:
        if isinstance(action, TrainAction):
            return self._score_training(state, action)
        if isinstance(action, RestAction):
            return self._score_rest(state)
        if isinstance(action, RaceAction):
            return self._score_race(state, action)
        if isinstance(action, RecreationAction):
            return self._score_recreation(state)
        return 0.0

    def _score_training(self, state: CareerState, action: TrainAction) -> float:
        training = action.training
        fail_rate = self.engine.training_fail_rate(state.energy, training, state)
        fail_penalty = 10.0
        success_prob = 1 - fail_rate

        turn = self.engine.current_turn(state)
        facility_level = state.facility_levels[training]
        if turn.is_summer_camp:
            facility_level = 5
        base = self.engine.scenario.base_training_stats(training, turn, facility_level)

        growth = state.growth_rates
        total_stat_gain = 0.0
        for stat_name in ("speed", "stamina", "power", "guts", "wisdom"):
            base_val = getattr(base, stat_name)
            growth_mult = 1 + growth.get(stat_name, 0) / 100
            total_stat_gain += base_val * growth_mult

        expected_value = success_prob * (total_stat_gain + base.skill_points * 0.5) * 0.6
        expected_value -= fail_rate * fail_penalty
        return expected_value * state.motivation.training_multiplier

    def _score_rest(self, state: CareerState) -> float:
        energy_deficit = (100 - state.energy) / 100.0
        expected_recovery = (30 * 0.125 + 50 * 0.625 + 70 * 0.25)
        recovery_value = min(energy_deficit, expected_recovery / 100.0)
        return recovery_value * 8.0

    def _score_race(self, state: CareerState, action: RaceAction) -> float:
        turn = self.engine.current_turn(state)
        for obj in state.objectives:
            if obj.id in state.completed_objective_ids:
                continue
            if obj.objective_type == ObjectiveType.RACE and obj.deadline_turn_index == turn.index:
                return 100.0

        win_prob = self.engine.estimate_win_probability(state.stats)
        energy_value = -15 / 100.0

        fan_value = 0.0
        race = self.engine.scenario.race_by_id(action.race_id) if action.race_id else None
        if race is not None:
            fan_value = race.fan_gain_first / 10000.0

        fan_pressure = 0.0
        for obj in state.objectives:
            if obj.id in state.completed_objective_ids:
                continue
            if obj.objective_type == ObjectiveType.FAN_COUNT:
                turns_left = obj.deadline_turn_index - turn.index
                if turns_left <= 0:
                    continue
                fan_deficit = max(0, obj.required_fans - state.fans)
                if race is not None and race.fan_gain_first > 0:
                    deficit_fraction = fan_deficit / max(1, obj.required_fans)
                    fan_pressure = max(fan_pressure, deficit_fraction * 30.0)
            if obj.objective_type == ObjectiveType.RACE and obj.race_id is not None:
                obj_race = self.engine.scenario.race_by_id(obj.race_id)
                if obj_race is not None and obj_race.fan_requirement > state.fans:
                    turns_left = max(1, obj.deadline_turn_index - turn.index)
                    fan_pressure = max(fan_pressure, 30.0 / turns_left)

        consecutive_penalty = 0.0
        if state.consecutive_races >= 2:
            consecutive_penalty = state.consecutive_races * 3.0

        return win_prob * (5.0 + fan_value * 10) + energy_value + fan_pressure + 25.0 - consecutive_penalty

    def _score_recreation(self, state: CareerState) -> float:
        if state.motivation >= Motivation.GREAT:
            return 0.0
        mood_deficit = (Motivation.GREAT - state.motivation) / 4.0
        return mood_deficit * 6.0
