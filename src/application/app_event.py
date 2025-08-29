from abc import abstractmethod, ABC

from pydantic import BaseModel


class AppEvent(BaseModel):
    """Ein Event, welches durch die UI ausgelöst und an einen Listener gesendet wird."""

    evt_type: str
    evt_data: str | None = None

