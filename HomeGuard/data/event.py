import dataclasses
import datetime
import json
import uuid
from enum import Enum


class Event:

    def __init__(self, name: str):
        self.__name = name
        self.__ids: set[uuid.UUID] = set()
        self.__trigger: EventTrigger = EventTrigger(self)

        # Represents the devices that triggered this event today.
        self.__triggered_devices: set[uuid.UUID] = set()

    @classmethod
    def parse(cls, data):

        event = Event(data['name'])

        for unique_id in data['ids']:

            try:
                event.__ids.add(uuid.UUID(unique_id))
            except ValueError:
                pass

        event.__trigger = EventTrigger.parse(event, data['trigger'])

        return event

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

    @classmethod
    def parse(cls, event, data):

        trigger = EventTrigger(event)

        split_start = [int(x) for x in data['start_date'].split('/')]
        split_end = [int(x) for x in data['end_date'].split('/')]

        split_start_time = [int(x) for x in data['start_time'].split(':')]
        split_end_time = [int(x) for x in data['end_time'].split(':')]

        start = datetime.date(split_start[2], split_start[1], split_start[0])
        end = datetime.date(split_end[2], split_end[1], split_end[0])

        start_time = datetime.time(split_start_time[0], split_start_time[1])
        end_time = datetime.time(split_end_time[0], split_end_time[1])

        trigger.update_time_range(start_time, end_time)
        trigger.update_date_range(start, end)

        for day in data['weekdays']:
            trigger.add_weekday(Weekdays[day])

        return trigger

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
        self.parse_events()

    def reset_events(self):
        for event in self.__events:
            event.reset()

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

    def parse_events(self):
        try:
            with open("events.json", "r") as infile:
                json_data = json.loads(infile.read())

                for data in json_data:
                    try:
                        self.__events.add(Event.parse(data))
                    except BaseException:
                        pass

        except BaseException:
            pass