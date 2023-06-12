import dataclasses
import datetime
import json
import uuid
from enum import Enum
from json import JSONEncoder

from HomeGuard.log.logger import Logger


class Event:

    def __init__(self, name: str):
        self.__name = name
        self.__ids: set[uuid.UUID] = set()
        self.__trigger: EventTrigger = EventTrigger(self)

        # Represents the devices that triggered this event today.
        self.__triggered_devices: set[uuid.UUID] = set()

    def to_json(self):
        return {
            'name': self.__name,
            'ids': self.__ids,
            'trigger': self.__trigger,
        }

    def reset(self):
        self.__triggered_devices.clear()

    def trigger(self, device_id: uuid.UUID):

        if device_id not in self.__ids:
            return None

        now = datetime.date.today()
        now_time = datetime.datetime.now().time()

        if self.__trigger.should_trigger(now, now_time):

            if device_id in self.__triggered_devices:
                return None

            self.__triggered_devices.add(device_id)
            return self.__trigger

        return None

    def add_identity(self, device_id: uuid):
        self.__ids.add(device_id)

    def name(self):
        return self.__name

    def get_trigger(self):
        return self.__trigger


class Weekdays(Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 5
    Saturday = 6
    Sunday = 7


class EventTrigger:

    def __init__(self, event: Event):
        self.__start_date: datetime.date = datetime.date.today()
        self.__end_date: datetime.date = datetime.date.today()
        self.__start_time: datetime.time = datetime.time()
        self.__end_time: datetime.time = datetime.time()
        self.__weekdays: set[Weekdays] = set()
        self.__event = event

    def to_json(self):
        return {
            'start_date': self.__start_date,
            'end_date': self.__end_date,
            'start_time': self.__start_time,
            'end_time': self.__end_time,
            'weekdays': self.__weekdays
        }

    def reset(self):
        self.__start_date = datetime.date.today()
        self.__end_date = datetime.date.today()
        self.__start_time = datetime.time()
        self.__end_time = datetime.time()
        self.__weekdays.clear()

    def should_trigger(self, current_date: datetime.date, current_time: datetime.time):
        return self.__start_date <= current_date <= self.__end_date and \
            self.__start_time <= current_time <= self.__end_time and \
            Weekdays(current_date.weekday()) in self.__weekdays

    def update_date_range(self, begin: datetime.date, end: datetime.date):
        if begin > end:
            return False

        self.__start_date = begin
        self.__end_date = end

        return True

    def update_time_range(self, begin: datetime.time, end: datetime.time):
        if begin > end:
            return False

        self.__start_time = begin
        self.__end_time = end

        return True

    def add_weekday(self, day: Weekdays):
        return self.__weekdays.add(day)

    def event(self) -> Event:
        return self.__event


class EventEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, Event):
            return obj.to_json()
        if isinstance(obj, EventTrigger):
            return obj.to_json()
        if isinstance(obj, datetime.datetime):
            return '{0}/{1}/{2} {3}:{4}'.format(str(obj.day).zfill(2), str(obj.month).zfill(2),
                                                obj.year, str(obj.hour).zfill(2), str(obj.minute).zfill(2))
        if isinstance(obj, datetime.date):
            return '{0}/{1}/{2}'.format(str(obj.day).zfill(2), str(obj.month).zfill(2), obj.year)
        if isinstance(obj, datetime.time):
            return '{0}:{1}'.format(str(obj.hour).zfill(2), str(obj.minute).zfill(2))
        if isinstance(obj, Weekdays):
            return obj.name
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)

        return json.JSONEncoder.default(self, obj)


class EventManager:

    def __init__(self):
        self.__events: set[Event] = set()

    def reset_events(self):
        for event in self.__events:
            event.reset()

        Logger.log('Event manager reset all avents.')

    def event_exists(self, name: str) -> bool:
        for event in self.__events:
            if event.name() == name:
                return True

        return False

    def event(self, name: str) -> Event:

        for event in self.__events:
            if event.name() == name:
                return event

        event = Event(name)
        self.__events.add(event)
        return event

    def events(self):
        return self.__events

    def trigger(self, device_id: uuid) -> EventTrigger | None:

        for event in self.__events:
            trigger = event.trigger(device_id)
            if trigger is not None:
                return trigger

        return None

    def write_events(self):

        json_object = json.dumps(self.__events, cls=EventEncoder,
                                 indent=2, ensure_ascii=False).encode('utf-8')

        with open("events.json", "w") as outfile:
            outfile.write(json_object.decode())
