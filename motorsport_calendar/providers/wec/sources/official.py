"""OfficialWecSource — fetches from the official FIA WEC data platform."""

from motorsport_calendar.models import Event
from motorsport_calendar.providers.wec.source import WecSource


class OfficialWecSource(WecSource):
    """Fetches WEC season data from the official FIA WEC platform.

    Not yet implemented. The target endpoint and authentication method
    are under investigation.

    Sessions supported: FREE_PRACTICE, QUALIFYING, HYPERPOLE, RACE.
    """

    async def get_season(self, year: int) -> list[Event]:
        raise NotImplementedError
