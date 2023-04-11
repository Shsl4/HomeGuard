from time import time


class Identity:

    def __init__(self):
        self.ips: list[str] = []
        self.mac_address: str = 'ff:ff:ff:ff:ff:ff'
        self.recognized_names: list[str] = []
        self.display_name: str = ''
        self.last_activity: time = time()

    @staticmethod
    def make_identity(mac):
        return Identity()


class IdentityManager:
    def __init__(self):
        self._identities: list[Identity] = []

    def get_or_create_identity(self, ip, mac) -> Identity:

        for identity in self._identities:
            if identity.ips.count(ip) > 0:
                return identity

        return Identity.make_identity()
