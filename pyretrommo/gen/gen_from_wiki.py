#!/usr/bin/env python3
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)
from bs4 import BeautifulSoup
import requests
import logging
import hashlib
import pathlib


#
# helpers
#


def cleanup_name(s: str, remove_quote=False) -> str:
    if remove_quote:
        return s.replace("'", '').title().replace(' ', '')
    else:
        return s.replace("'", "\\'").title().replace(' ', '')


def get_wiki(url: str) -> str:
    digest = hashlib.md5(bytes(url, 'utf-8')).hexdigest()
    cache = pathlib.Path('wiki_cache') / digest
    if cache.exists():
        return cache.read_text()

    print(f'fetching: {url}')

    html = requests.get(url).text
    with cache.open('w') as f:
        f.write(html)
    return html


def start_python_file(filename: str):
    logging.info(f'writing file {filename}')
    f = open(filename, 'w')
    f.write('#!/usr/bin/env python3\n')
    f.write('# this file is auto-generated by gen_from_wiki.py\n')
    f.write('from __future__ import annotations\n')
    return f


#
# PlayerClass
#


_player_classes: Optional[List[str]] = None
_player_class_abilities: Optional[Dict[str, Dict[str, int]]] = None
_player_class_equipment: Optional[Dict[str, Dict[str, int]]] = None


def gen_player_classes() -> List[str]:
    global _player_classes
    global _player_class_abilities
    global _player_class_equipment
    if _player_classes is not None:
        return _player_classes
    logging.info('fetching classes from wiki')

    html = get_wiki('https://wiki.retro-mmo.com/wiki/Category:Classes')
    soup = BeautifulSoup(html, 'html.parser')

    content = soup.select('#mw-pages')[0]
    lis = content.findAll('li')
    classes = []
    for li in lis:
        children = li.select('a')
        assert len(children) == 1
        classes.append(children[0].string)

    class_abilities: Dict[str, Dict[str, int]] = {}
    class_equipment: Dict[str, Dict[str, int]] = {}
    for classname in classes:
        html = get_wiki(f'https://wiki.retro-mmo.com/wiki/{classname}')
        soup = BeautifulSoup(html, 'html.parser')
        ability_table, equipment_table, *_ = soup.select('.wikitable')

        # abilities
        class_abilities[classname] = {}
        trs = ability_table.select('tbody')[0].select('tr')
        for tr in trs:
            tds = tr.select('td')
            if len(tds) != 3: continue
            _, ability, level = tds
            ability = ability.select('a')[0].string
            level = int(level.string)
            class_abilities[classname][ability] = level

        class_equipment[classname] = {}
        trs = equipment_table.select('tbody')[0].select('tr')
        for tr in trs:
            tds = tr.select('td')
            if len(tds) != 3: continue
            _, equipment , level = tds
            equipment = equipment.select('a')[0].string
            level = int(level.string)
            class_equipment[classname][equipment] = level

    _player_class_abilities = class_abilities
    _player_class_equipment = class_equipment
    _player_classes = classes
    return classes


def gen_player_class_abilities() -> Dict[str, Dict[str, int]]:
    gen_player_classes()
    assert _player_class_abilities is not None
    return _player_class_abilities


def gen_player_class_equipment() -> Dict[str, Dict[str, int]]:
    gen_player_classes()
    assert _player_class_equipment is not None
    return _player_class_equipment


def write_player_classes() -> None:
    classes = gen_player_classes()
    f = start_python_file('player_class.py')
    f.write('from typing import (\n')
    f.write('    Dict,\n')
    f.write('    Tuple,\n')
    f.write(')\n')
    f.write('import enum\n')
    f.write('import functools\n')
    f.write('\n')
    f.write('from ..item import EquipmentItem\n')
    f.write('from .ability import Ability\n')
    f.write('\n\n')
    f.write('class PlayerClass(enum.Enum):\n')
    f.write('\n')

    for pc in classes:
        f.write(f"    {pc} = '{pc.lower()}'\n")
    f.write('\n')

    f.write(f'    @staticmethod\n')
    f.write(f'    @functools.cache\n')
    f.write(f'    def get_abilities(cls: PlayerClass, level=10) -> Tuple[Ability, ...]:\n')
    f.write(f'        from .class_info import CLASS_ABILITIES\n')
    f.write(f'        abilities = CLASS_ABILITIES[cls]\n')
    f.write(f'        return tuple(\n')
    f.write(f'            a for a, lv in abilities.items()\n')
    f.write(f'            if lv <= level\n')
    f.write(f'        )\n')
    f.write('\n')
    f.write(f'    @staticmethod\n')
    f.write(f'    @functools.cache\n')
    f.write(f'    def get_equipment(cls: PlayerClass, level=10) -> Tuple[\'EquipmentItem\', ...]:\n')
    f.write(f'        from .class_info import CLASS_EQUIPMENT\n')
    f.write(f'        equipment = CLASS_EQUIPMENT[cls]\n')
    f.write(f'        return tuple(\n')
    f.write(f'            e for e, lv in equipment.items()\n')
    f.write(f'            if lv <= level\n')
    f.write(f'        )\n')
    f.write('\n')
    f.close()

def write_class_info() -> None:
    classes = gen_player_classes()
    f = start_python_file('class_info.py')
    f.write('from typing import (\n')
    f.write('    Dict,\n')
    f.write('    Tuple,\n')
    f.write(')\n')
    f.write('from ..item import EquipmentItem\n')
    f.write('from .ability import Ability\n')
    f.write('from .equipment import find_equipment\n')
    f.write('from .player_class import PlayerClass\n')
    f.write('\n\n')
    abilities = gen_player_class_abilities()
    f.write('CLASS_ABILITIES: Dict[PlayerClass, Dict[Ability, int]] = {\n')
    for pc in classes:
        f.write(f'    PlayerClass.{pc}: {{\n')
        for ability, level in abilities[pc].items():
            name = cleanup_name(ability)
            f.write(f'        Ability.{name}: {level},\n')
        f.write('    },\n')
    f.write('}\n\n\n')

    equipments = gen_player_class_equipment()
    f.write('CLASS_EQUIPMENT: Dict[PlayerClass, Dict[\'EquipmentItem\', int]] = {\n')
    for pc in classes:
        f.write(f'    PlayerClass.{pc}: {{\n')
        for equipment, level in equipments[pc].items():
            name = cleanup_name(equipment)
            f.write(f'        find_equipment(\'{name}\'): {level},\n')
        f.write('    },\n')
    f.write('}\n')

    f.write('\n')
    f.close()


#
# PlayerStats
#


_player_stats = None


def gen_player_stats(player_class: str) -> List[List[int]]:
    global _player_stats
    if _player_stats is not None:
        return _player_stats
    logging.info('fetching player stats from wiki')

    html = get_wiki(f'https://wiki.retro-mmo.com/wiki/{player_class}')
    soup = BeautifulSoup(html, 'html.parser')

    contents = soup.select('.mw-parser-output')
    assert len(contents) == 1
    content = contents[0]

    table = None
    found_stats = False
    for child in content.children:
        if child.name == 'h2':
            span = child.select('span')
            if len(span) == 1:
                attrs = span[0].get_attribute_list('id')
                if attrs == ['Stats']:
                    found_stats = True
        elif found_stats and child.name == 'table':
            table = child
            break

    if table is None:
        raise ValueError('could not find Stats table')

    tbody = table.select('tbody')[0]
    current_level = 1
    stats_list = [
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
    for tr in tbody.select('tr'):
        tds = tr.select('td')
        if len(tds) == 0:
            continue
        level, *stats = map(int, [td.string for td in tds])
        assert level == len(stats_list)
        assert len(stats) == 8
        stats_list.append(stats)

    _player_stats = stats_list
    return stats_list


def write_player_stats() -> None:
    f = start_python_file('player_stats.py')
    f.write('from .player_class import PlayerClass\n')
    f.write('from ..stats import Stats\n')
    f.write('\n\n')
    f.write('STATS_BY_PLAYER_CLASS = {\n')

    for pc in gen_player_classes():
        f.write(f'    PlayerClass.{pc}: [\n')
        stats = gen_player_stats(pc)
        for row in stats:
            f.write(f'        Stats(*{tuple(row)}),\n')
        f.write('    ],\n')

    f.write('}\n')
    f.close()


#
# Abilities
#


_abilities = None


def gen_abilities() -> List[str]:
    global _abilities
    if _abilities is not None:
        return _abilities
    logging.info('fetching abilities from wiki')

    html = get_wiki(f'https://wiki.retro-mmo.com/wiki/Category:Abilities')
    soup = BeautifulSoup(html, 'html.parser')

    content = soup.select('.mw-category')[0]
    lis = content.findAll('li')
    abilities = []
    for li in lis:
        children = li.select('a')
        assert len(children) == 1
        abilities.append(children[0].string)
    return abilities


def write_abilities() -> None:
    f = start_python_file('ability.py')
    f.write('import enum\n')
    f.write('\n\n')
    f.write('class Ability(enum.Enum):\n')
    f.write('\n')

    for ability in gen_abilities():
        key = cleanup_name(ability)
        val = ability.lower()
        f.write(f"    {key} = '{val}'\n")

    f.write('\n')
    f.close()


#
# Equipment
#


_equipment_names = None
_equipment_slots = None
_equipment = None


def gen_equipment_names() -> List[str]:
    global _equipment_names
    if _equipment_names is not None:
        return _equipment_names
    logging.info('fetching equipment names from wiki')

    html = get_wiki(f'https://wiki.retro-mmo.com/wiki/Category:Equipment_items')
    soup = BeautifulSoup(html, 'html.parser')

    content = soup.select('.mw-category')[0]
    lis = content.findAll('li')
    equipment_names = []
    for li in lis:
        children = li.select('a')
        assert len(children) == 1
        equipment_names.append(children[0].string)

    _equipment_names = equipment_names
    return equipment_names


def gen_equipment() -> Dict[str, Any]:
    global _equipment
    global _equipment_slots
    global _equipment_names
    if _equipment is not None:
        return _equipment
    logging.info('fetching equipment from wiki')

    equipment = {}
    slots = set()
    for name in gen_equipment_names():
        html = get_wiki(f'https://wiki.retro-mmo.com/wiki/{name}')
        soup = BeautifulSoup(html, 'html.parser')

        content = soup.select('.retrommo-infobox')[0]

        level = None
        classes = None
        slot = None
        stats = [0] * 8
        tradable = None
        sell = None

        for tr in content.findAll('tr'):
            tds = tr.findAll('td')
            if len(tds) != 2:
                continue
            key, val = tds
            key = key.select('a')[0].string.strip()

            if key == 'Class':
                classes = [
                    a.string.strip()
                    for a in val.select('a')
                ]
                if len(classes) == 0 and val.string.strip() == 'All':
                    classes = [c for c in gen_player_classes()]
                continue

            val = val.string.strip()

            if key == 'Level':
                level = int(val)
            elif key == 'Slot':
                slots.add(val)
                slot = val
            elif key == 'Agility':
                stats[4] = int(val)
            elif key == 'Defense':
                stats[3] = int(val)
            elif key == 'Intelligence':
                stats[5] = int(val)
            elif key == 'Luck':
                stats[7] = int(val)
            elif key == 'Strength':
                stats[2] = int(val)
            elif key == 'Wisdom':
                stats[6] = int(val)
            elif key == 'Tradable':
                tradable = val == 'Yes'
            elif key == 'Sell':
                sell = int(val)

        attributes = (level, classes, slot, tradable, sell)
        assert None not in attributes, f'{name} - {attributes}'

        equipment[cleanup_name(name)] = {
            'name': name,
            'classes': classes,
            'stats': stats,
            'slot': slot,
            'tradable': tradable,
            'sell': sell,
        }

    _equipment_slots = slots
    _equipment = equipment
    return equipment


def gen_equipment_slots() -> Set[str]:
    gen_equipment()
    assert _equipment_slots is not None
    return _equipment_slots


def write_equipment_slots() -> None:
    f = start_python_file('equipment_slot.py')
    f.write('import enum\n')
    f.write('\n\n')

    f.write('class EquipmentSlot(enum.Enum):\n')
    for slot in gen_equipment_slots():
        slot_name = cleanup_name(slot)
        slot = slot.lower()
        f.write(f"    {slot_name} = '{slot}'\n")
    f.write('\n')


def write_equipment() -> None:
    by_slot: Dict[str, List[Dict[str, Any]]] = {}
    for name, item in gen_equipment().items():
        slot = item['slot']
        if slot not in by_slot:
            by_slot[slot] = []
        by_slot[slot].append(item)

    f = start_python_file('equipment.py')
    f.write('from typing import Optional, Tuple\n')
    f.write('import enum\n')
    f.write('import functools\n')
    f.write('\n')
    f.write('from ..item import EquipmentItem\n')
    f.write('from ..stats import Stats\n')
    f.write('from .equipment_slot import EquipmentSlot\n')
    f.write('from .player_class import PlayerClass\n')
    f.write('\n\n')
    f.write('def find_equipment(name: str) -> EquipmentItem:\n')
    f.write("    name = name.replace(\"'\", \"\\'\").title().replace(' ', '')\n")
    f.write('    try: return OffHandEquipment[name]\n')
    f.write('    except KeyError: pass\n')
    f.write('    try: return MainHandEquipment[name]\n')
    f.write('    except KeyError: pass\n')
    f.write('    try: return HeadEquipment[name]\n')
    f.write('    except KeyError: pass\n')
    f.write('    try: return BodyEquipment[name]\n')
    f.write('    except KeyError: pass\n')
    f.write("    raise ValueError(f\'invalid equipment: {name}\')\n")
    f.write('\n\n')

    for slot_name in by_slot:
        classname = cleanup_name(slot_name) + 'Equipment'
        f.write(f'class {classname}(EquipmentItem, enum.Enum):\n\n')

        f.write(f'    @staticmethod\n')
        f.write(f'    @functools.cache\n')
        f.write(f'    def by_class(cls: PlayerClass) -> Tuple[{classname}, ...]:\n')
        f.write(f'        return tuple(\n')
        f.write(f'            c for c in {classname}\n')
        f.write(f'            if cls in c.value.classes\n')
        f.write(f'        )\n')
        f.write('\n')

        for item in by_slot[slot_name]:
            name = item['name'].replace("'", "\\'")
            item_name = cleanup_name(item['name'], True)
            tradable = item['tradable']
            value = item['sell']
            classes = item['classes']
            stats = item['stats']
            slot = cleanup_name(item['slot'])

            classes_str = ', '.join(f'PlayerClass.{c}' for c in classes)

            f.write(f'    {item_name} = (\n')
            f.write(f"        '{name}',\n")
            f.write(f'        {tradable},  # tradable\n')
            f.write(f'        {value},  # sell value\n')
            f.write(f'        ({classes_str}),\n')
            f.write(f'        Stats.from_sequence({stats}),\n')
            f.write(f'        EquipmentSlot.{slot},\n')
            f.write(f'    )\n')

    f.write('\n\n')
    f.write('GearType = Tuple[\n')
    f.write('    Optional[HeadEquipment],\n')
    f.write('    Optional[BodyEquipment],\n')
    f.write('    Optional[MainHandEquipment],\n')
    f.write('    Optional[OffHandEquipment],\n')
    f.write(']\n')
    f.write('\n')
    f.close()


# TODO: cosmetic items
# TODO: consumable items


#
# All
#


def write_all():
    write_player_classes()
    write_player_stats()
    write_abilities()
    write_equipment_slots()
    write_equipment()
    write_class_info()


if __name__ == '__main__':
    write_all()
