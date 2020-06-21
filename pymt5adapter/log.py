import logging
import time
from pathlib import Path

from . import core
from .types import *


class _UTCFormatter(logging.Formatter):
    converter = time.gmtime


_loglevel_map = {
    logging.DEBUG   : 'DEBUG',
    logging.INFO    : 'INFO',
    logging.WARNING : 'WARNING',
    logging.ERROR   : 'ERROR',
    logging.CRITICAL: 'CRITICAL',
}


@core._context_manager_modified(participation=False, advanced_features=False)
def get_logger(path_to_logfile: Union[Path, str],
               loglevel: int,
               time_utc: bool = True
               ) -> logging.Logger:
    """Get the default logging.Logger instance for pymy5adapter

    :param path_to_logfile: Path to the logfile destination. This can be a string path or a pathlib.Path object
    :param loglevel: This takes the logging loglevel. Same as the parameter from the logging module, eg. logging.INFO
    :param time_utc: When True this will output the log lines in UTC time and Local time when False
    :return:
    """
    try:
        cache = get_logger.cache
    except AttributeError:
        cache = get_logger.cache = {}

    file = Path(path_to_logfile)
    name = [
        'pymt5adapter',
        file.name,
        _loglevel_map.get(loglevel, 'GENERIC'),
        ('time_utc' if time_utc else 'time_local'),
    ]
    name = '.'.join(name)
    if name in cache:
        return cache[name]
    FORMAT = "%(asctime)s\t%(levelname)s\t%(message)s"
    logger = logging.getLogger(name)
    logger.setLevel(loglevel)
    ch = logging.FileHandler(file)
    ch.setLevel(logging.DEBUG)
    Formatter = _UTCFormatter if time_utc else logging.Formatter
    ch.setFormatter(Formatter(FORMAT))
    logger.addHandler(ch)
    cache[name] = logger
    return logger
