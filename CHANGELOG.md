# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.1.0] — 2026-07-05

Initial release. Formula 1 calendars are fully functional; WEC architecture is in place
pending a working data source.

### Added

#### Architecture
- **`ProviderRegistry`** — central registry with auto-discovery (`pkgutil.iter_modules`).
  Provider factories register themselves at import time; the CLI calls `registry.discover()`
  once and never hardcodes provider names.
- **`SourceRegistry`** — symmetric registry keyed by `(championship_id, source_name)`.
  Source factories auto-register in each `providers/X/sources/__init__.py`.
- **Opt-out configuration** — a provider absent from `config.yaml` is enabled by default;
  set `enabled: false` to exclude it.

#### Data models (Pydantic v2, `frozen=True`)
- `Championship` / `ChampionshipCategory` (SINGLE_SEATER, ENDURANCE, …)
- `Circuit` with IANA timezone
- `Session` / `SessionType` (RACE, QUALIFYING, FREE_PRACTICE, HYPERPOLE, …)
- `Event` / `EventStatus` with `event_uid`

#### Providers
- **Formula 1** — `Formula1Provider` + `OpenF1Source` (openf1.org API, 2023 onwards).
  Mapping covers 25 circuits with correct IANA timezones. Stubs: `ErgastSource`,
  `OfficialFormula1Source`, `CachedFormula1Source`.
- **WEC** — `WecProvider` + `OfficialWecSource` stub (architecture complete, HTTP not yet
  implemented).

#### Exporters
- **`IcsExporter`** — RFC 5545 compliant. One VEVENT per session. Configurable VALARM
  reminder via `alarm_minutes`. Supports `export()` (file) and `export_to_string()`.

#### Cache
- **`HttpCache`** — disk-based JSON cache. Key: SHA-256(url + sorted params). Configurable
  TTL (default 24 h). `--refresh` flag bypasses cache on demand.

#### Configuration
- **`ConfigService`** — reads `config.yaml` from CWD then `~/.config/motorsport-calendar/`.
  Falls back to Pydantic defaults when no file is found.
- **`config.example.yaml`** — fully commented reference configuration.

#### CLI (`motocal`)
- `generate-f1 YEAR OUTPUT.ics [--refresh]` — Formula 1 calendar via OpenF1.
- `generate-wec YEAR OUTPUT.ics [--refresh]` — WEC calendar (exits cleanly with a
  descriptive message while the source is unimplemented).
- `generate YEAR OUTPUT.ics [--refresh]` — fetches all enabled providers and merges them
  into a single ICS file. Per-provider resilience: if one fails, the others continue.
  Exit 0 if at least one provider succeeds.
- `providers` — lists all auto-discovered providers.
- `version` — shows the current version.

#### Tests & quality
- 306 tests — 0 failures — 92 % coverage.
- `pytest-asyncio` with `asyncio_mode = "auto"`.
- `ruff` + `mypy` + `pre-commit` hooks.
- GitHub Actions CI on Python 3.12 and 3.13.

[Unreleased]: https://github.com/naviss29/motorsport-calendar/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/naviss29/motorsport-calendar/releases/tag/v0.1.0
