# AI_CONTEXT.md

> Fichier de reprise rapide pour une IA. Mis à jour après chaque session.
> Dernière mise à jour : 2026-07-05

---

## État du projet

- **Nom** : motorsport-calendar
- **Version** : 0.1.0 (alpha)
- **Phase** : Sprint 9 — ProviderRegistry terminé
- **Tests** : 250 passants, 0 échouants — couverture 93 %
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
│   │       ├── openf1.py    # ✅ IMPLÉMENTÉ — API openf1.org + HttpCache
│   │       ├── ergast.py    # 🔴 STUB — raise NotImplementedError
│   │       ├── official.py  # 🔴 STUB — raise NotImplementedError
│   │       └── cached.py    # 🔴 STUB — raise NotImplementedError
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
│   ├── __init__.py          # export ProviderRegistry + registry singleton
│   ├── registry.py          # ✅ ProviderRegistry — register/get/list_all/enabled/discover
│   └── service.py           # 🔴 NON IMPLÉMENTÉ — placeholder
│
├── exporters/
│   ├── base.py              # Exporter (ABC) — export / export_to_string
│   └── ics.py               # ✅ IMPLÉMENTÉ — RFC 5545, 1 VEVENT par Session
│
├── cli.py                   # Typer CLI — generate-f1 (--refresh), providers, export (stub)
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

---

## Fonctionnalités en cours / prochaines

**Prochaines tâches recommandées** :

1. **CLI `generate-wec YEAR OUTPUT.ics`** — utilise `registry.get("wec")`, symétrique à `generate-f1`
2. **CLI `generate YEAR OUTPUT.ics`** — itère `registry.enabled(config.providers)`, merge tous les ICS
3. **Implémenter `OfficialWecSource`** — endpoint `fiawec.com` (investigation API/scraping nécessaire)

Endpoint : `https://ergast.com/api/f1/{year}/races.json`
Fichier cible : `motorsport_calendar/providers/formula1/sources/ergast.py`
Tests cibles : `tests/test_ergast_source.py`

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
- **ProviderRegistry** : singleton `motorsport_calendar.core.registry.registry`. Providers s'enregistrent via leur `__init__.py`. CLI appelle `registry.discover()` puis `registry.get("formula1")` → factory `(cfg, cache, refresh) → Provider`.
- **Auto-enregistrement** : importer n'importe quoi de `providers/formula1/` suffit à déclencher `formula1/__init__.py` → registration. `discover()` force l'import si rien n'a encore été importé (cold start CLI).
- **ProviderConfig** : `enabled: bool = True` (opt-out), `source: str = ""` (optionnel — factory fallback vers sa valeur par défaut si vide).
- **ProvidersConfig.get(id)** : cherche dans les champs nommés (`formula1`, `wec`) puis dans `model_extra` (providers YAML extra). Retourne `None` si absent (= activé par défaut dans `registry.enabled()`).
- **Source selection** : factory du provider sélectionne la source depuis `cfg.source` — source inconnue → `ValueError` → CLI exit 1 avec message clair.

---

## Dette technique

| Item | Impact | Priorité |
|---|---|---|
| `export` CLI est un stub (exit 1) | Commande inutilisable | HAUTE |
| `ErgastSource` non implémentée | Pas de données historiques | HAUTE |
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
