from .const import *
from .core import order_send
from .core import symbol_info
from .core import symbol_info_tick
from .types import *


class Trade:
    _request_keys = MQL_TRADE_REQUEST_PROPS.keys()

    @classmethod
    def from_request(cls, request: dict):
        return cls(symbol=request.get('symbol', None), magic=request.get('magic', None))

    def __init__(self, symbol: Union[str, SymbolInfo] = None, magic=0):
        self._symbol = None
        self._magic = magic
        self._request = {}
        if symbol is not None:
            self.symbol = symbol

    @property
    def magic(self) -> int:
        return self._magic

    @magic.setter
    def magic(self, new_magic: int):
        self._request['magic'] = self._magic = new_magic

    @property
    def symbol(self) -> Union[SymbolInfo, None]:
        return self._symbol

    @symbol.setter
    def symbol(self, new_symbol):
        if isinstance(new_symbol, str):
            s = symbol_info(new_symbol)
        elif isinstance(new_symbol, SymbolInfo):
            s = new_symbol
        else:
            raise TypeError('Wrong assignment type. Must be str or SymbolInfo')
        self._request['symbol'] = s.name
        self._symbol = s

    def tick(self):
        return symbol_info_tick(self._symbol.name)

    def _market_order(self, type, volume, comment=None):
        tick = self.tick()
        price = tick.ask if type == ORDER_TYPE_BUY else tick.bid
        result = order_send(
            symbol=self.symbol.name,
            magic=self.magic,
            action=TRADE_ACTION_DEAL,
            type=type,
            volume=float(volume),
            price=price,
            comment=comment,
        )
        return result

    def market_buy(self, volume: float, comment: str = None) -> OrderSendResult:
        result = self._market_order(type=ORDER_TYPE_BUY, volume=volume, comment=comment)
        return result

    def market_sell(self, volume: float, comment: str = None) -> OrderSendResult:
        result = self._market_order(type=ORDER_TYPE_SELL, volume=volume, comment=comment)
        return result
