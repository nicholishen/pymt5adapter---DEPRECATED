"""
MT5 adaptor by nicholishen
"""
import contextlib
import functools
from typing import Tuple, Callable, Union
from collections import namedtuple
from datetime import datetime

import MetaTrader5 as mt5
import numpy
from packaging.version import parse as parse_version

__version__ = mt5.__version__
# ONLY use package versions more recent than...
assert parse_version(__version__) >= parse_version('5.0.31')
__author__ = mt5.__author__

# timeframes
TIMEFRAME_M1 = 1
TIMEFRAME_M2 = 2
TIMEFRAME_M3 = 3
TIMEFRAME_M4 = 4
TIMEFRAME_M5 = 5
TIMEFRAME_M6 = 6
TIMEFRAME_M10 = 10
TIMEFRAME_M12 = 12
TIMEFRAME_M15 = 15
TIMEFRAME_M20 = 20
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 1 | 0x4000
TIMEFRAME_H2 = 2 | 0x4000
TIMEFRAME_H4 = 4 | 0x4000
TIMEFRAME_H3 = 3 | 0x4000
TIMEFRAME_H6 = 6 | 0x4000
TIMEFRAME_H8 = 8 | 0x4000
TIMEFRAME_H12 = 12 | 0x4000
TIMEFRAME_D1 = 24 | 0x4000
TIMEFRAME_W1 = 1 | 0x8000
TIMEFRAME_MN1 = 1 | 0xC000
# tick copy flags
COPY_TICKS_ALL = -1
COPY_TICKS_INFO = 1
COPY_TICKS_TRADE = 2
# tick flags
TICK_FLAG_BID = 0x02
TICK_FLAG_ASK = 0x04
TICK_FLAG_LAST = 0x08
TICK_FLAG_VOLUME = 0x10
TICK_FLAG_BUY = 0x20
TICK_FLAG_SELL = 0x40
# position type, ENUM_POSITION_TYPE
POSITION_TYPE_BUY = 0  # Buy
POSITION_TYPE_SELL = 1  # Sell
# position reason, ENUM_POSITION_REASON
POSITION_REASON_CLIENT = 0  # The position was opened as a result of activation of an order placed from a desktop terminal
POSITION_REASON_MOBILE = 1  # The position was opened as a result of activation of an order placed from a mobile application
POSITION_REASON_WEB = 2  # The position was opened as a result of activation of an order placed from the web platform
POSITION_REASON_EXPERT = 3  # The position was opened as a result of activation of an order placed from an MQL5 program, i.e. an Expert Advisor or a script
# order types, ENUM_ORDER_TYPE
ORDER_TYPE_BUY = 0  # Market Buy order
ORDER_TYPE_SELL = 1  # Market Sell order
ORDER_TYPE_BUY_LIMIT = 2  # Buy Limit pending order
ORDER_TYPE_SELL_LIMIT = 3  # Sell Limit pending order
ORDER_TYPE_BUY_STOP = 4  # Buy Stop pending order
ORDER_TYPE_SELL_STOP = 5  # Sell Stop pending order
ORDER_TYPE_BUY_STOP_LIMIT = 6  # Upon reaching the order price, a pending Buy Limit order is placed at the StopLimit price
ORDER_TYPE_SELL_STOP_LIMIT = 7  # Upon reaching the order price, a pending Sell Limit order is placed at the StopLimit price
ORDER_TYPE_CLOSE_BY = 8  # Order to close a position by an opposite one
# order state, ENUM_ORDER_STATE
ORDER_STATE_STARTED = 0  # Order checked, but not yet accepted by broker
ORDER_STATE_PLACED = 1  # Order accepted
ORDER_STATE_CANCELED = 2  # Order canceled by client
ORDER_STATE_PARTIAL = 3  # Order partially executed
ORDER_STATE_FILLED = 4  # Order fully executed
ORDER_STATE_REJECTED = 5  # Order rejected
ORDER_STATE_EXPIRED = 6  # Order expired
ORDER_STATE_REQUEST_ADD = 7  # Order is being registered (placing to the trading system)
ORDER_STATE_REQUEST_MODIFY = 8  # Order is being modified (changing its parameters)
ORDER_STATE_REQUEST_CANCEL = 9  # Order is being deleted (deleting from the trading system)
# ENUM_ORDER_TYPE_FILLING
ORDER_FILLING_FOK = 0
ORDER_FILLING_IOC = 1
ORDER_FILLING_RETURN = 2
# ENUM_ORDER_TYPE_TIME
ORDER_TIME_GTC = 0  # Good till cancel order
ORDER_TIME_DAY = 1  # Good till current trade day order
ORDER_TIME_SPECIFIED = 2  # Good till expired order
ORDER_TIME_SPECIFIED_DAY = 3  # The order will be effective till 23:59:59 of the specified day. If this time is outside a trading session, the order expires in the nearest trading time.
# ENUM_ORDER_REASON
ORDER_REASON_CLIENT = 0  # The order was placed from a desktop terminal
ORDER_REASON_MOBILE = 1  # The order was placed from a mobile application
ORDER_REASON_WEB = 2  # The order was placed from a web platform
ORDER_REASON_EXPERT = 3  # The order was placed from an MQL5-program, i.e. by an Expert Advisor or a script
ORDER_REASON_SL = 4  # The order was placed as a result of Stop Loss activation
ORDER_REASON_TP = 5  # The order was placed as a result of Take Profit activation
ORDER_REASON_SO = 6  # The order was placed as a result of the Stop Out event
# deal types, ENUM_DEAL_TYPE
DEAL_TYPE_BUY = 0  # Buy
DEAL_TYPE_SELL = 1  # Sell
DEAL_TYPE_BALANCE = 2  # Balance
DEAL_TYPE_CREDIT = 3  # Credit
DEAL_TYPE_CHARGE = 4  # Additional charge
DEAL_TYPE_CORRECTION = 5  # Correction
DEAL_TYPE_BONUS = 6  # Bonus
DEAL_TYPE_COMMISSION = 7  # Additional commission
DEAL_TYPE_COMMISSION_DAILY = 8  # Daily commission
DEAL_TYPE_COMMISSION_MONTHLY = 9  # Monthly commission
DEAL_TYPE_COMMISSION_AGENT_DAILY = 10  # Daily agent commission
DEAL_TYPE_COMMISSION_AGENT_MONTHLY = 11  # Monthly agent commission
DEAL_TYPE_INTEREST = 12  # Interest rate
DEAL_TYPE_BUY_CANCELED = 13  # Canceled buy deal.
DEAL_TYPE_SELL_CANCELED = 14  # Canceled sell deal.
DEAL_DIVIDEND = 15  # Dividend operations
DEAL_DIVIDEND_FRANKED = 16  # Franked (non-taxable) dividend operations
DEAL_TAX = 17  # Tax charges
# ENUM_DEAL_ENTRY
DEAL_ENTRY_IN = 0  # Entry in
DEAL_ENTRY_OUT = 1  # Entry out
DEAL_ENTRY_INOUT = 2  # Reverse
DEAL_ENTRY_OUT_BY = 3  # Close a position by an opposite one
# ENUM_DEAL_REASON
DEAL_REASON_CLIENT = 0  # The deal was executed as a result of activation of an order placed from a desktop terminal
DEAL_REASON_MOBILE = 1  # The deal was executed as a result of activation of an order placed from a mobile application
DEAL_REASON_WEB = 2  # The deal was executed as a result of activation of an order placed from the web platform
DEAL_REASON_EXPERT = 3  # The deal was executed as a result of activation of an order placed from an MQL5 program, i.e. an Expert Advisor or a script
DEAL_REASON_SL = 4  # The deal was executed as a result of Stop Loss activation
DEAL_REASON_TP = 5  # The deal was executed as a result of Take Profit activation
DEAL_REASON_SO = 6  # The deal was executed as a result of the Stop Out event
DEAL_REASON_ROLLOVER = 7  # The deal was executed due to a rollover
DEAL_REASON_VMARGIN = 8  # The deal was executed after charging the variation margin
DEAL_REASON_SPLIT = 9  # The deal was executed after the split (price reduction) of an instrument, which had an open position during split announcement
# ENUM_TRADE_REQUEST_ACTIONS, Trade Operation Types
TRADE_ACTION_DEAL = 1  # Place a trade order for an immediate execution with the specified parameters (market order)
TRADE_ACTION_PENDING = 5  # Place a trade order for the execution under specified conditions (pending order)
TRADE_ACTION_SLTP = 6  # Modify Stop Loss and Take Profit values of an opened position
TRADE_ACTION_MODIFY = 7  # Modify the parameters of the order placed previously
TRADE_ACTION_REMOVE = 8  # Delete the pending order placed previously
TRADE_ACTION_CLOSE_BY = 10  # Close a position by an opposite one
# ENUM_SYMBOL_CHART_MODE
SYMBOL_CHART_MODE_BID = 0
SYMBOL_CHART_MODE_LAST = 1
# ENUM_SYMBOL_CALC_MODE
SYMBOL_CALC_MODE_FOREX = 0
SYMBOL_CALC_MODE_FUTURES = 1
SYMBOL_CALC_MODE_CFD = 2
SYMBOL_CALC_MODE_CFDINDEX = 3
SYMBOL_CALC_MODE_CFDLEVERAGE = 4
SYMBOL_CALC_MODE_FOREX_NO_LEVERAGE = 5
SYMBOL_CALC_MODE_EXCH_STOCKS = 32
SYMBOL_CALC_MODE_EXCH_FUTURES = 33
SYMBOL_CALC_MODE_EXCH_OPTIONS = 34
SYMBOL_CALC_MODE_EXCH_OPTIONS_MARGIN = 36
SYMBOL_CALC_MODE_EXCH_BONDS = 37
SYMBOL_CALC_MODE_EXCH_STOCKS_MOEX = 38
SYMBOL_CALC_MODE_EXCH_BONDS_MOEX = 39
SYMBOL_CALC_MODE_SERV_COLLATERAL = 64
# ENUM_SYMBOL_TRADE_MODE
SYMBOL_TRADE_MODE_DISABLED = 0
SYMBOL_TRADE_MODE_LONGONLY = 1
SYMBOL_TRADE_MODE_SHORTONLY = 2
SYMBOL_TRADE_MODE_CLOSEONLY = 3
SYMBOL_TRADE_MODE_FULL = 4
# ENUM_SYMBOL_TRADE_EXECUTION
SYMBOL_TRADE_EXECUTION_REQUEST = 0
SYMBOL_TRADE_EXECUTION_INSTANT = 1
SYMBOL_TRADE_EXECUTION_MARKET = 2
SYMBOL_TRADE_EXECUTION_EXCHANGE = 3
# ENUM_SYMBOL_SWAP_MODE
SYMBOL_SWAP_MODE_DISABLED = 0
SYMBOL_SWAP_MODE_POINTS = 1
SYMBOL_SWAP_MODE_CURRENCY_SYMBOL = 2
SYMBOL_SWAP_MODE_CURRENCY_MARGIN = 3
SYMBOL_SWAP_MODE_CURRENCY_DEPOSIT = 4
SYMBOL_SWAP_MODE_INTEREST_CURRENT = 5
SYMBOL_SWAP_MODE_INTEREST_OPEN = 6
SYMBOL_SWAP_MODE_REOPEN_CURRENT = 7
SYMBOL_SWAP_MODE_REOPEN_BID = 8
# ENUM_DAY_OF_WEEK
DAY_OF_WEEK_SUNDAY = 0
DAY_OF_WEEK_MONDAY = 1
DAY_OF_WEEK_TUESDAY = 2
DAY_OF_WEEK_WEDNESDAY = 3
DAY_OF_WEEK_THURSDAY = 4
DAY_OF_WEEK_FRIDAY = 5
DAY_OF_WEEK_SATURDAY = 6
# ENUM_SYMBOL_ORDER_GTC_MODE
SYMBOL_ORDERS_GTC = 0
SYMBOL_ORDERS_DAILY = 1
SYMBOL_ORDERS_DAILY_NO_STOPS = 2
# ENUM_SYMBOL_OPTION_RIGHT
SYMBOL_OPTION_RIGHT_CALL = 0
SYMBOL_OPTION_RIGHT_PUT = 1
# ENUM_SYMBOL_OPTION_MODE
SYMBOL_OPTION_MODE_EUROPEAN = 0
SYMBOL_OPTION_MODE_AMERICAN = 1
# ENUM_ACCOUNT_TRADE_MODE
ACCOUNT_TRADE_MODE_DEMO = 0
ACCOUNT_TRADE_MODE_CONTEST = 1
ACCOUNT_TRADE_MODE_REAL = 2
# ENUM_ACCOUNT_STOPOUT_MODE
ACCOUNT_STOPOUT_MODE_PERCENT = 0
ACCOUNT_STOPOUT_MODE_MONEY = 1
# ENUM_ACCOUNT_MARGIN_MODE
ACCOUNT_MARGIN_MODE_RETAIL_NETTING = 0
ACCOUNT_MARGIN_MODE_EXCHANGE = 1
ACCOUNT_MARGIN_MODE_RETAIL_HEDGING = 2
# order send/check return codes
TRADE_RETCODE_REQUOTE = 10004
TRADE_RETCODE_REJECT = 10006
TRADE_RETCODE_CANCEL = 10007
TRADE_RETCODE_PLACED = 10008
TRADE_RETCODE_DONE = 10009
TRADE_RETCODE_DONE_PARTIAL = 10010
TRADE_RETCODE_ERROR = 10011
TRADE_RETCODE_TIMEOUT = 10012
TRADE_RETCODE_INVALID = 10013
TRADE_RETCODE_INVALID_VOLUME = 10014
TRADE_RETCODE_INVALID_PRICE = 10015
TRADE_RETCODE_INVALID_STOPS = 10016
TRADE_RETCODE_TRADE_DISABLED = 10017
TRADE_RETCODE_MARKET_CLOSED = 10018
TRADE_RETCODE_NO_MONEY = 10019
TRADE_RETCODE_PRICE_CHANGED = 10020
TRADE_RETCODE_PRICE_OFF = 10021
TRADE_RETCODE_INVALID_EXPIRATION = 10022
TRADE_RETCODE_ORDER_CHANGED = 10023
TRADE_RETCODE_TOO_MANY_REQUESTS = 10024
TRADE_RETCODE_NO_CHANGES = 10025
TRADE_RETCODE_SERVER_DISABLES_AT = 10026
TRADE_RETCODE_CLIENT_DISABLES_AT = 10027
TRADE_RETCODE_LOCKED = 10028
TRADE_RETCODE_FROZEN = 10029
TRADE_RETCODE_INVALID_FILL = 10030
TRADE_RETCODE_CONNECTION = 10031
TRADE_RETCODE_ONLY_REAL = 10032
TRADE_RETCODE_LIMIT_ORDERS = 10033
TRADE_RETCODE_LIMIT_VOLUME = 10034
TRADE_RETCODE_INVALID_ORDER = 10035
TRADE_RETCODE_POSITION_CLOSED = 10036
TRADE_RETCODE_INVALID_CLOSE_VOLUME = 10038
TRADE_RETCODE_CLOSE_ORDER_EXIST = 10039
TRADE_RETCODE_LIMIT_POSITIONS = 10040
TRADE_RETCODE_REJECT_CANCEL = 10041
TRADE_RETCODE_LONG_ONLY = 10042
TRADE_RETCODE_SHORT_ONLY = 10043
TRADE_RETCODE_CLOSE_ONLY = 10044
TRADE_RETCODE_FIFO_CLOSE = 10045
# functio error codes, last_error()

RES_S_OK = 1  # generic success
RES_E_FAIL = -1  # generic fail
RES_E_INVALID_PARAMS = -2  # invalid arguments/parameters
RES_E_NO_MEMORY = -3  # no memory condition
RES_E_NOT_FOUND = -4  # no history
RES_E_INVALID_VERSION = -5  # invalid version
RES_E_AUTH_FAILED = -6  # authorization failed
RES_E_UNSUPPORTED = -7  # unsupported method
RES_E_AUTO_TRADING_DISABLED = -8  # auto-trading disabled
RES_E_INTERNAL_FAIL = -10000  # internal IPC general error
RES_E_INTERNAL_FAIL_SEND = -10001  # internal IPC send failed
RES_E_INTERNAL_FAIL_RECV = -10002  # internal IPC recv failed
RES_E_INTERNAL_FAIL_INIT = -10003  # internal IPC initialization fail
RES_E_INTERNAL_FAIL_CONN = -10004  # internal IPC no ipc
RES_E_INTERNAL_FAIL_TIMEOUT = -10005  # internal timeout
# CUSTOM ERROR CODES ----------------------------------------------------------------------
RES_X_AUTO_TRADE_DISABLED = -20000  # terminal auto-trading is disabled

# MT5 namedtuple objects for typing
Rate = namedtuple("Rate", "time open high low close tick_volume spread real_volume")
Tick = mt5.Tick
AccountInfo = mt5.AccountInfo
SymbolInfo = mt5.SymbolInfo
TerminalInfo = mt5.TerminalInfo
OrderCheckResult = mt5.OrderCheckResult
OrderSendResult = mt5.OrderSendResult
TradeOrder = mt5.TradeOrder
TradeDeal = mt5.TradeDeal
TradeRequest = mt5.TradeRequest
TradePosition = mt5.TradePosition

__GLOBAL_FORCE_NAMEDTUPLE = False
__GLOBAL_RAISE_FLAG = False
__GLOBAL_DEBUG_LOGGING_FLAG = False
__GLOBAL_LOG = print

_DEFAULT_FROM_DATETIME = datetime(2010, 1, 1)
_DEFAULT_MAX_BARS = 10_000


class MT5Error(Exception):
    pass


def _is_global_force_namedtuple():
    return __GLOBAL_FORCE_NAMEDTUPLE


def _set_global_force_namedtuple(flag: bool = False):
    global __GLOBAL_FORCE_NAMEDTUPLE
    __GLOBAL_FORCE_NAMEDTUPLE = flag


def _is_global_debugging():
    return __GLOBAL_DEBUG_LOGGING_FLAG


def _set_global_debugging(flag: bool = False):
    global __GLOBAL_DEBUG_LOGGING_FLAG
    __GLOBAL_DEBUG_LOGGING_FLAG = flag


def _is_global_raise():
    return __GLOBAL_RAISE_FLAG


def _set_global_raise(flag: bool = False):
    global __GLOBAL_RAISE_FLAG
    __GLOBAL_RAISE_FLAG = flag


def _set_global_logger(logger: Callable = None):
    global __GLOBAL_LOG
    __GLOBAL_LOG = logger or print


def _set_globals_defaults():
    _set_global_raise()
    _set_global_debugging()
    _set_global_logger()
    _set_global_force_namedtuple()


def _clean_args(kwargs: dict) -> dict:
    kwargs.pop('kwargs', None)
    return {k: v for k, v in kwargs.items() if v is not None}


def _args_to_str(args: tuple, kwargs: dict):
    ar = ', '.join(map(str, args))
    kw = ', '.join(f"{k}={v}" for k, v in kwargs.items())
    return ar + (', ' if ar and kw else '') + kw


def _is_rates_array(array):
    try:
        rate = array[0]
        return type(rate) is tuple and len(rate) == 8
    except:
        return False


def _get_ticket_type_stuff(func, symbol, group, ticket, function):
    d = locals().copy()
    kw = {i: d[i] for i in ['group', 'ticket'] if d[i]}
    items = func(symbol, **kw)
    if function:
        items = tuple(filter(function, items))
    return items if items is not None else tuple()


def _get_history_type_stuff(func, args):
    args = _clean_args(args)
    function = args.pop('function', None)
    datetime_from = args.get('datetime_from', None)
    datetime_to = args.get('datetime_to', None)
    if not args:
        datetime_from = datetime(2000, 1, 1)
        datetime_to = datetime.utcnow()
    if datetime_from is not None and datetime_to is not None:
        deals = func(datetime_from, datetime_to, **args)
    else:
        deals = func(**args)
    if function:
        deals = tuple(filter(function, deals))
    return deals if deals is not None else tuple()


def _do_trade_action(func, args):
    request = args.pop('request', {})
    cleaned = _clean_args(args)
    order_request = {**request, **cleaned}
    return func(order_request)


def remap(item):
    if hasattr(item, '_asdict'):
        return item._asdict()
    if type(item) is tuple:
        return tuple(remap(x) for x in item)
    return item


def _context_manager_modified(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        if _is_global_force_namedtuple():
            if _is_rates_array(result):
                result = [Rate(*r) for r in result]
        if _is_global_debugging():  # and not result:
            call_sig = f"{f.__name__}({_args_to_str(args, kwargs)})"
            log = __GLOBAL_LOG
            log(f"[{call_sig}][{last_error()}][{str(result)[:80]}]")
        if _is_global_raise():
            error_code, description = last_error()
            if error_code != RES_S_OK:
                raise MT5Error(error_code, description)
        return result

    return wrapper


@contextlib.contextmanager
def connected(*,
              path: str = None,
              portable: bool = None,
              server: str = None,
              login: int = None,
              password: str = None,
              timeout: int = None,
              ensure_trade_enabled: bool = False,
              logger: Callable[[str], None] = None,
              raise_on_error=False,
              debug_logging=False,
              force_named_tuple=False,
              **kwargs
              ) -> None:
    """Context manager for managing the connection with a MT5 terminal using the python ``with`` statement.

    :param path:  Path to terminal
    :param portable: Load terminal in portable mode
    :param server:  Server name
    :param login:  Account login number
    :param password:  Account password
    :param timeout: Connection init timeout
    :param ensure_trade_enabled: Ensure that auto-trading is enabled
    :param logger: Logging function. Will pass connection status messages to this function
    :param raise_on_error: bool - Raise Mt5Error Exception when the last_error() result of a function is not RES_S_OK
    :param debug_logging: Logs each function call that results in an error or empty data return
    :param force_named_tuple:
    :param kwargs:
    :return: None
    """
    _set_global_debugging(debug_logging)
    _set_global_raise(raise_on_error)
    _set_global_logger(logger)
    _set_global_force_namedtuple(force_named_tuple)
    log = __GLOBAL_LOG
    try:
        args = _clean_args(locals().copy())
        mt5_keys = "path portable server login password timeout".split()
        mt5_kwargs = {k: v for k, v in args.items() if k in mt5_keys}
        if not initialize(**mt5_kwargs):
            raise MT5Error(*last_error())
        elif debug_logging:
            log("MT5 connection has been initialized.")
        if ensure_trade_enabled and not terminal_info().trade_allowed:
            if debug_logging:
                log("Failed to initialize because auto-trade is disabled in terminal.")
            raise MT5Error(RES_X_AUTO_TRADE_DISABLED, "Terminal Auto-Trading is disabled.")
        yield
    finally:
        shutdown()
        _set_globals_defaults()
        if debug_logging:
            log("MT5 connection has been shutdown.")


@_context_manager_modified
def initialize(path: str = None,
               *,
               login: str = None,
               password: str = None,
               server: str = None,
               portable: bool = False,
               timeout: int = None,
               **kwargs
               ) -> bool:
    """Establish a connection with the MetaTrader 5 terminal. Call without parameters. The terminal for connection is found automatically.

    :param portable:
    :param path:  Path to the metatrader.exe or metatrader64.exe file. Optional unnamed parameter. It is indicated first without a parameter name. If the path is not specified, the module attempts to find the executable file on its own.
    :param login: Connection timeout in milliseconds. Optional named parameter. If not specified, the value of 60 000 (60 seconds) is applied. If the connection is not established within the specified time, the call is forcibly terminated and the exception is generated.
    :param password: Trading account password. Optional named parameter. If the password is not set, the password saved in the terminal database is applied automatically.
    :param server: Trade server name. Optional named parameter. If no server is set, the last used server is applied automatically.
    :return: Returns True in case of successful connection to the MetaTrader 5 terminal, otherwise - False.
    """
    cleaned = _clean_args(locals().copy())
    result = mt5.initialize(**cleaned)
    return result


@_context_manager_modified
def login(login: int, *,
          password: str = None,
          server: str = None,
          timeout: int = None,
          **kwargs,
          ) -> bool:
    """Connect to a trading account using specified parameters.

    :param login: Trading account number. Required unnamed parameter.
    :param password: Trading account password.
    :param server: Trade server name
    :param timeout: Connection timeout in milliseconds.
    :param kwargs:
    :return: True if success.
    """
    args = _clean_args(locals().copy())
    login = args.pop('login')
    return mt5.login(login, **args)


@_context_manager_modified
def shutdown() -> None:
    """Close the previously established connection to the MetaTrader 5 terminal.

    :return: None
    """
    return mt5.shutdown()


@_context_manager_modified
def version() -> Tuple[int, int, str]:
    """Return the MetaTrader 5 terminal version.

    :return: Returns the MetaTrader 5 terminal version, build and release date. Return None in case of an error. The info on the error can be obtained using last_error().
    """
    return mt5.version()


def last_error() -> Tuple[int, str]:
    """last_error() allows obtaining an error code in case of a failed execution of a MetaTrader 5 library function.
    It is similar to GetLastError(). However, it applies its own error codes.

    :return: Return the last error code and description as a tuple.
    """
    return mt5.last_error()


@_context_manager_modified
def account_info() -> AccountInfo:
    """Get info on the current trading account. The function returns all data that can be obtained using AccountInfoInteger, AccountInfoDouble and AccountInfoString in one call.

    :return: Return info in the form of a named tuple structure (namedtuple). Return None in case of an error. The info on the error can be obtained using last_error().
    """
    return mt5.account_info()


@_context_manager_modified
def terminal_info() -> TerminalInfo:
    """Get the connected MetaTrader 5 client terminal status and settings. The function returns all data that can be
    obtained using TerminalInfoInteger, TerminalInfoDouble and TerminalInfoDouble in one call.

    :return: Return info in the form of a named tuple structure (namedtuple). Return None in case of an error. The info on the error can be obtained using last_error().
    """
    return mt5.terminal_info()


@_context_manager_modified
def symbols_total() -> int:
    """Get the number of all financial instruments in the MetaTrader 5 terminal. The function is similar to SymbolsTotal(). However, it returns the number of all symbols including custom ones and the ones disabled in MarketWatch.

    :return: <int>
    """
    return mt5.symbols_total()


@_context_manager_modified
def symbols_get(group=None,
                function: Callable[[SymbolInfo], bool] = None,
                **kwargs
                ) -> Tuple[SymbolInfo]:
    """Get all financial instruments from the MetaTrader 5 terminal.
        The group parameter allows sorting out symbols by name. '*' can be used at the beginning and the end of a string.
        The group parameter can be used as a named or an unnamed one. Both options work the same way. The named option (group="GROUP") makes the code easier to read.
        The group parameter may contain several comma separated conditions. A condition can be set as a mask using '*'. The logical negation symbol '!' can be used for an exclusion. All conditions are applied sequentially, which means conditions of including to a group should be specified first followed by an exclusion condition. For example, group="*, !EUR" means that all symbols should be selected first and the ones containing "EUR" in their names should be excluded afterwards.
        Unlike symbol_info(), the symbols_get() function returns data on all requested symbols within a single call.

    :param group: The filter for arranging a group of necessary symbols. Optional parameter. If the group is specified, the function returns only symbols meeting a specified criteria.
    :param kwargs:
    :return: A tuple of SymbolInfo objects
    """
    symbols = mt5.symbols_get(group=group) if group else mt5.symbols_get()
    if function:
        symbols = tuple(filter(function, symbols))
    return symbols


@_context_manager_modified
def symbol_info(symbol: str) -> SymbolInfo:
    """Get data on the specified financial instrument.

    :param symbol:
    :return: Return info in the form of a named tuple structure (namedtuple). Return None in case of an error. The info on the error can be obtained using last_error().
    """
    return mt5.symbol_info(symbol)


@_context_manager_modified
def symbol_info_tick(symbol: str) -> Tick:
    """Get the last tick for the specified financial instrument.

    :param symbol:
    :return:
    """
    return mt5.symbol_info_tick(symbol)


@_context_manager_modified
def symbol_select(symbol: str, enable: bool = True) -> bool:
    """Select a symbol in the MarketWatch window or remove a symbol from the window.

    :param symbol:
    :param enable:
    :return: True if successful, otherwise – False.
    """
    return mt5.symbol_select(symbol, enable)


@_context_manager_modified
def copy_rates_from(symbol: str,
                    timeframe: int,
                    datetime_from: Union[datetime, int],
                    count: int
                    ) -> Union[numpy.ndarray, None]:
    """Get bars from the MetaTrader 5 terminal starting from the specified date.

    :param symbol: Financial instrument name, for example, "EURUSD".
    :param timeframe: Timeframe the bars are requested for. Set by a value from the TIMEFRAME enumeration.
    :param datetime_from: Date of opening of the first bar from the requested sample. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01.
    :param count: Number of bars to receive.
    :return: Returns bars as the numpy array with the named time, open, high, low, close, tick_volume, spread and real_volume columns. Return None in case of an error. The info on the error can be obtained using last_error().
    """
    try:
        return mt5.copy_rates_from(symbol, timeframe, datetime_from, count)
    except SystemError:
        return None


@_context_manager_modified
def copy_rates_from_pos(symbol: str,
                        timeframe: int,
                        start_pos: int,
                        count: int
                        ) -> Union[numpy.ndarray, None]:
    """Get bars from the MetaTrader 5 terminal starting from the specified index.

    :param symbol: Financial instrument name, for example, "EURUSD".
    :param timeframe: Timeframe the bars are requested for. Set by a value from the TIMEFRAME enumeration.
    :param start_pos: Initial index of the bar the data are requested from. The numbering of bars goes from present to past. Thus, the zero bar means the current one.
    :param count: Number of bars to receive.
    :return: Returns bars as the numpy array with the named time, open, high, low, close, tick_volume, spread and real_volume columns. Return None in case of an error. The info on the error can be obtained using last_error().
    """
    try:
        return mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
    except SystemError:
        return None


@_context_manager_modified
def copy_rates_range(symbol: str,
                     timeframe: int,
                     datetime_from: Union[datetime, int],
                     datetime_to: Union[datetime, int]
                     ) -> Union[numpy.ndarray, None]:
    """Get bars from the MetaTrader 5 terminal starting from the specified index.

        :param symbol: Financial instrument name, for example, "EURUSD".
        :param timeframe: Timeframe the bars are requested for. Set by a value from the TIMEFRAME enumeration.
        :param datetime_from: Date of opening of the first bar from the requested sample. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01.
        :param datetime_to: Date, up to which the bars are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars with the open time <= date_to are returned.
        :return: Returns bars as the numpy array with the named time, open, high, low, close, tick_volume, spread and real_volume columns. Return None in case of an error. The info on the error can be obtained using last_error().
        """
    try:
        return mt5.copy_rates_range(symbol, timeframe, datetime_from, datetime_to)
    except SystemError:
        return None


@_context_manager_modified
def copy_rates(symbol: str,
               timeframe: int,
               *,
               datetime_from: Union[datetime, int] = None,
               datetime_to: Union[datetime, int] = None,
               start_pos: int = None,
               count: int = None,
               ) -> Union[numpy.ndarray, None]:
    """Generic function to use keywords to automatically call the correct copy rates function depending on the keyword args passed in.

    :param symbol: Financial instrument name, for example, "EURUSD".
    :param timeframe: Timeframe the bars are requested for. Set by a value from the TIMEFRAME enumeration.
    :param datetime_from: Date of opening of the first bar from the requested sample. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01.
    :param datetime_to: Date, up to which the bars are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Bars with the open time <= date_to are returned.
    :param start_pos: Initial index of the bar the data are requested from. The numbering of bars goes from present to past. Thus, the zero bar means the current one.
    :param count: Number of bars to receive.
    :return: Returns bars as the numpy array with the named time, open, high, low, close, tick_volume, spread and real_volume columns. Return None in case of an error. The info on the error can be obtained using last_error().
    """
    try:
        if datetime_from is not None:
            if count is not None:
                return mt5.copy_rates_from(symbol, timeframe, datetime_from, count)
            if datetime_to is not None:
                return mt5.copy_rates_range(symbol, timeframe, datetime_from, datetime_to)
        if all(x is None for x in [datetime_from, datetime_to, start_pos, count]):
            return mt5.copy_rates_from_pos(symbol, timeframe, _DEFAULT_MAX_BARS, 0)
        return mt5.copy_rates_from_pos(symbol, timeframe, start_pos, count)
    except SystemError:
        return None


@_context_manager_modified
def copy_ticks_from(symbol: str,
                    datetime_from: Union[datetime, int],
                    count: int,
                    flags: int,
                    ) -> Union[numpy.ndarray, None]:
    """Get ticks from the MetaTrader 5 terminal starting from the specified date.

    :param symbol: Financial instrument name, for example, "EURUSD". Required unnamed parameter.
    :param datetime_from: Date the ticks are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01.
    :param count: Number of ticks to receive.
    :param flags: A flag to define the type of the requested ticks. COPY_TICKS_INFO – ticks with Bid and/or Ask changes, COPY_TICKS_TRADE – ticks with changes in Last and Volume, COPY_TICKS_ALL – all ticks. Flag values are described in the COPY_TICKS enumeration.
    :return: Returns ticks as the numpy array with the named time, bid, ask, last and flags columns. The 'flags' value can be a combination of flags from the TICK_FLAG enumeration. Return None in case of an error. The info on the error can be obtained using last_error().

    Note:
        See the CopyTicks function for more information.

        When creating the 'datetime' object, Python uses the local time zone, while MetaTrader 5 stores tick and bar open time in UTC time zone (without the shift). Therefore, 'datetime' should be created in UTC time for executing functions that use time. Data received from the MetaTrader 5 terminal has UTC time.
    """
    try:
        return mt5.copy_ticks_from(symbol, datetime_from, count, flags)
    except SystemError:
        return None


@_context_manager_modified
def copy_ticks_range(symbol: str,
                     datetime_from: Union[datetime, int],
                     datetime_to: Union[datetime, int],
                     flags: int,
                     ) -> Union[numpy.ndarray, None]:
    """Get ticks from the MetaTrader 5 terminal starting from the specified date.

        :param symbol: Financial instrument name, for example, "EURUSD". Required unnamed parameter.
        :param datetime_from: Date the ticks are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01.
        :param datetime_to: Date, up to which the ticks are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01.
        :param flags: A flag to define the type of the requested ticks. COPY_TICKS_INFO – ticks with Bid and/or Ask changes, COPY_TICKS_TRADE – ticks with changes in Last and Volume, COPY_TICKS_ALL – all ticks. Flag values are described in the COPY_TICKS enumeration.
        :return: Returns ticks as the numpy array with the named time, bid, ask, last and flags columns. The 'flags' value can be a combination of flags from the TICK_FLAG enumeration. Return None in case of an error. The info on the error can be obtained using last_error().

        Note:
            See the CopyTicks function for more information.

            When creating the 'datetime' object, Python uses the local time zone, while MetaTrader 5 stores tick and bar open time in UTC time zone (without the shift). Therefore, 'datetime' should be created in UTC time for executing functions that use time. Data received from the MetaTrader 5 terminal has UTC time.
        """
    try:
        return mt5.copy_ticks_range(symbol, datetime_from, datetime_to, flags)
    except SystemError:
        return None


@_context_manager_modified
def orders_total() -> int:
    """Get the number of active orders.

    :return: Integer value.
    """
    return mt5.orders_total()


@_context_manager_modified
def orders_get(symbol: str = None,
               *,
               group: str = None,
               ticket: int = None,
               function: Callable[[TradeOrder], bool] = None,
               **kwargs
               ) -> Tuple[TradeOrder]:
    """Get active orders with the ability to filter by symbol or ticket.

    :param symbol: Symbol name. Optional named parameter. If a symbol is specified, the ticket parameter is ignored.
    :param group: The filter for arranging a group of necessary symbols.
    :param ticket: Order ticket (ORDER_TICKET). Optional named parameter.
    :return: tuple of TradeOrder objects

    Note:
        The function allows receiving all active orders within one call similar to the OrdersTotal and OrderSelect tandem.
        The group parameter allows sorting out orders by symbols. '*' can be used at the beginning and the end of a string.
        The group parameter may contain several comma separated conditions. A condition can be set as a mask using '*'. The logical negation symbol '!' can be used for an exclusion. All conditions are applied sequentially, which means conditions of including to a group should be specified first followed by an exclusion condition. For example, group="*, !EUR" means that orders for all symbols should be selected first and the ones containing "EUR" in symbol names should be excluded afterwards.
    """
    return _get_ticket_type_stuff(mt5.orders_get, symbol, group=group, ticket=ticket, function=function)


@_context_manager_modified
def order_calc_margin(action: int,
                      symbol: str,
                      volume: float,
                      price: float,
                      ) -> float:
    """Return margin in the account currency to perform a specified trading operation.

    :param action: Order type taking values from the ORDER_TYPE enumeration
    :param symbol: Financial instrument name.
    :param volume: Trading operation volume.
    :param price: Open price.
    :return: Real value if successful, otherwise None. The error info can be obtained using last_error().
    """
    return mt5.order_calc_margin(action, symbol, volume, price)


@_context_manager_modified
def order_calc_profit(action: int,
                      symbol: str,
                      volume: float,
                      price_open: float,
                      price_close: float,
                      ) -> float:
    """Return margin in the account currency to perform a specified trading operation.

    :param action: Order type taking values from the ORDER_TYPE enumeration
    :param symbol: Financial instrument name.
    :param volume: Trading operation volume.
    :param price: Open price.
    :return: Real value if successful, otherwise None. The error info can be obtained using last_error().
    """
    return mt5.order_calc_profit(action, symbol, volume, price_open, price_close)


@_context_manager_modified
def order_check(request: dict = None,
                *,
                action: int = None, magic: int = None, order: int = None,
                symbol: str = None, volume: float = None, price: float = None,
                stoplimit: float = None, sl: float = None, tp: float = None,
                deviation: int = None, type: int = None, type_filling: int = None,
                type_time: int = None, expiration: datetime = None,
                comment: str = None, position: int = None, position_by: int = None,
                **kwargs,
                ) -> OrderCheckResult:
    """Check funds sufficiency for performing a required trading operation. Check result are returned as the MqlTradeCheckResult structure.

    :param action: Trade operation type
    :param magic: Expert Advisor ID (magic number)
    :param order: Order ticket
    :param symbol: Trade symbol
    :param volume: Requested volume for a deal in lots
    :param price: Price
    :param stoplimit: Stop-limit level
    :param sl: Stop loss level
    :param tp: Take profit level
    :param deviation: Maximum possible deviation from the requested price
    :param type: Order type
    :param type_filling: Order execution type
    :param type_time: Order expiration type
    :param expiration: Order expiration time (for the orders of ORDER_TIME_SPECIFIED type)
    :param comment: Order comment
    :param position: Position ticket
    :param position_by: The ticket of an opposite position
    :param kwargs:
    :return: OrderSendResult namedtuple
    """
    return _do_trade_action(mt5.order_check, locals().copy())


@_context_manager_modified
def order_send(request: dict = None,
               *,
               action: int = None, magic: int = None, order: int = None,
               symbol: str = None, volume: float = None, price: float = None,
               stoplimit: float = None, sl: float = None, tp: float = None,
               deviation: int = None, type: int = None, type_filling: int = None,
               type_time: int = None, expiration: datetime = None,
               comment: str = None, position: int = None, position_by: int = None,
               **kwargs,
               ) -> OrderSendResult:
    """Interaction between the client terminal and a trade server for executing the order placing operation is performed
    by using trade requests. The trade request is represented by the special predefined structure of MqlTradeRequest
    type, which contain all the fields necessary to perform trade deals. The request processing result is represented
    by the structure of MqlTradeResult type.

    :param action: Trade operation type
    :param magic: Expert Advisor ID (magic number)
    :param order: Order ticket
    :param symbol: Trade symbol
    :param volume: Requested volume for a deal in lots
    :param price: Price
    :param stoplimit: Stop-limit level
    :param sl: Stop loss level
    :param tp: Take profit level
    :param deviation: Maximum possible deviation from the requested price
    :param type: Order type
    :param type_filling: Order execution type
    :param type_time: Order expiration type
    :param expiration: Order expiration time (for the orders of ORDER_TIME_SPECIFIED type)
    :param comment: Order comment
    :param position: Position ticket
    :param position_by: The ticket of an opposite position
    :param kwargs:
    :return: OrderSendResult namedtuple
    """
    return _do_trade_action(mt5.order_send, locals().copy())


@_context_manager_modified
def positions_total() -> int:
    """Get the number of open positions.

    :return: Integer value.
    """
    return mt5.positions_total()


@_context_manager_modified
def positions_get(symbol: str = None,
                  *,
                  group: str = None,
                  ticket: int = None,
                  function: Callable[[TradePosition], bool] = None,
                  **kwargs
                  ) -> Tuple[TradePosition]:
    """Get open positions with the ability to filter by symbol or ticket. There are three call options.

    :param symbol:
    :param group:
    :param ticket:
    :return:
    """
    return _get_ticket_type_stuff(symbol, group=group, ticket=ticket, function=function)


@_context_manager_modified
def history_deals_get(datetime_from: datetime = None,
                      datetime_to: datetime = None,
                      *,
                      group: str = None,
                      ticket: int = None,
                      position: int = None,
                      function: Callable[[TradeDeal], bool] = None,
                      **kwargs
                      ) -> Tuple[TradeDeal]:
    """Get deals from trading history within the specified interval with the ability to filter by ticket or position.

    :param datetime_from: Date the orders are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01.
    :param datetime_to: Date, up to which the orders are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01.
    :param group: The filter for arranging a group of necessary symbols. Optional named parameter. If the group is specified, the function returns only deals meeting a specified criteria for a symbol name.
    :param ticket: Ticket of an order (stored in DEAL_ORDER) all deals should be received for. Optional parameter.
    :param position: Ticket of a position (stored in DEAL_POSITION_ID) all deals should be received for. Optional parameter.
    :param function: A function that accepts a TradeDeal object and returns True if that object is to be used else False
    :param kwargs:
    :return: a tuple of TradeDeal objects
    """
    return _get_history_type_stuff(mt5.history_deals_get, locals().copy())


@_context_manager_modified
def history_orders_total(datetime_from: datetime, datetime_to: datetime, **kwargs) -> int:
    """Get the number of orders in trading history within the specified interval.

    :param datetime_from: Date the orders are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.
    :param datetime_to: Date, up to which the orders are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.
    :param kwargs:
    :return:
    """
    return mt5.history_orders_total(datetime_from, datetime_to)


@_context_manager_modified
def history_deals_total(datetime_from: datetime, datetime_to: datetime, **kwargs) -> int:
    """Get the number of ``deals`` in trading history within the specified interval.

    :param datetime_from: Date the orders are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.
    :param datetime_to: Date, up to which the orders are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01. Required unnamed parameter.
    :param kwargs:
    :return:
    """
    return mt5.history_deals_total(datetime_from, datetime_to)


@_context_manager_modified
def history_orders_get(datetime_from: datetime = None,
                       datetime_to: datetime = None,
                       *,
                       group: str = None,
                       ticket: int = None,
                       position: int = None,
                       function: Callable[[TradeOrder], bool] = None,
                       **kwargs
                       ) -> Tuple[TradeOrder]:
    """Get deals from trading history within the specified interval with the ability to filter by ticket or position.

    :param datetime_from: Date the orders are requested from. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01.
    :param datetime_to: Date, up to which the orders are requested. Set by the 'datetime' object or as a number of seconds elapsed since 1970.01.01.
    :param group: The filter for arranging a group of necessary symbols.
    :param ticket: Ticket of an order (stored in DEAL_ORDER) all deals should be received for. Optional parameter.
    :param position: Ticket of a position (stored in DEAL_POSITION_ID) all deals should be received for. Optional parameter.
    :param function: A function that accepts a TradeOrder object and returns True if that object is to be used else False
    :param kwargs:
    :return: a tuple of TradeOrder objects
    """
    return _get_history_type_stuff(mt5.history_orders_get, locals().copy())


@_context_manager_modified
def deal_from_send_result(result: OrderSendResult) -> Union[TradeDeal, None]:
    """Get the TradeDeal from order send result.

    :param result: OrderSendResult
    :return: TradeDeal object or None
    """
    try:
        return history_deals_get(ticket=result.deal)[0]
    except:
        return None


@_context_manager_modified
def position_from_send_result(result: OrderSendResult) -> Union[TradePosition, None]:
    """Get the TradePosition from order send result.

    :param result: OrderSendResult
    :return: TradeDeal object or None
    """
    deal = deal_from_send_result(result)
    try:
        return positions_get(ticket=deal.position_id)[0]
    except:
        return None


@_context_manager_modified
def order_from_send_result(result: OrderSendResult) -> Union[TradeOrder, None]:
    """Get the TradeOrder from order send result.

    :param result: OrderSendResult
    :return: TradeDeal object or None
    """
    try:
        return orders_get(ticket=result.order)[0]
    except:
        return None


if __name__ == "__main__":
    import logging
    from datetime import datetime, timedelta

    time_to = datetime.utcnow()
    time_from = time_to - timedelta(hours=2)

    logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
    mt5_connected = connected(
        timeout=3500,
        ensure_trade_enabled=True,
        raise_on_error=False,
        debug_logging=True,
        logger=logging.debug,
    )

    with mt5_connected:
        x = copy_rates("@EP", TIMEFRAME_H1, start_pos=0, count=10)
        # for i in x:
        #     print(datetime.utcfromtimestamp(i[0]), datetime.utcnow())
        # print(_DEFAULT_FROM_DATETIME.timestamp())
        # print(x)
        # print(len(x))
        # print(type(x))
        _ = login(1132419)
        _ = version()
        _ = last_error()
        _ = account_info()
        _ = terminal_info()
        _ = symbols_total()
        _ = symbols_get()
        _ = symbol_info("@EP")
        _ = symbol_info_tick("@EP")
        _ = symbol_select("@EP", True)
        _ = copy_rates_from()
        _ = copy_rates_from_pos()
        _ = copy_rates_range(datetime_from=time_from, datetime_to=time_to)
        _ = copy_ticks_from()
        _ = copy_ticks_range()
        _ = orders_total()
        _ = orders_get()
        _ = order_calc_margin()
        _ = order_calc_profit()
        _ = order_check()
        _ = order_send({})
        _ = positions_total()
        _ = positions_get()
        _ = history_orders_total()
        _ = history_orders_get()
        _ = history_deals_total()
        _ = history_deals_get()

    # print(s[0])
