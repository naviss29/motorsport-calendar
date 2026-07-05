# motorsport-calendar

> Generate motorsport race calendars in ICS format — subscribe once, stay updated automatically.

[![CI](https://github.com/naviss29/motorsport-calendar/actions/workflows/ci.yml/badge.svg)](https://github.com/naviss29/motorsport-calendar/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

---

## Overview

**motorsport-calendar** fetches race calendars from public APIs and exports them as `.ics` files
you can subscribe to in Google Calendar, Apple Calendar, Outlook, or any iCalendar-compatible app.

```bash
# Generate a full 2026 Formula 1 calendar
motocal generate-f1 2026 f1-2026.ics

# Generate all enabled championships in one file
motocal generate 2026 motorsport-2026.ics
```

Import `motorsport-2026.ics` into your calendar app — every race, qualifying session, and
practice appears automatically with the correct local time.

---

## Features

- **ICS export** — one VEVENT per session, compatible with every major calendar app
- **Multi-championship** — Formula 1 and WEC today; more disciplines on the roadmap
- **Extensible architecture** — add a provider in four files, zero changes elsewhere
- **HTTP cache** — disk-based JSON cache with configurable TTL; skip with `--refresh`
- **YAML configuration** — sources, cache path, alarm reminders, opt-out per championship
- **CLI** — `motocal` powered by Typer + Rich, with coloured output and progress feedback

---

## Installation

### With uv (recommended)

```bash
uv tool install motorsport-calendar
```

### With pip

```bash
pip install motorsport-calendar
```

### From source

```bash
git clone https://github.com/naviss29/motorsport-calendar.git
cd motorsport-calendar
uv sync --all-extras
```

---

## Usage

### Formula 1

```bash
# 2026 season (cached by default)
motocal generate-f1 2026 f1-2026.ics

# Force re-download from the API
motocal generate-f1 2026 f1-2026.ics --refresh
```

### WEC — FIA World Endurance Championship

```bash
motocal generate-wec 2026 wec-2026.ics
```

> **Note:** The WEC source is not yet implemented. The command architecture is ready;
> the data source is on the roadmap (v0.2).

### All enabled championships

```bash
# Fetches every enabled provider and merges them into one ICS file
motocal generate 2026 motorsport-2026.ics
```

If one provider fails (network error, unimplemented source…), the others continue.
A per-provider summary is displayed:

```
Génération calendrier 2026 — 2 providers activés…
  ✓ formula1 : 24 événements
  ✗ wec : source non implémentée

Export terminé : motorsport-2026.ics (24 événements, 72 sessions)
```

### Other commands

```bash
# List all registered providers
motocal providers

# Show version
motocal version
```

---

## Configuration

Create `config.yaml` in your working directory (or `~/.config/motorsport-calendar/config.yaml`).
All keys are optional — sensible defaults apply when absent.

```yaml
# Timezone for display (IANA format)
timezone: Europe/Paris

cache:
  enabled: true
  path: ~/.cache/motorsport-calendar
  ttl_hours: 24        # re-download after 24 h

ics:
  alarm_minutes: 30    # VALARM reminder before each session (0 = disabled)

providers:
  formula1:
    enabled: true
    source: openf1     # openf1.org API — covers 2023 onwards
  wec:
    enabled: true
    source: official   # not yet implemented
  # Disable a future championship without touching any code:
  # f2:
  #   enabled: false
```

---

## Architecture

```
config.yaml
     │
     ▼ registry.enabled()
  ┌──────────┬──────────┐
  │Formula 1 │   WEC    │  …more (auto-discovered)
  │ Provider │ Provider │
  └────┬─────┴────┬─────┘
       │          │
  OpenF1      Official
  Source       Source
       │          │
       ▼          ▼
     Events     Events
        └────┬────┘
             ▼
       IcsExporter
             ▼
       calendar.ics
```

Each provider package **auto-registers** itself at import time via `ProviderRegistry`.
Each source auto-registers via `SourceRegistry`. The CLI calls `registry.discover()` once —
no hardcoded lists anywhere.

### Key concepts

| Concept | Role |
|---|---|
| `Provider` | Fetches data from one source and maps it to `list[Event]` |
| `Source` | Encapsulates the HTTP/scraping logic for one data endpoint |
| `ProviderRegistry` | Auto-discovers and holds all registered provider factories |
| `SourceRegistry` | Auto-discovers and holds all registered source factories |
| `IcsExporter` | Serialises a `list[Event]` to an RFC 5545 `.ics` file |
| `HttpCache` | Disk-based JSON cache keyed by SHA-256(url + params) |
| `ConfigService` | Reads `config.yaml` and merges with Pydantic defaults |

---

## Championships

| Championship | Status | Source | Availability |
|---|---|---|---|
| Formula 1 | ✅ Available | [openf1.org](https://openf1.org) | 2023 → present |
| WEC | 🟡 Architecture ready | fiawec.com (TODO) | v0.2 |
| ELMS | 🔴 Planned | TBD | v0.3 |
| Michelin Le Mans Cup | 🔴 Planned | TBD | v0.3 |
| Road to Le Mans | 🔴 Planned | TBD | v0.3 |
| Formula 2 | 🔴 Planned | TBD | v0.3 |
| Formula 3 | 🔴 Planned | TBD | v0.3 |
| F1 Academy | 🔴 Planned | TBD | v0.4 |

---

## Roadmap

| Version | Highlights |
|---|---|
| **v0.1** ✅ | Formula 1 via OpenF1, WEC architecture, multi-provider CLI, cache, config |
| **v0.2** | `ErgastSource` (F1 1950+), `OfficialWecSource`, VEVENT descriptions |
| **v0.3** | ELMS, Le Mans Cup, Road to Le Mans, Formula 2/3 providers |
| **v1.0** | PyPI release, MkDocs documentation, stable public API |

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the detailed per-version breakdown.

---

## Contribution

### Run the tests

```bash
# All tests with coverage
uv run pytest

# A specific file
uv run pytest tests/test_cli_generate.py -v

# Lint + type check
uv run ruff check motorsport_calendar tests
uv run mypy motorsport_calendar
```

### Add a provider

1. Create `motorsport_calendar/providers/mychampionship/`
2. Add `source.py` (abstract `Source` class) and `provider.py` (concrete `Provider`)
3. Add `sources/official.py` with the HTTP/scraping implementation
4. Register in `__init__.py`:

```python
# providers/mychampionship/__init__.py
from motorsport_calendar.core.registry import registry
from .provider import MyProvider

def _make_provider(source):
    return MyProvider(source)

registry.register("mychampionship", _make_provider)
```

5. Register the source in `sources/__init__.py`:

```python
# providers/mychampionship/sources/__init__.py
from motorsport_calendar.core.source_registry import source_registry
from .official import OfficialMySource

source_registry.register(
    "mychampionship", "official",
    lambda cache, refresh: OfficialMySource(cache=cache, refresh=refresh),
)
```

That's it — no other files to touch. `motocal generate` picks it up automatically.

### Commit conventions

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(cli): add generate-wec command
fix(openf1): handle missing date_end gracefully
docs(readme): update championship table
test(registry): add enabled() edge cases
```

---

## License

[MIT](LICENSE) © 2026 Alan Yvenou
