import copy

from . import const
from .const import MQL_TRADE_REQUEST_PROPS
from .core import order_check
from .core import order_send
from .helpers import reduce_combine
from .types import OrderCheckResult
from .types import OrderSendResult
from .types import TradePosition


def create_order_request(request: dict = None, *, action: int = None, magic: int = None,
                         order: int = None, symbol: str = None, volume: float = None,
                         price: float = None, stoplimit: float = None, sl: float = None, tp: float = None,
                         deviation: int = None, type: int = None, type_filling: int = None, type_time: int = None,
                         expiration: int = None, comment: str = None, position: int = None, position_by: int = None,
                         **kwargs) -> dict:
    """Construct a trade request dictionary using the predefined keywords.

    :param request: Pass in an existing request dictionary and the keyword args will update existing or add new.
    :return:
    """
    return Order(**locals().copy()).request()


class Order:
    __slots__ = MQL_TRADE_REQUEST_PROPS.keys()

    @classmethod
    def as_buy(cls, **kwargs):
        return cls(action=const.TRADE_ACTION_DEAL, type=const.ORDER_TYPE_BUY, **kwargs)

    @classmethod
    def as_sell(cls, **kwargs):
        return cls(action=const.TRADE_ACTION_DEAL, type=const.TRADE_ACTION_DEAL, **kwargs)

    @classmethod
    def as_buy_limit(cls, **kwargs):
        return cls(action=const.TRADE_ACTION_PENDING, type=const.ORDER_TYPE_BUY_LIMIT, **kwargs)

    @classmethod
    def as_sell_limit(cls, **kwargs):
        return cls(action=const.TRADE_ACTION_PENDING, type=const.ORDER_TYPE_SELL_LIMIT, **kwargs)

    @classmethod
    def as_buy_stop(cls, **kwargs):
        return cls(action=const.TRADE_ACTION_PENDING, type=const.ORDER_TYPE_BUY_STOP, **kwargs)

    @classmethod
    def as_sell_stop(cls, **kwargs):
        return cls(action=const.TRADE_ACTION_PENDING, type=const.ORDER_TYPE_SELL_STOP, **kwargs)

    @classmethod
    def as_flatten(cls, position: TradePosition, **kwargs):
        res = cls.as_sell() if position.type == const.ORDER_TYPE_BUY else cls.as_buy()
        return res(position=position.ticket, symbol=position.symbol,
                   volume=position.volume, magic=position.magic, **kwargs)

    @classmethod
    def as_reverse(cls, position: TradePosition, **kwargs):
        res = cls.as_flatten(position)
        res.volume *= 2
        return res

    def __init__(self,
                 request: dict = None, *, action: int = None, magic: int = None,
                 order: int = None, symbol: str = None, volume: float = None,
                 price: float = None, stoplimit: float = None, sl: float = None, tp: float = None,
                 deviation: int = None, type: int = None, type_filling: int = None, type_time: int = None,
                 expiration: int = None, comment: str = None, position: int = None, position_by: int = None,
                 **kwargs
                 ):
        args = locals().copy()
        del args['self']
        self.action = self.magic = self.order = self.symbol = self.volume = self.price = None
        self.stoplimit = self.sl = self.tp = self.deviation = self.type = self.type_filling = None
        self.type_time = self.expiration = self.comment = self.position = self.position_by = None
        self.__call__(**args)

    def __call__(self,
                 request: dict = None, *, action: int = None, magic: int = None,
                 order: int = None, symbol: str = None, volume: float = None,
                 price: float = None, stoplimit: float = None, sl: float = None, tp: float = None,
                 deviation: int = None, type: int = None, type_filling: int = None, type_time: int = None,
                 expiration: int = None, comment: str = None, position: int = None, position_by: int = None,
                 **kwargs
                 ):

        args = locals().copy()
        request = args.pop('request', None) or {}
        self._set_self_kw(reduce_combine(request, args))
        return self

    def __repr__(self):
        name = type(self).__name__
        args = [f'{k}={v}' for k, v in self.request().items()]
        sig = f"({', '.join(args)})"
        return name + sig

    def _set_self_kw(self, kw: dict):
        for k, v in kw.items():
            if v is not None and k in self.__slots__:
                setattr(self, k, v)

    def request(self) -> dict:
        # TODO check this against a control. Make sure it works when passing request as well as when overriding the rew.
        req = {k: v for k in self.__slots__ if (v := getattr(self, k)) is not None}
        return req

    def check(self) -> OrderCheckResult:
        # TODO test
        return order_check(self.request())

    def send(self) -> OrderSendResult:
        # TODO test
        return order_send(self.request())

    def copy(self) -> 'Order':
        return copy.deepcopy(self)
