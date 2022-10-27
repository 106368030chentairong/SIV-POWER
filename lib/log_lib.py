import logging
import logging.config
import os
import sys
import threading
from logging import StreamHandler

logger_lock = threading.Lock()

class RootLoggingFilter(logging.Filter):
    def filter(self, record):
        thread_name = threading.current_thread().name

        logger = logging.getLogger('root.report')
        original_name = thread_name

        logger.propagate = False
        if hasattr(record, 'asctime'):
            msg = '[{}][{}][{}] - {}'.format(record.asctime, record.levelname,
                                             thread_name, record.msg)
        else:
            record.threadNmae = thread_name
            msg = record.msg
        logger.log(record.levelno, msg, *record.args)
        if record.levelno >= logging.getLevelName('ERROR') and record.exc_text:
            logger.log(record.levelno, record.exc_text)
        logger.propagate = True
        logging.getLogger('root')
        threading.current_thread().name = original_name
        return True

def setup_loggers(start_time, prefix=''):
    """Setup logger for all the process, including MainProcess, and test
    stations.
    Args:
      start_time: The log create time.
      prefix: prefix directory of the log file.
      filename: log file name.
    Returns:
      file_name: The log abs. filename.
    Raises:
      None
    """
    with logger_lock:
        term = sys.stdout

        config = {
            'version': 1,
            'filters': {
                'RootLoggingFilter': {
                    '()': RootLoggingFilter
                },
            },
            'formatters': {
                'standard_formatter': {
                    'format': '%(asctime)s | %(levelname)-7s '
                                '| %(threadName)-7s |   %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
            },
            'handlers': {
                'console_handler': {
                    'class': 'logging.StreamHandler',
                    'level': logging.DEBUG,
                    'formatter': 'standard_formatter',
                    'stream': term,
                    'filters': ['RootLoggingFilter']
                },
            },
            'root': {
                'level': logging.DEBUG,
                'handlers': ['console_handler']
            },
        }
        logging.config.dictConfig(config)

    if prefix and not os.path.isdir(prefix):
        os.makedirs(prefix, exist_ok=True, mode=0o777)

    file_name = 'report_{}.log'.format(start_time)

    file_name_path = '{}/{}'.format(prefix, file_name)

    handler = logging.FileHandler(file_name_path)
    handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s | %(levelname)-7s '
                                  '| %(threadName)-7s |    %(message)s',
                                  '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    slot_logger = logging.getLogger('root.report')
    slot_logger.handlers = []
    slot_logger.addHandler(handler)

    return file_name

class TextHandler(logging.StreamHandler):
    """Log handler output to QTextEdit in MainWindow, through      
    callback function."""
    def __init__(self, callback=None):
        StreamHandler.__init__(self, stream=None)
        self._callback = callback

    def emit(self, record):
        try:
            if self._callback:
                msg = self.format(record)
                self._callback(str(msg))
        except Exception as e:
            print(e)
            pass
def add_text_handler(callback=None):
    """Add TextHandler to specific logger, to output log messages to 
    user interface."""
    try:
        formatter = logging.Formatter('%(asctime)s | %(levelname)-7s'
                                    '| %(threadName)-7s | %(message)s',
                                    '%Y-%m-%d %H:%M:%S')
        slot_logger = logging.getLogger('root.report')

        text_handler = TextHandler(callback)
        text_handler.setFormatter(formatter)
        text_handler.setLevel(logging.DEBUG)
        slot_logger.addHandler(text_handler)
    except Exception as e:
        print(e)
        pass