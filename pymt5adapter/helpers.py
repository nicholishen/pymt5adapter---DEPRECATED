from datetime import datetime

from .types import *

try:
    import ujson as json
except ImportError:
    import json


class LogJson(dict):
    def __init__(self, short_message_=None, dictionary_=None, **kwargs):
        self.default_short_message = 'JSON ENTRY'
        if dictionary_ is None and isinstance(short_message_, dict):
            dictionary_, short_message_ = short_message_, None
        is_dict = isinstance(dictionary_, dict)
        self.short_message = str(short_message_)
        if is_dict:
            super().__init__(dictionary_)
        else:
            super().__init__(**kwargs)

    def __str__(self):
        type_ = self['type']
        msg = self.short_message or type_ or self.default_short_message
        res = f"{msg}\t{json.dumps(self)}"
        return res


def any_symbol(symbol):
    """Pass any symbol object with a name property or string.

    :param symbol: Any symbol.
    :return: Symbol as string.
    """
    name = getattr(symbol, 'name', symbol)
    return name


def args_to_str(args: tuple, kwargs: dict):
    ar = ', '.join(map(str, args))
    kw = ', '.join(f"{k}={v}" for k, v in kwargs.items())
    return ar + (', ' if ar and kw else '') + kw


def __ify(data, apply_methods):
    for method in apply_methods:
        if hasattr(data, method):  # noqa
            return __ify(getattr(data, method)(), apply_methods)  # noqa
    T = type(data)
    if T is tuple or T is list:
        return T(__ify(i, apply_methods) for i in data)
    if T is dict:
        return {k: __ify(v, apply_methods) for k, v in data.items()}
    return data


def dictify(data: Any):
    """Convert all nested data returns to native python (pickleable) data structures. Example: List[OrderSendResult]
    -> List[dict]

    :param data: Any API returned result from the MetaTrader5 API
    :return:
    """
    # if hasattr(data, '_asdict'):  # noqa
    #     return dictify(data._asdict()) # noqa
    # T = type(data)
    # if T is tuple or T is list:
    #     return T(dictify(i) for i in data)
    # if T is dict:
    #     return {k: dictify(v) for k, v in data.items()}
    return __ify(data, ['_asdict'])


def make_native(data):
    return __ify(data, ['_asdict', 'tolist'])


def do_trade_action(func, args):
    cleaned = reduce_args(args)
    request = cleaned.pop('request', {})
    symbol = cleaned.pop('symbol', None) or request.pop('symbol', None)
    cleaned['symbol'] = any_symbol(symbol)
    order_request = reduce_combine(request, cleaned)
    if 'volume' in order_request and isinstance(order_request['volume'], int):
        order_request['volume'] = float(order_request['volume'])
    return func(order_request)


def get_ticket_type_stuff(func, *, symbol, group, ticket, function):
    d = locals().copy()
    kw = reduce_args_by_keys(d, ['symbol', 'group', 'ticket'])
    items = func(**kw)
    # if magic:
    #     items = filter(lambda p: p.magic == magic, items)
    if function:
        items = tuple(filter(function, items))

    if items is None:
        items = ()
    elif type(items) is not tuple:
        items = (items,)
    return items


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
    if deals is None:
        deals = ()
    elif type(deals) is not tuple:
        deals = (deals,)
    return deals


def is_rates_array(array):
    try:
        rate = array[0]
        return type(rate) is tuple and len(rate) == 8
    except:
        return False


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
