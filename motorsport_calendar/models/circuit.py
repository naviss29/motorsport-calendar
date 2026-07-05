"""Circuit model."""

from pydantic import BaseModel, Field


class Circuit(BaseModel):
    """A motorsport circuit."""

    id: str = Field(description="Unique identifier for this circuit")
    name: str = Field(description="Full circuit name")
    short_name: str | None = Field(default=None, description="Abbreviated name")
    country: str = Field(description="Country (ISO 3166-1 alpha-2 or full name)")
    city: str | None = Field(default=None, description="Nearest city")
    timezone: str = Field(description="IANA timezone identifier (e.g. 'Europe/Monaco')")
    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)
    url: str | None = Field(default=None, description="Official circuit URL")
