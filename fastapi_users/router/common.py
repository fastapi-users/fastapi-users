import asyncio
from collections import defaultdict
from enum import Enum, auto
from typing import Callable, DefaultDict, List

from fastapi import APIRouter


class ErrorCode:
    REGISTER_USER_ALREADY_EXISTS = "REGISTER_USER_ALREADY_EXISTS"
    LOGIN_BAD_CREDENTIALS = "LOGIN_BAD_CREDENTIALS"
    RESET_PASSWORD_BAD_TOKEN = "RESET_PASSWORD_BAD_TOKEN"


class Event(Enum):
    ON_AFTER_REGISTER = auto()
    ON_AFTER_FORGOT_PASSWORD = auto()


class EventHandlersRouter(APIRouter):
    event_handlers: DefaultDict[Event, List[Callable]]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_handlers = defaultdict(list)

    def add_event_handler(self, event_type: Event, func: Callable) -> None:
        self.event_handlers[event_type].append(func)

    async def run_handlers(self, event_type: Event, *args, **kwargs) -> None:
        for handler in self.event_handlers[event_type]:
            if asyncio.iscoroutinefunction(handler):
                await handler(*args, **kwargs)
            else:
                handler(*args, **kwargs)
