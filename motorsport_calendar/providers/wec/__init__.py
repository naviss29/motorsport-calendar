"""FIA WEC provider — pluggable sources, no download logic in the provider."""

from motorsport_calendar.core.registry import registry

from .provider import WecProvider
from .source import WecSource

__all__ = ["WecProvider", "WecSource"]


def _make_provider(cfg, cache, refresh):  # type: ignore[no-untyped-def]
    """Factory WEC : crée un WecProvider avec la bonne source."""
    from motorsport_calendar.providers.wec.sources.official import OfficialWecSource

    source_name = cfg.source or "official"
    if source_name == "official":
        return WecProvider(OfficialWecSource())
    raise ValueError(
        f"Source WEC inconnue : '{source_name}'. "
        "Valeurs acceptées : official"
    )


registry.register("wec", _make_provider)
