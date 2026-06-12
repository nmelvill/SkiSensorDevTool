from typing import Callable

class EventListener:

    def __init__(self) -> None:
        self.callback: None = None

    def notify(self, event_data: dict) -> None:
        pass

    def set_callback(self, callback_func: Callable[[dict]]) -> None:
        pass