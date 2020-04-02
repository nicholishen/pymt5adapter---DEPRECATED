import MetaTrader5 as _mt5

from .types import *


# internal order send
def _RawOrder(order_type: int,
              symbol: str,
              volume: float,
              price: float,
              comment: str = None,
              ticket: int = None
              ) -> OrderSendResult:
    return _mt5._RawOrder(order_type, symbol, volume, price, comment, ticket)


# Close all specific orders
def Close(symbol: str, *, comment: str = None, ticket: int = None) -> Union[bool, str]:
    return _mt5.Close(symbol, comment=comment, ticket=ticket)


# Buy order
def Buy(symbol: str, volume: float, price: float = None, *,
        comment: str = None, ticket: int = None) -> OrderSendResult:
    return _mt5.Buy(symbol, volume, price, comment=comment, ticket=ticket)


# Sell order
def Sell(symbol: str, volume: float, price: float = None, *,
         comment: str = None, ticket: int = None) -> OrderSendResult:
    return _mt5.Sell(symbol, volume, price, comment=comment, ticket=ticket)
