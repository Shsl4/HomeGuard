import csv
import os
from pathlib import Path

from HomeGuard.utils.resource_paths import ResourcePaths


class MacDatabase:
    _data = {}

    @staticmethod
    def __database():
        if len(MacDatabase._data) == 0:

            if os.getcwd() == '/':
                path = '/opt/HomeGuard/Resources'

            with(open(ResourcePaths.mac_addresses_path(), encoding="utf8")) as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for row in reader:
                    MacDatabase._data[row[0]] = row[1]

        return MacDatabase._data

    @staticmethod
    def get(addr):
        try:
            return MacDatabase.__database()[addr[0: 8].upper()]
        except KeyError:
            return "Unknown"
