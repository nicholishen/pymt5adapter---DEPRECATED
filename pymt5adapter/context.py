import contextlib
import signal
import sys

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
              convert_namedtuples_to_dict:bool=False,
              **kwargs
              ) -> None:
    """Context manager for managing the connection with a MT5 terminal using the python ``with`` statement.

    >>> mt5_connected = mt5.connected(raise_on_errors=True, ensure_trade_enabled=True)
    >>> with mt5_connected:
    ...     print(mt5.symbols_get())
    >>>

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
    args = helpers.reduce_args(args)
    mt5_keys = ('path', 'portable', 'server', 'login', 'password', 'timeout')
    mt5_kwargs = {k: v for k, v in args.items() if k in mt5_keys}
    _state.global_debugging = debug_logging
    _state.raise_on_errors = raise_on_errors
    # _state.convert_namedtuples_to_dict = convert_namedtuples_to_dict
    # _state.force_namedtuple = bool(force_namedtuple)
    _state.log = logger or print
    log = _state.log
    try:
        if not initialize(**mt5_kwargs):
            raise MT5Error(*last_error())
        elif debug_logging:
            log("MT5 connection has been initialized.")
        acc_info = account_info()
        if not enable_real_trading and acc_info.trade_mode == const.ACCOUNT_TRADE_MODE.REAL:
            raise MT5Error(
                const.ERROR_CODE.REAL_ACCOUNT_DISABLED,
                "REAL ACCOUNT TRADING HAS NOT BEEN ENABLED IN THE CONTEXT MANAGER")
        term_info = terminal_info()
        if ensure_trade_enabled and not term_info.trade_allowed:
            if debug_logging:
                log("Failed to initialize because auto-trade is disabled in terminal.")
            raise MT5Error(const.ERROR_CODE.AUTO_TRADING_DISABLED, "Terminal Auto-Trading is disabled.")
        _state.max_bars = term_info.maxbars
        yield
    finally:
        shutdown()
        if debug_logging:
            log("MT5 connection has been shutdown.")
        _state.set_defaults()


def _sigterm_handler(signum, frame):
    sys.exit(0)


_sigterm_handler.__enter_ctx__ = False


@contextlib.contextmanager
def handle_exit(callback=None, append=False):
    """A context manager which properly handles SIGTERM and SIGINT
    (KeyboardInterrupt) signals, registering a function which is
    guaranteed to be called after signals are received.
    Also, it makes sure to execute previously registered signal
    handlers as well (if any).

    >>> app = App()
    >>> with handle_exit(app.stop):
    ...     app.start()
    ...
    >>>

    If append == False raise RuntimeError if there's already a handler
    registered for SIGTERM, otherwise both new and old handlers are
    executed in this order.
    """
    old_handler = signal.signal(signal.SIGTERM, _sigterm_handler)
    if (old_handler != signal.SIG_DFL) and (old_handler != _sigterm_handler):
        if not append:
            raise RuntimeError("there is already a handler registered for "
                               "SIGTERM: %r" % old_handler)

        def handler(signum, frame):
            try:
                _sigterm_handler(signum, frame)
            finally:
                old_handler(signum, frame)

        signal.signal(signal.SIGTERM, handler)

    if _sigterm_handler.__enter_ctx__:
        raise RuntimeError("can't use nested contexts")
    _sigterm_handler.__enter_ctx__ = True

    try:
        yield
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        # code != 0 refers to an application error (e.g. explicit
        # sys.exit('some error') call).
        # We don't want that to pass silently.
        # Nevertheless, the 'finally' clause below will always
        # be executed.
        if err.code != 0:
            raise
    finally:
        _sigterm_handler.__enter_ctx__ = False
        if callback is not None:
            callback()
