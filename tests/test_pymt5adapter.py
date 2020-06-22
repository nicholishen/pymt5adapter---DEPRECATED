import itertools
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest

from .context import pymt5adapter as mta
from pymt5adapter.state import global_state as state
from pymt5adapter import MT5Error


import logging
from pathlib import Path

LOGPATH = Path.home() / 'Desktop/pytest_mt5.log'
# PYTEST SETUP
@pytest.fixture
def connected():
    logger = mta.get_logger(loglevel=logging.DEBUG, path_to_logfile=LOGPATH)
    context = mta.connected(
        logger=logger,
        ensure_trade_enabled=True,
        enable_real_trading=False,
        timeout=3000
    )
    return context


# def test_connected_class():
#     connected = mt5.context.connected_class()
#     with connected as conn:
#         conn.raise_on_errors = True
#         conn.debug_logging = True
#         conn.


def first_symbol():
    return mta.symbols_get(function=lambda s: s.visible and s.trade_mode == mta.SYMBOL_TRADE_MODE_FULL)[0]


def make_kwargs_func(func):
    return lambda **kwargs: func(**kwargs)


def test_mt5_connection_context():
    from pymt5adapter.context import Ping
    state.set_defaults()
    assert not state.logger
    assert not state.raise_on_errors
    connected = mta.connected(timeout=5000)
    with connected as conn:
        # make sure the conn is setting the global state from properties
        assert not state.logger
        conn.logger = mta.get_logger(path_to_logfile=LOGPATH, loglevel=logging.DEBUG)
        assert state.logger

        assert not state.raise_on_errors
        conn.raise_on_errors = True
        assert state.raise_on_errors

        with pytest.raises(MT5Error):
            x = mta.history_deals_get("sadf", "asdf")

        conn.raise_on_errors = False
        try:
            x = mta.history_deals_get("sadf", "asdf")
        except MT5Error:
            pytest.fail("Raised MT5Error when feature was toggled off")
        ping = conn.ping()
        assert isinstance(ping, Ping)
        # pass


def test_make_native():
    import json
    with mta.connected(return_as_native_python_objects=True) as conn:
        rates = mta.copy_rates_from_pos("EURUSD", mta.TIMEFRAME_M1, 0, 1)
        account = mta.account_info()
        x = dict(rates=rates, account=account)
        try:
            j = json.dumps(x)
        except Exception:
            pytest.fail()



def test_return_as_dict_all(connected):
    assert mta.as_dict_all is mta.dictify
    import pickle
    with connected as conn:
        conn.return_as_dict = True
        symbol_dict = first_symbol()
        conn.return_as_dict = False
        symbol_tuple = first_symbol()
    assert type(symbol_dict) is dict
    assert isinstance(symbol_tuple, tuple)
    # MetaTrader5 return data is not picklable
    with pytest.raises(pickle.PicklingError):
        x = pickle.dumps(symbol_tuple)
    try:
        x = pickle.dumps(symbol_dict)
    except pickle.PicklingError:
        pytest.fail()


def test_terminal_version(connected):
    with connected:
        version = mta.version()
        assert isinstance(version, tuple)
        assert len(version) == 3
        assert isinstance(version[0], int)
        assert isinstance(version[1], int)
        assert isinstance(version[2], str)


def test_package_version():
    v = mta.__version__
    assert isinstance(v, dict)
    assert 'MetaTrader5' in v
    assert 'pymt5adapter' in v
    assert 'pymt5adapter' in v


# CORE TESTING
def test_account_info(connected):
    with connected:
        info = mta.account_info()
        assert isinstance(info, mta.AccountInfo)


def test_consistency_for_empty_data_returns(connected):
    def all_same_return_types(results):
        g = itertools.groupby(results, key=lambda v: type(v))
        return next(g, True) and not next(g, False)

    funcs = (mta.positions_get, mta.orders_get, mta.history_orders_get, mta.history_deals_get,)
    with connected:
        results = [f(ticket=0) for f in funcs]
        assert all_same_return_types(results)


def test_copy_rates(connected):
    with connected as conn:
        rstate = conn.raise_on_errors
        conn.raise_on_errors = True
        try:
            s = first_symbol().name
            rates = mta.copy_rates(s, mta.TIMEFRAME_M1, count=10_000)
            assert len(rates) > 0
        finally:
            conn.raise_on_errors = rstate


def test_copy_ticks_range(connected):
    import time

    with connected:
        symbol = first_symbol()
        last_bar_time = mta.copy_rates_from_pos(symbol.name, mta.TIMEFRAME.M1, 0, 1)[0]['time']
        time_to = datetime.fromtimestamp(last_bar_time, tz=timezone.utc)
        time_from = time_to - timedelta(minutes=3)

        for i in range(20):
            ticks = mta.copy_ticks_range(symbol.name, time_from, time_to, mta.COPY_TICKS.ALL)
            if len(ticks) > 0:
                break
            time.sleep(1)
        assert mta.last_error()[0] == mta.ERROR_CODE.OK
        assert len(ticks) > 0


def test_copy_ticks_from(connected):
    with connected:
        symbol = first_symbol()
        last_bar_time = datetime.now() - timedelta(
            minutes=1)  # mt5.copy_rates_from_pos(symbol.name, mt5.TIMEFRAME.M1, 0, 1)[0]['time']
        print(last_bar_time)
        ticks = mta.copy_ticks_from(symbol.name,
                                    datetime_from=last_bar_time,
                                    count=mta.MAX_TICKS,
                                    flags=mta.COPY_TICKS.ALL, )
        assert len(ticks) > 0


def test_history_deals_get(connected):
    with connected:
        deals = mta.history_deals_get(ticket=0)
        # assert isinstance(deals, tuple)


def test_history_orders_get(connected):
    with connected:
        orders = mta.history_orders_get(ticket=0)
        # assert isinstance(orders, tuple)


def test_initialize(connected):
    assert isinstance(mta.initialize(), bool)
    error_code = mta.last_error()[0]
    assert error_code == mta.RES_S_OK
    mta.shutdown()
    assert isinstance(make_kwargs_func(mta.initialize)(), bool)
    error_code = mta.last_error()[0]
    assert error_code == mta.RES_S_OK
    mta.shutdown()


def test_last_error_res_codes(connected):
    with connected:
        defined_error_codes = [getattr(mta, name) for name in dir(mta) if name.startswith('RES_')]
        for code in defined_error_codes:
            assert isinstance(code, int)


def test_order_class(connected):
    from pymt5adapter.order import Order
    control = dict(symbol="EURUSD", action=mta.TRADE_ACTION_DEAL, type=mta.ORDER_TYPE_BUY, price=1.2345,
                   comment="control")
    order = Order(control)
    assert order.request() == control
    order.comment = "control"
    assert order.request() == control
    order(control, type=mta.ORDER_TYPE_BUY)
    assert order.request() == control

    buy_order = Order.as_buy()
    assert buy_order.type == mta.ORDER_TYPE_BUY
    assert buy_order.action == mta.TRADE_ACTION_DEAL
    sell_order = Order.as_sell()
    assert sell_order.type == mta.ORDER_TYPE_SELL
    assert sell_order.action == mta.TRADE_ACTION_DEAL

    with connected:
        symbol = first_symbol()
        tick = mta.symbol_info_tick(symbol.name)
        result = buy_order(symbol=symbol, volume=1.0).send()
        assert isinstance(result, mta.OrderSendResult)


def test_last_error(connected):
    with connected:
        defined_error_codes = [getattr(mta, name) for name in dir(mta) if name.startswith('RES_')]
        error = mta.last_error()
        assert isinstance(error, tuple)
        assert len(error) == 2
        code, description = error
        assert code in defined_error_codes
        assert isinstance(code, int)
        assert isinstance(description, str)


def test_orders_get(connected):
    with connected:
        assert (orders := mta.orders_get()) is not None
        assert make_kwargs_func(mta.orders_get)() is not None
        assert isinstance(orders, tuple)


def test_orders_total(connected):
    with connected:
        total = mta.orders_total()
        assert isinstance(total, int)


def test_period_seconds():
    assert mta.period_seconds(mta.TIMEFRAME.M1) == 60
    assert mta.period_seconds(99999) is None


def test_positions_get(connected):
    with connected:
        assert (p1 := mta.positions_get()) is not None
        assert (p2 := make_kwargs_func(mta.positions_get)()) is not None
        assert len(p1) == len(p2)
        invalid_positions = mta.positions_get(symbol="FAKE_SYMBOL")
        assert isinstance(invalid_positions, tuple)
        assert len(invalid_positions) == 0
        invalid_positions = mta.positions_get(ticket=0)
        assert isinstance(invalid_positions, tuple)
        assert len(invalid_positions) == 0


def test_positions_total(connected):
    with connected:
        total = mta.positions_total()
        assert isinstance(total, int)


def test_symbol_info(connected):
    with connected:
        info = mta.symbol_info("EURUSD")
        assert isinstance(info, mta.SymbolInfo)


def test_symbol_info_tick(connected):
    with connected:
        info = mta.symbol_info_tick("EURUSD")
        print(type(info))
        assert isinstance(info, mta.Tick)


def test_symbol_select(connected):
    with connected:
        selected = mta.symbol_select("EURUSD")
        assert isinstance(selected, bool)


def test_symbols_get(connected):
    with connected:
        assert (symbols := mta.symbols_get()) is not None
        assert make_kwargs_func(mta.symbols_get)() is not None
        assert isinstance(symbols, tuple)
        assert len(symbols) > 0
        assert isinstance(symbols[0], mta.SymbolInfo)
        symbols = mta.symbols_get(group="NON_EXISTENT_GROUP")
        assert symbols is not None
        assert isinstance(symbols, tuple)
        assert len(symbols) == 0


def test_symbols_total(connected):
    with connected:
        total = mta.symbols_total()
        assert total is not None
        assert isinstance(total, int)


def test_terminal_info(connected):
    with connected:
        info = mta.terminal_info()
        assert isinstance(info, mta.TerminalInfo)


# HELPERS
def test_as_dict_all(connected):
    from pymt5adapter import dictify
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
        deals = mta.history_deals_get()[:3]
        mutated_deals = dictify(deals)
        assert len(deals) == len(mutated_deals)
        assert all(isinstance(d, dict) for d in mutated_deals)
        symbols = mta.symbols_get()
        # b = perf_counter_ns()
        symbols = dictify(symbols)
        # total = perf_counter_ns() - b
        assert no_namedtuples(symbols)
        # print(f"as_dict_all_time = {total / 1000}")


def test_borg_state_class():
    from pymt5adapter.state import _GlobalState
    s1 = _GlobalState()
    s2 = _GlobalState()
    s1.raise_on_errors = True
    s2.raise_on_errors = False
    assert not s1.raise_on_errors


def test_raise_on_errors():
    with mta.connected(raise_on_errors=True):
        with pytest.raises(mta.MT5Error) as e:
            _ = mta.history_orders_total(',', ',')
    # does not raise
    with mta.connected(raise_on_errors=False):
        try:
            _ = mta.history_orders_total(',', ',')
        except mta.MT5Error as e:
            pytest.fail()
    with mta.connected(raise_on_errors=True) as conn:
        conn.raise_on_errors = False
        try:
            _ = mta.history_orders_total(',', ',')
        except mta.MT5Error as e:
            pytest.fail()
    with mta.connected(raise_on_errors=True):
        try:
            _ = mta.history_orders_total(',', ',')
        except mta.MT5Error as e:
            print(e)


# NEW STUFF
def test_trade_class(connected):
    from pymt5adapter.trade import Trade
    with connected:
        trade = Trade(symbol=first_symbol(), magic=1234)
        res = trade.buy(1.0)
        assert isinstance(res, mta.OrderSendResult)


if __name__ == "__main__":
    pass
