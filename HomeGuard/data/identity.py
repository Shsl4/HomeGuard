import dataclasses, json, uuid
from time import time
from uuid import UUID
from dataclasses import dataclass, field
from HomeGuard.net.adapter import Adapter
from HomeGuard.utils.mac_database import MacDatabase


@dataclass(order=True)
class DeviceIdentity:
    mac_address: str
    uuid: UUID
    display_name: str = ''
    ip_addresses: set[str] = field(default_factory=set[str])
    recognized_names: set[str] = field(default_factory=set[str])
    last_activity: time = time()

    def touch(self):
        self.last_activity = time()

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

        return json.JSONEncoder.default(self, obj)


class IdentityManager:
    def __init__(self):
        self._identities: list[DeviceIdentity] = []

    def __identity_from_mac(self, mac):
        for identity in self._identities:
            if mac == identity.mac_address:
                return identity

    def __identity_from_ip(self, ip):
        for identity in self._identities:
            if ip in identity.ip_addresses:
                return identity

    def __identity_from_name(self, name, mac):

        identity = self.__identity_from_mac(mac)

        if identity and name in identity.recognized_names or name == identity.display_name:
            return identity

    def identity_with_name(self, name, mac, ip):

        name_identity = self.__identity_from_name(name, mac)

        if name_identity is not None:
            name_identity.touch()
            return name_identity

        identity = self.identity(mac, ip)

        if len(identity.recognized_names) == 0:
            identity.display_name = name

        identity.recognized_names.add(name)

        return identity

    def write_identities(self):

        json_object = json.dumps(self._identities, cls=IdentityEncoder,
                                 indent=2, ensure_ascii=False).encode('utf-8')

        with open("identities.json", "w") as outfile:
            outfile.write(json_object.decode())

    def identity(self, mac, ip) -> DeviceIdentity | None:

        if mac == 'ff:ff:ff:ff:ff:ff':
            return

        mac_identity = self.__identity_from_mac(mac)

        if mac_identity is not None:
            mac_identity.ip_addresses.add(ip)
            mac_identity.touch()
            self.write_identities()
            return mac_identity

        new_identity = DeviceIdentity.make_identity(mac)
        new_identity.ip_addresses.add(ip)

        self._identities.append(new_identity)
        self.write_identities()

        if ip == Adapter.get_gateway():
            new_identity.display_name = 'Gateway'
            new_identity.recognized_names.add('Gateway')
        else:
            new_identity.display_name = f'{MacDatabase.get(mac)} device'

        return new_identity
