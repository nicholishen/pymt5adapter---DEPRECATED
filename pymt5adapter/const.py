import enum
import functools


class _MyIntFlag(enum.IntFlag):
    @classmethod
    def all_flags(cls):
        flags = functools.reduce(lambda x, y: x | y, cls)
        return flags


MIN_TERMINAL_BUILD = 2375
MAX_BARS = 3000
MAX_TICKS = 1_000_000_000

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


class TIMEFRAME(enum.IntEnum):
    """timeframes, ENUM_TIMEFRAME

    M1, M2, M3, M4, M5, M6, M10, M12, M15, M20, M30, H1, H2, H3, H4, H6, H8, H12, D1, W1, MN1
    """
    M1 = 1
    M2 = 2
    M3 = 3
    M4 = 4
    M5 = 5
    M6 = 6
    M10 = 10
    M12 = 12
    M15 = 15
    M20 = 20
    M30 = 30
    H1 = 1 | 0x4000
    H2 = 2 | 0x4000
    H3 = 3 | 0x4000
    H4 = 4 | 0x4000
    H6 = 6 | 0x4000
    H8 = 8 | 0x4000
    H12 = 12 | 0x4000
    D1 = 24 | 0x4000
    W1 = 1 | 0x8000
    MN1 = 1 | 0xC000


MINUTES_TO_TIMEFRAME = {
    1            : TIMEFRAME.M1,
    2            : TIMEFRAME.M2,
    3            : TIMEFRAME.M3,
    4            : TIMEFRAME.M4,
    5            : TIMEFRAME.M5,
    6            : TIMEFRAME.M6,
    10           : TIMEFRAME.M10,
    12           : TIMEFRAME.M12,
    15           : TIMEFRAME.M15,
    20           : TIMEFRAME.M20,
    30           : TIMEFRAME.M30,
    (1 * 60)     : TIMEFRAME.H1,
    (2 * 60)     : TIMEFRAME.H2,
    (3 * 60)     : TIMEFRAME.H3,
    (6 * 60)     : TIMEFRAME.H6,
    (8 * 60)     : TIMEFRAME.H8,
    (12 * 60)    : TIMEFRAME.H12,
    (24 * 60)    : TIMEFRAME.D1,
    (7 * 24 * 60): TIMEFRAME.W1,
    43200        : TIMEFRAME.MN1,
}

# tick copy flags
COPY_TICKS_ALL = -1
COPY_TICKS_INFO = 1
COPY_TICKS_TRADE = 2


class COPY_TICKS(enum.IntEnum):
    """ENUM_COPY_TICKS

    ALL, INFO, TRADE
    """
    ALL = -1
    INFO = 1
    TRADE = 2


# tick flags

TICK_FLAG_BID = 0x02
TICK_FLAG_ASK = 0x04
TICK_FLAG_LAST = 0x08
TICK_FLAG_VOLUME = 0x10
TICK_FLAG_BUY = 0x20
TICK_FLAG_SELL = 0x40


class TICK_FLAG(_MyIntFlag):
    """ENUM_TICK_FLAG

    BID, ASK, LAST, VOLUME, BUY, SELL
    """
    BID = 0x02
    ASK = 0x04
    LAST = 0x08
    VOLUME = 0x10
    BUY = 0x20
    SELL = 0x40


# position type, ENUM_POSITION_TYPE
POSITION_TYPE_BUY = 0  # Buy
POSITION_TYPE_SELL = 1  # Sell


class POSITION_TYPE(enum.IntEnum):
    """position type, ENUM_POSITION_TYPE

    BUY, SELL
    """
    BUY = POSITION_TYPE_BUY
    SELL = POSITION_TYPE_SELL


# position reason, ENUM_POSITION_REASON
POSITION_REASON_CLIENT = 0  # The position was opened as a result of activation of an order placed from a desktop terminal
POSITION_REASON_MOBILE = 1  # The position was opened as a result of activation of an order placed from a mobile application
POSITION_REASON_WEB = 2  # The position was opened as a result of activation of an order placed from the web platform
POSITION_REASON_EXPERT = 3  # The position was opened as a result of activation of an order placed from an MQL5 program, i.e. an Expert Advisor or a script


class POSITION_REASON(enum.IntEnum):
    CLIENT = 0  # The position was opened as a result of activation of an order placed from a desktop terminal
    MOBILE = 1  # The position was opened as a result of activation of an order placed from a mobile application
    WEB = 2  # The position was opened as a result of activation of an order placed from the web platform
    EXPERT = 3  # The position was opened as a result of activation of an order placed from an MQL5 program, i.e. an Expert Advisor or a script


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


class ORDER_TYPE(enum.IntEnum):
    BUY = 0  # Market Buy order
    SELL = 1  # Market Sell order
    BUY_LIMIT = 2  # Buy Limit pending order
    SELL_LIMIT = 3  # Sell Limit pending order
    BUY_STOP = 4  # Buy Stop pending order
    SELL_STOP = 5  # Sell Stop pending order
    BUY_STOP_LIMIT = 6  # Upon reaching the order price, a pending Buy Limit order is placed at the StopLimit price
    SELL_STOP_LIMIT = 7  # Upon reaching the order price, a pending Sell Limit order is placed at the StopLimit price
    CLOSE_BY = 8  # Order to close a position by an opposite one


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


class ORDER_STATE(enum.IntEnum):
    STARTED = 0  # Order checked, but not yet accepted by broker
    PLACED = 1  # Order accepted
    CANCELED = 2  # Order canceled by client
    PARTIAL = 3  # Order partially executed
    FILLED = 4  # Order fully executed
    REJECTED = 5  # Order rejected
    EXPIRED = 6  # Order expired
    REQUEST_ADD = 7  # Order is being registered (placing to the trading system)
    REQUEST_MODIFY = 8  # Order is being modified (changing its parameters)
    REQUEST_CANCEL = 9  # Order is being deleted (deleting from the trading system)


# ENUM_ORDER_TYPE_FILLING
ORDER_FILLING_FOK = 0
ORDER_FILLING_IOC = 1
ORDER_FILLING_RETURN = 2


class ORDER_FILLING(enum.IntEnum):
    FOK = 0
    IOC = 1
    RETURN = 2


# ENUM_ORDER_TYPE_TIME
ORDER_TIME_GTC = 0  # Good till cancel order
ORDER_TIME_DAY = 1  # Good till current trade day order
ORDER_TIME_SPECIFIED = 2  # Good till expired order
ORDER_TIME_SPECIFIED_DAY = 3  # The order will be effective till 23:59:59 of the specified day. If this time is outside a trading session, the order expires in the nearest trading time.


class ORDER_TIME(enum.IntEnum):
    GTC = 0  # Good till cancel order
    DAY = 1  # Good till current trade day order
    SPECIFIED = 2  # Good till expired order
    SPECIFIED_DAY = 3  # The order will be effective till 23:59:59 of the specified day. If this time is outside a trading session, the order expires in the nearest tr


# ENUM_ORDER_REASON
ORDER_REASON_CLIENT = 0  # The order was placed from a desktop terminal
ORDER_REASON_MOBILE = 1  # The order was placed from a mobile application
ORDER_REASON_WEB = 2  # The order was placed from a web platform
ORDER_REASON_EXPERT = 3  # The order was placed from an MQL5-program, i.e. by an Expert Advisor or a script
ORDER_REASON_SL = 4  # The order was placed as a result of Stop Loss activation
ORDER_REASON_TP = 5  # The order was placed as a result of Take Profit activation
ORDER_REASON_SO = 6  # The order was placed as a result of the Stop Out event


class ORDER_REASON(enum.IntEnum):
    CLIENT = 0  # The order was placed from a desktop terminal
    MOBILE = 1  # The order was placed from a mobile application
    WEB = 2  # The order was placed from a web platform
    EXPERT = 3  # The order was placed from an MQL5-program, i.e. by an Expert Advisor or a script
    SL = 4  # The order was placed as a result of Stop Loss activation
    TP = 5  # The order was placed as a result of Take Profit activation
    SO = 6  # The order was placed as a result of the Stop Out event


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


class DEAL_TYPE(enum.IntEnum):
    BUY = 0  # Buy
    SELL = 1  # Sell
    BALANCE = 2  # Balance
    CREDIT = 3  # Credit
    CHARGE = 4  # Additional charge
    CORRECTION = 5  # Correction
    BONUS = 6  # Bonus
    COMMISSION = 7  # Additional commission
    COMMISSION_DAILY = 8  # Daily commission
    COMMISSION_MONTHLY = 9  # Monthly commission
    COMMISSION_AGENT_DAILY = 10  # Daily agent commission
    COMMISSION_AGENT_MONTHLY = 11  # Monthly agent commission
    INTEREST = 12  # Interest rate
    BUY_CANCELED = 13  # Canceled buy deal.
    SELL_CANCELED = 14  # Canceled sell deal.
    DIVIDEND = 15  # Dividend operations
    DIVIDEND_FRANKED = 16  # Franked (non-taxable) dividend operations
    TAX = 17  # Tax ch


# ENUM_DEAL_ENTRY
DEAL_ENTRY_IN = 0  # Entry in
DEAL_ENTRY_OUT = 1  # Entry out
DEAL_ENTRY_INOUT = 2  # Reverse
DEAL_ENTRY_OUT_BY = 3  # Close a position by an opposite one


class DEAL_ENTRY(enum.IntEnum):
    IN = 0  # Entry in
    OUT = 1  # Entry out
    INOUT = 2  # Reverse
    OUT_BY = 3  # Close a position by an o


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


class DEAL_REASON(enum.IntEnum):
    CLIENT = 0  # The deal was executed as a result of activation of an order placed from a desktop terminal
    MOBILE = 1  # The deal was executed as a result of activation of an order placed from a mobile application
    WEB = 2  # The deal was executed as a result of activation of an order placed from the web platform
    EXPERT = 3  # The deal was executed as a result of activation of an order placed from an MQL5 program, i.e. an Expert Advisor or a script
    SL = 4  # The deal was executed as a result of Stop Loss activation
    TP = 5  # The deal was executed as a result of Take Profit activation
    SO = 6  # The deal was executed as a result of the Stop Out event
    ROLLOVER = 7  # The deal was executed due to a rollover
    VMARGIN = 8  # The deal was executed after charging the variation margin
    SPLIT = 9  # The deal was executed after the split (price reduction) of an instrument, which had an open position during split announcement


# ENUM_TRADE_REQUEST_ACTIONS, Trade Operation Types
TRADE_ACTION_DEAL = 1  # Place a trade order for an immediate execution with the specified parameters (market order)
TRADE_ACTION_PENDING = 5  # Place a trade order for the execution under specified conditions (pending order)
TRADE_ACTION_SLTP = 6  # Modify Stop Loss and Take Profit values of an opened position
TRADE_ACTION_MODIFY = 7  # Modify the parameters of the order placed previously
TRADE_ACTION_REMOVE = 8  # Delete the pending order placed previously
TRADE_ACTION_CLOSE_BY = 10  # Close a position by an opposite one


class TRADE_ACTION(enum.IntEnum):
    DEAL = 1  # Place a trade order for an immediate execution with the specified parameters (market order)
    PENDING = 5  # Place a trade order for the execution under specified conditions (pending order)
    SLTP = 6  # Modify Stop Loss and Take Profit values of an opened position
    MODIFY = 7  # Modify the parameters of the order placed previously
    REMOVE = 8  # Delete the pending order placed previously
    CLOSE_BY = 10  # Close a position by an opposite one


# ENUM_SYMBOL_CHART_MODE
SYMBOL_CHART_MODE_BID = 0
SYMBOL_CHART_MODE_LAST = 1


class SYMBOL_CHART_MODE(enum.IntEnum):
    BID = 0
    LAST = 1


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


class SYMBOL_CALC_MODE(enum.IntEnum):
    FOREX = 0
    FUTURES = 1
    CFD = 2
    CFDINDEX = 3
    CFDLEVERAGE = 4
    FOREX_NO_LEVERAGE = 5
    EXCH_STOCKS = 32
    EXCH_FUTURES = 33
    EXCH_OPTIONS = 34
    EXCH_OPTIONS_MARGIN = 36
    EXCH_BONDS = 37
    EXCH_STOCKS_MOEX = 38
    EXCH_BONDS_MOEX = 39
    SERV_COLLATERAL = 64


# ENUM_SYMBOL_TRADE_MODE
SYMBOL_TRADE_MODE_DISABLED = 0
SYMBOL_TRADE_MODE_LONGONLY = 1
SYMBOL_TRADE_MODE_SHORTONLY = 2
SYMBOL_TRADE_MODE_CLOSEONLY = 3
SYMBOL_TRADE_MODE_FULL = 4


class SYMBOL_TRADE_MODE(enum.IntEnum):
    DISABLED = 0
    LONGONLY = 1
    SHORTONLY = 2
    CLOSEONLY = 3
    FULL = 4


# ENUM_SYMBOL_TRADE_EXECUTION
SYMBOL_TRADE_EXECUTION_REQUEST = 0
SYMBOL_TRADE_EXECUTION_INSTANT = 1
SYMBOL_TRADE_EXECUTION_MARKET = 2
SYMBOL_TRADE_EXECUTION_EXCHANGE = 3


class SYMBOL_TRADE_EXECUTION(enum.IntEnum):
    REQUEST = 0
    INSTANT = 1
    MARKET = 2
    EXCHANGE = 3


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


class SYMBOL_SWAP_MODE(enum.IntEnum):
    DISABLED = 0
    POINTS = 1
    CURRENCY_SYMBOL = 2
    CURRENCY_MARGIN = 3
    CURRENCY_DEPOSIT = 4
    INTEREST_CURRENT = 5
    INTEREST_OPEN = 6
    REOPEN_CURRENT = 7
    REOPEN_BID = 8


# ENUM_DAY_OF_WEEK
DAY_OF_WEEK_SUNDAY = 0
DAY_OF_WEEK_MONDAY = 1
DAY_OF_WEEK_TUESDAY = 2
DAY_OF_WEEK_WEDNESDAY = 3
DAY_OF_WEEK_THURSDAY = 4
DAY_OF_WEEK_FRIDAY = 5
DAY_OF_WEEK_SATURDAY = 6


class DAY_OF_WEEK(enum.IntEnum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6


# ENUM_SYMBOL_ORDER_GTC_MODE
SYMBOL_ORDERS_GTC = 0
SYMBOL_ORDERS_DAILY = 1
SYMBOL_ORDERS_DAILY_NO_STOPS = 2


class SYMBOL_ORDERS(enum.IntEnum):
    GTC = 0
    DAILY = 1
    DAILY_NO_STOPS = 2


# ENUM_SYMBOL_OPTION_RIGHT
SYMBOL_OPTION_RIGHT_CALL = 0
SYMBOL_OPTION_RIGHT_PUT = 1


class SYMBOL_OPTION_RIGHT(enum.IntEnum):
    CALL = 0
    PUT = 1


# ENUM_SYMBOL_OPTION_MODE
SYMBOL_OPTION_MODE_EUROPEAN = 0
SYMBOL_OPTION_MODE_AMERICAN = 1


class SYMBOL_OPTION_MODE(enum.IntEnum):
    EUROPEAN = 0
    AMERICAN = 1


# ENUM_ACCOUNT_TRADE_MODE
ACCOUNT_TRADE_MODE_DEMO = 0
ACCOUNT_TRADE_MODE_CONTEST = 1
ACCOUNT_TRADE_MODE_REAL = 2


class ACCOUNT_TRADE_MODE(enum.IntEnum):
    DEMO = 0
    CONTEST = 1
    REAL = 2


# ENUM_ACCOUNT_STOPOUT_MODE
ACCOUNT_STOPOUT_MODE_PERCENT = 0
ACCOUNT_STOPOUT_MODE_MONEY = 1


class ACCOUNT_STOPOUT_MODE(enum.IntEnum):
    ACCOUNT_STOPOUT_MODE_PERCENT = 0
    ACCOUNT_STOPOUT_MODE_MONEY = 1


# ENUM_ACCOUNT_MARGIN_MODE
ACCOUNT_MARGIN_MODE_RETAIL_NETTING = 0
ACCOUNT_MARGIN_MODE_EXCHANGE = 1
ACCOUNT_MARGIN_MODE_RETAIL_HEDGING = 2


class ACCOUNT_MARGIN_MODE(enum.IntEnum):
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


class TRADE_RETCODE(enum.IntEnum):
    REQUOTE = 10004
    REJECT = 10006
    CANCEL = 10007
    PLACED = 10008
    DONE = 10009
    DONE_PARTIAL = 10010
    ERROR = 10011
    TIMEOUT = 10012
    INVALID = 10013
    INVALID_VOLUME = 10014
    INVALID_PRICE = 10015
    INVALID_STOPS = 10016
    TRADE_DISABLED = 10017
    MARKET_CLOSED = 10018
    NO_MONEY = 10019
    PRICE_CHANGED = 10020
    PRICE_OFF = 10021
    INVALID_EXPIRATION = 10022
    ORDER_CHANGED = 10023
    TOO_MANY_REQUESTS = 10024
    NO_CHANGES = 10025
    SERVER_DISABLES_AT = 10026
    CLIENT_DISABLES_AT = 10027
    LOCKED = 10028
    FROZEN = 10029
    INVALID_FILL = 10030
    CONNECTION = 10031
    ONLY_REAL = 10032
    LIMIT_ORDERS = 10033
    LIMIT_VOLUME = 10034
    INVALID_ORDER = 10035
    POSITION_CLOSED = 10036
    INVALID_CLOSE_VOLUME = 10038
    CLOSE_ORDER_EXIST = 10039
    LIMIT_POSITIONS = 10040
    REJECT_CANCEL = 10041
    LONG_ONLY = 10042
    SHORT_ONLY = 10043
    CLOSE_ONLY = 10044
    FIFO_CLOSE = 10045


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
RES_X_REAL_ACCOUNT_DISABLED = -200_001  # REAL ACCOUNT TRADING HAS NOT BEEN ENABLED IN THE CONTEXT MANAGER
RES_X_TERMINAL_VERSION_OUTDATED = -200_002  # terminal version is out of date and does not support the current feature.
RES_X_UNKNOWN_ERROR = -200_003
RES_X_INVALID_COMMANDLINE_ARGS = -200_004


class ERROR_CODE(enum.IntEnum):
    OK = 1  # generic success
    FAIL = -1  # generic fail
    INVALID_PARAMS = -2  # invalid arguments/parameters
    NO_MEMORY = -3  # no memory condition
    NOT_FOUND = -4  # no history
    INVALID_VERSION = -5  # invalid version
    AUTH_FAILED = -6  # authorization failed
    UNSUPPORTED = -7  # unsupported method
    AUTO_TRADING_DISABLED = -8  # auto-trading disabled
    INTERNAL_FAIL = -10000  # internal IPC general error
    INTERNAL_FAIL_SEND = -10001  # internal IPC send failed
    INTERNAL_FAIL_RECV = -10002  # internal IPC recv failed
    INTERNAL_FAIL_INIT = -10003  # internal IPC initialization fail
    INTERNAL_FAIL_CONN = -10004  # internal IPC no ipc
    INTERNAL_FAIL_TIMEOUT = -10005  # internal timeout
    # CUSTOM ERROR CODES ----------------------------------------------------------------------

    REAL_ACCOUNT_DISABLED = -200_001  # REAL ACCOUNT TRADING HAS NOT BEEN ENABLED IN THE CONTEXT MANAGER
    TERMINAL_VERSION_OUTDATED = -200_002  # terminal version is out of date and does not support the current feature.
    UNKNOWN_ERROR = -200_003
    INVALID_COMMANDLINE_ARGS = -200_004


MQL_TRADE_REQUEST_PROPS = dict(
    action=int,
    magic=int,
    order=int,
    symbol=str,
    volume=float,
    price=float,
    stoplimit=float,
    sl=float,
    tp=float,
    deviation=int,
    type=int,
    type_filling=int,
    type_time=int,
    expiration=int,
    comment=str,
    position=int,
    position_by=int,
)

PERIOD_SECONDS = {
    TIMEFRAME_M1 : 60,
    TIMEFRAME_M2 : 120,
    TIMEFRAME_M3 : 180,
    TIMEFRAME_M4 : 240,
    TIMEFRAME_M5 : 300,
    TIMEFRAME_M6 : 360,
    TIMEFRAME_M10: 600,
    TIMEFRAME_M12: 720,
    TIMEFRAME_M15: 900,
    TIMEFRAME_M20: 1200,
    TIMEFRAME_M30: 1800,
    TIMEFRAME_H1 : 3600,
    TIMEFRAME_H2 : 7200,
    TIMEFRAME_H3 : 10800,
    TIMEFRAME_H4 : 14400,
    TIMEFRAME_H6 : 21600,
    TIMEFRAME_H8 : 28800,
    TIMEFRAME_H12: 43200,
    TIMEFRAME_D1 : 86400,
    TIMEFRAME_W1 : 604800,
    TIMEFRAME_MN1: 2592000,
}
