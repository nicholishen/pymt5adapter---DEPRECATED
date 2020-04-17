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
                     ):
        # self.convert_namedtuples_to_dict = False
        self.debug_logging = debug_logging or False
        self.raise_on_errors = raise_on_errors or False
        self.max_bars = max_bars or 100_000
        self.logger = log or print
        self.return_as_dict = return_as_dict or False

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
