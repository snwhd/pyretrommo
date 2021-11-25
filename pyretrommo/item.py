#!/usr/bin/env python3
from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Tuple,
)

if TYPE_CHECKING:
    # This file dependend on by gen.player_class and gen.equipment, be careful
    # not to create cyclic imports.
    from .stats import Stats
    from .gen.equipment_slot import EquipmentSlot
    from .gen.player_class import PlayerClass


class Item:

    def __init__(
        self,
        name: str,
        tradable: str,
        sell_value: int,
    ) -> None:
        self.itemname = name
        self.tradable = tradable
        self.sell_value = sell_value


class EquipmentItem(Item):

    def __init__(
        self,
        name: str,
        tradable: str,
        value: int,
        classes: Tuple[PlayerClass],
        stats: Stats,
        slot: EquipmentSlot,
    ) -> None:
        super().__init__(name, tradable, value)
        self.classes = classes
        self.stats = stats
        self.slot = slot
