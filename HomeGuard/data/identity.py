import dataclasses
import datetime
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from uuid import UUID

from HomeGuard.net.adapter import Adapter
from HomeGuard.utils.mac_database import MacDatabase
from HomeGuard.utils.resource_paths import ResourcePaths


@dataclass(order=True)
class DeviceIdentity:
    mac_address: str
    uuid: UUID
    display_name: str = ''
    ip_addresses: set[str] = field(default_factory=set[str])
    recognized_names: set[str] = field(default_factory=set[str])
    last_activity: datetime.datetime = datetime.datetime.now()

    def touch(self):
        self.last_activity = datetime.datetime.now()

    def try_assign_host_name(self):

        for ip in self.ip_addresses:

            netbios_name = Adapter.host_name(ip)
            if netbios_name != ip:

                if len(self.recognized_names) == 0:
                    self.display_name = netbios_name

                self.recognized_names.add(netbios_name)
                return

    def refresh(self, name: str | None, ip: str | None, mac: str):

        if self.mac_address != mac:
            return self

        had_names = len(self.recognized_names) > 0

        if name is not None:
            self.recognized_names.add(name)

        if not had_names and len(self.recognized_names) > 0:
            self.display_name = list(self.recognized_names)[0]

        if self.display_name == '':
            self.display_name = f'{MacDatabase.get(mac)} device'

        if ip is not None and ip != '0.0.0.0':
            self.ip_addresses.add(ip)

        self.touch()

        return self

    @staticmethod
    def make_identity(mac):
        return DeviceIdentity(mac, uuid.uuid4())

    @classmethod
    def parse(cls, data):

        identity = DeviceIdentity(data['mac_address'], UUID(data['uuid']))

        identity.display_name = data['display_name']
        identity.ip_addresses = set(data['ip_addresses'])
        identity.recognized_names = set(data['recognized_names'])

        split = data['last_activity'].split(' ')

        split_date = [int(x) for x in split[0].split('/')]
        split_time = [int(x) for x in split[1].split(':')]

        identity.last_activity = datetime.datetime(split_date[0], split_date[1], split_date[2], split_time[0], split_time[1])

        return identity


class IdentityEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        if isinstance(obj, datetime.datetime):
            return '{0}/{1}/{2} {3}:{4}'.format(obj.year, str(obj.month).zfill(2), str(obj.day).zfill(2), str(obj.hour).zfill(2), str(obj.minute).zfill(2))

        return json.JSONEncoder.default(self, obj)


class IdentityManager:
    def __init__(self):
        self.__identities: list[DeviceIdentity] = []
        self.parse_identities()

    def print(self):

        print('Printing identities: ')

        if len(self.__identities) == 0:
            print('No activity found yet.')

        for identity in self.__identities:

            print(f'Display name: {identity.display_name}')
            print(f'UUID: {identity.uuid}')
            print(f'MAC: {identity.mac_address}')
            print(f'IPs: {identity.ip_addresses}')

            if len(identity.recognized_names) > 0:
                print(f'Names: {",".join(list(identity.recognized_names))}')
            else:
                print('Names: None')

            print('')

    def identity_by_id(self, id: uuid.UUID):
        for identity in self.__identities:
            if identity.uuid == id:
                return identity
        return None

    def identity(self, name: str | None, ip: str | None, mac: str) -> DeviceIdentity | None:

        if not Adapter.validate_mac(mac) or ip == Adapter.get_gateway():
            return

        identity = self.__find_identity(name, ip, mac)

        if identity is not None:
            return identity

        new_identity = DeviceIdentity.make_identity(mac).refresh(None, ip, mac)
        new_identity.try_assign_host_name()

        self.__identities.append(new_identity)
        self.write_identities()

        return new_identity

    def write_identities(self):

        json_object = json.dumps(self.__identities, cls=IdentityEncoder,
                                 indent=2, ensure_ascii=False).encode('utf-8')

        filename = ResourcePaths.identities_path()

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w") as outfile:
            outfile.write(json_object.decode())

    def identities(self):
        return self.__identities

    def __find_identity(self, name: str | None, ip: str | None, mac: str):
        for identity in self.__identities:
            if mac == identity.mac_address:
                return identity.refresh(name, ip, mac)

    def parse_identities(self):

        try:
            with open(ResourcePaths.identities_path(), "r") as infile:

                json_data = json.loads(infile.read())

                for data in json_data:
                    try:
                        self.__identities.append(DeviceIdentity.parse(data))
                    except BaseException as e:
                        print(f'Failed to parse DeviceIdentity!: {e}')

        except BaseException as e:
            print(f'Failed to open identities data file: {e}')
