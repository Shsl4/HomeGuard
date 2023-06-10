import logging
import os
import threading

from HomeGuard.log.filters import HostnameFilter

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

class Logger():

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.logger = logging.getLogger('HomeGuard')

        if len(self.logger.handlers) == 0:
            console_handler = logging.StreamHandler()
            file_handler = logging.FileHandler(os.path.expanduser('~/HomeGuard.log'), mode='w')

            console_handler.addFilter(HostnameFilter())

            fmt = logging.Formatter('%(asctime)s %(hostname)s %(processName)s[%(process)s]: %(message)s',
                                    datefmt='%b %d %H:%M:%S')

            file_handler.setFormatter(fmt)

            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    @staticmethod
    def instance():
        return Logger()

    @staticmethod
    def log(m):
        Logger.instance().logger.info(m)
