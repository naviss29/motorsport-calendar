# JOURNAL.md

---

## Session 2026-07-05 — Sprint 10 : Source Registry

### Objectif
Inverser la responsabilité de la sélection de source. Le provider ne connaît plus ses sources. Le `SourceRegistry` gère la correspondance `(championnat, nom_source) → factory`.

### Travail effectué

**`motorsport_calendar/core/source_registry.py`** — nouveau fichier
- `SourceRegistry` : `register()`, `get()`, `list_for()`, `list_all()`, `discover()`
- Clé composite `(championship_id, source_name)`
- `discover()` : importe `providers/X/sources/__init__.py` de chaque provider
- `source_registry` singleton
- Couverture 93 %

**`motorsport_calendar/providers/formula1/sources/__init__.py`**
- Ajout `source_registry.register("formula1", "openf1", lambda cache, refresh: OpenF1Source(...))`
- Les stubs (Ergast, Official, Cached) ne sont pas encore enregistrés

**`motorsport_calendar/providers/wec/sources/__init__.py`**
- Ajout `source_registry.register("wec", "official", lambda cache, refresh: OfficialWecSource())`

**`motorsport_calendar/providers/formula1/__init__.py`**
- Factory simplifiée : `_make_provider(source) → Formula1Provider(source)`
- Plus aucune référence à OpenF1Source, Ergast, etc.

**`motorsport_calendar/providers/wec/__init__.py`**
- Factory simplifiée : `_make_provider(source) → WecProvider(source)`

**`motorsport_calendar/cli.py`**
- `generate-f1` orchestre : `source_registry.get("formula1", source_name)(cache, refresh)` puis `registry.get("formula1")(source)`

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/core/source_registry.py` | Créé |
| `motorsport_calendar/core/__init__.py` | Modifié — export SourceRegistry + source_registry |
| `motorsport_calendar/providers/formula1/__init__.py` | Modifié — factory simplifiée |
| `motorsport_calendar/providers/wec/__init__.py` | Modifié — factory simplifiée |
| `motorsport_calendar/providers/formula1/sources/__init__.py` | Modifié — enregistrement openf1 |
| `motorsport_calendar/providers/wec/sources/__init__.py` | Modifié — enregistrement official |
| `motorsport_calendar/cli.py` | Modifié — orchestration via source_registry |
| `tests/test_source_registry.py` | Créé — 24 tests |
| `tests/test_registry.py` | Modifié — factories mises à jour |
| `docs/DECISIONS.md` | ADR-012 ajouté |

### Bugs rencontrés
Aucun.

### Tests exécutés
```
273 passed — 0 failed — couverture 93 %
```

---

## Session 2026-07-05 — Sprint 9 : Provider Registry

### Objectif
Créer un `ProviderRegistry` central. Chaque provider s'enregistre automatiquement à l'import de son `__init__.py`. La CLI ne connaît plus aucun provider individuellement.

### Travail effectué

**`motorsport_calendar/core/registry.py`** — nouveau fichier
- `ProviderRegistry` : `register()`, `get()`, `list_all()`, `enabled()`, `discover()`
- `registry` singleton partagé par toute l'application
- `discover()` : `pkgutil.iter_modules` sur `providers/` → importe chaque sous-paquet
- `enabled(providers_config)` : logique opt-out (absent de la config = activé)
- Couverture 100 %

**`motorsport_calendar/config/models.py`**
- `ProviderConfig` : ajout `enabled: bool = True` et `source: str = ""` (source optionnelle)
- `ProvidersConfig` : ajout `extra="allow"` (Pydantic stocke les providers YAML hors nommés) + méthode `get(championship_id)` (cherche champs nommés puis extras)

**`motorsport_calendar/providers/formula1/__init__.py`**
- Ajout import `registry` + factory `_make_provider(cfg, cache, refresh)` → `Formula1Provider(OpenF1Source(...))`
- `registry.register("formula1", _make_provider)` à l'import

**`motorsport_calendar/providers/wec/__init__.py`**
- Ajout import `registry` + factory `_make_provider(cfg, cache, refresh)` → `WecProvider(OfficialWecSource())`
- `registry.register("wec", _make_provider)` à l'import

**`motorsport_calendar/cli.py`**
- `generate-f1` : remplace la logique `if source == "openf1"` par `registry.discover()` + `registry.get("formula1")`
- `providers` : mise à jour — affiche la liste depuis `registry.list_all()`

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/core/registry.py` | Créé |
| `motorsport_calendar/core/__init__.py` | Modifié — export ProviderRegistry + registry |
| `motorsport_calendar/config/models.py` | Modifié — enabled + source optionnels + get() |
| `motorsport_calendar/providers/formula1/__init__.py` | Modifié — auto-enregistrement |
| `motorsport_calendar/providers/wec/__init__.py` | Modifié — auto-enregistrement |
| `motorsport_calendar/cli.py` | Modifié — registry-driven, providers cmd fonctionnelle |
| `config.example.yaml` | Modifié — champ enabled documenté |
| `tests/test_registry.py` | Créé — 25 tests |
| `tests/test_config_service.py` | Modifié — 7 tests ajoutés (enabled, get) |
| `docs/DECISIONS.md` | ADR-011 ajouté |

### Bugs rencontrés
Aucun.

### Tests exécutés
```
250 passed — 0 failed — couverture 93 %
```

---

## Session 2026-07-05 — Sprint 8 : Configuration centralisée

### Objectif
Supprimer tous les paramètres codés en dur. Créer un `ConfigService` qui lit `config.yaml` et alimente le cache, les providers et l'exporteur ICS.

### Travail effectué

**Module `motorsport_calendar/config/`**
- `AppConfig`, `CacheConfig`, `IcsConfig`, `ProviderConfig`, `ProvidersConfig` — tous Pydantic v2 `frozen=True`
- `ConfigService` : cherche `config.yaml` (CWD → `~/.config/…`) puis utilise les défauts
- Dépendance `pyyaml>=6.0` ajoutée à `pyproject.toml`

**IcsExporter**
- Ajout de `alarm_minutes: int = 0` au constructeur
- Si `alarm_minutes > 0` : VALARM `ACTION:DISPLAY`, `TRIGGER:-PTNm` dans chaque VEVENT

**CLI `generate-f1`**
- Lecture `ConfigService()` au démarrage de la commande
- Cache construit depuis `config.cache` (path + TTL)
- Source F1 sélectionnée depuis `config.providers.formula1.source`
- `IcsExporter(alarm_minutes=config.ics.alarm_minutes)` — plus de valeur codée en dur

**Fichiers**
- `config.example.yaml` — référence commentée de toutes les options
- `config.yaml` ajouté à `.gitignore`

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/config/__init__.py` | Créé |
| `motorsport_calendar/config/models.py` | Créé — 5 modèles Pydantic |
| `motorsport_calendar/config/service.py` | Créé — ConfigService |
| `motorsport_calendar/exporters/ics.py` | Modifié — alarm_minutes + VALARM |
| `motorsport_calendar/cli.py` | Modifié — wiring ConfigService |
| `pyproject.toml` | Modifié — pyyaml>=6.0 |
| `tests/test_config_service.py` | Créé — 30 tests |
| `tests/test_ics_exporter.py` | Modifié — 7 tests VALARM |
| `config.example.yaml` | Créé — documentation utilisateur |
| `.gitignore` | Modifié — config.yaml exclu |
| `docs/DECISIONS.md` | ADR-009 + ADR-010 |

### Bugs rencontrés
Aucun.

### Tests exécutés
```
219 passed — 0 failed — couverture 91 %
```

---

## Session 2026-07-05 — Sprint 7 : Provider WEC

### Objectif
Créer l'architecture du provider WEC, symétrique à F1. Pas d'implémentation HTTP pour l'instant.

### Travail effectué

**Architecture `providers/wec/`**
- `WecSource` (ABC) — contrat identique à `Formula1Source`
- `WecProvider` — délègue à `WecSource`, retourne `Championship(category=ENDURANCE)`
- `OfficialWecSource` — stub `raise NotImplementedError`

**SessionTypes WEC**
- `FREE_PRACTICE`, `QUALIFYING`, `HYPERPOLE`, `RACE` — déjà présents dans le modèle `SessionType`
- Vérification explicite dans les tests

**Tests** (`test_wec_provider.py`)
- WecSource ABC non instanciable
- WecProvider identity (name="wec", supported_championships=["wec"])
- fetch_events : délégation, empty, passage year, non-mutation
- fetch_championship : id, name, category ENDURANCE, years différents
- SessionType WEC : les 4 types supportés
- OfficialWecSource : NotImplementedError, isinstance WecSource
- Interopérabilité modèles : Event, Circuit, Championship identiques F1/WEC

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/providers/wec/__init__.py` | Créé |
| `motorsport_calendar/providers/wec/provider.py` | Créé |
| `motorsport_calendar/providers/wec/source.py` | Créé |
| `motorsport_calendar/providers/wec/sources/__init__.py` | Créé |
| `motorsport_calendar/providers/wec/sources/official.py` | Créé |
| `tests/test_wec_provider.py` | Créé — 24 tests |
| `docs/AI_CONTEXT.md` | Mis à jour |
| `docs/JOURNAL.md` | Mis à jour |
| `docs/TODO.md` | Mis à jour |

### Bugs rencontrés
Aucun.

### Tests exécutés
```
182 passed — 0 failed — couverture 90 %
```

---

## Session 2026-07-05 — Sprint 6 : Cache HTTP centralisé

### Objectif
Créer un cache HTTP mutualisé, indépendant de httpx, réutilisable par tous les futurs providers. Migrer OpenF1Source. Ajouter `--refresh` à la CLI.

### Travail effectué

**Module `motorsport_calendar/cache/`**
- `HttpCache` : cache disque JSON, TTL configurable (défaut 24h), clé SHA-256(url + params triés)
- API : `get_json(url, params, fetch, *, refresh)` / `invalidate()` / `clear()`
- Aucune dépendance httpx : le caller fournit la coroutine `fetch`
- Création automatique du dossier `.cache/`

**Migration OpenF1Source**
- Nouveaux paramètres : `cache: HttpCache | None`, `refresh: bool = False`
- Heuristique backward-compat : client injecté (tests) → cache désactivé par défaut → 45 tests existants non touchés
- `_get_json` : route via cache si présent, appel direct sinon

**CLI `generate-f1`**
- Ajout `--refresh` (boolean flag)
- Propagation `refresh=True` → `OpenF1Source(refresh=True)` → `HttpCache.get_json(refresh=True)`

**Tests**
- 24 tests unitaires `HttpCache` (miss, hit, expiry, refresh, corruption, invalidate, clear)
- 4 tests CLI `--refresh` (exit 0, fichier créé, flag propagé True/False)
- 45 tests OpenF1Source : aucune modification, tous passants

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/cache/__init__.py` | Créé |
| `motorsport_calendar/cache/http_cache.py` | Créé |
| `motorsport_calendar/providers/formula1/sources/openf1.py` | Modifié — ajout cache + refresh |
| `motorsport_calendar/cli.py` | Modifié — ajout `--refresh` |
| `tests/test_http_cache.py` | Créé — 24 tests |
| `tests/test_cli_generate_f1.py` | Modifié — 4 tests --refresh |
| `.gitignore` | Modifié — ajout `.cache/` |
| `docs/AI_CONTEXT.md` | Mis à jour |
| `docs/JOURNAL.md` | Mis à jour |
| `docs/DECISIONS.md` | ADR-008 ajouté |
| `docs/TODO.md` | Mis à jour |

### Bugs rencontrés
Aucun. La heuristique "client injecté = cache désactivé" a permis d'éviter de toucher les 45 tests existants.

### Tests exécutés
```
158 passed — 0 failed — couverture 89 %
```

---

## Session 2026-07-05 — Phase 7 + documentation initiale

### Objectif
Finaliser le MVP Formula 1 : commande CLI `generate-f1` + tests d'intégration + documentation projet.

### Travail effectué

**Phase 7 — CLI `generate-f1`**
- Ajout de la commande `motocal generate-f1 YEAR OUTPUT.ics` dans `motorsport_calendar/cli.py`
- Wiring complet : `OpenF1Source` → `Formula1Provider` → `IcsExporter`
- Gestion d'erreur : `httpx.HTTPStatusError` (exit 1) et `httpx.TimeoutException` (exit 1)
- Imports lazy pour ne pas ralentir le démarrage CLI
- 11 tests d'intégration créés dans `tests/test_cli_generate_f1.py`
  - Happy path : exit 0, fichier créé, `BEGIN:VCALENDAR`, N VEVENTs, localisations, saison vide
  - Error path : HTTP 4xx/5xx et timeout → exit 1, pas de fichier créé

**Documentation**
- Création du dossier `docs/` avec 6 fichiers :
  - `PROJECT_RULES.md` — règles d'architecture
  - `DECISIONS.md` — 7 ADRs documentant les choix techniques
  - `ROADMAP.md` — vision v0.1 → v1.0
  - `TODO.md` — backlog priorisé
  - `AI_CONTEXT.md` — état projet pour reprise IA
  - `JOURNAL.md` — ce fichier

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/cli.py` | Ajout commande `generate-f1` |
| `tests/test_cli_generate_f1.py` | Créé — 11 tests d'intégration |
| `docs/PROJECT_RULES.md` | Créé |
| `docs/DECISIONS.md` | Créé — 7 ADRs |
| `docs/ROADMAP.md` | Créé |
| `docs/TODO.md` | Créé |
| `docs/AI_CONTEXT.md` | Créé |
| `docs/JOURNAL.md` | Créé |

### Bugs rencontrés

1. **Test `test_event_summaries_contain_gp_names` échoue**
   - Cause : l'IcsExporter met `session.title` en SUMMARY (ex: "Race"), pas le nom du GP
   - Fix : remplacer l'assertion par un check sur le champ LOCATION (circuit name/city)

### Tests exécutés

```
130 passed — 0 failed — couverture 87 %
```

### Résultat du commit (à venir)
Voir section "Commit proposé" en bas de session.

---

## Session précédente (reconstituée depuis git)

### Phase 1 — Scaffold
- `pyproject.toml`, CI GitHub Actions, structure de packages, `motocal` entry point

### Phase 2 — Modèles métier
- `Championship`, `Circuit`, `Session`, `Event`, `SessionType`
- Pydantic v2, `frozen=True`, validator `end > start` sur `Session`

### Phase 3 — EventStatus + event_uid
- Ajout de `EventStatus(StrEnum)` et champ `event_uid` dans `Event`

### Phase 4 — IcsExporter
- `IcsExporter` avec `icalendar`, 1 VEVENT par Session, `METHOD:PUBLISH`

### Phase 5 — Architecture F1
- `Formula1Provider`, `Formula1Source` (ABC), 4 stubs (OpenF1, Ergast, Official, Cached)

### Phase 6 — OpenF1Source
- Implémentation complète : `_get_json`, mapping meetings/sessions, 25 circuits IANA
- 45 tests unitaires avec mock HTTP stdlib uniquement
