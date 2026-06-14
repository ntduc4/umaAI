from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

from uma_ai.career.actions import TrainingType


STAT_CAP = 1200
MAX_ENERGY = 100
FRIENDSHIP_BOND_THRESHOLD = 80


class Motivation(IntEnum):
    AWFUL = 0
    BAD = 1
    NORMAL = 2
    GOOD = 3
    GREAT = 4

    @property
    def training_multiplier(self) -> float:
        return {
            Motivation.AWFUL: 0.8,
            Motivation.BAD: 0.9,
            Motivation.NORMAL: 1.0,
            Motivation.GOOD: 1.1,
            Motivation.GREAT: 1.2,
        }[self]


@dataclass
class Stats:
    speed: int = 0
    stamina: int = 0
    power: int = 0
    guts: int = 0
    wisdom: int = 0
    skill_points: int = 0

    def add(self, other: Stats, multiplier: float = 1.0) -> None:
        self.speed = min(STAT_CAP, self.speed + round(other.speed * multiplier))
        self.stamina = min(STAT_CAP, self.stamina + round(other.stamina * multiplier))
        self.power = min(STAT_CAP, self.power + round(other.power * multiplier))
        self.guts = min(STAT_CAP, self.guts + round(other.guts * multiplier))
        self.wisdom = min(STAT_CAP, self.wisdom + round(other.wisdom * multiplier))
        self.skill_points += round(other.skill_points * multiplier)

    @property
    def total_without_skill_points(self) -> int:
        return self.speed + self.stamina + self.power + self.guts + self.wisdom


@dataclass(frozen=True)
class SupportCard:
    """Manual support-card values until an external card database is added."""

    name: str
    card_type: TrainingType
    level: int
    training_stats: dict[TrainingType, Stats]
    initial_bond: int = 0
    bond_gain_on_training: int = 7
    friendship_multiplier: float = 1.25

    def stats_for(self, training: TrainingType, current_bond: int) -> Stats:
        stats = self.training_stats.get(training, Stats())
        if training == self.card_type and current_bond >= FRIENDSHIP_BOND_THRESHOLD:
            boosted = Stats()
            boosted.add(stats, self.friendship_multiplier)
            return boosted
        return stats


@dataclass
class SupportState:
    card: SupportCard
    bond: int

    @classmethod
    def from_card(cls, card: SupportCard) -> SupportState:
        return cls(card=card, bond=max(0, min(100, card.initial_bond)))


@dataclass(frozen=True)
class Turn:
    index: int
    year: str
    month: int
    half: str
    label: str
    is_summer_camp: bool = False
    is_ura_race: bool = False


@dataclass
class RaceResult:
    race_name: str
    win_probability: float
    won: bool
    stats_gained: Stats


@dataclass
class TurnLogEntry:
    turn: Turn
    action: str
    details: dict[str, object] = field(default_factory=dict)


@dataclass
class CareerState:
    stats: Stats
    energy: int = MAX_ENERGY
    motivation: Motivation = Motivation.NORMAL
    turn_index: int = 0
    supports: list[SupportState] = field(default_factory=list)
    logs: list[TurnLogEntry] = field(default_factory=list)
    race_results: list[RaceResult] = field(default_factory=list)

    @classmethod
    def new(cls, base_stats: Stats, support_cards: list[SupportCard] | None = None) -> CareerState:
        return cls(
            stats=base_stats,
            supports=[SupportState.from_card(card) for card in support_cards or []],
        )

    def clamp_energy(self) -> None:
        self.energy = max(0, min(MAX_ENERGY, self.energy))
