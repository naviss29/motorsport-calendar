"""Concrete Formula1Source implementations — auto-registration dans SourceRegistry."""

from motorsport_calendar.core.source_registry import source_registry

from .cached import CachedFormula1Source
from .ergast import ErgastSource
from .official import OfficialFormula1Source
from .openf1 import OpenF1Source

__all__ = [
    "CachedFormula1Source",
    "ErgastSource",
    "OfficialFormula1Source",
    "OpenF1Source",
]

# Seules les sources implémentées sont enregistrées.
# Ergast, Official, Cached seront ajoutés ici quand leurs get_season() seront opérationnels.
source_registry.register(
    "formula1",
    "openf1",
    lambda cache, refresh: OpenF1Source(cache=cache, refresh=refresh),
)
