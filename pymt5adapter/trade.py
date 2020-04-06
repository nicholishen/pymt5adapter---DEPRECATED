from .const import *
from .core import order_send
from .core import symbol_info
from .core import symbol_info_tick
from .types import *
from .order import Order
from .symbol import Symbol


class Trade:

    def __init__(self, symbol: Union[str, SymbolInfo], magic=0):
        self._symbol = None
        self.symbol = symbol
        self.magic = magic
        self._order = Order(symbol=self.symbol, magic=self.magic)

    @property
    def symbol(self) -> Union[Symbol, None]:
        return self._symbol

    @symbol.setter
    def symbol(self, new_symbol):
        if isinstance(new_symbol, (str, Symbol, SymbolInfo)):
            s = Symbol(new_symbol)
        else:
            raise TypeError('Wrong assignment type. Must be str, Symbol, or SymbolInfo')
        self._symbol = s

    def _get_order(self, obj: Order) -> Order:
        return obj(symbol=self.symbol, magic=self.magic)

    # def _market_order(self, order, volume, comment=None):
    #     self._order = self._get_order(order)
    #     tick = self.symbol.refresh_rates().tick
    #     price = tick.ask if type == ORDER_TYPE_BUY else tick.bid
    #     self._order(volume=volume, price=price, comment=comment)
    #     result = self._order.send()
    #     return result

    def buy(self, volume: float, comment: str = None) -> OrderSendResult:
        price = self.symbol.refresh_rates().tick.ask
        self._order = self._get_order(Order.as_buy)(
            price=price, volume=volume, comment=comment)
        result = self._order.send()
        return result

    def sell(self, volume: float, comment: str = None) -> OrderSendResult:
        price = self.symbol.refresh_rates().tick.bid
        self._order = self._get_order(Order.as_sell)(
            price=price, volume=volume, comment=comment)
        result = self._order.send()
        return result
