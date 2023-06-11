import datetime
import json
import uuid
from json import JSONEncoder


class TimeWindow:
    def __init__(self, begin: float, end: float):

        if begin < 0.0 or begin > 24.0:
            raise RuntimeError("Invalid begin time provided to TimeWindow.")

        if end < 0.0 or end > 24.0 or end < begin:
            raise RuntimeError("Invalid end time provided to TimeWindow.")

        self.begin = begin
        self.end = end

    def included(self, value: float) -> bool:
        return self.begin <= value <= self.end

    @staticmethod
    def all_day():
        return TimeWindow(0.0, 24.0)


class Event:

    def __init__(self, name: str):
        self.__name = name
        self.__ids: set[uuid.UUID] = set()
        self.__triggers: list[EventTrigger] = []

        # Represents the devices that triggered this event today.
        self.__triggered_devices: set[uuid.UUID] = set()


    def to_json(self):
        return {
            'name': self.__name,
            'ids': self.__ids,
            'triggers': self.__triggers,
        }

    def reset(self):
        self.__triggered_devices.clear()

    def trigger(self, device_id: uuid.UUID):

        if device_id not in self.__ids:
            return None

        now = datetime.date.today()
        now_time = datetime.datetime.now()

        for trigger in self.__triggers:

            if trigger.should_trigger(now.month, now.day, now_time.hour + now_time.minute / 60.0):

                if device_id in self.__triggered_devices:
                    return None

                self.__triggered_devices.add(device_id)
                return trigger

        return None

    def add_identity(self, device_id: uuid):
        self.__ids.add(device_id)

    def name(self):
        return self.__name

    def create_trigger(self):
        trigger = EventTrigger(self)
        self.__triggers.append(trigger)
        return trigger


class EventTrigger:

    def __init__(self, event: Event):
        self.__months: set[int] = set()
        self.__days: set[int] = set()
        self.__time_window: TimeWindow = TimeWindow.all_day()
        self.__event = event

    def to_json(self):
        return {
            'months': self.__months,
            'days': self.__days,
            'time_window': self.__time_window,
        }

    def should_trigger(self, month: int, day: int, current_time: float):
        return month in self.__months and day in self.__days and self.__time_window.included(current_time)

    def add_month(self, month: int):

        if month < 0 or month > 12:
            return

        self.__months.add(month)

    def add_day(self, day: int):

        if day < 0 or day > 31:
            return

        self.__days.add(day)

    def update_time_window(self, window: TimeWindow):
        self.__time_window = window

    def event(self) -> Event:
        return self.__event

    def time_window(self) -> TimeWindow:
        return self.__time_window


class EventEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, TimeWindow):
            return obj.__dict__
        if isinstance(obj, Event):
            return obj.to_json()
        if isinstance(obj, EventTrigger):
            return obj.to_json()

        return json.JSONEncoder.default(self, obj)


class EventManager:

    def __init__(self):
        self.__events: set[Event] = set()

    def reset_events(self):
        for event in self.__events:
            event.reset()

        print('Event manager reset all avents.')

    def event(self, name: str) -> Event:

        for event in self.__events:
            if event.name() == name:
                return event

        event = Event(name)
        self.__events.add(event)
        return event

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
