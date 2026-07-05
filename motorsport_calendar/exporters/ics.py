"""ICS exporter — converts motorsport events to iCalendar (.ics) format."""

from collections.abc import Iterable
from pathlib import Path

from icalendar import Calendar
from icalendar import Event as ICalEvent

from motorsport_calendar.exporters.base import Exporter
from motorsport_calendar.models import Event

_PRODID = "-//Motorsport Calendar//motorsport-calendar//EN"


class IcsExporter(Exporter):
    """Exports a list of Events to RFC 5545 iCalendar format.

    Compatible with Google Calendar, Apple Calendar, and Outlook.
    One VEVENT is generated per Session inside each Event.
    """

    @property
    def name(self) -> str:
        return "ics"

    @property
    def file_extension(self) -> str:
        return "ics"

    def export(self, events: Iterable[Event], output_path: Path) -> None:
        output_path.write_bytes(self._build_calendar(events).to_ical())

    def export_to_string(self, events: Iterable[Event]) -> str:
        return self._build_calendar(events).to_ical().decode("utf-8")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_calendar(self, events: Iterable[Event]) -> Calendar:
        cal = Calendar()
        cal.add("prodid", _PRODID)
        cal.add("version", "2.0")
        cal.add("calscale", "GREGORIAN")
        # PUBLISH = read-only feed; required by several clients for correct import
        cal.add("method", "PUBLISH")

        for event in events:
            for session in event.sessions:
                vevent = ICalEvent()
                vevent.add("uid", f"{event.event_uid}-{session.type}")
                vevent.add("summary", session.title)
                if session.description:
                    vevent.add("description", session.description)
                vevent.add("dtstart", session.start_datetime)
                vevent.add("dtend", session.end_datetime)
                vevent.add("location", f"{event.circuit.name}, {event.circuit.country}")
                vevent.add("status", "CONFIRMED")
                cal.add_component(vevent)

        return cal
