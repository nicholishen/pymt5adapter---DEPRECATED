import contextlib
import logging
import signal
import sys
import time
from pathlib import Path

from . import const
from .core import mt5_account_info
from .core import mt5_initialize
from .core import mt5_last_error
from .core import mt5_shutdown
from .core import mt5_terminal_info
from .core import MT5Error
from .helpers import LogJson
from .helpers import reduce_args
from .log import get_logger
from .state import global_state as _state
from .types import *

Ping = namedtuple('Ping', 'trade_server terminal')


class _ContextAwareBase:
    __state = _state

    def __new__(cls, *args, **kwargs):
        if cls.__state.return_as_dict:
            raise MT5Error(
                const.ERROR_CODE.UNSUPPORTED,
                f"Cannot use {cls.__name__} class when API state set to return all as dict.")
        return super().__new__(cls)


class connected:
    def __init__(self, *,
                 path: Union[str, Path] = None,
                 portable: bool = None,
                 server: str = None,
                 login: int = None,
                 password: str = None,
                 timeout: int = None,
                 logger: Union[logging.Logger, str, Path] = None,
                 ensure_trade_enabled: bool = None,
                 enable_real_trading: bool = None,
                 raise_on_errors: bool = None,
                 return_as_dict: bool = False,
                 return_as_native_python_objects: bool = False,
                 **kwargs
                 ):
        """Context manager for managing the connection with a MT5 terminal using the python ``with`` statement.

        :param path:  Path to terminal.
        :param portable: Load terminal in portable mode.
        :param server:  Server name.
        :param login:  Account login number.
        :param password:  Account password.
        :param timeout: Connection init timeout.
        :param ensure_trade_enabled: Ensure that auto-trading is enabled. Will raise MT5Error when set to True and the terminal auto-trading is disabled.
        :param enable_real_trading:  Must be explicitly set to True to run on a live account.
        :param raise_on_errors: Automatically checks last_error() after each function call and will raise a Mt5Error when the error-code is not RES_S_OK
        :param debug_logging: Logs each function call.
        :param logger: logging.Logger instance. Setting logger.debugLevel to DEBUG will profile and log function calls
        :param return_as_dict: Converts all namedtuple to dictionaries.
        :param return_as_native_python_objects: Converts all returns to JSON. Namedtuples become JSON objects and numpy arrays become JSON arrays.

        :param kwargs:
        :return: None

        Note:
           The param ``enable_real_trading`` must be set to True to work on live accounts.
        """
        # DATA VALIDATION
        if path:
            try:
                path = Path(path)
                if path.is_dir():
                    path = next(path.glob('**/terminal64.exe'))
                if not path.exists() or 'terminal64' not in str(path):
                    raise Exception
                path = str(path.absolute())
            except Exception:
                if logger:
                    logger.error(LogJson('Invalid Terminal Path', {
                        'type'     : 'init_error',
                        'exception': {
                            'type'      : 'MT5Error',
                            'message'   : 'Invalid path to terminal.',
                            'last_error': [const.ERROR_CODE.INVALID_PARAMS.value, 'Invalid path to terminal.'],
                        }
                    }))
                raise MT5Error(const.ERROR_CODE.INVALID_PARAMS, 'Invalid path to terminal.')
        if password:
            password = str(password)

        self._init_kwargs = reduce_args(dict(
            path=path, portable=portable, server=server,
            login=login, password=password, timeout=timeout,
        ))
        self._ensure_trade_enabled = ensure_trade_enabled
        self._enable_real_trading = enable_real_trading
        # managing global state
        if isinstance(logger, (str, Path)):
            self._logger = get_logger(path_to_logfile=logger, loglevel=logging.INFO, time_utc=True)
        else:
            self._logger = logger
        self._raise_on_errors = raise_on_errors
        # self._debug_logging = debug_logging
        self._terminal_info = None
        self._return_as_dict = return_as_dict
        self._native_python_objects = return_as_native_python_objects

    def __enter__(self):
        self._state_on_enter = _state.get_state()
        _state.raise_on_errors = self.raise_on_errors
        # _state.debug_logging = self.debug_logging
        _state.logger = logger = self._logger
        _state.return_as_dict = self.return_as_dict
        _state.return_as_native_python_objects = self.native_python_objects
        try:
            if not mt5_initialize(**self._init_kwargs):
                # TODO is this logging in correctly?
                last_err = mt5_last_error()
                err_code, err_description = last_err
                err_code = const.ERROR_CODE(err_code)
                if self.logger:
                    self.logger.critical(LogJson('Initialization Failure', {
                        'type'       : 'init_error',
                        'exception'  : {
                            'type'      : 'MT5Error',
                            'message'   : err_description,
                            'last_error': last_err,
                        },
                        'init_kwargs': self._init_kwargs,
                    }))

                raise MT5Error(err_code, err_description)
            self._account_info = mt5_account_info()
            self._terminal_info = mt5_terminal_info()
            if logger:
                logger.info(LogJson('Terminal Initialize Success', {
                    'type' : 'terminal_connection_state',
                    'state': True
                }))
                logger.info(LogJson('Init TerminalInfo', {
                    'type'         : 'init_terminal_info',
                    'terminal_info': self._terminal_info._asdict()
                }))
                logger.info(LogJson('Init AccountInfo', {
                    'type'        : 'init_account_info',
                    'account_info': self._account_info._asdict()
                }))
            if not self._enable_real_trading:
                if self._account_info.trade_mode == const.ACCOUNT_TRADE_MODE.REAL:
                    msg = "Real account trading has not been enabled in the context manager"
                    if logger:
                        logger.critical(LogJson('Real Account Trading Disabled', {
                            'type'     : 'init_error',
                            'exception': {
                                'type'      : 'MT5Error',
                                'message'   : msg,
                                'last_error': [const.ERROR_CODE.REAL_ACCOUNT_DISABLED.value, msg],
                            }
                        }))
                    raise MT5Error(const.ERROR_CODE.REAL_ACCOUNT_DISABLED, msg)
            if self._ensure_trade_enabled:
                term_info = self.terminal_info
                _state.max_bars = term_info.maxbars
                if not term_info.trade_allowed:
                    if logger:
                        logger.critical(LogJson('Initialization Error', {
                            'type'     : 'init_error',
                            'exception': {
                                'type'      : 'MT5Error',
                                'message'   : "Terminal Auto-Trading is disabled.",
                                'last_error': [
                                    const.ERROR_CODE.AUTO_TRADING_DISABLED.value,
                                    "Terminal Auto-Trading is disabled."
                                ],
                            }
                        }))
                    raise MT5Error(const.ERROR_CODE.AUTO_TRADING_DISABLED, "Terminal Auto-Trading is disabled.")
            return self
        except:
            self.__exit__(*sys.exc_info())
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.logger and exc_val:
            self.logger.critical(LogJson(f'UNCAUGHT EXCEPTION: {exc_val}', {
                'type'      : 'exception',
                'last_error': mt5_last_error(),
                'exception' : {
                    'type'   : exc_type.__name__,
                    'message': str(exc_val),
                }
            }))
        mt5_shutdown()
        _state.set_defaults(**self._state_on_enter)
        if self.logger:
            self.logger.info(LogJson('Terminal Shutdown', {'type': 'terminal_connection_state', 'state': False}))

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @logger.setter
    def logger(self, new_logger):
        self._logger = new_logger
        _state.logger = new_logger

    @property
    def raise_on_errors(self) -> bool:
        return self._raise_on_errors

    @raise_on_errors.setter
    def raise_on_errors(self, flag: bool):
        _state.raise_on_errors = flag
        self._raise_on_errors = flag

    @property
    def terminal_info(self) -> TerminalInfo:
        if self._terminal_info is None:
            self._terminal_info = mt5_terminal_info()
        return self._terminal_info

    @property
    def return_as_dict(self):
        return self._return_as_dict

    @return_as_dict.setter
    def return_as_dict(self, flag: bool):
        _state.return_as_dict = flag
        self._return_as_dict = flag

    @property
    def native_python_objects(self):
        return self._native_python_objects

    @native_python_objects.setter
    def native_python_objects(self, flag: bool):
        _state.return_as_native_python_objects = flag
        self._native_python_objects = flag

    def ping(self) -> Ping:
        """Get ping in microseconds for the terminal and trade_server.
        Ping attrs = Ping.terminal and Ping.trade_server

        :return: dict with 'server' and 'terminal' ping
        """
        timed = time.perf_counter()
        self._terminal_info = mt5_terminal_info()
        timed = int((time.perf_counter() - timed) * 1000)
        res = Ping(trade_server=self.terminal_info.ping_last,
                   terminal=timed)
        return res


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
