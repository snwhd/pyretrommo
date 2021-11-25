#!/usr/bin/env python3
from typing import (
    cast,
    Any,
    Dict,
    List,
    Optional,
    Union,
)
from datetime import (
    datetime,
    timedelta,
)
import requests


BASE_URL = 'https://play.retro-mmo.com'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'


class ApiError(Exception):
    ...


class ApiPlayerInfo:

    def __init__(
        self,
        username: str,
        experience: int,
        permissions: int,
        rank: Optional[int] = None,
        registered_at: Optional[datetime] = None,
        time_played: Optional[timedelta] = None,
        *,
        auto_fetch = True,
    ) -> None:
        self.username = username
        self.experience = experience
        self.permissions = permissions
        self._rank = rank
        self._registered_at = registered_at
        self._time_played = time_played
        self.auto_fetch = auto_fetch

    @property
    def rank(self) -> int:
        if self._rank is None:
            self.try_autofetch()
            assert self._rank is not None
        return self._rank        

    @property
    def registered_at(self) -> datetime:
        if self._registered_at is None:
            self.try_autofetch()
            assert self._registered_at is not None
        return self._registered_at

    @property
    def time_played(self) -> timedelta:
        if self._time_played is None:
            self.try_autofetch()
            assert self._time_played is not None
        return self._time_played

    def try_autofetch(self) -> None:
        if not self.auto_fetch:
            raise ApiError('ApiPlayerInfo field is not populated')
        info = get_player(self.username)
        self._rank = info.rank
        self._registered_at = info.registered_at
        self._time_played = info.time_played


def api_get(endpoint: str) -> Any:
    url = f'{BASE_URL}/{endpoint}'
    print(f'fetching: {url}')
    r = requests.get(url)
    if r.status_code != 200:
        raise ApiError(r.status_code)
    return r.json()


def get_players() -> List[str]:
    json = api_get('players.json')
    if not isinstance(json, list):
        raise ApiError('unexpected response from player.json')
    return cast(List[str], json)


def get_registered_users() -> int:
    json = api_get('registered-users.json')
    if not isinstance(json, int):
        raise ApiError('unexpected response from registered-users.json')
    return json


def get_leaderboard(page=1) -> List[ApiPlayerInfo]:
    json = api_get(f'leaderboards.json?page={page}')
    if not isinstance(json, list):
        raise ApiError('unexpected response from leaderboards.json')

    players = []
    for player in json:
        assert isinstance(player, dict)
        players.append(ApiPlayerInfo(
            player['username'],
            player['experience'],
            player['permissions'],
        ))
    return players
        

def get_player(username: str) -> ApiPlayerInfo:
    json = api_get(f'users/{username}.json')
    if not isinstance(json, dict):
        raise ApiError(f'unexpected response from {username}.json')
    return ApiPlayerInfo(
        json['username'],
        json['lifetimeExperience'],
        json['permissions'],
        json['rank'],
        datetime.strptime(json['registeredAt'], DATE_FORMAT),
        timedelta(seconds=json['timePlayed']),
        auto_fetch=False,
    )
