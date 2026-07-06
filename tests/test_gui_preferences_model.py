"""Tests for PreferencesModel."""

from __future__ import annotations

import pytest

from motorsport_calendar.gui.models import PreferencesModel


class TestPreferencesModelDefaults:
    def test_default_language(self):
        assert PreferencesModel().language == "fr"

    def test_default_timezone(self):
        assert PreferencesModel().timezone == "Europe/Paris"

    def test_default_first_day_of_week(self):
        assert PreferencesModel().first_day_of_week == 1

    def test_default_favorite_championships_is_empty_tuple(self):
        model = PreferencesModel()
        assert model.favorite_championships == ()
        assert isinstance(model.favorite_championships, tuple)

    def test_default_preferred_calendar(self):
        assert PreferencesModel().preferred_calendar == "google"

    def test_default_bapps_sync_disabled(self):
        assert PreferencesModel().bapps_sync_enabled is False


class TestPreferencesModelFrozen:
    def test_frozen_cannot_set_language(self):
        model = PreferencesModel()
        with pytest.raises((AttributeError, TypeError)):
            model.language = "en"  # type: ignore[misc]

    def test_frozen_cannot_set_timezone(self):
        model = PreferencesModel()
        with pytest.raises((AttributeError, TypeError)):
            model.timezone = "America/New_York"  # type: ignore[misc]

    def test_frozen_cannot_set_bapps_sync(self):
        model = PreferencesModel()
        with pytest.raises((AttributeError, TypeError)):
            model.bapps_sync_enabled = True  # type: ignore[misc]


class TestPreferencesModelCustomValues:
    def test_custom_language(self):
        model = PreferencesModel(language="en")
        assert model.language == "en"

    def test_custom_timezone(self):
        model = PreferencesModel(timezone="America/New_York")
        assert model.timezone == "America/New_York"

    def test_custom_first_day_sunday(self):
        model = PreferencesModel(first_day_of_week=0)
        assert model.first_day_of_week == 0

    def test_custom_favorite_championships(self):
        model = PreferencesModel(favorite_championships=("formula1", "wec"))
        assert model.favorite_championships == ("formula1", "wec")

    def test_custom_preferred_calendar(self):
        model = PreferencesModel(preferred_calendar="apple")
        assert model.preferred_calendar == "apple"

    def test_bapps_sync_enabled(self):
        model = PreferencesModel(bapps_sync_enabled=True)
        assert model.bapps_sync_enabled is True


class TestPreferencesModelEquality:
    def test_two_defaults_are_equal(self):
        assert PreferencesModel() == PreferencesModel()

    def test_different_language_not_equal(self):
        assert PreferencesModel(language="fr") != PreferencesModel(language="en")

    def test_different_timezone_not_equal(self):
        a = PreferencesModel(timezone="Europe/Paris")
        b = PreferencesModel(timezone="America/New_York")
        assert a != b


class TestPreferencesModelTypes:
    def test_favorite_championships_is_tuple_not_list(self):
        model = PreferencesModel(favorite_championships=("formula1",))
        assert isinstance(model.favorite_championships, tuple)

    def test_first_day_is_int(self):
        assert isinstance(PreferencesModel().first_day_of_week, int)

    def test_bapps_sync_is_bool(self):
        assert isinstance(PreferencesModel().bapps_sync_enabled, bool)
