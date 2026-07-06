"""GUI state — no business logic, no Flet dependency."""

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
