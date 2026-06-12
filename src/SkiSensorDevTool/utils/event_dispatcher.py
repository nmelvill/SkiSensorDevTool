
from SkiSensorDevTool.utils.event_listener import EventListener

class EventDispatcher:
    def __init__(self) -> None:
        self._listeners: list[EventListener] = []

    def add_listener(self, listener: EventListener) -> None:
        self._listeners.append(listener)

    def remove_listener(self, listener) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def trigger_event(self, event_data: dict={}) -> None:
        for listener in self._listeners:
            listener.notify(event_data)