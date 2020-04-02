from .const import *
from .core import *
from .types import *

# internal order send
def _RawOrder(order_type:int,
              symbol:str,
              volume:float,
              price:float,
              comment:str=None,
              ticket:int=None
              ) -> OrderSendResult:
    order = {
        "action"   : TRADE_ACTION_DEAL,
        "symbol"   : symbol,
        "volume"   : volume,
        "type"     : order_type,
        "price"    : price,
        "deviation": 10,
    }
    if comment != None:
        order["comment"] = comment
    if ticket != None:
        order["position"] = ticket
    r = order_send(order)
    return r


# Close all specific orders
def Close(symbol:str, *, comment:str=None, ticket:int=None) -> Union[bool, str]:
    if ticket != None:
        positions = positions_get(ticket=ticket)
    else:
        positions = positions_get(symbol=symbol)

    tried = 0
    done = 0

    for pos in positions:
        # process only simple buy, sell
        if pos.type == ORDER_TYPE_BUY or pos.type == ORDER_TYPE_SELL:
            tried += 1
            for tries in range(10):
                info = symbol_info_tick(symbol)
                if pos.type == ORDER_TYPE_BUY:
                    r = _RawOrder(ORDER_TYPE_SELL, symbol, pos.volume, info.bid, comment, pos.ticket)
                else:
                    r = _RawOrder(ORDER_TYPE_BUY, symbol, pos.volume, info.ask, comment, pos.ticket)
                # check results
                if r.retcode != TRADE_RETCODE_REQUOTE and r.retcode != TRADE_RETCODE_PRICE_OFF:
                    if r.retcode == TRADE_RETCODE_DONE:
                        done += 1
                    break

    if done > 0:
        if done == tried:
            return True
        else:
            return "Partially"
    return False


# Buy order
def Buy(symbol:str, volume:float, price:float=None, *, comment:str=None, ticket:int=None) -> OrderSendResult:
    # with direct call
    if price != None:
        return _RawOrder(ORDER_TYPE_BUY, symbol, volume, price, comment, ticket)
    # no price, we try several times with current price
    for tries in range(10):
        info = symbol_info_tick(symbol)
        r = _RawOrder(ORDER_TYPE_BUY, symbol, volume, info.ask, comment, ticket)
        if r.retcode != TRADE_RETCODE_REQUOTE and r.retcode != TRADE_RETCODE_PRICE_OFF:
            break
    return r


# Sell order
def Sell(symbol:str, volume:float, price:float=None, *, comment:str=None, ticket:int=None) -> OrderSendResult:
    # with direct call
    if price != None:
        return _RawOrder(ORDER_TYPE_SELL, symbol, volume, price, comment, ticket)
    # no price, we try several times with current price
    for tries in range(10):
        info = symbol_info_tick(symbol)
        r = _RawOrder(ORDER_TYPE_SELL, symbol, volume, info.bid, comment, ticket)
        if r.retcode != TRADE_RETCODE_REQUOTE and r.retcode != TRADE_RETCODE_PRICE_OFF:
            break
    return r
