import os
import errno
import logging
import logging.handlers


class CustomerFileHandler(logging.handlers.RotatingFileHandler):
    """
    Customer file handler for logging
    """
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        self.mkdir_p(os.path.dirname(filename))

        logging.handlers.RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)

    @staticmethod
    def mkdir_p(path):
        try:
            """
            Python > 3.2
            """
            os.makedirs(path, exist_ok=True)  # Python>3.2
        except TypeError:
            try:
                os.makedirs(path)
                """
                Python > 2.5
                """
            except OSError as exc: # Python >2.5
                if exc.errno == errno.EEXIST and os.path.isdir(path):
                    pass
                else: raise

