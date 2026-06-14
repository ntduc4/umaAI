from __future__ import annotations

from random import Random

from uma_ai.career.actions import CareerAction, RaceAction, RecreationAction, RestAction, TrainAction, TrainingType
from uma_ai.career.models import CareerState, Motivation, RaceResult, Stats, TurnLogEntry
from uma_ai.career.scenario import Scenario


class CareerEngine:
    def __init__(self, scenario: Scenario, rng: Random | None = None) -> None:
        self.scenario = scenario
        self.rng = rng or Random()

    def current_turn(self, state: CareerState):
        return self.scenario.turns[state.turn_index]

    def is_complete(self, state: CareerState) -> bool:
        return state.turn_index >= len(self.scenario.turns)

    def step(self, state: CareerState, action: CareerAction) -> CareerState:
        if self.is_complete(state):
            raise ValueError("career is already complete")

        turn = self.current_turn(state)
        if turn.is_ura_race and not isinstance(action, RaceAction):
            action = RaceAction(name=turn.label)

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

        state.turn_index += 1
        return state

    def _train(self, state: CareerState, action: TrainAction) -> None:
        turn = self.current_turn(state)
        fail_rate = self.training_fail_rate(state.energy, action.training)
        failed = self.rng.random() < fail_rate
        if failed:
            state.energy -= 10
            state.clamp_energy()
            state.logs.append(TurnLogEntry(turn, "train_failed", {"training": action.training.value, "fail_rate": fail_rate}))
            return

        gains = self.scenario.base_training_stats(action.training, turn)
        for support in state.supports:
            gains.add(support.card.stats_for(action.training, support.bond))
            if support.card.card_type == action.training:
                support.bond = min(100, support.bond + support.card.bond_gain_on_training)

        gains.add(self._training_secondary_bonus(action.training))
        state.stats.add(gains, state.motivation.training_multiplier)
        state.energy += self.energy_delta_for_training(action.training)
        state.clamp_energy()
        state.logs.append(
            TurnLogEntry(
                turn,
                "train",
                {"training": action.training.value, "fail_rate": fail_rate, "gains": gains},
            )
        )

    def _rest(self, state: CareerState) -> None:
        turn = self.current_turn(state)
        recovered = self.rng.randint(30, 70)
        state.energy += recovered
        state.clamp_energy()
        state.logs.append(TurnLogEntry(turn, "rest", {"energy_recovered": recovered}))

    def _race(self, state: CareerState, action: RaceAction) -> None:
        turn = self.current_turn(state)
        probability = self.estimate_win_probability(state.stats)
        won = self.rng.random() < probability
        gains = self.scenario.race_stats(won=won, is_ura_race=turn.is_ura_race)
        state.stats.add(gains)
        state.energy -= 15
        state.clamp_energy()
        result = RaceResult(action.name, probability, won, gains)
        state.race_results.append(result)
        state.logs.append(TurnLogEntry(turn, "race", {"result": result}))

    def _recreation(self, state: CareerState) -> None:
        turn = self.current_turn(state)
        state.energy += 20
        state.motivation = Motivation(min(Motivation.GREAT, state.motivation + 1))
        state.clamp_energy()
        state.logs.append(TurnLogEntry(turn, "recreation", {"motivation": state.motivation.name}))

    def estimate_win_probability(self, stats: Stats) -> float:
        # Placeholder race model: enough to make search trade off stat growth vs racing.
        score = stats.total_without_skill_points + stats.skill_points * 0.25
        return max(0.05, min(0.95, score / 3000))

    def training_fail_rate(self, energy: int, training: TrainingType) -> float:
        if training == TrainingType.WISDOM:
            return 0.0
        if energy >= 70:
            return 0.0
        if energy >= 50:
            return 0.05
        if energy >= 30:
            return 0.15
        return 0.30

    def energy_delta_for_training(self, training: TrainingType) -> int:
        return 5 if training == TrainingType.WISDOM else -21

    def _training_secondary_bonus(self, training: TrainingType) -> Stats:
        return {
            TrainingType.SPEED: Stats(power=5, skill_points=2),
            TrainingType.STAMINA: Stats(guts=5, skill_points=2),
            TrainingType.POWER: Stats(stamina=5, skill_points=2),
            TrainingType.GUTS: Stats(speed=3, power=3, skill_points=2),
            TrainingType.WISDOM: Stats(speed=2, skill_points=5),
        }[training]
