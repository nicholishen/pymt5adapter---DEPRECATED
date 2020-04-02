from .types import *

GLOBAL_FORCE_NAMEDTUPLE = False
GLOBAL_RAISE_FLAG = False
GLOBAL_DEBUG_LOGGING_FLAG = False
GLOBAL_LOG = print

def is_global_force_namedtuple():
    return GLOBAL_FORCE_NAMEDTUPLE


def set_global_force_namedtuple(flag: bool = False):
    global GLOBAL_FORCE_NAMEDTUPLE
    GLOBAL_FORCE_NAMEDTUPLE = flag


def is_global_debugging():
    return GLOBAL_DEBUG_LOGGING_FLAG


def set_global_debugging(flag: bool = False):
    global GLOBAL_DEBUG_LOGGING_FLAG
    GLOBAL_DEBUG_LOGGING_FLAG = flag


def is_global_raise():
    return GLOBAL_RAISE_FLAG


def set_global_raise(flag: bool = False):
    global GLOBAL_RAISE_FLAG
    GLOBAL_RAISE_FLAG = flag


def set_global_logger(logger: Callable = None):
    global GLOBAL_LOG
    GLOBAL_LOG = logger or print


def set_globals_defaults():
    set_global_raise()
    set_global_debugging()
    set_global_logger()
    set_global_force_namedtuple()