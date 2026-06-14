from __future__ import annotations

from abc import ABC, abstractmethod

from uma_ai.career.actions import TrainingType
from uma_ai.career.models import Stats, Turn


class Scenario(ABC):
    """Scenario contract so URA can later be replaced by Aoharu, MANT, etc."""

    name: str

    @property
    @abstractmethod
    def turns(self) -> list[Turn]:
        raise NotImplementedError

    @abstractmethod
    def base_training_stats(self, training: TrainingType, turn: Turn) -> Stats:
        raise NotImplementedError

    @abstractmethod
    def race_stats(self, won: bool, is_ura_race: bool) -> Stats:
        raise NotImplementedError
