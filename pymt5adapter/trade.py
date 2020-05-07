from . import const
from .context import _ContextAwareBase
from .core import positions_get
from .order import Order
from .symbol import Symbol
from .types import *


class Trade(_ContextAwareBase):

    def __init__(self, symbol: Union[str, SymbolInfo], magic=0):
        super().__init__()
        self._symbol = None
        self.symbol = symbol
        self.magic = magic
        # self._order = Order(symbol=self.symbol, magic=self.magic)
        self._position = None

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

    @property
    def position(self) -> TradePosition:
        if self._position is None:
            self.refresh()
        return self._position

    def refresh(self):
        p = positions_get(symbol=self.symbol.name, function=lambda p: p.magic == self.magic)
        self._position = p[0] if p else None
        return self

    def _do_market(self, order_constructor, volume: float, comment: str = None, **kwargs) -> OrderSendResult:
        price = self.symbol.refresh_rates().tick.ask
        order = order_constructor(
            symbol=self.symbol,
            magic=self.magic,
            price=price,
            volume=volume,
            comment=comment,
            **kwargs
        )
        result = order.send()
        return result

    def buy(self, volume: float, comment: str = None, **kwargs) -> OrderSendResult:
        return self._do_market(Order.as_buy, volume, comment, **kwargs)

    def sell(self, volume: float, comment: str = None, **kwargs) -> OrderSendResult:
        return self._do_market(Order.as_sell, volume, comment, **kwargs)

    def sltp_price(self, sl: int = None, tp: int = None, **kwargs):
        p = kwargs.get('position') or self.refresh().position
        order = Order.as_modify_sltp(p, sl=sl, tp=tp)
        result = order.send()
        return result

    def sltp_ticks(self, sl: int = None, tp: int = None, **kwargs):
        sl, tp = abs(sl), abs(tp)
        position = self.refresh().position
        tick_size = self.symbol.trade_tick_size
        tick = self.symbol.refresh_rates().tick
        if position.type == const.POSITION_TYPE.BUY:
            price = tick.bid
            sl = -sl
        else:
            price = tick.ask
            tp = -tp
        stop = price + sl * tick_size
        take = price + tp * tick_size
        result = self.sltp_price(sl=stop, tp=take, position=position, **kwargs)
        return result
