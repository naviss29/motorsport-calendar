"""GUI state and preference models — no business logic, no Flet dependency."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


def _current_year() -> int:
    return date.today().year


@dataclass
class GenerateState:
    """Mutable state shared across the main view."""

    year: int = field(default_factory=_current_year)
    selected_championships: list[str] = field(default_factory=list)
    output_path: str = ""
    is_generating: bool = False

    def is_ready(self) -> bool:
        """True when all required fields are set and no generation is running."""
        return (
            bool(self.selected_championships)
            and bool(self.output_path)
            and not self.is_generating
        )


@dataclass(frozen=True)
class PreferencesModel:
    """Typed model for user preferences.

    Acts as the single source of truth for all configurable settings.
    Future UI sections will bind directly to these fields.
    Default values reflect the French-speaking motorsport fan baseline.

    Fields:
        language:                 UI language code (e.g. "fr", "en")
        timezone:                 IANA tz string (e.g. "Europe/Paris")
        first_day_of_week:        0 = Sunday, 1 = Monday (ISO 8601 default)
        favorite_championships:   ordered list of championship IDs
        preferred_calendar:       target app slug ("google", "apple", "outlook")
        bapps_sync_enabled:       future BApps cloud sync opt-in
    """

    language: str = "fr"
    timezone: str = "Europe/Paris"
    first_day_of_week: int = 1
    favorite_championships: tuple[str, ...] = ()
    preferred_calendar: str = "google"
    bapps_sync_enabled: bool = False
