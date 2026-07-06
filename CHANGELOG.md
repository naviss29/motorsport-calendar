# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] — Hotfix GUI-01 — Compatibilité Flet 0.85

### Fixed

- **`ft.Dropdown.on_change` → `on_select`** : l'argument `on_change` a été supprimé dans
  Flet 0.80+ au profit de `on_select` pour les menus déroulants. Le sélecteur de saison
  levait `TypeError: Dropdown.__init__() got an unexpected keyword argument 'on_change'`
  au lancement.
- **`ft.Button(text=...)` → `content=`** : dans Flet 0.80+, `ft.Button` (et tous les boutons)
  n'acceptent plus `text` mais `content: str | Control`. Le texte du bouton "Générer"
  n'était pas affiché et causait un `TypeError` au démarrage.
- La GUI s'ouvre désormais correctement sous Flet 0.85.3.

---

## [Unreleased] — Sprint 22 — Desktop Edition (Phase 1)

### Added

- **Interface graphique desktop** — `motocal-gui` (ou `python -m motorsport_calendar.gui`).
  Fenêtre Flet avec :
  - Sélecteur de saison (année courante ±5)
  - Cases à cocher par championnat (liste automatique depuis `ProviderRegistry`)
  - Sélecteur de fichier de sortie via `FilePicker` natif
  - Bouton "Générer" (actif seulement si tous les champs sont remplis)
  - Anneau de progression pendant la génération
  - Affichage du résultat par championnat (✓ N événements / ✗ erreur)
- **`motorsport_calendar/gui/`** — package dédié, zéro duplication du moteur :
  - `models.py` — `GenerateState` (dataclass, état mutable de la vue)
  - `controller.py` — `list_championships()` + `async generate_calendar()` (miroir exact du pipeline CLI `generate`)
  - `main_view.py` — vue Flet complète (requiert `flet>=0.80`)
  - `app.py` — point d'entrée `ft.run()`
  - `__main__.py` — support `python -m motorsport_calendar.gui`
- **Dépendance optionnelle** `flet>=0.80` : `pip install motorsport-calendar[gui]`
  (la CLI reste installable sans Flet)
- **Entrée script** `motocal-gui` dans `pyproject.toml`
- **32 tests GUI** : `test_gui_models.py` (12 tests) + `test_gui_controller.py` (20 tests).
  Aucune dépendance Flet dans les tests — `controller.py` et `models.py` sont purement Python.

### Technical

- Flet 0.85 API : `ft.run()` (remplace `ft.app()` déprécié), `ft.Button` (remplace `ft.ElevatedButton`), `ft.Icons` / `ft.Colors` (capitalisés), `FilePicker.save_file()` async.
- Génération dans le thread de l'event loop Flet — les appels httpx s'exécutent dans la boucle asyncio de Flet, l'anneau de progression tourne pendant les requêtes réseau.

---

## [Unreleased] — Sprint QA-03

### Fixed

- **Bug critique : F2/F3/F1 Academy retournaient systématiquement 0 événements** (ADR-017).
  `F1CalendarBaseSource._get_season()` utilisait `raw.get("events", [])` mais le dataset
  `sportstimes/f1` (GitHub) utilise la clé `"races"` — pas `"events"`. Ce bug existait
  depuis l'introduction du Support Series Framework (Sprint 14) et a masqué 100 % des données
  F2/F3/F1 Academy en production depuis le début.
  Correction : `raw.get("races", [])` dans `f1calendar_base.py`.
  **Pourquoi les tests n'ont rien détecté** : les fixtures de tests utilisaient aussi `"events"`
  (copiées/collées depuis le code), ce qui faisait correspondre les tests au code incorrect
  sans jamais tester le comportement réel du dataset.

### Added

- **Fixtures réelles** `tests/fixtures/real/` : extraits minimaux (2 events) du dataset réel
  `sportstimes/f1` pour F2 (Australian + Bahrain 2025), F3 (Australian + Bahrain 2025) et
  F1 Academy (Chinese + Jeddah 2025). Utilisent la clé `"races"` et les clés de sessions
  réelles. Ces fixtures servent de garde-fou contre toute régression similaire.
- **Tests `tests/test_real_fixtures.py`** : 3 classes (`TestF2RealFixture`, `TestF3RealFixture`,
  `TestF1AcademyRealFixture`), chacune vérifiant que le fixture contient `"races"`, que 2 events
  sont chargés, et que le CLI produit le bon nombre de VEVENTs.
- **`TestRacesKeyRegression`** dans `test_f1calendar_base.py` : 3 tests documentant que
  `"races"` est lu, `"events"` est ignoré, et que si les deux clés coexistent seul `"races"`
  est lu.
- **Isolation des tests CLI `generate`** : fixture `autouse=True` `_isolate_support_series`
  dans `test_cli_generate.py` empêche F2/F3/F1 Academy de faire de vrais appels réseau vers
  GitHub pendant les tests d'intégration F1/WEC.

### Changed

- `tests/test_f1calendar_base.py` : `"events"` → `"races"` dans `_TEST_RESPONSE` et
  `_EMPTY_RESPONSE` (fixtures alignées sur le dataset réel).
- `tests/test_f1calendar_source.py` : `"events"` → `"races"` dans toutes les fixtures.
- `tests/test_cli_generate_f2.py`, `test_cli_generate_f3.py`, `test_cli_generate_f1_academy.py` :
  `"events"` → `"races"` dans toutes les fixtures de chaque fichier.

---

## [Unreleased] — Sprint 21.2

### Fixed

- **Formula 2 : rétrocompatibilité des clés de sessions** (hotfix — ADR-014 mis à jour).
  Le dataset `sportstimes/f1` a renommé deux clés F2 à partir de 2025 :
  `fp1` → `practice` et `sprintRace` → `sprint`.
  Conséquence : les calendriers F2 2025+ n'exportaient que 2 sessions sur 4.
  `_SESSION_MAP` accepte désormais les quatre formes ; les saisons 2024 et antérieures
  continuent de fonctionner sans modification.
  6 tests de régression ajoutés dans `test_cli_generate_f2.py` (`TestF2SessionKeyCompat`) :
  3 tests unitaires `_build_event` et 3 tests CLI VEVENT pour 2024, 2025 et 2026.

---

## [Unreleased] — Sprint 21

### Added

- **F1 Academy provider** — `motocal generate-f1-academy YEAR OUTPUT.ics` génère le calendrier F1 Academy complet.
  - `F1AcademyProvider` + `F1AcademySource` (ABC) — même architecture que F1/F2/F3/WEC.
  - `F1CalendarSource(F1CalendarBaseSource, F1AcademySource)` — ~60 lignes, 4 overrides uniquement.
    Source : `https://raw.githubusercontent.com/sportstimes/f1/main/_db/f1-academy/{year}.json` (MIT).
    Sessions : Free Practice 1 (45 min), Free Practice 2 (30 min), Qualifying 1/2 (30 min),
    Race 1 (30 min), Race 2 (30 min), Race 3 (30 min). 15 circuits avec fuseaux IANA.
  - Format de sessions propre à F1 Academy : `fp1`, `fp2`, `qualifying1`, `qualifying2` (2023-2024),
    `race1`, `race2`, `race3`. `qualifying2` absent en 2025+.
  - Couverture : 2023 → présent.
  - Auto-inclus dans `motocal generate` (opt-out via `config.yaml`).
  - `config.example.yaml` mis à jour avec la section `f1-academy`.
  - ADR-016 : mapping `race2 → FP3` pour garantir l'unicité des UIDs ICS sans modifier
    les modèles métier. Recommandation : ajouter `RACE2`/`RACE3` à `SessionType` dans v0.4.
  - 41 nouveaux tests (F1AcademyProvider : 13, CLI generate-f1-academy : 28).

---

## [Unreleased] — Sprint 20

### Added

- **Formula 3 provider** — `motocal generate-f3 YEAR OUTPUT.ics` génère le calendrier FIA F3 complet.
  - `Formula3Provider` + `Formula3Source` (ABC) — même architecture que F1/F2/WEC.
  - `F1CalendarSource(F1CalendarBaseSource, Formula3Source)` — ~50 lignes, 4 overrides uniquement.
    Source : `https://raw.githubusercontent.com/sportstimes/f1/main/_db/f3/{year}.json` (MIT).
    Sessions mappées : Free Practice (45 min), Qualifying (30 min), Sprint Race (30 min),
    Feature Race (40 min). Clés dataset F3 : `practice`, `qualifying`, `sprint`, `feature`
    (diffèrent de F2). 13 circuits avec fuseaux IANA (couverts 2021-2025).
  - Couverture : 2022 → présent (avant 2022, les sessions `race1/race2/race3` sont ignorées).
  - Auto-inclus dans `motocal generate` (opt-out via `config.yaml`).
  - Enregistré sous `source: f1calendar` dans `config.yaml`.
  - `config.example.yaml` mis à jour avec la section `formula3`.
  - 36 nouveaux tests (Formula3Provider : 12, CLI generate-f3 : 24).

---

## [0.2.0] — 2026-07-05

### Fixed

- **`typer[all]` extra supprimé** — typer 0.26.x n'expose pas d'extra `all` ; causait un WARNING
  à chaque `pip install`. Remplacé par `typer>=0.12` (rich reste une dépendance directe).
- **`python-dateutil` supprimé** — dépendance déclarée mais jamais utilisée dans le code.
- **Version `0.1.0` → `0.2.0`** dans `pyproject.toml` et `__init__.py` (incohérence depuis Sprint 15).

### Added

- **`python -m motorsport_calendar`** — `__main__.py` ajouté : permet de lancer la CLI sans que le
  dossier `Scripts` soit dans le PATH (utile sur Windows). Toutes les commandes sont disponibles.
- **Tests de packaging** (`tests/test_packaging.py`, 36 tests) — vérifient que le package installé
  est correctement câblé : version metadata, `python -m` entry point, commandes CLI enregistrées,
  imports publics, auto-découverte des registries.
- **CI multi-plateforme** — ajout de `macos-latest` et `windows-latest` dans la matrice GitHub Actions.

- **Support Series Framework** (`providers/support_series/f1calendar_base.py`) — base commune pour
  F2, F3, F1 Academy, Porsche Supercup. Extrait la logique partagée de `F1CalendarSource` :
  - `F1CalendarBaseSource(JsonDataSource, ABC)` — `__init__`, `get_season`, `fetch_json`,
    `_resolve_circuit_data`, `_build_circuit`, `_build_event` tous paramétrés via 4 propriétés abstraites.
  - `_build_session()` — fonction pure module-level, générique.
  - Chaque nouveau support series ne nécessite que ~15 lignes : `_series_key`, `_session_map`,
    `_circuit_data`, `_make_championship`.
  - `F1CalendarSource` (F2) refactorisée pour hériter de la base — aucun changement de comportement.
  - 36 nouveaux tests dans `tests/test_f1calendar_base.py`.

- **Formula 2 provider** — `motocal generate-f2 YEAR OUTPUT.ics` génère le calendrier FIA F2 complet.
  - `Formula2Provider` + `Formula2Source` (ABC) — même architecture que F1/WEC.
  - `F1CalendarSource` — source JSON MIT via `github.com/sportstimes/f1`, un seul GET par saison.
    Requête : `https://raw.githubusercontent.com/sportstimes/f1/main/_db/f2/{year}.json`.
    Sessions mappées : FP (45 min), Qualifying (30 min), Sprint Race (45 min), Feature Race (65 min).
    23 circuits avec fuseaux IANA ; fallback `"Unknown"` / `"UTC"` pour les circuits inconnus.
  - Auto-inclus dans `motocal generate` (opt-out via `config.yaml`).
  - Enregistré sous `source: f1calendar` dans `config.yaml`.
  - `config.example.yaml` mis à jour avec la section `formula2`.
  - 74 nouveaux tests (F1CalendarSource : 44, Formula2Provider : 9, CLI generate-f2 : 21).

- **Data Acquisition Layer** (`motorsport_calendar/core/datasource/`) — abstract interfaces
  separating raw data retrieval from domain mapping:
  - `DataSource` — common ABC marker
  - `JsonDataSource` — abstract `fetch_json(url, params)` for REST JSON APIs
  - `HtmlDataSource` — abstract `fetch_html(url)` for HTML scraping
  - `IcsDataSource` — abstract `fetch_ics(url)` for iCalendar feeds
- **`OpenF1Source` migrated to `JsonDataSource`** — implements `fetch_json`, validating the
  DAL pattern. `_get_json` is preserved as a thin wrapper for backward-compatible test mocks.
  Zero change to the public `get_season()` API.
- 25 new tests in `tests/test_datasource.py`.

- **`JolpicaSource`** — full implementation of `Formula1Source` using the Jolpica API
  (`http://api.jolpi.ca/ergast/f1/{year}/races.json`), the Ergast-compatible successor
  (Apache-2.0). Covers F1 data from 1950 onwards. Single request per season; session end
  times inferred from session type; 34 circuits with IANA timezones; historical races without
  time data fall back to noon UTC. Registered as `source: jolpica` in `config.yaml`.
- `ErgastSource` is now a backward-compatibility alias for `JolpicaSource` (Ergast was shut
  down end-2024). Its test now asserts the alias relationship.
- 43 new tests in `tests/test_jolpica_source.py`.

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
