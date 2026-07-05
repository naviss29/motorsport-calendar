"""OpenF1Source — fetches from the OpenF1 open API (2023+)."""

from motorsport_calendar.models import Event
from motorsport_calendar.providers.formula1.source import Formula1Source


class OpenF1Source(Formula1Source):
    """Fetches F1 season data from the OpenF1 REST API.

    Not yet implemented. Covers seasons from 2023 onwards.
    API reference: https://openf1.org
    """

    async def get_season(self, year: int) -> list[Event]:
        raise NotImplementedError
