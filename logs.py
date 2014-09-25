
import logging

_LOG_LEVEL_NOTSET = 'NOTSET'

formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')

def logger(name):
    get_log_manager().configure(LoggingConfig(name))
    return _LOGGING_MANAGER.get_logger(name)

def get_log_manager():
    return _LOGGING_MANAGER

class LoggingConfig(object):
    def __init__(self, name):
        self.logfile = '/tmp/{}.log'.format(name)
        self.level = 'ERROR'
        self.console_enabled = True

class LoggingManager(object):
    def __init__(self):
        self._root_logger = logging.getLogger()
        self._handlers = list()

    def _add_handler(self, handler):
        self._handlers.append(handler)
        self._root_logger.addHandler(handler)

    def _clean_handlers(self):
        [self._root_logger.removeHandler(hdlr) for hdlr in self._handlers]
        del self._handlers[:]

    def configure(self, cfg):
        self._config = cfg
        self._clean_handlers()

        # Configuration handling
        self._root_logger.setLevel(self._config.level)

        if self._config.logfile is not None:
            handler = logging.FileHandler(self._config.logfile)
            handler.setFormatter(formatter)
            self._add_handler(handler)
        if self._config.console_enabled:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self._add_handler(handler)

    def get_logger(self, logger_name):
        logger = logging.getLogger(logger_name)
        logger.setLevel('INFO')
        return logger

    def disable_console_logging(self):
        self._config.console_enabled = False
        self.configure(self._config)

globals()['_LOGGING_MANAGER'] = LoggingManager()
