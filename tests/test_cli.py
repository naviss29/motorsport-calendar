"""Tests for the CLI entry point."""

from typer.testing import CliRunner

from motorsport_calendar import __version__
from motorsport_calendar.cli import app

runner = CliRunner()


class TestHelp:
    def test_help_exits_zero(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0

    def test_help_contains_app_name(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert "motocal" in result.output or "motorsport" in result.output.lower()


class TestVersion:
    def test_version_command(self) -> None:
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_version_flag(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output


class TestProviders:
    def test_providers_command_exits_zero(self) -> None:
        result = runner.invoke(app, ["providers"])
        assert result.exit_code == 0


class TestExport:
    def test_export_without_providers_exits_one(self) -> None:
        result = runner.invoke(
            app,
            ["export", "--provider", "ergast", "--championship", "formula1", "--year", "2025"],
        )
        assert result.exit_code == 1

    def test_export_missing_required_options(self) -> None:
        result = runner.invoke(app, ["export"])
        assert result.exit_code != 0
