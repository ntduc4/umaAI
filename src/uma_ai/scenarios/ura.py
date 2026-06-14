from __future__ import annotations

from functools import cached_property

from uma_ai.career.actions import RaceEnergyChoice, TrainingType
from uma_ai.career.models import DistanceType, RaceDefinition, RaceGrade, ScenarioEvent, Stats, Surface, Turn
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

        for stage in ("Preliminary", "Semifinal", "Final"):
            index += 1
            turns.append(Turn(index=index, year="URA", month=12, half="finals", label=f"URA Finals {stage} Training"))
            index += 1
            turns.append(Turn(index=index, year="URA", month=12, half="finals", label=f"URA Finals {stage} Race", is_ura_race=True))
        return turns

    @cached_property
    def race_calendar(self) -> list[RaceDefinition]:
        races = [
            self._race("junior_debut", "Junior Debut", "Junior", 6, "late", RaceGrade.DEBUT, Surface.TURF, 1600, 0, 700),
            self._race("asahi_hai_fs", "Asahi Hai Futurity Stakes", "Junior", 12, "early", RaceGrade.G1, Surface.TURF, 1600, 7000, 7000),
            self._race("hopeful_stakes", "Hopeful Stakes", "Junior", 12, "late", RaceGrade.G1, Surface.TURF, 2000, 7000, 7000),
            self._race("satsuki_sho", "Satsuki Sho", "Classic", 4, "early", RaceGrade.G1, Surface.TURF, 2000, 4500, 11000),
            self._race("oka_sho", "Oka Sho", "Classic", 4, "early", RaceGrade.G1, Surface.TURF, 1600, 4500, 10500),
            self._race("nhk_mile_cup", "NHK Mile Cup", "Classic", 5, "early", RaceGrade.G1, Surface.TURF, 1600, 5000, 10500),
            self._race("japanese_derby", "Japanese Derby", "Classic", 5, "late", RaceGrade.G1, Surface.TURF, 2400, 6000, 20000),
            self._race("japanese_oaks", "Japanese Oaks", "Classic", 5, "late", RaceGrade.G1, Surface.TURF, 2400, 6000, 11000),
            self._race("takarazuka_kinen_classic", "Takarazuka Kinen", "Classic", 6, "late", RaceGrade.G1, Surface.TURF, 2200, 20000, 15000),
            self._race("kikuka_sho", "Kikuka Sho", "Classic", 10, "late", RaceGrade.G1, Surface.TURF, 3000, 7500, 12000),
            self._race("shuka_sho", "Shuka Sho", "Classic", 10, "late", RaceGrade.G1, Surface.TURF, 2000, 7500, 10000),
            self._race("tenno_sho_autumn_classic", "Tenno Sho Autumn", "Classic", 10, "late", RaceGrade.G1, Surface.TURF, 2000, 20000, 15000),
            self._race("japan_cup_classic", "Japan Cup", "Classic", 11, "late", RaceGrade.G1, Surface.TURF, 2400, 25000, 30000),
            self._race("arima_kinen_classic", "Arima Kinen", "Classic", 12, "late", RaceGrade.G1, Surface.TURF, 2500, 25000, 30000),
            self._race("osaka_hai", "Osaka Hai", "Senior", 3, "late", RaceGrade.G1, Surface.TURF, 2000, 20000, 13500),
            self._race("tenno_sho_spring", "Tenno Sho Spring", "Senior", 4, "late", RaceGrade.G1, Surface.TURF, 3200, 20000, 15000),
            self._race("victoria_mile", "Victoria Mile", "Senior", 5, "early", RaceGrade.G1, Surface.TURF, 1600, 10000, 10500),
            self._race("yasuda_kinen", "Yasuda Kinen", "Senior", 6, "early", RaceGrade.G1, Surface.TURF, 1600, 15000, 13000),
            self._race("takarazuka_kinen_senior", "Takarazuka Kinen", "Senior", 6, "late", RaceGrade.G1, Surface.TURF, 2200, 20000, 15000),
            self._race("sprinters_stakes", "Sprinters Stakes", "Senior", 9, "late", RaceGrade.G1, Surface.TURF, 1200, 15000, 13000),
            self._race("tenno_sho_autumn_senior", "Tenno Sho Autumn", "Senior", 10, "late", RaceGrade.G1, Surface.TURF, 2000, 20000, 15000),
            self._race("japan_cup_senior", "Japan Cup", "Senior", 11, "late", RaceGrade.G1, Surface.TURF, 2400, 25000, 30000),
            self._race("arima_kinen_senior", "Arima Kinen", "Senior", 12, "late", RaceGrade.G1, Surface.TURF, 2500, 25000, 30000),
            self._race("ura_preliminary", "URA Finals Preliminary", "URA", 12, "finals", RaceGrade.EX, Surface.TURF, 2000, 0, 0, is_scenario_race=True),
            self._race("ura_semifinal", "URA Finals Semifinal", "URA", 12, "finals", RaceGrade.EX, Surface.TURF, 2000, 0, 0, is_scenario_race=True),
            self._race("ura_final", "URA Finals Final", "URA", 12, "finals", RaceGrade.EX, Surface.TURF, 2000, 0, 0, is_scenario_race=True),
        ]
        return races

    @cached_property
    def scenario_events(self) -> list[ScenarioEvent]:
        return [
            ScenarioEvent("aoi_three_legged_race", "A Three-Legged Race", 35, stats=Stats(wisdom=20), skill_points=20, min_fans=50_000),
            ScenarioEvent("classic_100k_fans", "Classic Year 100k Fans", 38, skill_points=30, min_fans=100_000),
            ScenarioEvent(
                "senior_early_april_fan_meeting",
                "Senior Early April Fan Meeting",
                45,
                motivation_delta=1,
                min_fans=70_000,
                alternate_min_fans=60_000,
                alternate_trainee_ids=frozenset({"haru_urara", "smart_falcon"}),
                min_director_bond=60,
            ),
            ScenarioEvent("senior_240k_fans", "Senior Year 240k Fans", 62, skill_points=30, min_fans=240_000),
        ]

    def base_training_stats(self, training: TrainingType, turn: Turn, facility_level: int = 1) -> Stats:
        level = max(1, min(5, facility_level))
        base = self._training_table()[training][level]
        return Stats(
            speed=base.speed,
            stamina=base.stamina,
            power=base.power,
            guts=base.guts,
            wisdom=base.wisdom,
            skill_points=base.skill_points,
        )

    def training_energy_delta(self, training: TrainingType, turn: Turn, facility_level: int = 1) -> int:
        return self._training_energy_table()[training][max(1, min(5, facility_level))]

    def race_energy_delta(self, won: bool, energy_choice: RaceEnergyChoice) -> int:
        return -15

    def race_stats(self, won: bool, is_ura_race: bool, race_id: str | None = None) -> Stats:
        if is_ura_race:
            skill_points_by_race = {
                "ura_preliminary": 40,
                "ura_semifinal": 60,
                "ura_final": 80,
            }
            return Stats(speed=10, stamina=10, power=10, guts=10, wisdom=10, skill_points=skill_points_by_race.get(race_id, 40) if won else 25)
        return Stats(skill_points=45 if won else 25)

    def available_races(self, turn: Turn, fans: int) -> list[RaceDefinition]:
        return [
            race
            for race in self.race_calendar
            if race.year == turn.year
            and race.month == turn.month
            and race.half == turn.half
            and race.fan_requirement <= fans
            and not race.is_scenario_race
        ]

    def race_by_id(self, race_id: str) -> RaceDefinition | None:
        return next((race for race in self.race_calendar if race.id == race_id), None)

    def scenario_events_for_turn(self, turn: Turn) -> list[ScenarioEvent]:
        return [event for event in self.scenario_events if event.turn_index == turn.index]

    def _race(
        self,
        race_id: str,
        name: str,
        year: str,
        month: int,
        half: str,
        grade: RaceGrade,
        surface: Surface,
        distance_m: int,
        fan_requirement: int,
        fan_gain_first: int,
        is_scenario_race: bool = False,
    ) -> RaceDefinition:
        return RaceDefinition(
            id=race_id,
            name=name,
            year=year,
            month=month,
            half=half,
            grade=grade,
            surface=surface,
            distance_m=distance_m,
            distance_type=self._distance_type(distance_m),
            fan_requirement=fan_requirement,
            fan_gain_first=fan_gain_first,
            stats_first=self._base_race_stats(grade),
            skill_points_first=self._base_race_skill_points(grade),
            is_scenario_race=is_scenario_race,
        )

    def _base_race_stats(self, grade: RaceGrade) -> Stats:
        if grade == RaceGrade.G1:
            return Stats(speed=10)
        if grade in {RaceGrade.G2, RaceGrade.G3}:
            return Stats(speed=8)
        if grade in {RaceGrade.OP, RaceGrade.PRE_OP}:
            return Stats(speed=5)
        return Stats()

    def _base_race_skill_points(self, grade: RaceGrade) -> int:
        if grade == RaceGrade.G1:
            return 45
        if grade in {RaceGrade.G2, RaceGrade.G3, RaceGrade.OP, RaceGrade.PRE_OP}:
            return 35
        return 45

    def _distance_type(self, distance_m: int) -> DistanceType:
        if distance_m <= 1400:
            return DistanceType.SPRINT
        if distance_m <= 1800:
            return DistanceType.MILE
        if distance_m <= 2400:
            return DistanceType.MEDIUM
        return DistanceType.LONG

    def _training_table(self) -> dict[TrainingType, dict[int, Stats]]:
        return {
            TrainingType.SPEED: {
                1: Stats(speed=10, power=5, skill_points=2),
                2: Stats(speed=11, power=5, skill_points=2),
                3: Stats(speed=12, power=5, skill_points=2),
                4: Stats(speed=13, power=6, skill_points=2),
                5: Stats(speed=14, power=7, skill_points=2),
            },
            TrainingType.STAMINA: {
                1: Stats(stamina=9, guts=4, skill_points=2),
                2: Stats(stamina=10, guts=4, skill_points=2),
                3: Stats(stamina=11, guts=4, skill_points=2),
                4: Stats(stamina=12, guts=5, skill_points=2),
                5: Stats(stamina=13, guts=6, skill_points=2),
            },
            TrainingType.POWER: {
                1: Stats(stamina=5, power=8, skill_points=2),
                2: Stats(stamina=5, power=9, skill_points=2),
                3: Stats(stamina=5, power=10, skill_points=2),
                4: Stats(stamina=6, power=11, skill_points=2),
                5: Stats(stamina=7, power=12, skill_points=2),
            },
            TrainingType.GUTS: {
                1: Stats(speed=4, power=4, guts=8, skill_points=2),
                2: Stats(speed=4, power=4, guts=9, skill_points=2),
                3: Stats(speed=4, power=4, guts=10, skill_points=2),
                4: Stats(speed=5, power=4, guts=11, skill_points=2),
                5: Stats(speed=5, power=5, guts=12, skill_points=2),
            },
            TrainingType.WISDOM: {
                1: Stats(speed=2, wisdom=9, skill_points=4),
                2: Stats(speed=2, wisdom=10, skill_points=4),
                3: Stats(speed=2, wisdom=11, skill_points=4),
                4: Stats(speed=3, wisdom=12, skill_points=4),
                5: Stats(speed=4, wisdom=13, skill_points=4),
            },
        }

    def _training_energy_table(self) -> dict[TrainingType, dict[int, int]]:
        return {
            TrainingType.SPEED: {1: -21, 2: -22, 3: -23, 4: -25, 5: -27},
            TrainingType.STAMINA: {1: -19, 2: -20, 3: -21, 4: -23, 5: -25},
            TrainingType.POWER: {1: -20, 2: -21, 3: -22, 4: -24, 5: -26},
            TrainingType.GUTS: {1: -22, 2: -23, 3: -24, 4: -26, 5: -28},
            TrainingType.WISDOM: {1: 5, 2: 5, 3: 5, 4: 5, 5: 5},
        }
