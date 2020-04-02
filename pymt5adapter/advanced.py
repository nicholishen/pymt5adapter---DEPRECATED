from .const import *
from .core import *


# class CSymbolInfo:
#     def __init__(self, symbol_name:str):
#         s = self._symbol_info = symbol_info(symbol_name)
#         d = s.__dict__.copy()
#         self.__dict__ = {k:v for k, v in d.items() if not k.startswith('_') and not k.startswith('n_')}
#
#     @property
#     def tick(self):
#         return symbol_info_tick(self.name)


class Trade:

    def __init__(self, symbol: Union[str, SymbolInfo] = None, magic=0):
        self._symbol = None
        self._magic = magic
        if symbol:
            self.symbol = symbol

    @property
    def magic(self) -> int:
        return self._magic

    @magic.setter
    def magic(self, magic: int):
        self._magic = int(magic)

    @property
    def symbol(self) -> SymbolInfo:
        return self._symbol

    @symbol.setter
    def symbol(self, new_symbol):
        if isinstance(new_symbol, str):
            self._symbol = symbol_info(new_symbol)
        elif isinstance(new_symbol, SymbolInfo):
            self._symbol = new_symbol
        else:
            raise TypeError('Wrong assignment type. Must be str or SymbolInfo')

    def setup(self, symbol=None, magic=None) -> 'Trade':
        if symbol:
            self.symbol = symbol
        if magic:
            self.magic = magic
        return self

    def _market_order(self, type, volume, comment=None):
        tick = symbol_info_tick(self.symbol.name)
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
