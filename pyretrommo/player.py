#!/usr/bin/env python3
from typing import (
    Tuple,
)

from .character import Character
from .gen.player_class import PlayerClass
from .gen.player_stats import STATS_BY_PLAYER_CLASS
from .gen.equipment import GearType
from .stats import Stats


class Player(Character):

    def __init__(
        self,
        username: str,
        level: int,
        player_class: PlayerClass,
        gear: GearType,
        boosts: Stats,
    ) -> None:
        self.level = level
        self.player_class = player_class
        self.gear = gear
        self.boosts = boosts

        stats = self.calculate_stats()
        abilities = PlayerClass.get_abilities(player_class, level)
        super().__init__(username, stats, abilities)

    def calculate_stats(self) -> Stats:
        stats = Stats(*STATS_BY_PLAYER_CLASS[self.player_class][self.level])
        for gear in self.gear:
            stats += gear
        stats += self.boosts
        return stats
