from abc import abstractmethod, ABC
import enum

from pydantic import BaseModel


class LogLevel(enum.Enum):
    NONE = enum.auto()
    TRACE = enum.auto()
    INFO = enum.auto()
    WARN = enum.auto()
    CRITICAL = enum.auto()


class AppEvent(BaseModel):
    """Ein Event, welches durch die UI ausgelöst und an einen Listener gesendet wird."""

    evt_lvl: LogLevel = LogLevel.NONE
    evt_type: str
    evt_data: str | None = None
