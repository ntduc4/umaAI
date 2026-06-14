from __future__ import annotations

from functools import cached_property

from uma_ai.career.actions import TrainingType
from uma_ai.career.models import Stats, Turn
from uma_ai.career.scenario import Scenario


class URAScenario(Scenario):
    name = "URA Finals"

    @cached_property
    def turns(self) -> list[Turn]:
        turns: list[Turn] = []
        index = 0
        for year, months in (
            ("Junior", range(6, 13)),
            ("Classic", range(1, 13)),
            ("Senior", range(1, 13)),
        ):
            for month in months:
                for half in ("early", "late"):
                    index += 1
                    turns.append(
                        Turn(
                            index=index,
                            year=year,
                            month=month,
                            half=half,
                            label=f"{year} {month:02d} {half}",
                            is_summer_camp=year in {"Classic", "Senior"} and month in {7, 8},
                        )
                    )

        for label in ("URA Finals Preliminary", "URA Finals Semifinal", "URA Finals Final"):
            index += 1
            turns.append(Turn(index=index, year="URA", month=12, half="finals", label=label, is_ura_race=True))
        return turns

    def base_training_stats(self, training: TrainingType, turn: Turn) -> Stats:
        camp_bonus = 1.2 if turn.is_summer_camp else 1.0
        base = {
            TrainingType.SPEED: Stats(speed=10),
            TrainingType.STAMINA: Stats(stamina=9),
            TrainingType.POWER: Stats(power=8),
            TrainingType.GUTS: Stats(guts=8),
            TrainingType.WISDOM: Stats(wisdom=8),
        }[training]
        boosted = Stats()
        boosted.add(base, camp_bonus)
        return boosted

    def race_stats(self, won: bool, is_ura_race: bool) -> Stats:
        if is_ura_race:
            return Stats(speed=10, stamina=10, power=10, guts=10, wisdom=10, skill_points=40 if won else 25)
        return Stats(skill_points=45 if won else 25)
