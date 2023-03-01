import csv


class MacDatabase:

    def __init__(self):
        self.data = {}
        with(open('resources/mac_addresses.csv')) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                self.data[row[0]] = row[1]

    def get(self, addr):
        try:
            return self.data[addr[0: 8].upper()]
        except:
            return "Unknown"
