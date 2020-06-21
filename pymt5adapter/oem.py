import MetaTrader5 as _mt5

from . import core
from .types import *

_mt5_close = _mt5.Close
_mt5_buy = _mt5.Buy
_mt5_sell = _mt5.Sell
_mt5_raw_order = _mt5._RawOrder

# internal order send
def _RawOrder(order_type: int,
              symbol: str,
              volume: float,
              price: float,
              comment: str = None,
              ticket: int = None
              ) -> OrderSendResult:
    return _mt5_raw_order(order_type, symbol, volume, price, comment, ticket)


# Close all specific orders
@core._context_manager_modified(participation=True, advanced_features=True)
def Close(symbol: str, *, comment: str = None, ticket: int = None) -> Union[bool, str, None]:
    try:
        return _mt5_close(symbol, comment=comment, ticket=ticket)
    except (TypeError, AttributeError):
        return None


# Buy order
@core._context_manager_modified(participation=True, advanced_features=True)
def Buy(symbol: str, volume: float, price: float = None, *,
        comment: str = None, ticket: int = None) -> Union[OrderSendResult, None]:
    try:
        return _mt5_buy(symbol, volume, price, comment=comment, ticket=ticket)
    except (TypeError, AttributeError):
        return None


# Sell order
@core._context_manager_modified(participation=True, advanced_features=True)
def Sell(symbol: str, volume: float, price: float = None, *,
         comment: str = None, ticket: int = None) -> Union[OrderSendResult, None]:
    try:
        return _mt5_sell(symbol, volume, price, comment=comment, ticket=ticket)
    except (TypeError, AttributeError):
        return None
