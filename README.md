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
# Formula 1 — 2026 season
motocal generate-f1 2026 f1-2026.ics

# Formula 2 — 2026 season
motocal generate-f2 2026 f2-2026.ics

# All enabled championships in one file
motocal generate 2026 motorsport-2026.ics
```

Import the `.ics` file into your calendar app — every race, qualifying session, and
practice appears automatically with the correct local time.

---

## Features

- **ICS export** — one VEVENT per session, compatible with every major calendar app
- **Formula 1** — via [OpenF1](https://openf1.org) (2023+) or [Jolpica](https://jolpi.ca) (1950+)
- **Formula 2** — via [f1calendar open dataset](https://github.com/sportstimes/f1) (MIT)
- **Extensible architecture** — add a new series in a few files, zero changes elsewhere
- **HTTP cache** — disk-based JSON cache with configurable TTL; skip with `--refresh`
- **YAML configuration** — sources, cache path, alarm reminders, opt-out per championship
- **CLI** — `motocal` powered by Typer + Rich, with coloured output and progress feedback

---

## Installation

### With pip (recommended)

```bash
pip install motorsport-calendar
```

### With uv

```bash
uv tool install motorsport-calendar
```

### From source

```bash
git clone https://github.com/naviss29/motorsport-calendar.git
cd motorsport-calendar
uv sync --all-extras
```

---

## Running the CLI

After installation, the `motocal` command is available in your terminal:

```bash
motocal --help
```

> **Windows note:** If `motocal` is not found after `pip install`, your Python `Scripts`
> directory may not be in `PATH`. As a fallback, use:
> ```
> python -m motorsport_calendar --help
> ```
> To add the Scripts directory to PATH permanently, see
> [Python on Windows FAQ](https://docs.python.org/3/using/windows.html#finding-the-python-executable).

---

## Usage

### Formula 1

```bash
# 2026 season via OpenF1 (cached by default)
motocal generate-f1 2026 f1-2026.ics

# Force re-download from the API
motocal generate-f1 2026 f1-2026.ics --refresh

# Historical data (1950+) via Jolpica
# Set source: jolpica in config.yaml
motocal generate-f1 1994 f1-1994.ics
```

### Formula 2

```bash
# 2026 FIA Formula 2 season
motocal generate-f2 2026 f2-2026.ics

# Force re-download
motocal generate-f2 2026 f2-2026.ics --refresh
```

### WEC — FIA World Endurance Championship

```bash
motocal generate-wec 2026 wec-2026.ics
```

> **Note:** The WEC source is not yet implemented. The command architecture is ready;
> the data source is on the roadmap.

### All enabled championships

```bash
# Fetches every enabled provider and merges them into one ICS file
motocal generate 2026 motorsport-2026.ics
```

If one provider fails (network error, unimplemented source…), the others continue.
A per-provider summary is displayed:

```
Génération calendrier 2026 — 3 providers activés…
  ✓ formula1 : 24 événements
  ✓ formula2 : 14 événements
  ✗ wec : source non implémentée

Export terminé : motorsport-2026.ics (38 événements, 152 sessions)
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
    # source: jolpica  # api.jolpi.ca (Ergast successor) — covers 1950 onwards
  formula2:
    enabled: true
    source: f1calendar # github.com/sportstimes/f1 (MIT open dataset)
  wec:
    enabled: true
    source: official   # not yet implemented
  # Disable a championship:
  # wec:
  #   enabled: false
```

---

## Architecture

```
config.yaml
     │
     ▼ registry.enabled()
  ┌──────────┬──────────┬──────────┐
  │Formula 1 │Formula 2 │   WEC    │  …more (auto-discovered)
  │ Provider │ Provider │ Provider │
  └────┬─────┴────┬─────┴────┬─────┘
       │          │          │
  OpenF1    F1Calendar    Official
  Source      Source       Source
       │          │          │
       ▼          ▼          ▼
     Events     Events     Events
          └──────┬──────┘
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
| `F1CalendarBaseSource` | Shared base for F2, F3, Academy, Supercup — one class to subclass |
| `ProviderRegistry` | Auto-discovers and holds all registered provider factories |
| `SourceRegistry` | Auto-discovers and holds all registered source factories |
| `IcsExporter` | Serialises a `list[Event]` to an RFC 5545 `.ics` file |
| `HttpCache` | Disk-based JSON cache keyed by SHA-256(url + params) |
| `ConfigService` | Reads `config.yaml` and merges with Pydantic defaults |

---

## Championships

| Championship | Status | Source | Availability |
|---|---|---|---|
| Formula 1 (recent) | ✅ Available | [openf1.org](https://openf1.org) | 2023 → present |
| Formula 1 (historical) | ✅ Available | [jolpi.ca](https://jolpi.ca) (Ergast successor) | 1950 → present |
| Formula 2 | ✅ Available | [f1calendar dataset](https://github.com/sportstimes/f1) (MIT) | Recent seasons |
| WEC | 🟡 Architecture ready | fiawec.com (TODO) | Roadmap |
| Formula 3 | 🟡 In progress | [f1calendar dataset](https://github.com/sportstimes/f1) (MIT) | Sprint 19 |
| F1 Academy | 🟡 Planned | f1calendar dataset | Sprint 20 |
| Porsche Supercup | 🟡 Planned | f1calendar dataset | Sprint 21 |
| ELMS | 🔴 Planned | TBD | Future |

---

## Roadmap

| Version | Highlights |
|---|---|
| **v0.1** ✅ | Formula 1 via OpenF1, WEC architecture, multi-provider CLI, cache, config |
| **v0.2** ✅ | Formula 2 ✅, JolpicaSource ✅, Data Acquisition Layer ✅, Support Series Framework ✅ |
| **v0.3** 🚧 | Formula 3, F1 Academy, Porsche Supercup, OfficialWecSource |
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

# Packaging integrity
uv run pytest tests/test_packaging.py -v

# Lint + type check
uv run ruff check motorsport_calendar tests
uv run mypy motorsport_calendar
```

### Add a support series (F3, Academy, Supercup…)

Support series share the [f1calendar open dataset](https://github.com/sportstimes/f1).
Subclass `F1CalendarBaseSource` — only four overrides needed:

```python
# providers/formula3/sources/f1calendar.py
from motorsport_calendar.providers.support_series.f1calendar_base import F1CalendarBaseSource
from motorsport_calendar.providers.formula3.source import Formula3Source
from motorsport_calendar.models import Championship, ChampionshipCategory, SessionType

_SESSION_MAP = {
    "fp1":       (SessionType.FP1,        45, "Free Practice"),
    "qualifying": (SessionType.QUALIFYING, 30, "Qualifying"),
    "sprintRace": (SessionType.SPRINT,    45, "Sprint Race"),
    "feature":   (SessionType.RACE,       65, "Feature Race"),
}
_CIRCUIT_DATA = { ... }  # slug → (country, IANA timezone)

class F1CalendarSource(F1CalendarBaseSource, Formula3Source):
    @property
    def _series_key(self) -> str: return "f3"

    @property
    def _session_map(self): return _SESSION_MAP

    @property
    def _circuit_data(self): return _CIRCUIT_DATA

    def _make_championship(self, year: int) -> Championship:
        return Championship(id=f"formula3-{year}", name="FIA Formula 3 Championship",
                            category=ChampionshipCategory.SINGLE_SEATER)
```

Then register in `sources/__init__.py` — one line. That's all.

### Add any other provider

1. Create `motorsport_calendar/providers/mychampionship/`
2. Add `source.py` (abstract `Source` class) and `provider.py` (concrete `Provider`)
3. Add `sources/mysource.py` with the HTTP/scraping implementation
4. Register in `__init__.py` and `sources/__init__.py` — two lines total

`motocal generate` picks it up automatically.

---

## License

[MIT](LICENSE) © 2026 Alan Yvenou
