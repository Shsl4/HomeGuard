from abc import abstractmethod

from HomeGuard.data.event import EventTrigger
from HomeGuard.data.identity import DeviceIdentity


class Bot:

    def __init__(self, token: str):
        self.__token: str = token

    @abstractmethod
    def notify_activity(self, identity: DeviceIdentity, trigger: EventTrigger):
        pass