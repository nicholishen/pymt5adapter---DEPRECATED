import itertools

import pytest

from .context import pymt5adapter as mt5
from pymt5adapter.state import global_state as state


# @pytest.fixture(autouse=True)
# def mt5_init_shutdown():
#     try:
#         mt5_init_shutdown.count += 1
#     except AttributeError:
#         mt5_init_shutdown.count = 1
#     c = mt5_init_shutdown.count
#     try:
#         mt5.initialize()
#         print(c, "testing init")
#         yield
#     finally:
#         mt5.shutdown()
#         print(c, "testing shutdown")

@pytest.fixture
def connected():
    context = mt5.connected(  # debug_logging=True,
        ensure_trade_enabled=True,
        enable_real_trading=False
    )
    return context


def make_kwargs_func(func):
    return lambda **kwargs: func(**kwargs)



def test_easy_example():
    mt5_connected = mt5.connected(
        # path=r'C:\Users\user\Desktop\MT5\terminal64.exe',
        # portable=True,
        # server='MetaQuotes-Demo',
        # login=1234567,
        # password='password1',
        # timeout=5000,
        ensure_trade_enabled=True,
        enable_real_trading=False,
        raise_on_errors=True,
        debug_logging=True,
        logger=print,
    )
    with mt5_connected:
        try:
            num_orders = mt5.history_orders_total("invalid", "arguments")
        except mt5.MT5Error as e:
            print("We modified the API to throw exceptions for all functions.")
            print(f"Error = {e}")

        visible_symbols = mt5.symbols_get(function=lambda s: s.visible)
        def out_deal(deal: mt5.TradeDeal):
            return deal.entry == mt5.DEAL_ENTRY_OUT
        out_deals = mt5.history_deals_get(function=out_deal)

def test_trade_class(connected):
    from pymt5adapter.advanced import Trade
    with connected:
        symbol = mt5.symbols_get(function=lambda s: s.visible)[0].name
        orig_req = Trade(symbol, 12345).market_buy(1).request
        print(orig_req)


def test_borg_state_class():
    from pymt5adapter.state import _GlobalState
    s1 = _GlobalState()
    s2 = _GlobalState()
    s1.raise_on_errors = True
    s2.raise_on_errors = False
    assert not s1.raise_on_errors


def test_mt5_connection_context():
    from pymt5adapter.state import _GlobalState
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
    from datetime import datetime, timedelta
    import time
    time_to = datetime.now()
    time_from = time_to - timedelta(minutes=3)
    with connected:
        for i in range(20):
            ticks = mt5.copy_ticks_range("USDJPY", time_from, time_to, mt5.COPY_TICKS_ALL)
            if len(ticks) > 0:
                break
            time.sleep(1)
        assert mt5.last_error()[0] == mt5.RES_S_OK
        assert len(ticks) > 0


if __name__ == "__main__":
    pass
