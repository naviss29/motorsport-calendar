"""Tests for GUI state models — no Flet dependency."""

from __future__ import annotations

from datetime import date

from motorsport_calendar.gui.models import GenerateState


class TestGenerateStateDefaults:
    def test_default_year_is_current(self) -> None:
        assert GenerateState().year == date.today().year

    def test_default_selection_is_empty(self) -> None:
        assert GenerateState().selected_championships == []

    def test_default_output_path_is_empty(self) -> None:
        assert GenerateState().output_path == ""

    def test_default_is_not_generating(self) -> None:
        assert GenerateState().is_generating is False

    def test_two_instances_share_no_list(self) -> None:
        a, b = GenerateState(), GenerateState()
        a.selected_championships.append("formula1")
        assert b.selected_championships == []


class TestGenerateStateIsReady:
    def test_not_ready_with_no_championships(self) -> None:
        state = GenerateState(output_path="/tmp/out.ics")
        assert not state.is_ready()

    def test_not_ready_with_no_output_path(self) -> None:
        state = GenerateState(selected_championships=["formula1"])
        assert not state.is_ready()

    def test_not_ready_when_generating(self) -> None:
        state = GenerateState(
            selected_championships=["formula1"],
            output_path="/tmp/out.ics",
            is_generating=True,
        )
        assert not state.is_ready()

    def test_ready_when_all_conditions_met(self) -> None:
        state = GenerateState(
            selected_championships=["formula1"],
            output_path="/tmp/out.ics",
        )
        assert state.is_ready()

    def test_ready_with_multiple_championships(self) -> None:
        state = GenerateState(
            selected_championships=["formula1", "formula2", "formula3"],
            output_path="/tmp/calendrier.ics",
        )
        assert state.is_ready()

    def test_becomes_not_ready_when_generating_starts(self) -> None:
        state = GenerateState(
            selected_championships=["formula1"],
            output_path="/tmp/out.ics",
        )
        assert state.is_ready()
        state.is_generating = True
        assert not state.is_ready()

    def test_becomes_ready_again_after_generation_ends(self) -> None:
        state = GenerateState(
            selected_championships=["formula1"],
            output_path="/tmp/out.ics",
            is_generating=True,
        )
        assert not state.is_ready()
        state.is_generating = False
        assert state.is_ready()
