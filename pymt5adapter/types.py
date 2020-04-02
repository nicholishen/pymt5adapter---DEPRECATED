import MetaTrader5 as _mt5
from collections import namedtuple

from typing import Callable
from typing import Iterable
from typing import Tuple
from typing import Union

# MT5 namedtuple objects for typing
Rate = namedtuple("Rate", "time open high low close tick_volume spread real_volume")
Tick = _mt5.Tick
AccountInfo = _mt5.AccountInfo
SymbolInfo = _mt5.SymbolInfo
TerminalInfo = _mt5.TerminalInfo
OrderCheckResult = _mt5.OrderCheckResult
OrderSendResult = _mt5.OrderSendResult
TradeOrder = _mt5.TradeOrder
TradeDeal = _mt5.TradeDeal
TradeRequest = _mt5.TradeRequest
TradePosition = _mt5.TradePosition
