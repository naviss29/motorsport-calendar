"""Tests pour WecProvider, WecSource et OfficialWecSource."""

from datetime import datetime, timezone

import pytest

from motorsport_calendar.models import (
    Championship,
    ChampionshipCategory,
    Circuit,
    Event,
    Session,
    SessionType,
)
from motorsport_calendar.providers.wec import WecProvider, WecSource
from motorsport_calendar.providers.wec.sources import OfficialWecSource

TZ = timezone.utc

# ---------------------------------------------------------------------------
# Test double — source en mémoire contrôlable
# ---------------------------------------------------------------------------


class FakeWecSource(WecSource):
    """WecSource minimal pour les tests unitaires."""

    def __init__(self, events: list[Event] | None = None) -> None:
        self._events = events or []
        self.last_year_requested: int | None = None

    async def get_season(self, year: int) -> list[Event]:
        self.last_year_requested = year
        return self._events


# ---------------------------------------------------------------------------
# Fixtures — événement WEC réaliste
# ---------------------------------------------------------------------------


@pytest.fixture
def wec_championship() -> Championship:
    return Championship(
        id="wec-2026",
        name="FIA World Endurance Championship",
        category=ChampionshipCategory.ENDURANCE,
    )


@pytest.fixture
def spa_circuit() -> Circuit:
    return Circuit(
        id="wec-spa",
        name="Spa-Francorchamps",
        city="Stavelot",
        country="Belgium",
        timezone="Europe/Brussels",
    )


@pytest.fixture
def wec_sessions() -> tuple[Session, ...]:
    return (
        Session(
            type=SessionType.FREE_PRACTICE,
            start_datetime=datetime(2026, 5, 7, 10, 0, tzinfo=TZ),
            end_datetime=datetime(2026, 5, 7, 13, 0, tzinfo=TZ),
            title="Free Practice",
        ),
        Session(
            type=SessionType.QUALIFYING,
            start_datetime=datetime(2026, 5, 8, 10, 0, tzinfo=TZ),
            end_datetime=datetime(2026, 5, 8, 11, 0, tzinfo=TZ),
            title="Qualifying",
        ),
        Session(
            type=SessionType.HYPERPOLE,
            start_datetime=datetime(2026, 5, 8, 14, 0, tzinfo=TZ),
            end_datetime=datetime(2026, 5, 8, 14, 30, tzinfo=TZ),
            title="Hyperpole",
        ),
        Session(
            type=SessionType.RACE,
            start_datetime=datetime(2026, 5, 9, 14, 0, tzinfo=TZ),
            end_datetime=datetime(2026, 5, 10, 14, 0, tzinfo=TZ),
            title="6 Hours of Spa-Francorchamps",
        ),
    )


@pytest.fixture
def spa_wec_event(
    wec_championship: Championship,
    spa_circuit: Circuit,
    wec_sessions: tuple[Session, ...],
) -> Event:
    return Event(
        championship=wec_championship,
        season=2026,
        round=1,
        name="6 Hours of Spa-Francorchamps",
        circuit=spa_circuit,
        sessions=wec_sessions,
        event_uid="wec-2026-01-spa@motorsport-calendar",
    )


# ---------------------------------------------------------------------------
# WecSource (abstract)
# ---------------------------------------------------------------------------


class TestWecSourceABC:
    def test_cannot_be_instantiated_directly(self) -> None:
        with pytest.raises(TypeError):
            WecSource()  # type: ignore[abstract]

    def test_concrete_subclass_can_be_instantiated(self) -> None:
        source = FakeWecSource()
        assert isinstance(source, WecSource)


# ---------------------------------------------------------------------------
# WecProvider — identité
# ---------------------------------------------------------------------------


class TestWecProviderIdentity:
    def test_name_is_wec(self) -> None:
        assert WecProvider(FakeWecSource()).name == "wec"

    def test_supported_championships_contains_wec(self) -> None:
        assert "wec" in WecProvider(FakeWecSource()).supported_championships

    def test_accepts_any_wec_source(self) -> None:
        for source in (FakeWecSource(), OfficialWecSource()):
            provider = WecProvider(source)
            assert provider.name == "wec"


# ---------------------------------------------------------------------------
# WecProvider — fetch_events
# ---------------------------------------------------------------------------


class TestFetchEvents:
    async def test_returns_events_from_source(self, spa_wec_event: Event) -> None:
        source = FakeWecSource([spa_wec_event])
        events = await WecProvider(source).fetch_events("wec", 2026)
        assert events == [spa_wec_event]

    async def test_returns_empty_list_when_source_is_empty(self) -> None:
        events = await WecProvider(FakeWecSource()).fetch_events("wec", 2026)
        assert events == []

    async def test_passes_year_to_source(self) -> None:
        source = FakeWecSource()
        await WecProvider(source).fetch_events("wec", 2026)
        assert source.last_year_requested == 2026

    async def test_does_not_mutate_source_output(self, spa_wec_event: Event) -> None:
        source = FakeWecSource([spa_wec_event])
        events = await WecProvider(source).fetch_events("wec", 2026)
        assert events is source._events


# ---------------------------------------------------------------------------
# WecProvider — fetch_championship
# ---------------------------------------------------------------------------


class TestFetchChampionship:
    async def test_returns_wec_championship(self) -> None:
        champ = await WecProvider(FakeWecSource()).fetch_championship("wec", 2026)
        assert champ.id == "wec-2026"
        assert champ.name == "FIA World Endurance Championship"
        assert champ.category == ChampionshipCategory.ENDURANCE

    async def test_id_contains_year(self) -> None:
        champ = await WecProvider(FakeWecSource()).fetch_championship("wec", 2024)
        assert "2024" in champ.id

    async def test_different_years_produce_different_ids(self) -> None:
        provider = WecProvider(FakeWecSource())
        c2025 = await provider.fetch_championship("wec", 2025)
        c2026 = await provider.fetch_championship("wec", 2026)
        assert c2025.id != c2026.id

    async def test_category_is_endurance(self) -> None:
        champ = await WecProvider(FakeWecSource()).fetch_championship("wec", 2026)
        assert champ.category == ChampionshipCategory.ENDURANCE


# ---------------------------------------------------------------------------
# SessionType — types WEC supportés
# ---------------------------------------------------------------------------


class TestWecSessionTypes:
    def test_free_practice_is_valid_session_type(self) -> None:
        assert SessionType.FREE_PRACTICE == "FREE_PRACTICE"

    def test_qualifying_is_valid_session_type(self) -> None:
        assert SessionType.QUALIFYING == "QUALIFYING"

    def test_hyperpole_is_valid_session_type(self) -> None:
        assert SessionType.HYPERPOLE == "HYPERPOLE"

    def test_race_is_valid_session_type(self) -> None:
        assert SessionType.RACE == "RACE"

    def test_wec_event_contains_all_four_session_types(
        self, wec_sessions: tuple[Session, ...]
    ) -> None:
        types = {s.type for s in wec_sessions}
        assert types == {
            SessionType.FREE_PRACTICE,
            SessionType.QUALIFYING,
            SessionType.HYPERPOLE,
            SessionType.RACE,
        }


# ---------------------------------------------------------------------------
# OfficialWecSource — stub
# ---------------------------------------------------------------------------


class TestOfficialWecSource:
    async def test_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            await OfficialWecSource().get_season(2026)

    def test_is_a_wec_source(self) -> None:
        assert isinstance(OfficialWecSource(), WecSource)


# ---------------------------------------------------------------------------
# Modèles — interopérabilité WEC / F1
# ---------------------------------------------------------------------------


class TestModelInteroperability:
    def test_wec_event_uses_standard_circuit_model(self, spa_wec_event: Event) -> None:
        assert isinstance(spa_wec_event.circuit, Circuit)

    def test_wec_event_uses_standard_championship_model(
        self, spa_wec_event: Event
    ) -> None:
        assert isinstance(spa_wec_event.championship, Championship)

    def test_wec_and_f1_events_share_the_same_event_class(
        self, spa_wec_event: Event, australian_gp: Event
    ) -> None:
        assert type(spa_wec_event) is type(australian_gp)

    def test_wec_event_is_frozen(self, spa_wec_event: Event) -> None:
        with pytest.raises(Exception):
            spa_wec_event.name = "modified"  # type: ignore[misc]
