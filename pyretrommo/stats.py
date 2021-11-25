#!/usr/bin/env python3
from __future__ import annotations
from typing import (
    Any,
    Generator,
    Sequence,
)

# This file is depended on by gen.equipment, be careful not to create cyclic
# imports here.


class Stats:

    def __init__(
        self,
        hp: int,
        mp: int,
        strength: int,
        defense: int,
        agility: int,
        intelligence: int,
        wisdom: int,
        luck: int,
    ) -> None:
        self.hp           = hp
        self.mp           = mp
        self.strength     = strength
        self.defense      = defense
        self.agility      = agility
        self.intelligence = intelligence
        self.wisdom       = wisdom
        self.luck         = luck

    def __iter__(self) -> Generator[int, None, None]:
        yield self.hp
        yield self.mp
        yield self.strength
        yield self.defense
        yield self.agility
        yield self.intelligence
        yield self.wisdom
        yield self.luck

    def __add__(self, o: Any) -> Stats:
        if isinstance(o, Stats):
            self.hp += o.hp
            self.mp += o.mp
            self.strength += o.strength
            self.defense += o.defense
            self.agility += o.agility
            self.intelligence += o.intelligence
            self.wisdom += o.wisdom
            self.luck += o.luck
            return self
        raise NotImplemented

    @classmethod
    def from_sequence(
        cls,
        stats: Sequence[int], 
    ) -> Stats:
        if len(stats) != 8:
            raise ValueError(f'invalid stats tuple: {stats}')
        return Stats(*stats)


    def clone(self) -> Stats:
        return Stats.from_sequence(tuple(self))
