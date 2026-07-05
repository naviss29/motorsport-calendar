"""Event and SessionType models."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class SessionType(StrEnum):
    """Type of motorsport session."""

    PRACTICE_1 = "practice_1"
    PRACTICE_2 = "practice_2"
    PRACTICE_3 = "practice_3"
    QUALIFYING = "qualifying"
    SPRINT_SHOOTOUT = "sprint_shootout"
    SPRINT = "sprint"
    RACE = "race"
    WARM_UP = "warm_up"
    SUPERPOLE = "superpole"
    UNKNOWN = "unknown"


class Event(BaseModel):
    """A single motorsport session (race, qualifying, practice, etc.)."""

    id: str = Field(description="Unique identifier for this event")
    name: str = Field(description="Human-readable event name")
    session_type: SessionType = Field(description="Type of session")
    start_time: datetime = Field(description="Session start (timezone-aware)")
    end_time: datetime = Field(description="Session end (timezone-aware)")
    timezone: str = Field(description="IANA timezone identifier (e.g. 'Europe/Monaco')")
    round_number: int | None = Field(default=None, description="Round number in the season")
    championship_id: str | None = Field(default=None, description="Parent championship ID")
    circuit_id: str | None = Field(default=None, description="Circuit ID")
    url: str | None = Field(default=None, description="Official event URL")
    notes: str | None = Field(default=None, description="Additional notes or description")
