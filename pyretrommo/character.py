#!/usr/bin/env python3
from typing import (
    Tuple,
)
from .gen.ability import Ability
from .stats import Stats


class Character:
    """base class for Monsters and Players"""

    def __init__(
        self,
        name: str,
        stats: Stats,
        abilities: Tuple[Ability, ...],
    ) -> None:
        self.name = name
        self.stats = stats
        self.abilities = abilities
