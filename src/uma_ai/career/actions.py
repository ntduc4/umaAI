from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TrainingType(StrEnum):
    SPEED = "speed"
    STAMINA = "stamina"
    POWER = "power"
    GUTS = "guts"
    WISDOM = "wisdom"


@dataclass(frozen=True)
class TrainAction:
    training: TrainingType


@dataclass(frozen=True)
class RestAction:
    pass


@dataclass(frozen=True)
class RaceAction:
    name: str = "Optional Race"
    target_rank: int = 1


@dataclass(frozen=True)
class RecreationAction:
    pass


CareerAction = TrainAction | RestAction | RaceAction | RecreationAction
