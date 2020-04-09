import enum
import functools
from datetime import datetime
from datetime import timedelta
from typing import Callable
from typing import Iterable
from typing import List
from typing import Type
from typing import Union

import requests


class Importance(enum.IntFlag):
    HOLIDAY = enum.auto()
    LOW = enum.auto()
    MEDIUM = enum.auto()
    HIGH = enum.auto()


class Currency(enum.IntFlag):
    USD = enum.auto()
    EUR = enum.auto()
    JPY = enum.auto()
    GBP = enum.auto()
    CAD = enum.auto()
    AUD = enum.auto()
    CHF = enum.auto()
    CNY = enum.auto()
    NZD = enum.auto()
    SEK = enum.auto()
    BRL = enum.auto()
    KRW = enum.auto()
    HKD = enum.auto()
    SGD = enum.auto()
    MXN = enum.auto()
    ZAR = enum.auto()
    INR = enum.auto()


@functools.lru_cache
def _get_calendar_events(datetime_from: datetime,
                         datetime_to: datetime,
                         importance: int,
                         currencies: int,
                         ) -> List[dict]:
    url = "https://www.mql5.com/en/economic-calendar/content"
    headers = {"x-requested-with": "XMLHttpRequest"}
    time_format = "%Y-%m-%dT%H:%M:%S"
    data = {
        "date_mode" : 0,
        "from"      : datetime_from.strftime(time_format),
        "to"        : datetime_to.strftime(time_format),
        "importance": importance,
        "currencies": currencies,
    }
    events = requests.post(url=url, headers=headers, data=data).json()
    filtered_events = []
    for e in events:
        e['ReleaseDate'] = time = e['ReleaseDate'] / 1000
        t = datetime.fromtimestamp(time)
        if datetime_from <= t <= datetime_to:
            filtered_events.append(e)
    return events


def _round_time_to_mins(time: datetime, round_minutes: int):
    secs = round_minutes * 60.0
    res = round(time.timestamp() / secs, 0) * secs
    new_time = datetime.fromtimestamp(res)
    return new_time


def _split_pairs(p: Iterable[str]):
    for s in p:
        yield from (s,) if len(s) < 6 else (s[:3], s[3:6])


@functools.lru_cache
def _make_flag(enum_cls: Union[Type[Importance], Type[Currency]],
               flags: Union[Iterable[str], int, str] = None
               ) -> int:
    if isinstance(flags, int):
        return int(flags)
    if flags is None:
        flags = enum_cls.__members__.keys()
    elif isinstance(flags, str):
        flags = flags.replace(',', ' ').split()
    if enum_cls is Currency:
        flags = _split_pairs(flags)
    flags = [enum_cls.__members__.get(f, 0) for f in set(map(str.upper, flags))]
    flag = functools.reduce(lambda x, y: x | y, flags)
    return int(flag)


def calendar_events(time_to: Union[datetime, timedelta] = None,
                    *,
                    time_from: Union[datetime, timedelta] = None,
                    importance: Union[Iterable[str], str, int] = None,
                    currencies: Union[Iterable[str], str, int] = None,
                    function: Callable = None,
                    round_minutes: int = 15,
                    cache_clear: bool = False,
                    **kwargs,
                    ) -> List[dict]:
    if cache_clear:
        _get_calendar_events.cache_clear()
    now = datetime.now()
    if time_to is None and time_from is None:
        time_to = now + timedelta(weeks=1)
    time_from, time_to = time_from or now, time_to or now
    _f = lambda x: now + x if isinstance(x, timedelta) else x
    time_from, time_to = _f(time_from), _f(time_to)
    if time_from > time_to:
        time_from, time_to = time_to, time_from
    time_from = _round_time_to_mins(time_from, round_minutes)
    time_to = _round_time_to_mins(time_to, round_minutes)
    _f = lambda x: tuple(x) if isinstance(x, Iterable) and not isinstance(x, str) else x
    importance, currencies = _f(importance), _f(currencies)
    i_flag, c_flag = _make_flag(Importance, importance), _make_flag(Currency, currencies)
    events = _get_calendar_events(datetime_from=time_from, datetime_to=time_to, importance=i_flag, currencies=c_flag)
    if function:
        events = list(filter(function, events))
    return events
