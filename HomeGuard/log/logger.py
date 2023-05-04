import logging
import os
from HomeGuard.log.filters import HostnameFilter
from HomeGuard.utils.singleton import Singleton

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

class Logger(metaclass=Singleton):

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
