# import itertools
#
# import MetaTrader5 as mt5
# import pytest
#
#
# @pytest.fixture(autouse=True)
# def mt5_init_shutdown():
#     try:
#         mt5.initialize()
#         yield
#     finally:
#         mt5.shutdown()
#
#
# def make_kwargs_func(func):
#     return lambda **kwargs: func(**kwargs)
#
#
# def test_initialize():
#     mt5.shutdown()
#     assert isinstance(mt5.initialize(), bool)
#     error_code = mt5.last_error()[0]
#     assert error_code == mt5.RES_S_OK
#     mt5.shutdown()
#     assert isinstance(make_kwargs_func(mt5.initialize)(), bool)
#     error_code = mt5.last_error()[0]
#     assert error_code == mt5.RES_S_OK
#
#
# def test_package_version():
#     import re
#     pattern = re.compile(r'^\d+\.\d+\.\d+$')
#     assert isinstance(version := mt5.__version__, str)
#     assert pattern.match(version)
#
#
# def test_terminal_version():
#     version = mt5.version()
#     assert isinstance(version, tuple)
#     assert len(version) == 3
#     assert isinstance(version[0], int)
#     assert isinstance(version[1], int)
#     assert isinstance(version[2], str)
#
#
# def test_last_error_res_codes():
#     defined_error_codes = [getattr(mt5, name) for name in dir(mt5) if name.startswith('RES_')]
#     for code in defined_error_codes:
#         assert isinstance(code, int)
#
#
# def test_last_error():
#     defined_error_codes = [getattr(mt5, name) for name in dir(mt5) if name.startswith('RES_')]
#     error = mt5.last_error()
#     assert isinstance(error, tuple)
#     assert len(error) == 2
#     code, description = error
#     assert code in defined_error_codes
#     assert isinstance(code, int)
#     assert isinstance(description, str)
#
#
# def test_account_info():
#     info = mt5.account_info()
#     assert isinstance(info, mt5.AccountInfo)
#
#
# def test_terminal_info():
#     info = mt5.terminal_info()
#     assert isinstance(info, mt5.TerminalInfo)
#
#
# def test_symbols_total():
#     total = mt5.symbols_total()
#     assert total is not None
#     assert isinstance(total, int)
#
#
# def test_symbols_get():
#     assert (symbols := mt5.symbols_get()) is not None
#     assert make_kwargs_func(mt5.symbols_get)() is not None
#     assert isinstance(symbols, tuple)
#     assert len(symbols) > 0
#     assert isinstance(symbols[0], mt5.SymbolInfo)
#     symbols = mt5.symbols_get(group="NON_EXISTENT_GROUP")
#     assert symbols is not None
#     assert isinstance(symbols, tuple)
#     assert len(symbols) == 0
#
#
# def test_symbol_info():
#     info = mt5.symbol_info("EURUSD")
#     assert isinstance(info, mt5.SymbolInfo)
#
#
# def test_symbol_info_tick():
#     info = mt5.symbol_info_tick("EURUSD")
#     assert isinstance(info, mt5.Tick)
#
#
# def test_symbol_select():
#     selected = mt5.symbol_select("EURUSD")
#     assert isinstance(selected, bool)
#
#
# def test_orders_total():
#     total = mt5.orders_total()
#     assert isinstance(total, int)
#
#
# def test_orders_get():
#     assert (orders := mt5.orders_get()) is not None
#     assert make_kwargs_func(mt5.orders_get)() is not None
#     assert isinstance(orders, tuple)
#
#
# def test_positions_total():
#     total = mt5.positions_total()
#     assert isinstance(total, int)
#
#
# def test_positions_get():
#     assert (p1 := mt5.positions_get()) is not None
#     assert (p2 := make_kwargs_func(mt5.positions_get)()) is not None
#     assert len(p1) == len(p2)
#     invalid_positions = mt5.positions_get(symbol="FAKE_SYMBOL")
#     assert isinstance(invalid_positions, tuple)
#     assert len(invalid_positions) == 0
#     invalid_positions = mt5.positions_get(ticket=0)
#     assert isinstance(invalid_positions, tuple)
#     assert len(invalid_positions) == 0
#
#
# def test_history_deals_get():
#     deals = mt5.history_deals_get(ticket=0)
#     # assert isinstance(deals, tuple)
#
#
# def test_history_orders_get():
#     orders = mt5.history_orders_get(ticket=0)
#     # assert isinstance(orders, tuple)
#
#
# def test_consistency_for_empty_data_returns():
#     def all_same_return_types(results):
#         g = itertools.groupby(results, key=lambda v: type(v))
#         return next(g, True) and not next(g, False)
#
#     funcs = (mt5.positions_get, mt5.orders_get, mt5.history_orders_get, mt5.history_deals_get,)
#     results = [f(ticket=0) for f in funcs]
#     assert all_same_return_types(results)
#
#
# def test_copy_ticks_range():
#     from datetime import datetime, timedelta
#     time_to = datetime.utcnow()
#     time_from = time_to - timedelta(minutes=3)
#     ticks = mt5.copy_ticks_range("EPM20", time_from, time_to, mt5.COPY_TICKS_ALL)
#     assert mt5.last_error()[0] == mt5.RES_S_OK
#     assert len(ticks) > 0
#
#
# #
# # def test_copy_ticks_range():
# #     from datetime import datetime, timedelta
# #     import time
# #     time_to = datetime.now()
# #     time_from = time_to - timedelta(minutes=5)
# #     print(mt5.initialize())
# #     for i in range(20):
# #         ticks = mt5.copy_ticks_range("USDJPY", time_from, time_to, mt5.COPY_TICKS_ALL)
# #         print(mt5.last_error())
# #         print(ticks)
# #         if len(ticks) > 0:
# #             break
# #         time.sleep(1)
# #         print(mt5.last_error()[0])
# #     assert mt5.last_error()[0] == mt5.RES_S_OK
# #     assert len(ticks) > 0
# #     mt5.shutdown()
#
#
#
#
#
#
# if __name__ == "__main__":
#     pass
