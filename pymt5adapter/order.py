import copy

from . import const
from .const import MQL_TRADE_REQUEST_PROPS
from .context import _ContextAwareBase
from .core import order_check
from .core import order_send
from .core import symbol_info_tick
from .helpers import any_symbol
from .helpers import reduce_combine
from .types import *


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


class Order(_ContextAwareBase):
    __slots__ = MQL_TRADE_REQUEST_PROPS.keys()

    @classmethod
    def as_buy(cls, **kwargs):
        return cls(action=const.TRADE_ACTION.DEAL, type=const.ORDER_TYPE.BUY, **kwargs)

    @classmethod
    def as_sell(cls, **kwargs):
        return cls(action=const.TRADE_ACTION.DEAL, type=const.ORDER_TYPE.SELL, **kwargs)

    @classmethod
    def as_buy_limit(cls, **kwargs):
        return cls(action=const.TRADE_ACTION.PENDING, type=const.ORDER_TYPE.BUY_LIMIT, **kwargs)

    @classmethod
    def as_sell_limit(cls, **kwargs):
        return cls(action=const.TRADE_ACTION.PENDING, type=const.ORDER_TYPE.SELL_LIMIT, **kwargs)

    @classmethod
    def as_buy_stop(cls, **kwargs):
        return cls(action=const.TRADE_ACTION.PENDING, type=const.ORDER_TYPE.BUY_STOP, **kwargs)

    @classmethod
    def as_sell_stop(cls, **kwargs):
        return cls(action=const.TRADE_ACTION.PENDING, type=const.ORDER_TYPE.SELL_STOP, **kwargs)

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

    @classmethod
    def as_adjusted_net_position(cls, position: TradePosition, new_net_position: float, **kwargs):
        volume = position.volume
        volume = -volume if position.type else volume
        new_volume = new_net_position - volume
        order_obj = cls.as_sell(**kwargs) if new_volume < 0.0 else cls.as_buy(**kwargs)
        order_obj.volume = abs(new_volume)
        order_obj.symbol = position.symbol
        order_obj.magic = position.magic
        order_obj.sl = position.sl
        order_obj.tp = position.tp
        return order_obj

    @classmethod
    def as_modify_sltp(cls, position: Union[TradePosition, int], sl=None, tp=None, **kwargs):
        order = cls(
            action=const.TRADE_ACTION.SLTP,
            position=getattr(position, 'ticket', position),
            sl=sl,
            tp=tp,
            **kwargs
        )
        if isinstance(position, TradePosition):
            order.symbol = position.symbol
            order.sl = sl or position.sl
            order.tp = tp or position.tp
        return order

    @classmethod
    def as_delete_pending(cls, order: Union[TradeOrder, int]):
        order_ticket = getattr(order, 'ticket', order)
        order_obj = cls(
            action=const.TRADE_ACTION.REMOVE,
            order=order_ticket,
        )
        return order_obj

    def __init__(self,
                 request: dict = None, *, action: int = None, magic: int = None,
                 order: int = None, symbol=None, volume: float = None,
                 price: float = None, stoplimit: float = None, sl: float = None, tp: float = None,
                 deviation: int = None, type: int = None, type_filling: int = None, type_time: int = None,
                 expiration: int = None, comment: str = None, position: int = None, position_by: int = None,
                 **kwargs
                 ):
        super().__init__()
        args = locals().copy()
        del args['self']
        self.action = self.magic = self.order = self.symbol = self.volume = self.price = None
        self.stoplimit = self.sl = self.tp = self.deviation = self.type = self.type_filling = None
        self.type_time = self.expiration = self.comment = self.position = self.position_by = None
        self.__call__(**args)

    def __call__(self,
                 request: dict = None, *, action: int = None, magic: int = None,
                 order: int = None, symbol=None, volume: float = None,
                 price: float = None, stoplimit: float = None, sl: float = None, tp: float = None,
                 deviation: int = None, type: int = None, type_filling: int = None, type_time: int = None,
                 expiration: int = None, comment: str = None, position: int = None, position_by: int = None,
                 **kwargs
                 ):

        args = locals().copy()
        request = args.pop('request', None) or {}
        symbol = args.get('symbol') or request.get('symbol')
        args['symbol'] = any_symbol(symbol)
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
        req = {}
        for k in self.__slots__:
            v = getattr(self, k)
            if v is not None:
                req[k] = v
        # refactor for older python versions
        # req = {k: v for k in self.__slots__ if (v := getattr(self, k)) is not None}
        return req

    def check(self) -> OrderCheckResult:
        # TODO test
        return order_check(self.request())

    def send(self) -> OrderSendResult:
        # TODO test
        req = self.request()
        action = req.get('action')
        if action == const.TRADE_ACTION.DEAL:
            price = req.get('price')
            if price is None:
                symbol = req.get('symbol')
                if symbol:
                    t = req.get('type')
                    tick = symbol_info_tick(symbol)
                    req['price'] = tick.ask if t == const.ORDER_TYPE.BUY else tick.bid
        res = order_send(req)
        return res

    def copy(self) -> 'Order':
        return copy.deepcopy(self)
