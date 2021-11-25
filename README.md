# pyretrommo
python library for RetroMMO related stuff, including API wrapper.

## install
`python3 -m pip install git+http://github.com/snwhd/pyretrommo.git`

## web api usage
`pyretrommo.api` exposes these api methods:
- `get_players() -> List[str]` - return usernames of logged-in players
- `get_registered_users() -> int` - return number of registered users
- `get_leaderboard(page=1) -> List[ApiPlayerInfo]` - fetch leaderboard page
- `get_player(username: str) -> ApiPlayerInfo` - fetch user details

The ApiPlayerInfo is used for both `get_leaderboard` and `get_player` methods.
The leaderboard API does not return the full player info so some fields will
not be populated, however when accessing the missing fields (rank,
registered\_at, and time\_played) a `get_player` request will be automatically
sent to populate that field.

```
>>> import pyretrommo.api as api
>>> player = api.get_player('d')
>>> p.rank
20
>>> for p in api.get_leaderboard()[:5]:
...     print(p)
...
<ApiPlayerInfo: SSMeaghan>
<ApiPlayerInfo: PapaSaturn>
<ApiPlayerInfo: Korben>
<ApiPlayerInfo: Eric>
<ApiPlayerInfo: fruloo>
```

## other pyretrommo features
The goal of `pyretrommo` is to provide Python classes for representing game
features (players, monsters, items, ...). In the root `pyretrommo` package you
can import:
- `pyretrommo.character` - base class for Player and (eventually) Monster
- `pyretrommo.player` - a player-character, username, class, level, etc.
- `pyretrommo.item` - Item, EquipmentItem, (TODO: Consumable and Cosmetic)
- `pyretrommo.stats` - A wrapper class for representing groups of stats,
could be player base stats, boosts, or equipment stats.

Some of the specific game details like classes, item stats, and abilities
that may be more subject to change are found in `pyretrommo.gen`. These values
are scraped from the RetroMMO wiki to make for easier updates
(see `gen_from_wiki.py`). Note that this script will cache html files in the
`wiki_cache/` directory to avoid unnecessary HTTP requests during development.
If you're not seeing expected results, try deleting this cache. The file names
are `md5(url)`.

```
>>> from pyretrommo.gen.equipment import HeadEquipment
>>> HeadEquipment.JaggedCrown.sell_value
283
>>> HeadEquipment.MageHat.stats.wisdom
2
```
