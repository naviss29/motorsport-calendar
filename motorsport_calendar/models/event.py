"""Event model — a race weekend (round) within a championship season."""

from pydantic import BaseModel, ConfigDict, Field

from .championship import Championship
from .circuit import Circuit
from .session import Session


class Event(BaseModel):
    """A race weekend: one round of a championship, at a circuit, with its sessions."""

    model_config = ConfigDict(frozen=True)

    championship: Championship
    season: int = Field(ge=1950, le=2100)
    round: int = Field(ge=1)
    name: str
    circuit: Circuit
    sessions: tuple[Session, ...] = ()
