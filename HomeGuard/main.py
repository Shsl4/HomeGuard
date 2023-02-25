import logging
import os
from log import filters


home_directory = os.path.expanduser('~/HomeGuard.log')
handler = logging.StreamHandler()
file_handler = logging.FileHandler(home_directory)
handler.addFilter(filters.HostnameFilter())
fmt = logging.Formatter('%(asctime)s %(hostname)s %(processName)s[%(process)s]: %(message)s', datefmt='%b %d %H:%M:%S')

handler.setFormatter(fmt)
file_handler.setFormatter(fmt)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addHandler(file_handler)

if __name__ == "__main__":
    logger.info("Starting HomeGuard...")
