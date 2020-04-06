import MetaTrader5 as _mt5

from . import types
from .const import *
from .context import connected
from .core import *
from .oem import *

__version__ = _mt5.__version__
__author__ = _mt5.__author__


def as_dict_all(data: Any):
    """Convert all nested data returns to native python (pickleable) data structures. Example: List[OrderSendResult]
    -> List[dict]

    :param data: Any API returned result from the MetaTrader5 API
    :return:
    """
    try:
        return as_dict_all(data._asdict())
    except AttributeError:
        T = type(data)
        if T is tuple or T is list:
            return T(as_dict_all(i) for i in data)
        if T is dict:
            return {k: as_dict_all(v) for k, v in data.items()}
        return data
