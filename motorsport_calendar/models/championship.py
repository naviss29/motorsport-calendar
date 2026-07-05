"""Championship model."""

from pydantic import BaseModel, Field

from .event import Event


class Championship(BaseModel):
    """A motorsport championship season."""

    id: str = Field(description="Unique identifier (e.g. 'f1-2025')")
    name: str = Field(description="Full championship name")
    short_name: str | None = Field(default=None, description="Abbreviated name (e.g. 'F1')")
    year: int = Field(description="Season year", ge=1950, le=2100)
    sport: str = Field(description="Sport slug (e.g. 'formula1', 'motogp', 'wec')")
    events: list[Event] = Field(default_factory=list, description="All sessions in this season")
    url: str | None = Field(default=None, description="Official championship URL")
