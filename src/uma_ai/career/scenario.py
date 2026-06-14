from __future__ import annotations

from abc import ABC, abstractmethod

from uma_ai.career.actions import RaceEnergyChoice, TrainingType
from uma_ai.career.models import RaceDefinition, ScenarioEvent, Stats, Turn


class Scenario(ABC):
    """Scenario contract so URA can later be replaced by Aoharu, MANT, etc."""

    name: str

    @property
    @abstractmethod
    def turns(self) -> list[Turn]:
        raise NotImplementedError

    @abstractmethod
    def base_training_stats(self, training: TrainingType, turn: Turn, facility_level: int = 1) -> Stats:
        raise NotImplementedError

    @abstractmethod
    def race_stats(self, won: bool, is_ura_race: bool, race_id: str | None = None) -> Stats:
        raise NotImplementedError

    def training_energy_delta(self, training: TrainingType, turn: Turn, facility_level: int = 1) -> int:
        return 5 if training == TrainingType.WISDOM else -21

    def race_energy_delta(self, won: bool, energy_choice: RaceEnergyChoice) -> int:
        return -15

    def available_races(self, turn: Turn, fans: int) -> list[RaceDefinition]:
        return []

    def race_by_id(self, race_id: str) -> RaceDefinition | None:
        return None

    def scenario_events_for_turn(self, turn: Turn) -> list[ScenarioEvent]:
        return []
