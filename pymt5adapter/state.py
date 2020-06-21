import logging


class _GlobalState:
    """
    Borg shared state class
    """
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        if 'max_bars' not in self.__shared_state:
            self.set_defaults()

    def set_defaults(self,
                     raise_on_errors=None,
                     max_bars=None,
                     logger=None,
                     return_as_dict=None,
                     return_as_native_python_objects=None,
                     ):
        """Initializes the instance variables and provides a method for setting the state with a single call.

        :param debug_logging:
        :param raise_on_errors:
        :param max_bars:
        :param logger:
        :param return_as_dict:
        :param return_as_native_python_objects:
        :return:
        """
        self.raise_on_errors = raise_on_errors or False
        self.max_bars = max_bars or 100_000
        self._logger = logger
        self.return_as_dict = return_as_dict or False
        self.return_as_native_python_objects = return_as_native_python_objects or False

    def get_state(self):
        state = dict(
            raise_on_errors=self.raise_on_errors,
            max_bars=self.max_bars,
            logger=self.logger,
            return_as_dict=self.return_as_dict
        )
        return state

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @logger.setter
    def logger(self, new_logger: logging.Logger):
        self._logger = new_logger


global_state: _GlobalState = _GlobalState()
