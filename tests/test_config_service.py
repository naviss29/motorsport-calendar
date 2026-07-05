"""Tests pour les modèles de configuration et ConfigService."""

from __future__ import annotations

from pathlib import Path

import pytest

from motorsport_calendar.config import (
    AppConfig,
    CacheConfig,
    ConfigService,
    IcsConfig,
    ProviderConfig,
    ProvidersConfig,
)


# ---------------------------------------------------------------------------
# Modèles — valeurs par défaut
# ---------------------------------------------------------------------------


class TestAppConfigDefaults:
    def test_default_timezone(self) -> None:
        assert AppConfig().timezone == "Europe/Paris"

    def test_default_cache_enabled(self) -> None:
        assert AppConfig().cache.enabled is True

    def test_default_cache_ttl_hours(self) -> None:
        assert AppConfig().cache.ttl_hours == 24

    def test_default_cache_path_contains_cache_dir(self) -> None:
        path = str(AppConfig().cache.path)
        assert ".cache" in path and "motorsport-calendar" in path

    def test_default_ics_alarm_minutes(self) -> None:
        assert AppConfig().ics.alarm_minutes == 30

    def test_default_f1_source_is_openf1(self) -> None:
        assert AppConfig().providers.formula1.source == "openf1"

    def test_default_wec_source_is_official(self) -> None:
        assert AppConfig().providers.wec.source == "official"


class TestCacheConfigProperties:
    def test_ttl_seconds_converts_hours(self) -> None:
        cache = CacheConfig(ttl_hours=24)
        assert cache.ttl_seconds == 86400

    def test_ttl_seconds_custom(self) -> None:
        cache = CacheConfig(ttl_hours=1)
        assert cache.ttl_seconds == 3600

    def test_resolved_path_expands_tilde(self) -> None:
        cache = CacheConfig(path=Path("~/.cache/test"))
        resolved = cache.resolved_path
        assert "~" not in str(resolved)
        assert resolved.is_absolute()

    def test_resolved_path_absolute_unchanged(self, tmp_path: Path) -> None:
        cache = CacheConfig(path=tmp_path)
        assert cache.resolved_path == tmp_path


class TestCacheConfigValidation:
    def test_ttl_hours_minimum_is_1(self) -> None:
        with pytest.raises(Exception):
            CacheConfig(ttl_hours=0)

    def test_alarm_minutes_minimum_is_0(self) -> None:
        IcsConfig(alarm_minutes=0)  # doit passer sans exception

    def test_alarm_minutes_negative_raises(self) -> None:
        with pytest.raises(Exception):
            IcsConfig(alarm_minutes=-1)


class TestProvidersConfigDefaults:
    def test_formula1_and_wec_have_independent_defaults(self) -> None:
        config = ProvidersConfig()
        assert config.formula1.source != config.wec.source


# ---------------------------------------------------------------------------
# ConfigService — pas de fichier
# ---------------------------------------------------------------------------


class TestConfigServiceNoFile:
    def test_returns_defaults_when_file_missing(self, tmp_path: Path) -> None:
        svc = ConfigService(config_path=tmp_path / "nonexistent.yaml")
        assert svc.config == AppConfig()

    def test_timezone_is_paris_by_default(self, tmp_path: Path) -> None:
        svc = ConfigService(config_path=tmp_path / "nonexistent.yaml")
        assert svc.timezone == "Europe/Paris"

    def test_cache_enabled_by_default(self, tmp_path: Path) -> None:
        svc = ConfigService(config_path=tmp_path / "nonexistent.yaml")
        assert svc.cache.enabled is True

    def test_alarm_minutes_30_by_default(self, tmp_path: Path) -> None:
        svc = ConfigService(config_path=tmp_path / "nonexistent.yaml")
        assert svc.ics.alarm_minutes == 30


# ---------------------------------------------------------------------------
# ConfigService — lecture YAML
# ---------------------------------------------------------------------------


class TestConfigServiceYaml:
    def test_reads_timezone(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text("timezone: America/New_York\n", encoding="utf-8")
        svc = ConfigService(config_path=cfg)
        assert svc.timezone == "America/New_York"

    def test_reads_cache_enabled_false(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text("cache:\n  enabled: false\n", encoding="utf-8")
        svc = ConfigService(config_path=cfg)
        assert svc.cache.enabled is False

    def test_reads_cache_ttl_hours(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text("cache:\n  ttl_hours: 48\n", encoding="utf-8")
        svc = ConfigService(config_path=cfg)
        assert svc.cache.ttl_hours == 48

    def test_reads_cache_path(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text(f"cache:\n  path: {tmp_path}\n", encoding="utf-8")
        svc = ConfigService(config_path=cfg)
        assert svc.cache.path == tmp_path

    def test_reads_ics_alarm_minutes(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text("ics:\n  alarm_minutes: 15\n", encoding="utf-8")
        svc = ConfigService(config_path=cfg)
        assert svc.ics.alarm_minutes == 15

    def test_reads_f1_source(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text(
            "providers:\n  formula1:\n    source: ergast\n", encoding="utf-8"
        )
        svc = ConfigService(config_path=cfg)
        assert svc.providers.formula1.source == "ergast"

    def test_reads_wec_source(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text(
            "providers:\n  wec:\n    source: custom\n", encoding="utf-8"
        )
        svc = ConfigService(config_path=cfg)
        assert svc.providers.wec.source == "custom"

    def test_reads_full_config(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text(
            "timezone: Asia/Tokyo\n"
            "cache:\n  enabled: true\n  ttl_hours: 12\n"
            "ics:\n  alarm_minutes: 60\n"
            "providers:\n  formula1:\n    source: openf1\n  wec:\n    source: official\n",
            encoding="utf-8",
        )
        svc = ConfigService(config_path=cfg)
        assert svc.timezone == "Asia/Tokyo"
        assert svc.cache.ttl_hours == 12
        assert svc.ics.alarm_minutes == 60
        assert svc.providers.formula1.source == "openf1"


# ---------------------------------------------------------------------------
# ConfigService — fusion avec les défauts (YAML partiel)
# ---------------------------------------------------------------------------


class TestConfigServicePartialYaml:
    def test_partial_cache_uses_defaults_for_missing_fields(
        self, tmp_path: Path
    ) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text("cache:\n  ttl_hours: 48\n", encoding="utf-8")
        svc = ConfigService(config_path=cfg)
        assert svc.cache.ttl_hours == 48
        assert svc.cache.enabled is True  # défaut préservé

    def test_partial_providers_uses_defaults_for_missing_provider(
        self, tmp_path: Path
    ) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text(
            "providers:\n  formula1:\n    source: ergast\n", encoding="utf-8"
        )
        svc = ConfigService(config_path=cfg)
        assert svc.providers.formula1.source == "ergast"
        assert svc.providers.wec.source == "official"  # défaut préservé

    def test_empty_yaml_uses_all_defaults(self, tmp_path: Path) -> None:
        cfg = tmp_path / "config.yaml"
        cfg.write_text("", encoding="utf-8")
        svc = ConfigService(config_path=cfg)
        assert svc.config == AppConfig()
