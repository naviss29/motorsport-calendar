"""ErgastSource — fetches from the Ergast Motor Racing API (historical)."""

from motorsport_calendar.models import Event
from motorsport_calendar.providers.formula1.source import Formula1Source


class ErgastSource(Formula1Source):
    """Fetches F1 season data from the Ergast API.

    Not yet implemented. Good for historical data (1950 – present).
    API reference: https://ergast.com/mrd
    """

    async def get_season(self, year: int) -> list[Event]:
        raise NotImplementedError
