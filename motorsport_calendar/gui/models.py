"""GUI state and preference models — no business logic, no Flet dependency."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


def _current_year() -> int:
    return date.today().year


@dataclass
class GenerateState:
    """Mutable state shared across the main view.

    ``current_step`` drives the "Mon calendrier" wizard (Sprint 26 — Release
    Alpha Phase 2): 0=saison, 1=championnats, 2=destination, 3=créer.
    """

    year: int = field(default_factory=_current_year)
    selected_championships: list[str] = field(default_factory=list)
    output_path: str = ""
    is_generating: bool = False
    current_step: int = 0

    STEP_COUNT = 4

    def is_ready(self) -> bool:
        """True when all required fields are set and no generation is running."""
        return (
            bool(self.selected_championships)
            and bool(self.output_path)
            and not self.is_generating
        )

    def step_valid(self, step: int) -> bool:
        """True when the required input for wizard *step* is present.

        Step 0 (saison) has a default value, so it is always valid.
        """
        if step == 0:
            return True
        if step == 1:
            return bool(self.selected_championships)
        if step == 2:
            return bool(self.output_path)
        if step == 3:
            return self.is_ready()
        raise ValueError(f"unknown wizard step: {step}")

    def can_advance(self) -> bool:
        """True when the current step is valid and it is not the last step."""
        return self.current_step < self.STEP_COUNT - 1 and self.step_valid(self.current_step)

    def can_go_back(self) -> bool:
        """True when the wizard is not on the first step."""
        return self.current_step > 0


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
