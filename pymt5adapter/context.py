import contextlib

from . import const
from . import helpers
from .core import account_info
from .core import initialize
from .core import last_error
from .core import MT5Error
from .core import shutdown
from .core import terminal_info
from .state import global_state as _state
from .types import *


@contextlib.contextmanager
def connected(*,
              path: str = None,
              portable: bool = None,
              server: str = None,
              login: int = None,
              password: str = None,
              timeout: int = None,
              ensure_trade_enabled: bool = False,
              enable_real_trading: bool = False,
              logger: Callable = None,
              raise_on_errors: bool = False,
              debug_logging: bool = False,
              # force_namedtuple: bool = False,
              **kwargs
              ) -> None:
    """Context manager for managing the connection with a MT5 terminal using the python ``with`` statement.

    :param path:  Path to terminal.
    :param portable: Load terminal in portable mode.
    :param server:  Server name.
    :param login:  Account login number.
    :param password:  Account password.
    :param timeout: Connection init timeout.
    :param ensure_trade_enabled: Ensure that auto-trading is enabled. Will raise MT5Error when set to True and the terminal auto-trading is disabled.
    :param enable_real_trading:  Must be explicitly set to True to run on a live account.
    :param logger: Logging function. Will pass connection status messages to this function.
    :param raise_on_errors: Automatically checks last_error() after each function call and will raise a Mt5Error when the error-code is not RES_S_OK
    :param debug_logging: Logs each function call.

    :param kwargs:
    :return: None

    Note:
        The param ``enable_real_trading`` must be set to True to work on live accounts.
    """
    args = locals().copy()
    args = helpers.clean_args(args)
    mt5_keys = ('path', 'portable', 'server', 'login', 'password', 'timeout')
    mt5_kwargs = {k: v for k, v in args.items() if k in mt5_keys}
    _state.global_debugging = bool(debug_logging)
    _state.raise_on_errors = bool(raise_on_errors)
    # _state.force_namedtuple = bool(force_namedtuple)
    _state.log = logger or print
    log = _state.log
    try:
        if not initialize(**mt5_kwargs):
            raise MT5Error(*last_error())
        elif debug_logging:
            log("MT5 connection has been initialized.")
        acc_info = account_info()
        if not enable_real_trading and acc_info.trade_mode == const.ACCOUNT_TRADE_MODE_REAL:
            raise MT5Error(
                const.RES_X_REAL_ACCOUNT_DISABLED,
                "REAL ACCOUNT TRADING HAS NOT BEEN ENABLED IN THE CONTEXT MANAGER")
        term_info = terminal_info()
        if ensure_trade_enabled and not term_info.trade_allowed:
            if debug_logging:
                log("Failed to initialize because auto-trade is disabled in terminal.")
            raise MT5Error(const.RES_X_AUTO_TRADE_DISABLED, "Terminal Auto-Trading is disabled.")
        _state.max_bars = term_info.maxbars
        yield
    finally:
        shutdown()
        if debug_logging:
            log("MT5 connection has been shutdown.")
        _state.set_defaults()
