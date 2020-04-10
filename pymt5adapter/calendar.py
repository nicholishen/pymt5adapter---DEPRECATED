import enum
import functools
import math
import re
from datetime import datetime
from datetime import timedelta
from typing import Callable
from typing import Iterable
from typing import List
from typing import Type
from typing import Union

import requests

__all__ = ['calendar_events', 'Importance', 'Currency']

_BASE_URL = "https://www.mql5.com"
_OMIT_RESULT_KEYS = ['FullDate']


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


def calendar_events(time_to: Union[datetime, timedelta] = None,
                    *,
                    time_from: Union[datetime, timedelta] = None,
                    importance: Union[Iterable[str], str, int] = None,
                    currencies: Union[Iterable[str], str, int] = None,
                    function: Callable = None,
                    round_minutes: int = 15,
                    cache_clear: bool = False,
                    language: str = None,
                    **kwargs,
                    ) -> List[dict]:
    """Get economic events from mql5.com/calendar. A call with empty args will results in all events for the next week.
    Since the function is memoized, the time is rounded to ``round_minutes`` and cached. This avoids repeat requests
    to the mql5.com server. In order to refresh the results on subsequest function calls you'll need to set the
    ``cache_clear`` param to True.

    :param time_to: Can be a timedelta or datetime object. If timedelta then the to time is calculated as
        datetime.now() + time_to. If the the time_from param is specified the the time_to will be calculated as
        time_from + time_to. Can also do a history look-back by passing in a negative timedelta to this param.
    :param time_from: Can be a timedelta or datetime object. If a timedelta object is passed then the time_from is
        calculated as time_from + now(), thus it needs to be a negative delta.
    :param importance: Can be int flags from the Importance enum class, and iterable of strings or a (space and/or
        comma separated string)
    :param currencies: Can be int flags from the Importance enum class, and iterable of strings or a (space and/or
        comma separated string) Pairs are automatically separated to the respective currency codes.
    :param function: A callback function that receives an event dict and returns bool for filtering.
    :param round_minutes: Round the number of minutes to this factor. Rounding aides the memoization of parameters.
    :param cache_clear: Clear the memo cache to refresh events from the server.
    :param language: The language code for the calendar. Default is 'en'
    :param kwargs:
    :return:
    """
    cal_args = _construct_args(**locals())
    if cache_clear:
        _get_calendar_events.cache_clear()
    events = _get_calendar_events(language=language, **cal_args)
    if function:
        events = list(filter(function, events))
    return events


@functools.lru_cache
def _get_calendar_events(datetime_from: datetime,
                         datetime_to: datetime,
                         importance: int,
                         currencies: int,
                         language: str = None,
                         ) -> List[dict]:
    lang = 'en' if language is None else language
    url = _BASE_URL + f"/{lang}/economic-calendar/content"
    headers = {"x-requested-with": "XMLHttpRequest"}
    time_format = "%Y-%m-%dT%H:%M:%S"
    data = {
        "date_mode" : 0,
        "from"      : datetime_from.strftime(time_format),
        "to"        : datetime_to.strftime(time_format),
        "importance": importance,
        "currencies": currencies,
    }
    response = requests.post(url=url, headers=headers, data=data)
    events = response.json()
    filtered_events = []
    for e in events:
        time = datetime.fromtimestamp(e['ReleaseDate'] / 1000)
        if datetime_from <= time <= datetime_to:
            e['Url'] = _BASE_URL + e['Url']
            e['ReleaseDate'] = time
            e['request'] = data
            formatted_event = {}
            for k, v in e.items():
                if k not in _OMIT_RESULT_KEYS:
                    formatted_event[_camel_to_snake(k)] = v
            filtered_events.append(formatted_event)
    return filtered_events


def _normalize_time(f, time: datetime, minutes: int):
    secs = minutes * 60
    res = f(time.timestamp() / secs) * secs
    new_time = datetime.fromtimestamp(res)
    return new_time


def _time_ceil(time: datetime, minutes: int):
    return _normalize_time(math.ceil, time, minutes)


def _time_floor(time: datetime, minutes: int):
    return _normalize_time(math.floor, time, minutes)


def _split_pairs(p: Iterable[str]):
    for s in p:
        yield from (s,) if len(s) < 6 else (s[:3], s[3:6])


def _camel_to_snake(w):
    if (c := _camel_to_snake.pattern.findall(w)):
        return '_'.join(map(str.lower, c))
    return w


_camel_to_snake.pattern = re.compile(r'[A-Z][a-z]*')


@functools.lru_cache(maxsize=128, typed=True)
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


def _construct_args(**kw):
    time_to = kw.get('time_to')
    time_from = kw.get('time_from')
    round_minutes = kw.get('round_minutes')
    importance = kw.get('importance')
    currencies = kw.get('currencies')
    now = datetime.now()
    if time_to is None and time_from is None:
        time_to = now + timedelta(weeks=1)
    time_from, time_to = (time_from or now, time_to or now)
    _f = lambda x: (now + x) if isinstance(x, timedelta) else x
    time_from = _f(time_from)  # time_from must go first in order to mutate it then add time_to
    time_to = _f(time_to)
    if time_from > time_to:
        time_from, time_to = time_to, time_from
    time_from = _time_floor(time_from, round_minutes)
    time_to = _time_ceil(time_to, round_minutes)
    _f = lambda x: tuple(x) if isinstance(x, Iterable) and not isinstance(x, str) else x
    importance, currencies = _f(importance), _f(currencies)
    i_flag, c_flag = _make_flag(Importance, importance), _make_flag(Currency, currencies)
    res_args = dict(datetime_to=time_to, datetime_from=time_from, importance=i_flag, currencies=c_flag)
    return res_args
