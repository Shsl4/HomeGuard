import os
import sys
from pathlib import Path


class ResourcePaths:

    @staticmethod
    def identities_path():

        if sys.platform != "win32" and os.getenv('HOMEGUARD_INSTALLED') is not None:
            return '/var/lib/HomeGuard/identities.json'

        return Path.home().joinpath('Documents/HomeGuard/identities.json')

    @staticmethod
    def mac_addresses_path():

        if sys.platform != "win32" and os.getenv('HOMEGUARD_INSTALLED') is not None:
            return '/opt/HomeGuard/Resources/mac_addresses.csv'

        return 'Resources/mac_addresses.csv'

    @staticmethod
    def events_path():

        if sys.platform != "win32" and os.getenv('HOMEGUARD_INSTALLED') is not None:
            return '/var/lib/HomeGuard/events.json'

        return Path.home().joinpath('Documents/HomeGuard/events.json')

