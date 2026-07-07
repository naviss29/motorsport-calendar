"""Tests for gui.upcoming_weekend — pure logic, no Flet, no HTTP.

Covers exactly what Sprint 29 asked for: weekend found, no weekend found,
category sort order (Formula before Endurance), and chronological order.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from motorsport_calendar.gui import upcoming_weekend as uw
from motorsport_calendar.gui.upcoming_weekend import WeekendEntry
from motorsport_calendar.models import (
    Championship,
    ChampionshipCategory,
    Circuit,
    Event,
    Session,
    SessionType,
)


def _session(session_type: SessionType, start: datetime, *, minutes: int = 60) -> Session:
    return Session(
        type=session_type,
        start_datetime=start,
        end_datetime=start + timedelta(minutes=minutes),
        title=session_type.value,
    )


def _entry(
    championship_id: str,
    *,
    name: str = "Grand Prix",
    circuit_name: str | None = None,
    circuit_city: str | None = None,
    country: str = "France",
    timezone_name: str = "Europe/Paris",
    round_: int = 1,
    sessions: tuple[Session, ...] = (),
) -> WeekendEntry:
    """Build a WeekendEntry — mirrors what controller.get_upcoming_weekend
    produces: a registry championship id paired with a fetched Event whose
    own Championship.id is intentionally something else (year-suffixed, as
    real providers do), to guard against ever reading it by mistake.

    ``circuit_name``/``circuit_city`` default to *name* — matching most
    fixtures here, which don't care about event-metadata normalization
    (Sprint 32). Pass them explicitly to build a fixture with genuinely
    distinct circuit data (like real F1) or a duplicate one (like the real
    F2/F3 bug — see test_gui_event_display.py for that scenario in depth).
    """
    championship = Championship(
        id=f"{championship_id}-9999",
        name=championship_id,
        category=ChampionshipCategory.SINGLE_SEATER,
    )
    circuit = Circuit(
        id=name.lower().replace(" ", "-"),
        name=circuit_name if circuit_name is not None else name,
        city=circuit_city if circuit_city is not None else name,
        country=country,
        timezone=timezone_name,
    )
    event = Event(
        championship=championship,
        season=sessions[0].start_datetime.year if sessions else 2026,
        round=round_,
        name=name,
        circuit=circuit,
        sessions=sessions,
        event_uid=f"{championship_id}-{round_}@test",
    )
    return WeekendEntry(championship_id=championship_id, event=event)


# A Tuesday — the upcoming weekend is Friday 2026-07-10 to Sunday 2026-07-12.
NOW = datetime(2026, 7, 7, 12, 0, tzinfo=UTC)


class TestWeekendBoundsContainingOrAfter:
    def test_tuesday_maps_to_this_weeks_friday_sunday(self) -> None:
        friday, sunday = uw._weekend_bounds_containing_or_after(NOW.date())
        assert friday.isoformat() == "2026-07-10"
        assert sunday.isoformat() == "2026-07-12"

    def test_friday_itself_maps_to_the_same_weekend(self) -> None:
        friday, sunday = uw._weekend_bounds_containing_or_after(datetime(2026, 7, 10).date())
        assert friday.isoformat() == "2026-07-10"
        assert sunday.isoformat() == "2026-07-12"

    def test_sunday_itself_maps_to_the_same_weekend(self) -> None:
        friday, sunday = uw._weekend_bounds_containing_or_after(datetime(2026, 7, 12).date())
        assert friday.isoformat() == "2026-07-10"
        assert sunday.isoformat() == "2026-07-12"

    def test_monday_after_a_weekend_rolls_to_the_next_one(self) -> None:
        friday, sunday = uw._weekend_bounds_containing_or_after(datetime(2026, 7, 13).date())
        assert friday.isoformat() == "2026-07-17"
        assert sunday.isoformat() == "2026-07-19"


class TestWeekendFound:
    def test_event_this_weekend_is_found(self) -> None:
        entry = _entry(
            "formula1",
            sessions=(_session(SessionType.RACE, datetime(2026, 7, 12, 13, 0, tzinfo=UTC)),),
        )
        result = uw.find_upcoming_weekend([entry], now=NOW)
        assert result.found is True
        assert result.friday.isoformat() == "2026-07-10"
        assert result.sunday.isoformat() == "2026-07-12"
        assert len(result.cards) == 1

    def test_event_next_month_is_not_this_weekend_but_is_eventually_found(self) -> None:
        entry = _entry(
            "formula1",
            sessions=(_session(SessionType.RACE, datetime(2026, 8, 15, 13, 0, tzinfo=UTC)),),
        )
        result = uw.find_upcoming_weekend([entry], now=NOW)
        assert result.found is True
        assert result.friday.isoformat() == "2026-08-14"
        assert result.sunday.isoformat() == "2026-08-16"

    def test_event_last_week_is_ignored(self) -> None:
        """A session strictly in the past must not resurface as "found"."""
        entry = _entry(
            "formula1",
            sessions=(_session(SessionType.RACE, datetime(2026, 6, 28, 13, 0, tzinfo=UTC)),),
        )
        result = uw.find_upcoming_weekend([entry], now=NOW)
        assert result.found is False

    def test_card_exposes_display_ready_fields(self) -> None:
        """A "real F1"-shaped fixture: event name already complete, and a
        circuit name genuinely distinct from it — the happy path where
        every line is shown as provided (no normalization surprises)."""
        entry = _entry(
            "formula1",
            name="Japanese Grand Prix",
            circuit_name="Suzuka Circuit",
            country="Japan",
            timezone_name="Asia/Tokyo",
            sessions=(
                _session(SessionType.FP1, datetime(2026, 7, 10, 1, 30, tzinfo=UTC)),
                _session(SessionType.QUALIFYING, datetime(2026, 7, 11, 6, 0, tzinfo=UTC)),
                _session(SessionType.RACE, datetime(2026, 7, 12, 5, 0, tzinfo=UTC)),
            ),
        )
        result = uw.find_upcoming_weekend([entry], now=NOW)
        card = result.cards[0]
        assert card.championship_id == "formula1"
        assert card.championship_name == "Formula 1"
        assert card.event_name == "Japanese Grand Prix"
        assert card.circuit_name == "Suzuka Circuit"
        assert card.country == "🇯🇵 Japon"
        assert [row.label for row in card.sessions] == [
            "Essais Libres 1",
            "Qualifications",
            "Course",
        ]
        assert card.sessions[0].day_time == "Vendredi 10:30"
        assert card.sessions[1].day_time == "Samedi 15:00"
        assert card.sessions[2].day_time == "Dimanche 14:00"

    def test_f2_style_duplicate_and_unknown_country_are_normalized(self) -> None:
        """Sprint 32: reproduces the real F2/F3 bug end to end — a bare
        round name reused for both the event and circuit, and an unmapped
        country — and confirms find_upcoming_weekend's cards never show
        "Belgian" twice or the literal "Unknown"."""
        entry = _entry(
            "formula2",
            name="Belgian",
            circuit_name="Belgian",
            circuit_city="Spa-Francorchamps",
            country="Unknown",
            sessions=(_session(SessionType.RACE, datetime(2026, 7, 12, 13, 0, tzinfo=UTC)),),
        )
        result = uw.find_upcoming_weekend([entry], now=NOW)
        card = result.cards[0]
        assert card.event_name == "Belgian Grand Prix"
        assert card.circuit_name == "Spa-Francorchamps"
        assert card.country is None

    def test_championship_id_comes_from_the_entry_not_the_event(self) -> None:
        """Regression guard: Event.championship.id is year-suffixed
        provider-internal data (e.g. "formula1-2026") — the card must use
        the registry id carried by WeekendEntry instead."""
        entry = _entry(
            "formula1",
            sessions=(_session(SessionType.RACE, datetime(2026, 7, 12, 13, 0, tzinfo=UTC)),),
        )
        assert entry.event.championship.id != "formula1"
        result = uw.find_upcoming_weekend([entry], now=NOW)
        assert result.cards[0].championship_id == "formula1"


class TestNoWeekendFound:
    def test_no_events_at_all(self) -> None:
        result = uw.find_upcoming_weekend([], now=NOW)
        assert result.found is False
        assert result.cards == ()
        assert result.next_hint_date is None

    def test_only_past_sessions(self) -> None:
        entry = _entry(
            "formula1",
            sessions=(_session(SessionType.RACE, datetime(2026, 1, 1, 13, 0, tzinfo=UTC)),),
        )
        result = uw.find_upcoming_weekend([entry], now=NOW)
        assert result.found is False
        assert result.next_hint_date is None

    def test_beyond_search_horizon_still_reports_a_hint_date(self) -> None:
        far_future = _entry(
            "formula1",
            sessions=(_session(SessionType.RACE, datetime(2030, 1, 4, 13, 0, tzinfo=UTC)),),
        )
        result = uw.find_upcoming_weekend([far_future], now=NOW, max_weeks_ahead=1)
        assert result.found is False
        assert result.next_hint_date.isoformat() == "2030-01-04"

    def test_find_next_weekend_entries_returns_none(self) -> None:
        assert uw.find_next_weekend_entries([], now=NOW) is None


class TestCategorySortOrder:
    """Formula must always come before Endurance."""

    def test_wec_and_formula1_same_weekend_formula_first(self) -> None:
        f1 = _entry(
            "formula1",
            round_=1,
            sessions=(_session(SessionType.RACE, datetime(2026, 7, 12, 13, 0, tzinfo=UTC)),),
        )
        wec = _entry(
            "wec",
            round_=1,
            sessions=(_session(SessionType.RACE, datetime(2026, 7, 11, 8, 0, tzinfo=UTC)),),
        )
        # WEC's session is chronologically EARLIER than F1's, but the
        # category order (Formula, then Endurance) must still win.
        result = uw.find_upcoming_weekend([wec, f1], now=NOW)
        assert [card.championship_id for card in result.cards] == ["formula1", "wec"]

    def test_multiple_formula_championships_before_endurance(self) -> None:
        f2 = _entry(
            "formula2",
            round_=1,
            sessions=(_session(SessionType.RACE, datetime(2026, 7, 12, 9, 0, tzinfo=UTC)),),
        )
        wec = _entry(
            "wec",
            round_=1,
            sessions=(_session(SessionType.RACE, datetime(2026, 7, 10, 8, 0, tzinfo=UTC)),),
        )
        f1 = _entry(
            "formula1",
            round_=1,
            sessions=(_session(SessionType.RACE, datetime(2026, 7, 12, 13, 0, tzinfo=UTC)),),
        )
        result = uw.find_upcoming_weekend([wec, f2, f1], now=NOW)
        ids = [card.championship_id for card in result.cards]
        assert ids.index("formula2") < ids.index("wec")
        assert ids.index("formula1") < ids.index("wec")


class TestChronologicalOrderWithinCategory:
    def test_earliest_race_first_within_formula_group(self) -> None:
        f1 = _entry(
            "formula1",
            round_=1,
            sessions=(_session(SessionType.RACE, datetime(2026, 7, 12, 13, 0, tzinfo=UTC)),),
        )
        f2 = _entry(
            "formula2",
            round_=1,
            sessions=(_session(SessionType.RACE, datetime(2026, 7, 11, 9, 0, tzinfo=UTC)),),
        )
        # F2's earliest session is before F1's — F2 must be listed first.
        result = uw.find_upcoming_weekend([f1, f2], now=NOW)
        ids = [card.championship_id for card in result.cards]
        assert ids == ["formula2", "formula1"]

    def test_sessions_within_a_card_are_chronological(self) -> None:
        entry = _entry(
            "formula1",
            sessions=(
                _session(SessionType.RACE, datetime(2026, 7, 12, 13, 0, tzinfo=UTC)),
                _session(SessionType.FP1, datetime(2026, 7, 10, 10, 0, tzinfo=UTC)),
                _session(SessionType.QUALIFYING, datetime(2026, 7, 11, 13, 0, tzinfo=UTC)),
            ),
        )
        result = uw.find_upcoming_weekend([entry], now=NOW)
        labels = [row.label for row in result.cards[0].sessions]
        assert labels == ["Essais Libres 1", "Qualifications", "Course"]


class TestInvalidCircuitTimezone:
    def test_falls_back_to_utc_instead_of_raising(self) -> None:
        entry = _entry(
            "formula1",
            timezone_name="Not/A_Real_Zone",
            sessions=(_session(SessionType.RACE, datetime(2026, 7, 12, 13, 0, tzinfo=UTC)),),
        )
        result = uw.find_upcoming_weekend([entry], now=NOW)
        assert result.found is True
        assert result.cards[0].sessions[0].day_time == "Dimanche 13:00"


class TestWeekendChampionshipIds:
    def test_exactly_the_five_specified_championships(self) -> None:
        assert uw.WEEKEND_CHAMPIONSHIP_IDS == (
            "formula1",
            "formula2",
            "formula3",
            "f1-academy",
            "wec",
        )
