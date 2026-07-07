"""Tests for GUI state models — no Flet dependency."""

from __future__ import annotations

from datetime import date

import pytest

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


class TestGenerateStateWizard:
    def test_default_step_is_zero(self) -> None:
        assert GenerateState().current_step == 0

    def test_step_count_is_four(self) -> None:
        assert GenerateState.STEP_COUNT == 4

    def test_step_zero_always_valid(self) -> None:
        assert GenerateState().step_valid(0)

    def test_step_one_invalid_without_championships(self) -> None:
        assert not GenerateState().step_valid(1)

    def test_step_one_valid_with_championships(self) -> None:
        state = GenerateState(selected_championships=["formula1"])
        assert state.step_valid(1)

    def test_step_two_invalid_without_output_path(self) -> None:
        assert not GenerateState().step_valid(2)

    def test_step_two_valid_with_output_path(self) -> None:
        state = GenerateState(output_path="/tmp/out.ics")
        assert state.step_valid(2)

    def test_step_three_mirrors_is_ready(self) -> None:
        state = GenerateState(
            selected_championships=["formula1"],
            output_path="/tmp/out.ics",
        )
        assert state.step_valid(3) == state.is_ready()

    def test_unknown_step_raises(self) -> None:
        with pytest.raises(ValueError):
            GenerateState().step_valid(4)

    def test_can_go_back_false_on_first_step(self) -> None:
        assert not GenerateState(current_step=0).can_go_back()

    def test_can_go_back_true_after_first_step(self) -> None:
        assert GenerateState(current_step=1).can_go_back()

    def test_can_advance_false_when_current_step_invalid(self) -> None:
        state = GenerateState(current_step=1)  # no championships selected
        assert not state.can_advance()

    def test_can_advance_true_when_current_step_valid(self) -> None:
        state = GenerateState(current_step=1, selected_championships=["formula1"])
        assert state.can_advance()

    def test_can_advance_false_on_last_step_even_if_valid(self) -> None:
        state = GenerateState(
            current_step=3,
            selected_championships=["formula1"],
            output_path="/tmp/out.ics",
        )
        assert not state.can_advance()
