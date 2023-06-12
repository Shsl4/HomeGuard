import csv
from pathlib import Path


class MacDatabase:
    _data = {}

    @staticmethod
    def __database():
        if len(MacDatabase._data) == 0:
            with(open(Path('Resources/mac_addresses.csv'), encoding="utf8")) as csvfile:
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
