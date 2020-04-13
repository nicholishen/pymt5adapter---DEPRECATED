import itertools

import pytest

from pymt5adapter.state import global_state as state
from .context import pymt5adapter as mt5


@pytest.fixture
def connected():
    context = mt5.connected(  # debug_logging=True,
        ensure_trade_enabled=True,
        enable_real_trading=False,
        timeout=3000
    )
    return context


def first_symbol():
    return mt5.symbols_get(function=lambda s: s.visible and s.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL)[0]


def make_kwargs_func(func):
    return lambda **kwargs: func(**kwargs)


def test_as_dict_all(connected):
    from pymt5adapter import as_dict_all
    from typing import Iterable
    # from time import perf_counter_ns

    def no_namedtuples(item):
        if isinstance(item, Iterable) and not isinstance(item, str):
            for i in item:
                if not no_namedtuples(i):
                    return False
        if isinstance(item, dict):
            for k, v in item.items():
                if not no_namedtuples(v):
                    return False
        if hasattr(item, '_asdict'):
            return False
        return True

    with connected:
        deals = mt5.history_deals_get()[:3]
        mutated_deals = as_dict_all(deals)
        assert len(deals) == len(mutated_deals)
        assert all(isinstance(d, dict) for d in mutated_deals)
        symbols = mt5.symbols_get()
        # b = perf_counter_ns()
        symbols = as_dict_all(symbols)
        # total = perf_counter_ns() - b
        assert no_namedtuples(symbols)
        # print(f"as_dict_all_time = {total / 1000}")


def test_trade_class(connected):
    from pymt5adapter.trade import Trade
    with connected:
        trade = Trade(symbol=first_symbol(), magic=1234)
        res = trade.buy(1.0)
        assert isinstance(res, mt5.OrderSendResult)


def test_order_class(connected):
    from pymt5adapter.order import Order, create_order_request
    control = dict(symbol="EURUSD", action=mt5.TRADE_ACTION_DEAL, type=mt5.ORDER_TYPE_BUY, price=1.2345,
                   comment="control")
    order = Order(control)
    assert order.request() == control
    order.comment = "control"
    assert order.request() == control
    order(control, type=mt5.ORDER_TYPE_BUY)
    assert order.request() == control

    buy_order = Order.as_buy()
    assert buy_order.type == mt5.ORDER_TYPE_BUY
    assert buy_order.action == mt5.TRADE_ACTION_DEAL
    sell_order = Order.as_sell()
    assert sell_order.type == mt5.ORDER_TYPE_SELL
    assert sell_order.action == mt5.TRADE_ACTION_DEAL

    with connected:
        symbol = first_symbol()
        tick = mt5.symbol_info_tick(symbol.name)
        result = buy_order(symbol=symbol, volume=1.0).send()
        assert isinstance(result, mt5.OrderSendResult)


def test_copy_rates(connected):
    with connected:
        maxbars = mt5.terminal_info().maxbars
        s = first_symbol().name
        rates = mt5.copy_rates(s, mt5.TIMEFRAME_M1, count=maxbars)
        assert len(rates) > 0


def test_raise_on_errors():
    with mt5.connected(raise_on_errors=True):
        with pytest.raises(mt5.MT5Error):
            _ = mt5.history_orders_total(',', ',')
    # does not raise
    with mt5.connected(raise_on_errors=False):
        try:
            _ = mt5.history_orders_total(',', ',')
        except mt5.MT5Error:
            pytest.fail()


# def test_trade_class(connected):
#     from pymt5adapter.trade import Trade
#     with connected:
#         symbol = mt5.symbols_get(function=lambda s: s.visible)[0].name
#         orig_req = Trade(symbol, 12345).market_buy(1).request
#         print(orig_req)


def test_borg_state_class():
    from pymt5adapter.state import _GlobalState
    s1 = _GlobalState()
    s2 = _GlobalState()
    s1.raise_on_errors = True
    s2.raise_on_errors = False
    assert not s1.raise_on_errors


def test_mt5_connection_context():
    state.set_defaults()
    assert not state.global_debugging
    assert not state.raise_on_errors
    connection = mt5.connected(raise_on_errors=True, debug_logging=True)
    with connection:
        assert state.global_debugging
        assert state.raise_on_errors
        try:
            x = mt5.history_deals_get("sadf", "asdf")
        except mt5.MT5Error as e:
            print(e)
        # pass


def test_initialize(connected):
    assert isinstance(mt5.initialize(), bool)
    error_code = mt5.last_error()[0]
    assert error_code == mt5.RES_S_OK
    mt5.shutdown()
    assert isinstance(make_kwargs_func(mt5.initialize)(), bool)
    error_code = mt5.last_error()[0]
    assert error_code == mt5.RES_S_OK
    mt5.shutdown()


def test_package_version():
    import re
    pattern = re.compile(r'^\d+\.\d+\.\d+$')
    assert isinstance(version := mt5.__version__, str)
    assert pattern.match(version)


def test_terminal_version(connected):
    with connected:
        version = mt5.version()
        assert isinstance(version, tuple)
        assert len(version) == 3
        assert isinstance(version[0], int)
        assert isinstance(version[1], int)
        assert isinstance(version[2], str)


def test_last_error_res_codes(connected):
    with connected:
        defined_error_codes = [getattr(mt5, name) for name in dir(mt5) if name.startswith('RES_')]
        for code in defined_error_codes:
            assert isinstance(code, int)


def test_last_error(connected):
    with connected:
        defined_error_codes = [getattr(mt5, name) for name in dir(mt5) if name.startswith('RES_')]
        error = mt5.last_error()
        assert isinstance(error, tuple)
        assert len(error) == 2
        code, description = error
        assert code in defined_error_codes
        assert isinstance(code, int)
        assert isinstance(description, str)


def test_account_info(connected):
    with connected:
        info = mt5.account_info()
        assert isinstance(info, mt5.AccountInfo)


def test_terminal_info(connected):
    with connected:
        info = mt5.terminal_info()
        assert isinstance(info, mt5.TerminalInfo)


def test_symbols_total(connected):
    with connected:
        total = mt5.symbols_total()
        assert total is not None
        assert isinstance(total, int)


def test_symbols_get(connected):
    with connected:
        assert (symbols := mt5.symbols_get()) is not None
        assert make_kwargs_func(mt5.symbols_get)() is not None
        assert isinstance(symbols, tuple)
        assert len(symbols) > 0
        assert isinstance(symbols[0], mt5.SymbolInfo)
        symbols = mt5.symbols_get(group="NON_EXISTENT_GROUP")
        assert symbols is not None
        assert isinstance(symbols, tuple)
        assert len(symbols) == 0


def test_symbol_info(connected):
    with connected:
        info = mt5.symbol_info("EURUSD")
        assert isinstance(info, mt5.SymbolInfo)


def test_symbol_info_tick(connected):
    with connected:
        info = mt5.symbol_info_tick("EURUSD")
        assert isinstance(info, mt5.Tick)


def test_symbol_select(connected):
    with connected:
        selected = mt5.symbol_select("EURUSD")
        assert isinstance(selected, bool)


def test_orders_total(connected):
    with connected:
        total = mt5.orders_total()
        assert isinstance(total, int)


def test_orders_get(connected):
    with connected:
        assert (orders := mt5.orders_get()) is not None
        assert make_kwargs_func(mt5.orders_get)() is not None
        assert isinstance(orders, tuple)


def test_positions_total(connected):
    with connected:
        total = mt5.positions_total()
        assert isinstance(total, int)


def test_positions_get(connected):
    with connected:
        assert (p1 := mt5.positions_get()) is not None
        assert (p2 := make_kwargs_func(mt5.positions_get)()) is not None
        assert len(p1) == len(p2)
        invalid_positions = mt5.positions_get(symbol="FAKE_SYMBOL")
        assert isinstance(invalid_positions, tuple)
        assert len(invalid_positions) == 0
        invalid_positions = mt5.positions_get(ticket=0)
        assert isinstance(invalid_positions, tuple)
        assert len(invalid_positions) == 0


def test_history_deals_get(connected):
    with connected:
        deals = mt5.history_deals_get(ticket=0)
        # assert isinstance(deals, tuple)


def test_history_orders_get(connected):
    with connected:
        orders = mt5.history_orders_get(ticket=0)
        # assert isinstance(orders, tuple)


def test_consistency_for_empty_data_returns(connected):
    def all_same_return_types(results):
        g = itertools.groupby(results, key=lambda v: type(v))
        return next(g, True) and not next(g, False)

    funcs = (mt5.positions_get, mt5.orders_get, mt5.history_orders_get, mt5.history_deals_get,)
    with connected:
        results = [f(ticket=0) for f in funcs]
        assert all_same_return_types(results)


def test_copy_ticks_range(connected):
    from datetime import datetime, timedelta, timezone
    import time

    with connected:
        symbol = first_symbol()
        last_bar_time = mt5.copy_rates_from_pos(symbol.name, mt5.TIMEFRAME.M1, 0, 1)[0]['time']
        time_to = datetime.fromtimestamp(last_bar_time, tz=timezone.utc)
        time_from = time_to - timedelta(minutes=3)

        for i in range(20):
            ticks = mt5.copy_ticks_range(symbol.name, time_from, time_to, mt5.COPY_TICKS.ALL)
            if len(ticks) > 0:
                break
            time.sleep(1)
        assert mt5.last_error()[0] == mt5.ERROR_CODE.OK
        assert len(ticks) > 0


def test_period_seconds():
    assert mt5.period_seconds(mt5.TIMEFRAME.M1) == 60
    assert mt5.period_seconds(99999) is None


if __name__ == "__main__":
    pass
