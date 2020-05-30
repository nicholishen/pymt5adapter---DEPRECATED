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
                     debug_logging=None,
                     raise_on_errors=None,
                     max_bars=None,
                     log=None,
                     return_as_dict=None,
                     native_python_objects=None,
                     ):
        """Initializes the instance variables and provides a method for setting the state with a single call.

        :param debug_logging:
        :param raise_on_errors:
        :param max_bars:
        :param log:
        :param return_as_dict:
        :param native_python_objects:
        :return:
        """
        self.debug_logging = debug_logging or False
        self.raise_on_errors = raise_on_errors or False
        self.max_bars = max_bars or 100_000
        self.logger = log or print
        self.return_as_dict = return_as_dict or False
        self.native_python_objects = native_python_objects or False

    def get_state(self):
        state = dict(
            debug_logging=self.debug_logging,
            raise_on_errors=self.raise_on_errors,
            max_bars=self.max_bars,
            log=self.logger,
            return_as_dict=self.return_as_dict
        )
        return state

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, new_logger):
        self._logger = new_logger or self._logger


global_state: _GlobalState = _GlobalState()
