# motorsport-calendar

> Generate motorsport race calendars in ICS format — subscribe once, stay updated automatically.

[![CI](https://github.com/naviss29/motorsport-calendar/actions/workflows/ci.yml/badge.svg)](https://github.com/naviss29/motorsport-calendar/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

---

## Features

- **ICS export** — subscribe your calendar app (Google Calendar, Apple Calendar, Outlook…) to a live `.ics` feed
- **Provider-agnostic** — pluggable data sources (Ergast, OpenF1, Jolpica, custom scrapers)
- **Multi-championship** — Formula 1, MotoGP, WEC, WRC and more (provider-dependent)
- **Typed & tested** — strict Mypy, Pydantic v2 models, Pytest test suite
- **CLI** — `motocal` command with Typer + Rich output

---

## Installation

### From PyPI

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

## Usage

```bash
# Show help
motocal --help

# Show version
motocal version

# List available providers
motocal providers

# Export a calendar
motocal export \
  --provider ergast \
  --championship formula1 \
  --year 2025 \
  --output f1-2025.ics
```

### Python API

```python
import asyncio
from pathlib import Path
from motorsport_calendar.core import CalendarService

# from motorsport_calendar.providers.ergast import ErgastProvider  # coming soon
# from motorsport_calendar.exporters.ics import ICSExporter        # coming soon

async def main():
    service = CalendarService()
    # service.register_provider(ErgastProvider())
    # service.register_exporter(ICSExporter())
    # await service.export_championship("ergast", "formula1", 2025, "ics", Path("f1.ics"))

asyncio.run(main())
```

---

## Architecture

```
motorsport_calendar/
├── cli.py                  # Typer CLI — presentation only, no business logic
├── core/
│   └── service.py          # CalendarService — wires providers ↔ exporters
├── providers/
│   └── base.py             # Provider ABC — implement to add a data source
├── exporters/
│   └── base.py             # Exporter ABC — implement to add an output format
├── models/
│   ├── event.py            # Event + SessionType
│   ├── circuit.py          # Circuit
│   └── championship.py     # Championship
└── utils/
    └── logging.py          # Rich-based logging

tests/
├── conftest.py             # Shared fixtures
├── test_models.py          # Model validation tests
└── test_cli.py             # CLI smoke tests

.github/workflows/
├── ci.yml                  # Lint + tests on push/PR (Python 3.12 & 3.13)
└── publish.yml             # Publish to PyPI on tag push
```

### Key concepts

| Concept | Role |
|---|---|
| `Provider` | Fetches raw data from a remote API and maps it to shared models |
| `Exporter` | Serializes a `Championship` to a file format (ICS, JSON, CSV…) |
| `CalendarService` | Orchestrates `Provider` + `Exporter`, holds no data itself |
| `Event` | One session (race, quali, practice) with start/end times |
| `Championship` | A full season: name, year, sport, flat list of `Event`s |
| `Circuit` | Circuit metadata with IANA timezone |

### Adding a provider

Create a class that extends `Provider` and implement two methods:

```python
from motorsport_calendar.providers.base import Provider
from motorsport_calendar.models import Championship, Event

class MyProvider(Provider):
    @property
    def name(self) -> str:
        return "my-provider"

    @property
    def supported_championships(self) -> list[str]:
        return ["formula1"]

    async def fetch_championship(self, championship_id: str, year: int) -> Championship:
        ...  # fetch + map to Championship

    async def fetch_events(self, championship_id: str, year: int) -> list[Event]:
        ...  # fetch + map to list[Event]
```

### Adding an exporter

```python
from pathlib import Path
from motorsport_calendar.exporters.base import Exporter
from motorsport_calendar.models import Championship

class MyExporter(Exporter):
    @property
    def name(self) -> str:
        return "my-format"

    @property
    def file_extension(self) -> str:
        return "txt"

    def export(self, championship: Championship, output: Path) -> None:
        output.write_text(self.export_to_string(championship))

    def export_to_string(self, championship: Championship) -> str:
        return "\n".join(e.name for e in championship.events)
```

---

## Development

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Lint
uv run ruff check motorsport_calendar tests

# Format
uv run ruff format motorsport_calendar tests

# Type check
uv run mypy motorsport_calendar

# Install pre-commit hooks
uv run pre-commit install
```

---

## Roadmap

- [ ] `ErgastProvider` — Formula 1 (historical data)
- [ ] `OpenF1Provider` — Formula 1 (live, 2023+)
- [ ] `ICSExporter` — standard `.ics` / iCalendar format
- [ ] `JSONExporter` — machine-readable JSON
- [ ] MotoGP provider
- [ ] WEC provider
- [ ] GitHub Release ICS hosting
- [ ] PyPI publish

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-provider`
3. Implement your provider or exporter
4. Add tests
5. Open a pull request

Please run `pre-commit run --all-files` before submitting.

---

## License

[MIT](LICENSE) — © 2026 Alan Yvenou
