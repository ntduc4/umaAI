from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, StrEnum

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
    def mood_value(self) -> float:
        return {
            Motivation.AWFUL: -0.2,
            Motivation.BAD: -0.1,
            Motivation.NORMAL: 0.0,
            Motivation.GOOD: 0.1,
            Motivation.GREAT: 0.2,
        }[self]

    @property
    def training_multiplier(self) -> float:
        return 1 + self.mood_value


class Condition(StrEnum):
    PRACTICE_PERFECT = "practice_perfect"
    PRACTICE_PERFECT_DOUBLE = "practice_perfect_double"
    CHARMING = "charming"
    POOR_PRACTICE = "poor_practice"
    NIGHT_OWL = "night_owl"
    SKIN_OUTBREAK = "skin_outbreak"
    MIGRAINE = "migraine"
    SLOW_METABOLISM = "slow_metabolism"
    SLACKER = "slacker"


class RaceGrade(StrEnum):
    DEBUT = "debut"
    PRE_OP = "pre-op"
    OP = "op"
    G3 = "g3"
    G2 = "g2"
    G1 = "g1"
    EX = "ex"


class Surface(StrEnum):
    TURF = "turf"
    DIRT = "dirt"


class DistanceType(StrEnum):
    SPRINT = "sprint"
    MILE = "mile"
    MEDIUM = "medium"
    LONG = "long"


class ObjectiveType(StrEnum):
    RACE = "race"
    FAN_COUNT = "fan_count"


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
class RaceDefinition:
    id: str
    name: str
    year: str
    month: int
    half: str
    grade: RaceGrade
    surface: Surface
    distance_m: int
    distance_type: DistanceType
    fan_requirement: int = 0
    fan_gain_first: int = 0
    stats_first: Stats = field(default_factory=Stats)
    stats_other: Stats = field(default_factory=Stats)
    skill_points_first: int = 45
    skill_points_other: int = 25
    is_scenario_race: bool = False


@dataclass(frozen=True)
class CareerObjective:
    id: str
    description: str
    objective_type: ObjectiveType
    deadline_turn_index: int
    race_id: str | None = None
    required_place: int = 1
    required_fans: int = 0


@dataclass(frozen=True)
class ScenarioEvent:
    id: str
    name: str
    turn_index: int
    stats: Stats = field(default_factory=Stats)
    skill_points: int = 0
    energy_delta: int = 0
    motivation_delta: int = 0
    min_fans: int = 0
    alternate_min_fans: int | None = None
    alternate_trainee_ids: frozenset[str] = frozenset()
    min_director_bond: int = 0


@dataclass(frozen=True)
class SupportCard:
    """Manual support-card values until an external card database is added."""

    name: str
    card_type: TrainingType
    level: int
    training_stats: dict[TrainingType, Stats]
    initial_bond: int = 0
    bond_gain_on_training: int = 7
    friendship_bonus_percent: int = 0
    mood_effect_percent: int = 0
    training_effectiveness_percent: int = 0
    energy_cost_reduction_percent: int = 0
    wisdom_friendship_recovery: int = 0
    race_bonus_percent: int = 0
    fan_bonus_percent: int = 0
    failure_protection_percent: int = 0
    specialty_rate: int = 0
    initial_stats: Stats = field(default_factory=Stats)

    def is_friendship_training(self, training: TrainingType, current_bond: int) -> bool:
        return training == self.card_type and current_bond >= FRIENDSHIP_BOND_THRESHOLD

    def stat_bonus_for(self, training: TrainingType) -> Stats:
        return self.training_stats.get(training, Stats())


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
    race_id: str | None = None
    fans_gained: int = 0
    placement: int = 1


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
    trainee_id: str | None = None
    fans: int = 0
    director_bond: int = 0
    failed: bool = False
    consecutive_races: int = 0
    facility_levels: dict[TrainingType, int] = field(default_factory=lambda: {training: 1 for training in TrainingType})
    training_counts: dict[TrainingType, int] = field(default_factory=lambda: {training: 0 for training in TrainingType})
    supports: list[SupportState] = field(default_factory=list)
    logs: list[TurnLogEntry] = field(default_factory=list)
    race_results: list[RaceResult] = field(default_factory=list)
    objectives: list[CareerObjective] = field(default_factory=list)
    completed_objective_ids: set[str] = field(default_factory=set)
    event_history: set[str] = field(default_factory=set)
    conditions: set[Condition] = field(default_factory=set)
    growth_rates: dict[str, int] = field(default_factory=dict)
    aptitudes: dict[str, str] = field(default_factory=dict)

    @classmethod
    def new(cls, base_stats: Stats, support_cards: list[SupportCard] | None = None, *, growth_rates: dict[str, int] | None = None, aptitudes: dict[str, str] | None = None) -> CareerState:
        state = cls(
            stats=base_stats,
            supports=[SupportState.from_card(card) for card in support_cards or []],
            growth_rates=growth_rates or {},
            aptitudes=aptitudes or {},
        )
        for card in support_cards or []:
            state.stats.add(card.initial_stats)
        return state

    def clamp_energy(self) -> None:
        self.energy = max(0, min(MAX_ENERGY, self.energy))

    def clone(self) -> CareerState:
        import copy
        from copy import deepcopy

        return CareerState(
            stats=Stats(
                speed=self.stats.speed, stamina=self.stats.stamina,
                power=self.stats.power, guts=self.stats.guts,
                wisdom=self.stats.wisdom, skill_points=self.stats.skill_points,
            ),
            energy=self.energy,
            motivation=self.motivation,
            turn_index=self.turn_index,
            trainee_id=self.trainee_id,
            fans=self.fans,
            director_bond=self.director_bond,
            failed=self.failed,
            consecutive_races=self.consecutive_races,
            facility_levels=dict(self.facility_levels),
            training_counts=dict(self.training_counts),
            supports=[SupportState(card=support.card, bond=support.bond) for support in self.supports],
            logs=list(self.logs),
            race_results=list(self.race_results),
            objectives=list(self.objectives),
            completed_objective_ids=set(self.completed_objective_ids),
            event_history=set(self.event_history),
            conditions=set(self.conditions),
            growth_rates=dict(self.growth_rates),
            aptitudes=dict(self.aptitudes),
        )
