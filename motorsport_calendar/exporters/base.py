"""Abstract base class for calendar exporters."""

from abc import ABC, abstractmethod
from pathlib import Path

from motorsport_calendar.models import Championship


class Exporter(ABC):
    """Converts a Championship to a specific calendar file format.

    Implement this class to add a new output format (e.g. ICS, JSON, CSV).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique exporter slug (e.g. 'ics', 'json')."""
        ...

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension without leading dot (e.g. 'ics', 'json')."""
        ...

    @abstractmethod
    def export(self, championship: Championship, output: Path) -> None:
        """Export a championship calendar to a file.

        Args:
            championship: The championship to export.
            output: Destination file path.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
            OSError: On file write failures.
        """
        ...

    @abstractmethod
    def export_to_string(self, championship: Championship) -> str:
        """Export a championship calendar to a string.

        Useful for testing or streaming without writing to disk.

        Args:
            championship: The championship to export.

        Returns:
            The serialized calendar as a string.
        """
        ...
