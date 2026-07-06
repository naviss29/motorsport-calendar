# AI_CONTEXT.md

> Fichier de reprise rapide pour une IA. Mis à jour après chaque session.
> Dernière mise à jour : 2026-07-06 (Sprint 24)

---

## État du projet

- **Nom** : motorsport-calendar
- **Version** : 0.2.0 (alpha)
- **Phase** : Sprint 24 — Desktop Alpha 3 — Product Polish ✅
- **Tests** : 720 passants, 0 échouants — couverture ~94 %
- **Branche** : `master`

---

## Stack technique

| Élément | Choix |
|---|---|
| Python | 3.12+ |
| Modèles | Pydantic v2, `frozen=True` |
| HTTP | `httpx.AsyncClient` (async) |
| CLI | Typer + Rich |
| Export ICS | `icalendar` ≥ 5.0 |
| Tests | pytest + pytest-asyncio (`asyncio_mode = "auto"`) |
| Linter | ruff |
| Type checker | mypy |
| Build | hatchling |
| CI | GitHub Actions |

---

## Architecture

```
motorsport_calendar/
├── cache/
│   ├── __init__.py          # export HttpCache
│   └── http_cache.py        # ✅ HttpCache — cache disque JSON, TTL, indépendant httpx
│
├── models/                  # Pydantic frozen — NE PAS MODIFIER sans ADR
│   ├── championship.py      # Championship, ChampionshipCategory
│   ├── circuit.py           # Circuit
│   ├── session.py           # Session, SessionType (StrEnum)
│   └── event.py             # Event, EventStatus (StrEnum)
│
├── providers/
│   ├── base.py              # Provider (ABC) — fetch_events / fetch_championship
│   ├── formula1/
│   │   ├── __init__.py      # ✅ auto-register : registry.register("formula1", _make_provider)
│   │   ├── provider.py      # Formula1Provider — délègue à Formula1Source
│   │   ├── source.py        # Formula1Source (ABC) — get_season(year)
│   │   └── sources/
│   │       ├── jolpica.py   # ✅ IMPLÉMENTÉ — API api.jolpi.ca (Ergast successor, 1950+)
│   │       ├── openf1.py    # ✅ IMPLÉMENTÉ — API openf1.org + HttpCache + JsonDataSource
│   │       ├── ergast.py    # ✅ alias → JolpicaSource (Ergast arrêté fin 2024)
│   │       ├── official.py  # 🔴 STUB — raise NotImplementedError
│   │       └── cached.py    # 🔴 STUB — raise NotImplementedError
│   ├── formula2/
│   │   ├── __init__.py      # ✅ auto-register : registry.register("formula2", _make_provider)
│   │   ├── provider.py      # Formula2Provider — délègue à Formula2Source
│   │   ├── source.py        # Formula2Source (ABC) — get_season(year)
│   │   └── sources/
│   │       ├── __init__.py  # ✅ source_registry.register("formula2", "f1calendar", ...)
│   │       └── f1calendar.py # ✅ F1CalendarSource(F1CalendarBaseSource, Formula2Source) — config F2 uniquement
│   ├── formula3/
│   │   ├── __init__.py      # ✅ auto-register : registry.register("formula3", _make_provider)
│   │   ├── provider.py      # Formula3Provider — délègue à Formula3Source
│   │   ├── source.py        # Formula3Source (ABC) — get_season(year)
│   │   └── sources/
│   │       ├── __init__.py  # ✅ source_registry.register("formula3", "f1calendar", ...)
│   │       └── f1calendar.py # ✅ F1CalendarSource(F1CalendarBaseSource, Formula3Source) — config F3 uniquement
│   ├── f1_academy/
│   │   ├── __init__.py      # ✅ auto-register : registry.register("f1-academy", _make_provider)
│   │   ├── provider.py      # F1AcademyProvider — délègue à F1AcademySource
│   │   ├── source.py        # F1AcademySource (ABC) — get_season(year)
│   │   └── sources/
│   │       ├── __init__.py  # ✅ source_registry.register("f1-academy", "f1calendar", ...)
│   │       └── f1calendar.py # ✅ F1CalendarSource(F1CalendarBaseSource, F1AcademySource) — config F1A uniquement
│   ├── __main__.py          # ✅ python -m motorsport_calendar — fallback quand Scripts pas dans PATH
│   ├── support_series/      # ✅ Framework partagé F2/F3/Academy/Supercup
│   │   ├── __init__.py      # package (non-provider)
│   │   └── f1calendar_base.py # F1CalendarBaseSource + _build_session — toute la logique HTTP/cache/mapping
│   └── wec/
│       ├── __init__.py      # ✅ auto-register : registry.register("wec", _make_provider)
│       ├── provider.py      # ✅ WecProvider — délègue à WecSource
│       ├── source.py        # ✅ WecSource (ABC) — get_season(year)
│       └── sources/
│           ├── __init__.py
│           └── official.py  # 🔴 STUB — raise NotImplementedError
│
├── config/
│   ├── __init__.py          # export ConfigService + tous les modèles
│   ├── models.py            # ✅ AppConfig, CacheConfig, IcsConfig, ProvidersConfig, ProviderConfig
│   └── service.py           # ✅ ConfigService — lit config.yaml, merge avec défauts Pydantic
│
├── core/
│   ├── __init__.py          # export ProviderRegistry + registry + SourceRegistry + source_registry
│   ├── datasource/          # ✅ Data Acquisition Layer — interfaces abstraites
│   │   ├── __init__.py      # export DataSource, JsonDataSource, HtmlDataSource, IcsDataSource
│   │   ├── base.py          # DataSource(ABC) — marqueur commun
│   │   ├── json_source.py   # JsonDataSource — fetch_json(url, params) → list | dict
│   │   ├── html_source.py   # HtmlDataSource — fetch_html(url) → str
│   │   └── ics_source.py    # IcsDataSource  — fetch_ics(url) → str
│   ├── registry.py          # ✅ ProviderRegistry — register/get/list_all/enabled/discover
│   ├── source_registry.py   # ✅ SourceRegistry — register/get/list_for/list_all/discover
│   └── service.py           # 🔴 NON IMPLÉMENTÉ — placeholder
│
├── exporters/
│   ├── base.py              # Exporter (ABC) — export / export_to_string
│   └── ics.py               # ✅ IMPLÉMENTÉ — RFC 5545, 1 VEVENT par Session
│
├── cli.py                   # Typer CLI — generate-f1, generate-f2, generate-f3, generate-f1-academy, generate-wec (--refresh), providers, generate, export (stub)
└── utils/logging.py         # 🔴 NON IMPLÉMENTÉ — placeholder
```

---

## Fonctionnalités terminées

1. **Modèles métier** — `Championship`, `Circuit`, `Session`, `Event`, `SessionType`, `EventStatus`, tous frozen
2. **IcsExporter** — génère un fichier `.ics` valide RFC 5545, 1 VEVENT par session
3. **Formula1Provider** — délègue à `Formula1Source`, injecte le championship
4. **OpenF1Source** — appels HTTP réels via `httpx`, mapping complet, 25 circuits IANA, gestion sessions incomplètes
5. **CLI `generate-f1`** — `motocal generate-f1 YEAR OUTPUT.ics [--refresh]`, gestion erreurs HTTP
6. **HttpCache** — cache disque JSON centralisé, TTL configurable, indépendant de httpx, `--refresh` pour bypass
7. **WecProvider** — architecture identique à F1 (`WecSource` ABC + `OfficialWecSource` stub), `ChampionshipCategory.ENDURANCE`
8. **ConfigService** — lit `config.yaml` (CWD puis `~/.config/…`), valeurs par défaut Pydantic, validation automatique
9. **IcsExporter** — ajout VALARM configurable via `alarm_minutes` (0 = désactivé)
10. **ProviderRegistry** — `register/get/list_all/enabled/discover`, auto-enregistrement à l'import de `__init__.py`
11. **SourceRegistry** — `register/get/list_for/list_all/discover`, clé `(championship, source_name)`, auto-enregistrement dans `sources/__init__.py`
12. **CLI `generate`** — `motocal generate YEAR OUTPUT.ics [--refresh]` — agrège tous les providers activés en un seul ICS, résilience partielle (provider qui échoue → ✗ résumé, les autres continuent), tri chronologique
13. **`JolpicaSource`** — données F1 historiques depuis 1950 via `api.jolpi.ca` (successeur Ergast Apache-2.0). `ErgastSource` = alias backward-compat. Enregistrée sous `"jolpica"`.
14. **Data Acquisition Layer** — `core/datasource/` : `DataSource`, `JsonDataSource`, `HtmlDataSource`, `IcsDataSource`. `OpenF1Source` migrée vers `JsonDataSource` (concept validé).
15. **Formula2Provider + F1CalendarSource** — support complet FIA F2 via JSON MIT (f1calendar.com). Sessions : FP (45 min), Qualifying (30 min), Sprint Race (45 min), Feature Race (65 min). 23 circuits IANA. CLI `generate-f2 YEAR OUTPUT.ics`. Auto-inclus dans `generate`.
16. **Support Series Framework** — `F1CalendarBaseSource(JsonDataSource, ABC)` dans `providers/support_series/f1calendar_base.py`. 4 propriétés abstraites (`_series_key`, `_session_map`, `_circuit_data`, `_make_championship`). Tout le reste hérité. F3/Academy/Supercup = ~15 lignes chacun.
17. **Packaging v0.2.0** — `pyproject.toml` : version 0.2.0, `typer>=0.12` (plus `[all]`), `python-dateutil` supprimé, Python 3.14 classifié. `__main__.py` : `python -m motorsport_calendar` opérationnel. CI : matrix Ubuntu + macOS + Windows × Python 3.12/3.13.
18. **Formula3Provider + F1CalendarSource** — support complet FIA F3 via JSON MIT (f1calendar.com). Sessions : Free Practice (45 min), Qualifying (30 min), Sprint Race (30 min), Feature Race (40 min). Clés dataset F3 : `practice`, `qualifying`, `sprint`, `feature` (≠ F2). 13 circuits IANA (2021-2025). CLI `generate-f3 YEAR OUTPUT.ics`. Auto-inclus dans `generate`. Couverture 2022+.
19. **F1AcademyProvider + F1CalendarSource** — support complet F1 Academy via JSON MIT. Slug dataset : `f1-academy`. Sessions : fp1/fp2/qualifying1/[qualifying2]/race1/race2/race3. 15 circuits IANA (2023-2025). CLI `generate-f1-academy YEAR OUTPUT.ics`. Couverture 2023+. Mapping contraint (ADR-016) : race2 → FP3 pour éviter collision d'UIDs ICS sans modifier les modèles métier.
20. **Dataset Reality Check (QA-03)** — Bug critique corrigé : `F1CalendarBaseSource` utilisait `raw.get("events", [])` alors que le dataset `sportstimes/f1` utilise `"races"`. F2/F3/F1 Academy retournaient 0 événements en production depuis Sprint 14. Correction : `raw.get("races", [])`. Fixtures de tests corrigées (`"events"` → `"races"` dans 5 fichiers). Fixtures réelles ajoutées dans `tests/fixtures/real/` (F2, F3, F1A — 2 événements chacun). 16 nouveaux tests (3 dans `TestRacesKeyRegression` + 13 dans `test_real_fixtures.py`).
21. **GUI Desktop Phase 1 (Sprint 22 + Hotfix GUI-01 + GUI-02)** — Package `motorsport_calendar/gui/` : `models.py` (GenerateState), `controller.py` (list_championships + async generate_calendar), `main_view.py` (Flet UI), `app.py` (ft.run), `__main__.py`. Dépendance optionnelle `flet>=0.80`. Entrée script `motocal-gui`. 32 tests GUI (12 models + 20 controller, sans Flet). Flet 0.85 : `ft.run()`, `ft.Button(content=str)` (plus `text=`), `ft.Icons`, `ft.Colors`, `FilePicker.save_file()` async, `Dropdown(on_select=)` (plus `on_change=`), `FilePicker` dans `page.services` (plus `page.overlay` — hérite de `Service` et non `Control`).
22. **GUI Desktop Alpha 2 — UX Polish (Sprint 23)** — `strings.py` (centralisation textes UI, `Strings.from_dict()` pour i18n future, `plural(n)`), `display_names.py` (mapping IDs → noms lisibles, `DEFAULT_SELECTED`), `preferences.py` (persistance dans `~/.config/motorsport-calendar/gui_prefs.json`), `assets/` (placeholder icône). `controller.generate_calendar()` retourne `tuple[int, int]` (events, sessions) au lieu de `int`. Dialogue succès : `page.show_dialog()` / `page.pop_dialog()`. Nom de fichier pré-rempli `motorsport-calendar-{year}.ics`. 36 nouveaux tests. 695 tests total.
23. **GUI Desktop Alpha 3 — Product Polish (Sprint 24)** — `categories.py` (`Category` StrEnum 5 valeurs, `ChampionshipGroup` frozen dataclass, `GROUPS` registre, `get_groups_for()` helper avec fallback). Navigation `ft.NavigationRail` 3 destinations (Accueil/Calendrier/À propos). `page.on_resize` pour rail étendu >900px. Championnats groupés visuellement (`🏎 Formula`, `🏁 Endurance`). Écran Accueil + écran À propos (lien GitHub via `ft.UrlLauncher`). `strings.py` + 11 chaînes (nav + about). 25 nouveaux tests. **720 tests total**. Services Flet : `FilePicker` + `UrlLauncher` dans `page.services`.

---

## Fonctionnalités en cours / prochaines

**Prochaines tâches recommandées** (Sprint 25+) :

1. **Packaging Windows `.exe`** — `flet build windows` → distributable sans Python
2. **`PorscheSupercupProvider`** — même pattern que F3/F1Academy, slug dataset à confirmer (probablement `porsche-supercup`). Regrouper dans `GROUPS` sous `Category.FORMULA`.
3. **`OfficialWecSource`** — scraping HTML de `fiawec.com/en/season`
   - Inspecter les XHR en DevTools avant d'implémenter
4. **`ELMSSource`** — scraping `europeanlemansseries.com` (XHR d'abord, HTML sinon)
5. **Icône application** — placer `icon.png` dans `gui/assets/`, décommenter `assets_dir` dans `app.py`

---

## Conventions importantes

- **Imports lazy dans la CLI** : tous les imports de providers/exporters sont à l'intérieur de la fonction de commande.
- **Mock HTTP** : `AsyncMock(side_effect=[meetings, sessions])` patché sur `OpenF1Source._get_json` pour les tests CLI. Client injecté directement pour les tests unitaires source.
- **Timezone** : OpenF1 retourne UTC. Le fuseau IANA est dérivé de `circuit_short_name` via `_CIRCUIT_TZ_MAP` dans `openf1.py`. Fallback : `"UTC"`.
- **event_uid** : `openf1-meeting-{meeting_key}@motorsport-calendar`
- **UID VEVENT** : `{event_uid}-{session.type}`
- **Sessions invalides** : `_build_session()` retourne `None` si date manquante, naive, ou end ≤ start.
- **Cache** : `HttpCache(cache_dir, ttl)` — fichiers `{sha256}.json` dans `.cache/`. Quand `OpenF1Source(client=mock)` est utilisé en test, le cache est désactivé automatiquement (client injecté = mode test).
- **`--refresh`** : passe `refresh=True` à `OpenF1Source`, propagé à `HttpCache.get_json(refresh=True)`.
- **WEC SessionTypes supportés** : `FREE_PRACTICE`, `QUALIFYING`, `HYPERPOLE`, `RACE` — tous déjà dans `SessionType` (StrEnum).
- **WEC Championship** : `id=f"wec-{year}"`, `name="FIA World Endurance Championship"`, `category=ChampionshipCategory.ENDURANCE`.
- **Config** : `ConfigService(config_path=None)` — cherche `config.yaml` dans CWD puis `~/.config/motorsport-calendar/`. Aucun fichier → défauts complets.
- **config.yaml** : ignoré par git (personnel). `config.example.yaml` commité comme référence.
- **VALARM** : `IcsExporter(alarm_minutes=N)` — N>0 → `TRIGGER:-PTNm` dans chaque VEVENT. CLI lit `config.ics.alarm_minutes`.
- **Data Acquisition Layer (DAL)** : `core/datasource/` — `DataSource` (ABC marker), `JsonDataSource` (abstract `fetch_json(url, params)`), `HtmlDataSource` (abstract `fetch_html(url)`), `IcsDataSource` (abstract `fetch_ics(url)`). Les sources implémentent l'interface DAL de leur catégorie **en plus** de l'interface domaine (`Formula1Source`, etc.). `OpenF1Source` et `F1CalendarSource` implémentent `JsonDataSource`.
- **F1CalendarSource (F2)** : config F2 uniquement — `_series_key="f2"`. `_SESSION_MAP` accepte 6 clés : `fp1` et `practice` → `FP1` (renommage dataset 2025), `qualifying`, `sprintRace` et `sprint` → `SPRINT` (renommage dataset 2025), `feature` → `RACE`. `_CIRCUIT_DATA` : 23 circuits. Module-level backward-compat functions conservées (importées directement par `test_f1calendar_source.py`).
- **F1CalendarSource (F3)** : config F3 uniquement — `_series_key="f3"`, sessions : `practice/qualifying/sprint/feature` (clés différentes de F2). `_CIRCUIT_DATA` : 13 circuits (subset F1 européen + Bahreïn + Melbourne). Pas de fonctions module-level (F3 n'a pas de tests hérités). URL construite par la base : `_BASE_URL/{series_key}/{year}.json`. `event_uid = f"f1calendar-{series_key}-{year}-{round}@motorsport-calendar"`.
- **F1CalendarSource (F1 Academy)** : config F1A uniquement — `_series_key="f1-academy"`, sessions : `fp1/fp2/qualifying1/qualifying2/race1/race2/race3`. `_CIRCUIT_DATA` : 15 circuits (2023-2025). Mapping contraint : `race2 → FP3` workaround ADR-016. Package Python : `f1_academy` (underscore), championship ID : `"f1-academy"` (tiret). `qualifying2` optionnel (absent en 2025+).
- **test_cli_generate.py — imports disambiguïsés** : F1Academy importée comme `F1AcademyCalendarSource`, mockée dans `test_all_providers_fail_*`.
- **F1CalendarBaseSource** : dans `providers/support_series/f1calendar_base.py`. `__init__(client, cache, *, refresh)`, `get_season(year)`, `fetch_json(url, params)`, `_resolve_circuit_data(slug)`, `_build_circuit(event_data)`, `_build_event(championship, event_data, year)`. `_build_session(timestamp, type, duration, title)` = fonction module-level pure.
- **Mock pour tests support series** : `patch.object(F1CalendarSource, "fetch_json", AsyncMock(return_value=...))` — fonctionne même si `fetch_json` est hérité de la base (patch sur la sous-classe). Pour F3 : `patch("motorsport_calendar.providers.formula3.sources.f1calendar.F1CalendarSource.fetch_json", ...)`. **La valeur de retour doit utiliser `"races"` comme clé, jamais `"events"` (ADR-017)**.
- **Dataset key `"races"`** : le dataset `sportstimes/f1` utilise `"races"` comme clé de premier niveau, **pas** `"events"`. Toutes les fixtures de test (réelles ou mock) doivent utiliser `{"races": [...]}`. `"events"` est silencieusement ignoré. Tests de régression dans `TestRacesKeyRegression` (`test_f1calendar_base.py`) et `tests/fixtures/real/`.
- **HttpCache mock** : depuis Sprint 18, patcher `"motorsport_calendar.providers.support_series.f1calendar_base.HttpCache"` (et non plus `f1calendar.HttpCache`).
- **test_cli_generate.py — imports disambiguïsés** : F2 importée comme `F2CalendarSource`, F3 comme `F3CalendarSource` pour éviter les conflits de noms dans les tests "tout échoue". Les deux sont mockées dans `test_all_providers_fail_*`.
- **Ajouter un support series** (F3, Academy, Supercup) : créer `providers/XYZ/` avec source héritant de `F1CalendarBaseSource` — 4 overrides, ~15 lignes. Même pattern que `F1CalendarSource`.
- **JolpicaSource** : endpoint `http://api.jolpi.ca/ergast/f1/{year}/races.json?limit=100`. Requête unique par saison. Sessions extraites des champs `FirstPractice`, `SecondPractice`, `ThirdPractice`, `Qualifying`, `SprintQualifying`, `Sprint` + champ race (`date`+`time` au top level). Durées inférées : FP 60 min, Qualifying 60 min, SprintQualifying 45 min, Sprint 35 min, Race 130 min. `circuitId` snake_case → IANA timezone. Fallback noon UTC si `time` absent (pré-2000). Enregistrée sous `"jolpica"` dans SourceRegistry.
- **ErgastSource** : alias backward-compat pour `JolpicaSource` (Ergast arrêté fin 2024). Non enregistrée dans SourceRegistry — utiliser `source: jolpica` dans config.yaml.
- **Architecture figée (Sprint 10)** : ProviderRegistry + SourceRegistry = architecture finale. Pas de refactoring structurel prévu.
- **ProviderRegistry** : singleton `motorsport_calendar.core.registry.registry`. Factory signature : `(source) → Provider`. `registry.discover()` importe chaque `providers/X/__init__.py`.
- **SourceRegistry** : singleton `motorsport_calendar.core.source_registry.source_registry`. Clé `(championship_id, source_name)`. Factory signature : `(cache, refresh) → Source`. `source_registry.discover()` importe chaque `providers/X/sources/__init__.py`.
- **Auto-enregistrement providers** : `providers/formula1/__init__.py` → `registry.register("formula1", _make_provider)`.
- **Auto-enregistrement sources** : `providers/formula1/sources/__init__.py` → `source_registry.register("formula1", "openf1", lambda cache, refresh: OpenF1Source(...))`.
- **CLI orchestration** : `source = source_registry.get(cid, source_name)(cache, refresh)` → `provider = registry.get(cid)(source)`.
- **ProviderConfig** : `enabled: bool = True` (opt-out), `source: str = ""` (optionnel — `or "openf1"` dans la CLI).
- **ProvidersConfig.get(id)** : cherche dans les champs nommés (`formula1`, `wec`) puis dans `model_extra`. Retourne `None` si absent (= activé par défaut dans `registry.enabled()`).
- **Ajouter une source** : une ligne dans `sources/__init__.py`. Aucun autre fichier.
- **Ajouter un championnat** : créer `providers/X/` + `providers/X/sources/`. Aucun autre fichier.

---

## Dette technique

| Item | Impact | Priorité |
|---|---|---|
| `export` CLI est un stub (exit 1) | Commande inutilisable | HAUTE |
| `ErgastSource` → alias `JolpicaSource` | ✅ Résolu — Sprint 15 | — |
| `CachedFormula1Source` non implémentée | Appels répétés à l'API | HAUTE |
| Cache `.cache/` en CWD (pas `~/.cache/`) | Moins adapté au déploiement | BASSE |
| `core/service.py` vide | Architecture incomplète | MOYENNE |
| `utils/logging.py` vide | Pas de logs structurés | BASSE |
| Couverture `cli.py` à 76 % | Branches non testées | MOYENNE |

---

## Commandes utiles

```bash
# Lancer les tests
python -m pytest

# Lancer les tests du cache uniquement
python -m pytest tests/test_http_cache.py -v

# Générer un calendrier F1 2024 (utilise le cache)
motocal generate-f1 2024 f1-2024.ics

# Forcer un re-téléchargement (ignore le cache)
motocal generate-f1 2024 f1-2024.ics --refresh
```
