"""Formula 1 provider — pluggable sources, no download logic in the provider."""

from motorsport_calendar.core.registry import registry

from .provider import Formula1Provider
from .source import Formula1Source

__all__ = ["Formula1Provider", "Formula1Source"]


def _make_provider(cfg, cache, refresh):  # type: ignore[no-untyped-def]
    """Factory Formula 1 : crée un Formula1Provider avec la bonne source."""
    # Import lazy — httpx n'est chargé que si le provider est réellement utilisé
    from motorsport_calendar.providers.formula1.sources.openf1 import OpenF1Source

    source_name = cfg.source or "openf1"
    if source_name == "openf1":
        return Formula1Provider(OpenF1Source(cache=cache, refresh=refresh))
    raise ValueError(
        f"Source F1 inconnue : '{source_name}'. "
        "Valeurs acceptées : openf1"
    )


registry.register("formula1", _make_provider)
