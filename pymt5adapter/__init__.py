import MetaTrader5 as _mt5

from . import types
from .const import *
from .context import connected
from .context import handle_exit
from .core import *
from .helpers import dictify
from .helpers import LogJson
from .log import get_logger
from .oem import *

as_dict_all = dictify  # alias
__version__ = _mt5.__version__
__author__ = _mt5.__author__
