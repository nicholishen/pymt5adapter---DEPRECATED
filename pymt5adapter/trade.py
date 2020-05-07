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

    def modify_sltp_by_price(self, sl: int = None, tp: int = None, **kwargs) -> OrderSendResult:
        """Modify an existing position by exact prices.

        :param sl: stop loss price
        :param tp: take profit price
        :param kwargs: kwargs are propagated to the Order class used for the order
        :return: Result of order_send
        """
        p = kwargs.get('position') or self.refresh().position
        if sl:
            sl = self.symbol.normalize_price(sl)
        if tp:
            tp = self.symbol.normalize_price(tp)
        order = Order.as_modify_sltp(position=p, sl=sl, tp=tp)
        result = order.send()
        return result

    def modify_sltp_by_ticks(self,
                             sl: int = None,
                             tp: int = None,
                             price_basis: Union[str, float] = 'open',
                             **kwargs
                             ) -> OrderSendResult:
        """Modify an existing position by number of ticks.

        :param sl: number of ticks away from the defined price for stoploss
        :param tp: number of ticks away from the defined price for take profit
        :param price_basis: the price basis for calculation of levels. if a str == 'open' is passed then the stops
        will be calculated using the position cost-basis. Otherwise, 'current' will use the current price.
        :param kwargs: kwargs are propagated to the Order class used for the order
        :return: Result of order_send
        """
        position = self.refresh().position
        tick_size = self.symbol.trade_tick_size
        if isinstance(price_basis, float):
            bid = ask = price_basis
        elif 'current' in price_basis.lower():
            tick = self.symbol.refresh_rates().tick
            bid, ask = tick.bid, tick.ask
        else:
            bid = ask = position.price_open
        if position.type == const.POSITION_TYPE.BUY:
            price = bid
            stop = -abs(sl) if sl else None
            take = abs(tp) if tp else None
        else:
            price = ask
            take = -abs(tp) if tp else None
            stop = abs(sl) if sl else None
        if stop:
            stop = price + stop * tick_size
        if take:
            take = price + take * tick_size
        result = self.modify_sltp_by_price(sl=stop, tp=take, position=position, **kwargs)
        return result
