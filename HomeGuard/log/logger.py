import logging
from . import filters
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

class Logger:

    def __init__(self, file_path):
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(file_path, mode='w')

        console_handler.addFilter(filters.HostnameFilter())

        fmt = logging.Formatter('%(asctime)s %(hostname)s %(processName)s[%(process)s]: %(message)s',
                                datefmt='%b %d %H:%M:%S')

        file_handler.setFormatter(fmt)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def log(self, m):
        self.logger.info(m)
