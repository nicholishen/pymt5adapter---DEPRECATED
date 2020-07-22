import functools
import logging
import re
import time
from datetime import datetime

import MetaTrader5 as _mt5
import numpy

from . import const as _const
from . import helpers as _h
from .state import global_state as _state
from .types import *


class MT5Error(Exception):
    """The exception class for all MetaTrader5 Errors.

    Example:
        >>> try:
        >>>     raise MT5Error(_const.ERROR_CODE.UNSUPPORTED, "This feature is unsupported.")
        >>> except MT5Error as e:
        >>>     print(e.error_code, e.description)


    """

    def __init__(self, error_code: _const.ERROR_CODE, description: str):
        """

        :param error_code: int error code returned my last_error()
        :param description: error description
        """
        super().__init__(f"{error_code.name}: {description}")
        self.errno = self.error_code = error_code
        self.strerror = self.description = description


def _timed_func(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        timer = time.perf_counter_ns()
        result = f(*args, **kwargs)
        timer = time.perf_counter_ns() - timer
        wrapper._perf_timer = round(timer / 1e6, 3)
        return result

    return wrapper


def _context_manager_modified(participation, advanced_features=True):
    def decorator(f):
        # f.__dispatch = True
        @functools.wraps(f)
        def pymt5adapter_wrapped_function(*args, **kwargs):
            if not participation:
                return f(*args, **kwargs)
            logger = _state.logger
            timed_func = None
            if logger and logger.level == logging.DEBUG and f is not order_send:
                timed_func = _timed_func(f)
            use_func = timed_func or f
            try:
                result = use_func(*args, **kwargs)
            except Exception as e:
                if logger:
                    logger.error(_h.LogJson('EXCEPTION', {
                        'type'          : 'exception',
                        'last_error'    : mt5_last_error(),
                        'exception'     : {
                            'type'   : type(e).__name__,
                            'message': str(e),
                        },
                        'call_signature': dict(function=use_func.__name__, args=args, kwargs=kwargs)
                    }))
                raise
            # make sure we logger before we raise
            if advanced_features:
                last_err = None
                if logger:
                    if result is None or logger.level == logging.DEBUG:
                        log = logger.warning if result is None else logger.debug
                        log_dict = _h.LogJson(short_message_=f'Function Debugging: {use_func.__name__}',
                                              type='function_debugging')
                        if hasattr(use_func, '_perf_timer'):
                            log_dict['latency_ms'] = use_func._perf_timer
                        last_err = mt5_last_error()
                        log_dict['last_error'] = mt5_last_error()
                        log_dict['call_signature'] = dict(function=use_func.__name__, args=args, kwargs=kwargs)
                        # call_sig = f"{f.__name__}({_h.args_to_str(args, kwargs)})"
                        log(log_dict)
                    if isinstance(result, OrderSendResult):
                        response = result._asdict()
                        request = response.pop('request')._asdict()
                        request_name = _const.ORDER_TYPE(request['type']).name
                        response_name = trade_retcode_description(response['retcode'])
                        request_dict = _h.LogJson(short_message_=f'Order Request: {request_name}', type='order_request')
                        request_dict['request'] = request
                        logger.info(request_dict)
                        response_dict = _h.LogJson(short_message_=f'Order Response: {response_name}',
                                                   type='order_response')
                        if hasattr(use_func, '_perf_timer'):
                            response_dict['latency_ms'] = use_func._perf_timer
                        response_dict['response'] = response
                        logger.info(response_dict)
                        if result.retcode != _const.TRADE_RETCODE.DONE:
                            logger.warning(_h.LogJson(f'Order Fail: {response_name}', {
                                'type'       : 'order_fail',
                                'retcode'    : result.retcode,
                                'description': response_name,
                            }))
                if _state.raise_on_errors:  # no need to check last error if we got a result
                    if isinstance(result, numpy.ndarray):
                        is_result = True if len(result) > 0 else False
                    else:
                        is_result = bool(result)
                    if not is_result:
                        error_code, description = last_err or mt5_last_error()
                        if error_code != _const.ERROR_CODE.OK:
                            if error_code == _const.ERROR_CODE.INVALID_PARAMS:
                                description += str(args) + str(kwargs)
                            raise MT5Error(_const.ERROR_CODE(error_code), description)
            if _state.return_as_native_python_objects:
                result = _h.make_native(result)
            elif _state.return_as_dict:
                result = _h.dictify(result)
            return result

        if participation:
            pymt5adapter_wrapped_function.__dispatch = True
        return pymt5adapter_wrapped_function

    return decorator


@_context_manager_modified(participation=False)
def parse_args(default_symbol: str = None,
               default_timeframe: Union[int, _const.TIMEFRAME] = None,
               ) -> Optional[Tuple[str, _const.TIMEFRAME]]:
    import sys
    try:
        symbol = sys.argv[1]
        arg2 = sys.argv[2]
        timeframe = _const.MINUTES_TO_TIMEFRAME.get(int(arg2))
        if timeframe is None:
            timeframe = _const.TIMEFRAME(arg2)
        return symbol, timeframe
    except Exception:
        if default_symbol and default_timeframe:
            return default_symbol, _const.TIMEFRAME(default_timeframe)
        if _state.raise_on_errors:
            raise MT5Error(_const.ERROR_CODE.INVALID_COMMANDLINE_ARGS, f"Invalid command line args {sys.argv}")
        else:
            return None


mt5_account_info = _mt5.account_info


@_context_manager_modified(participation=True)
def account_info() -> AccountInfo:
    """Get info on the current trading account. The function returns all data that can be obtained using
    AccountInfoInteger, AccountInfoDouble and AccountInfoString in one call.

    :return: Return info in the form of a named tuple structure (namedtuple). Return None in case of an error.
    The info on the error can be obtained using last_error().
    """
    return mt5_account_info()


@_context_manager_modified(participation=True)
def copy_rates(symbol,
               timeframe: int,
               *,
               datetime_from: Union[datetime, int] = None,
               datetime_to: Union[datetime, int] = None,
               start_pos: int = None,
               count: int = None,
               ) -> Union[numpy.ndarray, None]:
    """Generic function to use keywords to automatically call the correct copy rates function depending on the
    keyword args passed in.

    :param symbol: Financial instrument name, for example, "EURUSD".
    :param timeframe: Timeframe the bars are requested for. Set by a value from the TIMEFRAME enumeration.
    :param datetime_from: Date of opening of the first bar from the requested sample. Set by the 'datetime'
    object or as a number of seconds elapsed since 1970.01.01.
    :param datetime_to: Date, up to which the bars are requested. Set by the 'datetime' object or as a number
    of seconds elapsed since 1970.01.01. Bars with the open time <= date_to are returned.
    :param start_pos: Initial index of the bar the data are requested from. The numbering of bars goes from
    present to past. Thus, the zero bar means the current one.
    :param count: Number of bars to receive.
    :return: Returns bars as the numpy array with the named time, open, high, low, close, tick_volume,
    spread and real_volume columns. Return None in case of an error. The info on the error can be obtained
    using last_error().
    """
    # TODO: test this without args and with count only
    symbol = _h.any_symbol(symbol)
    try:
        if datetime_from is not None:
            if count is not None:
                return mt5_copy_rates_from(symbol, timeframe, datetime_from, count)
            if datetime_to is not None:
                return mt5_copy_rates_range(symbol, timeframe, datetime_from, datetime_to)
        if all(x is None for x in [datetime_from, datetime_to, start_pos]):
            start_pos = 0
        count = min((count or _state.max_bars), _state.max_bars - 1)
        return mt5_copy_rates_from_pos(symbol, timeframe, start_pos, count)
    except SystemError:
        return None


mt5_copy_rates_from = _mt5.copy_rates_from


@_context_manager_modified(participation=True)
def copy_rates_from(symbol,
                    timeframe: int,
                    datetime_from: Union[datetime, int],
                    count: int
                    ) -> Union[numpy.ndarray, None]:
    """Get bars from the MetaTrader 5 terminal starting from the specified date.

    :param symbol: Financial instrument name, for example, "EURUSD".
    :param timeframe: Timeframe the bars are requested for. Set by a value from the TIMEFRAME enumeration.
    :param datetime_from: Date of opening of the first bar from the requested sample. Set by the 'datetime'
    object or as a number of seconds elapsed since 1970.01.01.
    :param count: Number of bars to receive.
    :return: Returns bars as the numpy array with the named time, open, high, low, close, tick_volume,
    spread and real_volume columns. Return None in case of an error. The info on the error can be obtained
    using last_error().
    """
    symbol = _h.any_symbol(symbol)
    try:
        return mt5_copy_rates_from(symbol, timeframe, datetime_from, count)
    except SystemError:
        return None


mt5_copy_rates_from_pos = _mt5.copy_rates_from_pos


@_context_manager_modified(participation=True)
def copy_rates_from_pos(symbol,
                        timeframe: int,
                        start_pos: int,
                        count: int
                        ) -> Union[numpy.ndarray, None]:
    """Get bars from the MetaTrader 5 terminal starting from the specified index.

    :param symbol: Financial instrument name, for example, "EURUSD".
    :param timeframe: Timeframe the bars are requested for. Set by a value from the TIMEFRAME enumeration.
    :param start_pos: Initial index of the bar the data are requested from. The numbering of bars goes from
    present to past. Thus, the zero bar means the current one.
    :param count: Number of bars to receive.
    :return: Returns bars as the numpy array with the named time, open, high, low, close, tick_volume,
    spread and real_volume columns. Return None in case of an error. The info on the error can be obtained
    using last_error().
    """
    symbol = _h.any_symbol(symbol)
    try:
        return mt5_copy_rates_from_pos(symbol, timeframe, start_pos, count)
    except SystemError:
        return None


mt5_copy_rates_range = _mt5.copy_rates_range


@_context_manager_modified(participation=True)
def copy_rates_range(symbol,
                     timeframe: int,
                     datetime_from: Union[datetime, int],
                     datetime_to: Union[datetime, int]
                     ) -> Union[numpy.ndarray, None]:
    """Get bars from the MetaTrader 5 terminal starting from the specified index.

        :param symbol: Financial instrument name, for example, "EURUSD".
        :param timeframe: Timeframe the bars are requested for. Set by a value from the TIMEFRAME enumeration.
        :param datetime_from: Date of opening of the first bar from the requested sample. Set by the 'datetime'
        object or as a number of seconds elapsed since 1970.01.01.
        :param datetime_to: Date, up to which the bars are requested. Set by the 'datetime' object or as a number
        of seconds elapsed since 1970.01.01. Bars with the open time <= date_to are returned.
        :return: Returns bars as the numpy array with the named time, open, high, low, close, tick_volume,
        spread and real_volume columns. Return None in case of an error. The info on the error can be obtained
        using last_error().
        """
    symbol = _h.any_symbol(symbol)
    try:
        return mt5_copy_rates_range(symbol, timeframe, datetime_from, datetime_to)
    except SystemError:
        return None


mt5_copy_ticks_from = _mt5.copy_ticks_from


@_context_manager_modified(participation=True)
def copy_ticks_from(symbol,
                    datetime_from: Union[datetime, int],
                    count: int,
                    flags: int,
                    ) -> Union[numpy.ndarray, None]:
    """Get ticks from the MetaTrader 5 terminal starting from the specified date.

    :param symbol: Financial instrument name, for example, "EURUSD". Required unnamed parameter.
    :param datetime_from: Date the ticks are requested from. Set by the 'datetime' object or as a number of
    seconds elapsed since 1970.01.01.
    :param count: Number of ticks to receive.
    :param flags: A flag to define the type of the requested ticks. COPY_TICKS_INFO – ticks with Bid and/or
    Ask changes, COPY_TICKS_TRADE – ticks with changes in Last and Volume, COPY_TICKS_ALL – all ticks.
    Flag values are described in the COPY_TICKS enumeration.
    :return: Returns ticks as the numpy array with the named time, bid, ask, last and flags columns.
    The 'flags' value can be a combination of flags from the TICK_FLAG enumeration. Return None in case of an error.
    The info on the error can be obtained using last_error().

    Note:
        See the CopyTicks function for more information.

        When creating the 'datetime' object, Python uses the local time zone, while MetaTrader 5 stores tick and
        bar open time in UTC time zone (without the shift). Therefore, 'datetime' should be created in UTC time
        for executing functions that use time. Data received from the MetaTrader 5 terminal has UTC time.
    """
    symbol = _h.any_symbol(symbol)
    try:
        return mt5_copy_ticks_from(symbol, datetime_from, count, flags)
    except SystemError:
        return None


mt5_copy_ticks_range = _mt5.copy_ticks_range


@_context_manager_modified(participation=True)
def copy_ticks_range(symbol,
                     datetime_from: Union[datetime, int],
                     datetime_to: Union[datetime, int],
                     flags: int,
                     ) -> Union[numpy.ndarray, None]:
    """Get ticks from the MetaTrader 5 terminal starting from the specified date.

        :param symbol: Financial instrument name, for example, "EURUSD". Required unnamed parameter.
        :param datetime_from: Date the ticks are requested from. Set by the 'datetime' object or as a number of
        seconds elapsed since 1970.01.01.
        :param datetime_to: Date, up to which the ticks are requested. Set by the 'datetime' object or as a number
        of seconds elapsed since 1970.01.01.
        :param flags: A flag to define the type of the requested ticks. COPY_TICKS_INFO – ticks with Bid and/or
        Ask changes, COPY_TICKS_TRADE – ticks with changes in Last and Volume, COPY_TICKS_ALL – all ticks.
        Flag values are described in the COPY_TICKS enumeration.
        :return: Returns ticks as the numpy array with the named time, bid, ask, last and flags columns.
        The 'flags' value can be a combination of flags from the TICK_FLAG enumeration. Return None in case of
        an error. The info on the error can be obtained using last_error().

        Note:
            See the CopyTicks function for more information.

            When creating the 'datetime' object, Python uses the local time zone, while MetaTrader 5 stores tick
            and bar open time in UTC time zone (without the shift). Therefore, 'datetime' should be created in
            UTC time for executing functions that use time. Data received from the MetaTrader 5 terminal has UTC time.
        """
    symbol = _h.any_symbol(symbol)
    try:
        return mt5_copy_ticks_range(symbol, datetime_from, datetime_to, flags)
    except SystemError:
        return None


mt5_history_deals_get = _mt5.history_deals_get


@_context_manager_modified(participation=True)
def history_deals_get(datetime_from: datetime = None,
                      datetime_to: datetime = None,
                      *,
                      group: str = None,
                      ticket: int = None,
                      position: int = None,
                      function: Callable = None,
                      **kwargs
                      ) -> Tuple[TradeDeal]:
    """Get deals from trading history within the specified interval with the ability to filter by ticket or position.

    :param datetime_from: Date the orders are requested from. Set by the 'datetime' object or as a number of seconds
    elapsed since 1970.01.01.
    :param datetime_to: Date, up to which the orders are requested. Set by the 'datetime' object or as a number of
    seconds elapsed since 1970.01.01.
    :param group: The filter for arranging a group of necessary symbols. Optional named parameter. If the group is
    specified, the function returns only deals meeting a specified criteria for a symbol name.
    :param ticket: Ticket of an order (stored in DEAL_ORDER) all deals should be received for. Optional parameter.
    :param position: Ticket of a position (stored in DEAL_POSITION_ID) all deals should be received for. Optional
    parameter.
    :param function: A function that accepts a TradeDeal object and
    returns True if that object is to be used else False
    :param kwargs:
    :return: a tuple of TradeDeal objects
    """
    args = locals().copy()
    return _h.get_history_type_stuff(mt5_history_deals_get, args)


mt5_history_deals_total = _mt5.history_deals_total


@_context_manager_modified(participation=True)
def history_deals_total(datetime_from: datetime, datetime_to: datetime, **kwargs) -> int:
    """Get the number of ``deals`` in trading history within the specified interval.

    :param datetime_from: Date the orders are requested from. Set by the 'datetime' object or as a number of seconds
    elapsed since 1970.01.01. Required unnamed parameter.
    :param datetime_to: Date, up to which the orders are requested. Set by the 'datetime' object or as a number of
    seconds elapsed since 1970.01.01. Required unnamed parameter.
    :param kwargs:
    :return:
    """
    return mt5_history_deals_total(datetime_from, datetime_to)


mt5_history_orders_get = _mt5.history_orders_get


@_context_manager_modified(participation=True)
def history_orders_get(datetime_from: datetime = None,
                       datetime_to: datetime = None,
                       *,
                       group: str = None,
                       ticket: int = None,
                       position: int = None,
                       function: Callable = None,
                       **kwargs
                       ) -> Tuple[TradeOrder]:
    """Get deals from trading history within the specified interval with the ability to filter by ticket or position.

    :param datetime_from: Date the orders are requested from. Set by the 'datetime' object or as a number of
    seconds elapsed since 1970.01.01.
    :param datetime_to: Date, up to which the orders are requested. Set by the 'datetime' object or as a number of
    seconds elapsed since 1970.01.01.
    :param group: The filter for arranging a group of necessary symbols.
    :param ticket: Ticket of an order (stored in DEAL_ORDER) all deals should be received for. Optional parameter.
    :param position: Ticket of a position (stored in DEAL_POSITION_ID) all deals should be received for.
    Optional parameter.
    :param function: A function that accepts a TradeOrder object and
    returns True if that object is to be used else False
    :param kwargs:
    :return: a tuple of TradeOrder objects
    """
    args = locals().copy()
    return _h.get_history_type_stuff(mt5_history_orders_get, args)


mt5_history_orders_total = _mt5.history_orders_total


@_context_manager_modified(participation=True)
def history_orders_total(datetime_from: datetime, datetime_to: datetime, **kwargs) -> int:
    """Get the number of orders in trading history within the specified interval.

    :param datetime_from: Date the orders are requested from. Set by the 'datetime' object or as a number of seconds
    elapsed since 1970.01.01. Required unnamed parameter.
    :param datetime_to: Date, up to which the orders are requested. Set by the 'datetime' object or as a number of
    seconds elapsed since 1970.01.01. Required unnamed parameter.
    :param kwargs:
    :return:
    """
    return mt5_history_orders_total(datetime_from, datetime_to)


mt5_initialize = _mt5.initialize


@_context_manager_modified(participation=True)
def initialize(path: str = None,
               *,
               login: str = None,
               password: str = None,
               server: str = None,
               portable: bool = False,
               timeout: int = None,
               **kwargs
               ) -> bool:
    """Establish a connection with the MetaTrader 5 terminal. Call without parameters. The terminal for connection
    is found automatically.

    :param path:  Path to the metatrader.exe or metatrader64.exe file. Optional unnamed parameter. It is indicated
    first without a parameter name. If the path is not specified, the module attempts to find the executable file on
    its own.
    :param login: Connection timeout in milliseconds. Optional named parameter. If not specified, the value of
    60 000 (60 seconds) is applied. If the connection is not established within the specified time, the call is
    forcibly terminated and the exception is generated.
    :param password: Trading account password. Optional named parameter. If the password is not set, the password
    saved in the terminal database is applied automatically.
    :param server: Trade server name. Optional named parameter. If no server is set, the last used server is applied
    automatically.
    :param portable: Launch terminal in portable mode
    :timeout: Number of milliseconds for timeout
    :return: Returns True in case of successful connection to the MetaTrader 5 terminal, otherwise - False.
    """
    args = locals().copy()
    args = _h.reduce_args(args)
    result = mt5_initialize(**args)
    return result


mt5_last_error = _mt5.last_error


@_context_manager_modified(participation=True, advanced_features=False)
def last_error() -> Tuple[int, str]:
    """last_error() allows obtaining an error code in case of a failed execution of a MetaTrader 5 library function.
    It is similar to GetLastError(). However, it applies its own error codes.

    :return: Return the last error code and description as a tuple.
    """
    return mt5_last_error()


mt5_login = _mt5.login


@_context_manager_modified(participation=True)
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
    args = locals().copy()
    args = _h.reduce_args(args)
    login = args.pop('login')
    return mt5_login(login, **args)


mt5_order_calc_margin = _mt5.order_calc_margin


@_context_manager_modified(participation=True)
def order_calc_margin(order_type: int,
                      symbol,
                      volume: float,
                      price: float,
                      ) -> float:
    """Return margin in the account currency to perform a specified trading operation.

    :param order_type: Order type taking values from the ORDER_TYPE enumeration
    :param symbol: Financial instrument name.
    :param volume: Trading operation volume.
    :param price: Open price.
    :return: Real value if successful, otherwise None. The error info can be obtained using last_error().
    """
    symbol = _h.any_symbol(symbol)
    return mt5_order_calc_margin(order_type, symbol, volume, price)


mt5_order_calc_profit = _mt5.order_calc_profit


@_context_manager_modified(participation=True)
def order_calc_profit(order_type: int,
                      symbol,
                      volume: float,
                      price_open: float,
                      price_close: float,
                      ) -> float:
    """Return margin in the account currency to perform a specified trading operation.

    :param order_type: Order type taking values from the ORDER_TYPE enumeration
    :param symbol: Financial instrument name.
    :param volume: Trading operation volume.
    :param price_open: Open price.
    :param price_close: Close price.
    :return: Real value if successful, otherwise None. The error info can be obtained using last_error().
    """
    symbol = _h.any_symbol(symbol)
    return mt5_order_calc_profit(order_type, symbol, volume, price_open, price_close)


mt5_order_check = _mt5.order_check


@_context_manager_modified(participation=True)
def order_check(request: dict = None,
                *,
                action: int = None, magic: int = None, order: int = None,
                symbol=None, volume: float = None, price: float = None,
                stoplimit: float = None, sl: float = None, tp: float = None,
                deviation: int = None, type: int = None, type_filling: int = None,
                type_time: int = None, expiration: datetime = None,
                comment: str = None, position: int = None, position_by: int = None,
                **kwargs,
                ) -> OrderCheckResult:
    """Check funds sufficiency for performing a required trading operation. Check result are returned as the
    MqlTradeCheckResult structure.

    :param request: Pass the trade request as a preformed dictionary.
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
    symbol = _h.any_symbol(symbol)
    args = locals().copy()
    return _h.do_trade_action(mt5_order_check, args)


mt5_order_send = _mt5.order_send


@_context_manager_modified(participation=True)
@_timed_func
def order_send(request: dict = None,
               *,
               action: int = None, magic: int = None, order: int = None,
               symbol=None, volume: float = None, price: float = None,
               stoplimit: float = None, sl: float = None, tp: float = None,
               deviation: int = None, type: int = None, type_filling: int = None,
               type_time: int = None, expiration: datetime = None,
               comment: str = None, position: int = None, position_by: int = None,
               **kwargs,
               ) -> OrderSendResult:
    """Interaction between the client terminal and a trade server for executing the order placing operation
    is performed by using trade requests. The trade request is represented by the special predefined structure
    of MqlTradeRequest type, which contain all the fields necessary to perform trade deals. The request processing
    result is represented by the structure of MqlTradeResult type.

    :param request: Pass the order request as a dictionary.
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
    args = locals().copy()
    return _h.do_trade_action(mt5_order_send, args)


mt5_orders_get = _mt5.orders_get


@_context_manager_modified(participation=True)
def orders_get(symbol=None,
               *,
               group: str = None,
               ticket: int = None,
               function: Callable = None,
               **kwargs
               ) -> Tuple[TradeOrder]:
    """Get active orders with the ability to filter by symbol or ticket.

    :param symbol: Symbol name. Optional named parameter. If a symbol is specified, the ticket parameter is ignored.
    :param group: The filter for arranging a group of necessary symbols.
    :param ticket: Order ticket (ORDER_TICKET). Optional named parameter.
    :param function: A function that takes a TradeOrder object as its only arg
    and returns truth condition for filtering
    :return: tuple of TradeOrder objects

    Note:
        The function allows receiving all active orders within one call similar to the OrdersTotal and
        OrderSelect tandem.
        The group parameter allows sorting out orders by symbols. '*' can be used at the beginning and the
        end of a string.
        The group parameter may contain several comma separated conditions. A condition can be set as a mask
        using '*'. The logical negation symbol '!' can be used for an exclusion. All conditions are applied
        sequentially, which means conditions of including to a group should be specified first followed by
        an exclusion condition. For example, group="*, !EUR" means that orders for all symbols should be
        selected first and the ones containing "EUR" in symbol names should be excluded afterwards.
    """
    symbol = _h.any_symbol(symbol)
    orders = _h.get_ticket_type_stuff(
        mt5_orders_get,
        symbol=symbol,
        group=group,
        ticket=ticket,
        function=function)
    return orders


mt5_orders_total = _mt5.orders_total


@_context_manager_modified(participation=True)
def orders_total() -> int:
    """Get the number of active orders.

    :return: Integer value.
    """
    return mt5_orders_total()


@_context_manager_modified(participation=True, advanced_features=False)
def period_seconds(timeframe):
    """Get the number of seconds for the respective timeframe

    :param timeframe:
    :return:
    """
    return _const.PERIOD_SECONDS.get(int(timeframe))


mt5_positions_get = _mt5.positions_get


@_context_manager_modified(participation=True)
def positions_get(symbol=None,
                  *,
                  group: str = None,
                  ticket: int = None,
                  function: Callable = None,
                  **kwargs
                  ) -> Tuple[TradePosition]:
    """Get open positions with the ability to filter by symbol or ticket. There are three call options.

    :param symbol:
    :param group:
    :param ticket:
    :param function:
    :return:
    """
    symbol = _h.any_symbol(symbol)
    positions = _h.get_ticket_type_stuff(
        mt5_positions_get,
        symbol=symbol,
        group=group,
        ticket=ticket,
        function=function
    )
    return positions


mt5_positions_total = _mt5.positions_total


@_context_manager_modified(participation=True)
def positions_total() -> int:
    """Get the number of open positions.

    :return: Integer value.
    """
    return mt5_positions_total()


mt5_shutdown = _mt5.shutdown


@_context_manager_modified(participation=True)
def shutdown() -> None:
    """Close the previously established connection to the MetaTrader 5 terminal.

    :return: None
    """
    return mt5_shutdown()


mt5_symbol_info = _mt5.symbol_info


@_context_manager_modified(participation=True)
def symbol_info(symbol) -> SymbolInfo:
    """Get data on the specified financial instrument.

    :param symbol:
    :return: Return info in the form of a named tuple structure (namedtuple). Return None in case of an error.
    The info on the error can be obtained using last_error().
    """
    symbol = _h.any_symbol(symbol)
    return mt5_symbol_info(symbol)


mt5_symbol_info_tick = _mt5.symbol_info_tick


@_context_manager_modified(participation=True)
def symbol_info_tick(symbol) -> Tick:
    """Get the last tick for the specified financial instrument.

    :param symbol:
    :return:
    """
    symbol = _h.any_symbol(symbol)
    return mt5_symbol_info_tick(symbol)


# direct access to API function without any added overhead


mt5_symbol_select = _mt5.symbol_select


@_context_manager_modified(participation=True)
def symbol_select(symbol, enable: bool = True) -> bool:
    """Select a symbol in the MarketWatch window or remove a symbol from the window.

    :param symbol:
    :param enable:
    :return: True if successful, otherwise – False.
    """
    symbol = _h.any_symbol(symbol)
    return mt5_symbol_select(symbol, enable)


mt5_symbols_get = _mt5.symbols_get


@_context_manager_modified(participation=True)
def symbols_get(*,
                group: str = None,
                regex: str = None,
                function: Callable = None,
                **kwargs
                ) -> Union[Tuple[SymbolInfo], None]:
    """Get all financial instruments from the MetaTrader 5 terminal.
        The group parameter allows sorting out symbols by name. '*' can be used at the beginning and the
        end of a string.
        The group parameter can be used as a named or an unnamed one. Both options work the same way.
        The named option (group="GROUP") makes the code easier to read.
        The group parameter may contain several comma separated conditions. A condition can be set as a
        mask using '*'. The logical negation symbol '!' can be used for an exclusion. All conditions are applied
        sequentially, which means conditions of including to a group should be specified first followed by an
        exclusion condition. For example, group="*, !EUR" means that all symbols should be selected first and
        the ones containing "EUR" in their names should be excluded afterwards.
        Unlike symbol_info(), the symbols_get() function returns data on all requested symbols within a single call.

    :param group: The filter for arranging a group of necessary symbols. Optional parameter. If the group is
    specified, the function returns only symbols meeting a specified criteria.
    :param regex: Regex pattern for symbol filtering.
    :param function: A function that takes a SymbolInfo object as its only arg and returns <bool> for filtering
    the collection of SymbolInfo results.
    :param kwargs:
    :return: A tuple of SymbolInfo objects
    """
    symbols = mt5_symbols_get(group=group) if group else mt5_symbols_get()
    if symbols is None:
        if _state.raise_on_errors:
            build = version()
            if build and build[1] < _const.MIN_TERMINAL_BUILD:
                raise MT5Error(_const.ERROR_CODE.TERMINAL_VERSION_OUTDATED,
                               "The terminal build needs to be updated to support this feature.")
            else:
                error_code, des = last_error()
                if error_code == _const.RES_S_OK:
                    raise MT5Error(_const.ERROR_CODE.UNKNOWN_ERROR,
                                   "Unknown Error. Is the terminal connected?")
        else:
            return None
    if regex:
        if isinstance(regex, str):
            regex = re.compile(regex)
        symbols = filter(lambda s: regex.match(s.name), symbols)
    if function:
        symbols = filter(function, symbols)
    return tuple(symbols)


mt5_symbols_total = _mt5.symbols_total


@_context_manager_modified(participation=True)
def symbols_total() -> int:
    """Get the number of all financial instruments in the MetaTrader 5 terminal. The function is similar to
    SymbolsTotal(). However, it returns the number of all symbols including custom ones and the ones disabled
    in MarketWatch.

    :return: <int>
    """
    return mt5_symbols_total()


mt5_terminal_info = _mt5.terminal_info


@_context_manager_modified(participation=True)
def terminal_info() -> TerminalInfo:
    """Get the connected MetaTrader 5 client terminal status and settings. The function returns all data that can be
    obtained using TerminalInfoInteger, TerminalInfoDouble and TerminalInfoDouble in one call.

    :return: Return info in the form of a named tuple structure (namedtuple). Return None in case of an error.
    The info on the error can be obtained using last_error().
    """
    return mt5_terminal_info()


@_context_manager_modified(participation=True, advanced_features=False)
def trade_retcode_description(retcode):
    try:
        return _const.TRADE_RETCODE(int(retcode)).name
    except (ValueError, AttributeError):
        return "Unknown Trade Retcode"


mt5_version = _mt5.version


@_context_manager_modified(participation=True)
def version() -> Tuple[int, int, str]:
    """Return the MetaTrader 5 terminal version.

    :return: Returns the MetaTrader 5 terminal version, build and release date. Return None in case of an error.
    The info on the error can be obtained using last_error().
    """
    return mt5_version()


@_context_manager_modified(participation=False, advanced_features=False)
def get_function_dispatch():
    dispatch = dict(sorted((n, f) for n, f in globals().items() if hasattr(f, '__dispatch')))
    return dispatch
