from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TrainingType(StrEnum):
    SPEED = "speed"
    STAMINA = "stamina"
    POWER = "power"
    GUTS = "guts"
    WISDOM = "wisdom"


class RaceEnergyChoice(StrEnum):
    CONSISTENT = "consistent"
    GAMBLE = "gamble"


@dataclass(frozen=True)
class TrainAction:
    training: TrainingType


@dataclass(frozen=True)
class RestAction:
    pass


@dataclass(frozen=True)
class RaceAction:
    name: str = "Optional Race"
    race_id: str | None = None
    target_rank: int = 1
    energy_choice: RaceEnergyChoice = RaceEnergyChoice.CONSISTENT


@dataclass(frozen=True)
class RecreationAction:
    pass


CareerAction = TrainAction | RestAction | RaceAction | RecreationAction
