from datetime import datetime

from .types import *


def any_symbol(symbol):
    """Pass any symbol object with a name property or string.

    :param symbol: Any symbol.
    :return: Symbol as string.
    """
    try:
        return symbol.name
    except AttributeError:
        return symbol


def reduce_args(kwargs: dict) -> dict:
    return {k: v for k, v in kwargs.items() if v is not None and k != 'kwargs'}


def reduce_args_by_keys(d: dict, keys: Iterable) -> dict:
    return {k: v for k, v in d.items() if k in keys and v is not None}


def reduce_combine(d1: dict, d2: dict):
    d1 = reduce_args(d1)
    for k, v in d2.items():
        if v is not None:
            d1[k] = v
    return d1


def args_to_str(args: tuple, kwargs: dict):
    ar = ', '.join(map(str, args))
    kw = ', '.join(f"{k}={v}" for k, v in kwargs.items())
    return ar + (', ' if ar and kw else '') + kw


def is_rates_array(array):
    try:
        rate = array[0]
        return type(rate) is tuple and len(rate) == 8
    except:
        return False


def get_ticket_type_stuff(func, *, symbol, group, ticket, function):
    d = locals().copy()
    kw = reduce_args_by_keys(d, ['symbol', 'group', 'ticket'])
    items = func(**kw)
    # if magic:
    #     items = filter(lambda p: p.magic == magic, items)
    if function:
        items = filter(function, items)
    return tuple(items) if items is not None else tuple()


def get_history_type_stuff(func, args):
    args = reduce_args(args)
    function = args.pop('function', None)
    datetime_from = args.get('datetime_from', None)
    datetime_to = args.get('datetime_to', None)
    if not args:
        datetime_from = datetime(2000, 1, 1)
        datetime_to = datetime.now()
    if datetime_from is not None and datetime_to is not None:
        deals = func(datetime_from, datetime_to, **args)
    else:
        deals = func(**args)
    if function:
        deals = tuple(filter(function, deals))
    return deals if deals is not None else tuple()


def do_trade_action(func, args):
    cleaned = reduce_args(args)
    request = cleaned.pop('request', {})
    symbol = cleaned.pop('symbol', None) or request.pop('symbol', None)
    cleaned['symbol'] = any_symbol(symbol)
    order_request = reduce_combine(request, cleaned)
    return func(order_request)
