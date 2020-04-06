class _GlobalState:
    """
    Borg shared state class
    """
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        if 'global_debugging' not in self.__shared_state:
            self.set_defaults()

    def set_defaults(self):
        self.raise_on_errors = False
        self.global_debugging = False
        self.max_bars = 100_000
        self.log = print

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, logger):
        self._log = logger or self._log


global_state: _GlobalState = _GlobalState()
