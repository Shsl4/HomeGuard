import dataclasses
import datetime
import json
import time
import uuid
from dataclasses import dataclass, field
from uuid import UUID

from HomeGuard.net.adapter import Adapter
from HomeGuard.utils.mac_database import MacDatabase


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

    def try_assign_netbios_name(self):

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


class IdentityEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        if isinstance(obj, datetime.datetime):
            return '{0}/{1}/{2} {3}:{4}'.format(str(obj.day).zfill(2), str(obj.month).zfill(2),
                                                obj.year, str(obj.hour).zfill(2), str(obj.minute).zfill(2))

        return json.JSONEncoder.default(self, obj)


class IdentityManager:
    def __init__(self):
        self.__identities: list[DeviceIdentity] = []

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
        new_identity.try_assign_netbios_name()

        self.__identities.append(new_identity)
        self.write_identities()

        return new_identity

    def write_identities(self):

        json_object = json.dumps(self.__identities, cls=IdentityEncoder,
                                 indent=2, ensure_ascii=False).encode('utf-8')

        with open("identities.json", "w") as outfile:
            outfile.write(json_object.decode())

    def identities(self):
        return self.__identities

    def __find_identity(self, name: str | None, ip: str | None, mac: str):
        for identity in self.__identities:
            if mac == identity.mac_address:
                return identity.refresh(name, ip, mac)
