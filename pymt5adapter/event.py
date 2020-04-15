import enum
import time
from datetime import datetime
from datetime import timedelta

from . import period_seconds
from .const import COPY_TICKS
from .const import TIMEFRAME
from .core import copy_rates_from_pos
from .core import copy_ticks_range
from .core import symbol_info
from .types import *


class EVENT(enum.IntFlag):
    TICK_LAST_CHANGE = enum.auto()
    NEW_BAR = enum.auto()


def iter_event(symbol: Union[str, SymbolInfo],
               timeframe: TIMEFRAME,
               event_flags: Union[EVENT, int],
               sleep: float = 0.001):
    if event_flags == 0:
        return
    symbol = getattr(symbol, 'name', symbol_info(symbol))
    last_tick = None
    last_bar = copy_rates_from_pos(symbol.name, timeframe, 0, 1)[0]
    psec = timedelta(seconds=period_seconds(timeframe))
    next_bar_time = datetime.fromtimestamp(last_bar['time']) + psec
    # save as bool to prevent checking condition on each loop
    do_tick_event = EVENT.TICK_LAST_CHANGE in event_flags
    do_new_bar_event = EVENT.NEW_BAR in event_flags

    while True:
        if do_tick_event:
            now = datetime.now()
            last_tick_time = now - timedelta(seconds=1) if last_tick is None else datetime.fromtimestamp(last_tick.time)
            if last_tick_time > now:
                now, last_tick_time = last_tick_time, now
            ticks = copy_ticks_range(symbol.name, last_tick_time, now, COPY_TICKS.ALL)
            if ticks is not None:
                for tick in ticks:
                    tick = CopyTick(*tick)
                    if last_tick is None or tick.time_msc > last_tick.time_msc:
                        yield EVENT.TICK_LAST_CHANGE, tick
                        last_tick = tick
        if do_new_bar_event:
            if datetime.now() >= next_bar_time:
                bar = copy_rates_from_pos(symbol.name, timeframe, 0, 1)[0]
                if (bar_time := bar['time']) != last_bar['time']:
                    yield EVENT.NEW_BAR, CopyRate(*bar)
                    last_bar = bar
                    next_bar_time = datetime.fromtimestamp(bar_time) + psec
        time.sleep(sleep)
