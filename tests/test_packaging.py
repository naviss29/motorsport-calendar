"""Packaging integrity tests.

Verify that the installed package is correctly wired:
- importlib.metadata version matches __version__
- __main__.py entry point works (python -m motorsport_calendar)
- All CLI commands are registered in the Typer app
- Key public API imports succeed
- Providers and sources auto-register correctly
"""

from __future__ import annotations

import importlib
import importlib.metadata
import subprocess
import sys

import pytest
from typer.testing import CliRunner

from motorsport_calendar import __version__
from motorsport_calendar.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Package metadata
# ---------------------------------------------------------------------------


class TestPackageMetadata:
    def test_version_is_defined(self) -> None:
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_matches_metadata(self) -> None:
        metadata_version = importlib.metadata.version("motorsport-calendar")
        assert __version__ == metadata_version

    def test_version_is_semver(self) -> None:
        parts = __version__.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_package_importable(self) -> None:
        mod = importlib.import_module("motorsport_calendar")
        assert mod is not None

    def test_author_defined(self) -> None:
        from motorsport_calendar import __author__
        assert __author__


# ---------------------------------------------------------------------------
# Entry point — python -m motorsport_calendar
# ---------------------------------------------------------------------------


class TestMainEntryPoint:
    def test_python_m_help_exits_zero(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "motorsport_calendar", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0

    def test_python_m_help_shows_usage(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "motorsport_calendar", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert "usage" in result.stdout.lower() or "motocal" in result.stdout.lower()

    def test_python_m_version_exits_zero(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "motorsport_calendar", "version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0

    def test_python_m_version_shows_version(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "motorsport_calendar", "version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert __version__ in result.stdout

    def test_python_m_providers_exits_zero(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "motorsport_calendar", "providers"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# CLI commands registered
# ---------------------------------------------------------------------------


class TestCLICommands:
    def test_help_shows_generate_f1(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert "generate-f1" in result.output

    def test_help_shows_generate_f2(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert "generate-f2" in result.output

    def test_help_shows_generate_f3(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert "generate-f3" in result.output

    def test_help_shows_generate_f1_academy(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert "generate-f1-academy" in result.output

    def test_help_shows_generate_wec(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert "generate-wec" in result.output

    def test_help_shows_generate(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert "generate" in result.output

    def test_help_shows_providers(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert "providers" in result.output

    def test_help_shows_version(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert "version" in result.output

    def test_version_command_output_contains_version(self) -> None:
        result = runner.invoke(app, ["version"])
        assert __version__ in result.output
        assert result.exit_code == 0

    def test_providers_command_lists_formula1(self) -> None:
        result = runner.invoke(app, ["providers"])
        assert "formula1" in result.output
        assert result.exit_code == 0

    def test_providers_command_lists_formula2(self) -> None:
        result = runner.invoke(app, ["providers"])
        assert "formula2" in result.output

    def test_providers_command_lists_formula3(self) -> None:
        result = runner.invoke(app, ["providers"])
        assert "formula3" in result.output

    def test_providers_command_lists_f1_academy(self) -> None:
        result = runner.invoke(app, ["providers"])
        assert "f1-academy" in result.output

    def test_providers_command_lists_wec(self) -> None:
        result = runner.invoke(app, ["providers"])
        assert "wec" in result.output


# ---------------------------------------------------------------------------
# Public API imports
# ---------------------------------------------------------------------------


class TestPublicImports:
    def test_models_importable(self) -> None:
        from motorsport_calendar.models import (
            Championship,
            ChampionshipCategory,
            Circuit,
            Event,
            Session,
            SessionType,
        )
        assert Championship is not None
        assert ChampionshipCategory is not None
        assert Circuit is not None
        assert Event is not None
        assert Session is not None
        assert SessionType is not None

    def test_datasource_importable(self) -> None:
        from motorsport_calendar.core.datasource import (
            DataSource,
            HtmlDataSource,
            IcsDataSource,
            JsonDataSource,
        )
        assert DataSource is not None
        assert JsonDataSource is not None
        assert HtmlDataSource is not None
        assert IcsDataSource is not None

    def test_registry_importable(self) -> None:
        from motorsport_calendar.core import registry, source_registry
        assert registry is not None
        assert source_registry is not None

    def test_formula1_provider_importable(self) -> None:
        from motorsport_calendar.providers.formula1 import Formula1Provider, Formula1Source
        assert Formula1Provider is not None
        assert Formula1Source is not None

    def test_formula2_provider_importable(self) -> None:
        from motorsport_calendar.providers.formula2 import Formula2Provider, Formula2Source
        assert Formula2Provider is not None
        assert Formula2Source is not None

    def test_formula3_provider_importable(self) -> None:
        from motorsport_calendar.providers.formula3 import Formula3Provider, Formula3Source
        assert Formula3Provider is not None
        assert Formula3Source is not None

    def test_f1_academy_provider_importable(self) -> None:
        from motorsport_calendar.providers.f1_academy import F1AcademyProvider, F1AcademySource
        assert F1AcademyProvider is not None
        assert F1AcademySource is not None

    def test_support_series_base_importable(self) -> None:
        from motorsport_calendar.providers.support_series.f1calendar_base import F1CalendarBaseSource
        assert F1CalendarBaseSource is not None

    def test_wec_provider_importable(self) -> None:
        from motorsport_calendar.providers.wec import WecProvider, WecSource
        assert WecProvider is not None
        assert WecSource is not None

    def test_ics_exporter_importable(self) -> None:
        from motorsport_calendar.exporters.ics import IcsExporter
        assert IcsExporter is not None

    def test_http_cache_importable(self) -> None:
        from motorsport_calendar.cache import HttpCache
        assert HttpCache is not None

    def test_config_service_importable(self) -> None:
        from motorsport_calendar.config import ConfigService
        assert ConfigService is not None


# ---------------------------------------------------------------------------
# Registry auto-discovery
# ---------------------------------------------------------------------------


class TestRegistryDiscovery:
    """Tests use the application singletons — discover() populates the shared registry."""

    def test_discover_registers_formula1(self) -> None:
        from motorsport_calendar.core.registry import registry
        registry.discover()
        assert "formula1" in registry.list_all()

    def test_discover_registers_formula2(self) -> None:
        from motorsport_calendar.core.registry import registry
        registry.discover()
        assert "formula2" in registry.list_all()

    def test_discover_registers_formula3(self) -> None:
        from motorsport_calendar.core.registry import registry
        registry.discover()
        assert "formula3" in registry.list_all()

    def test_discover_registers_f1_academy(self) -> None:
        from motorsport_calendar.core.registry import registry
        registry.discover()
        assert "f1-academy" in registry.list_all()

    def test_discover_registers_wec(self) -> None:
        from motorsport_calendar.core.registry import registry
        registry.discover()
        assert "wec" in registry.list_all()

    def test_source_discover_registers_openf1(self) -> None:
        from motorsport_calendar.core.source_registry import source_registry
        source_registry.discover()
        assert "openf1" in source_registry.list_for("formula1")

    def test_source_discover_registers_jolpica(self) -> None:
        from motorsport_calendar.core.source_registry import source_registry
        source_registry.discover()
        assert "jolpica" in source_registry.list_for("formula1")

    def test_source_discover_registers_f1calendar_formula2(self) -> None:
        from motorsport_calendar.core.source_registry import source_registry
        source_registry.discover()
        assert "f1calendar" in source_registry.list_for("formula2")

    def test_source_discover_registers_f1calendar_formula3(self) -> None:
        from motorsport_calendar.core.source_registry import source_registry
        source_registry.discover()
        assert "f1calendar" in source_registry.list_for("formula3")

    def test_source_discover_registers_f1calendar_f1_academy(self) -> None:
        from motorsport_calendar.core.source_registry import source_registry
        source_registry.discover()
        assert "f1calendar" in source_registry.list_for("f1-academy")
