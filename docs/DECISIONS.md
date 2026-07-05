# DECISIONS.md — Architecture Decision Records

---

## ADR-001 — Pydantic v2 avec `frozen=True` pour tous les modèles

**Contexte**
Les modèles de calendrier (Event, Session, Circuit…) sont produits par des providers et consommés par des exporteurs. Ils ne doivent jamais être mutés après création.

**Décision**
Tous les modèles héritent de `pydantic.BaseModel` avec `model_config = ConfigDict(frozen=True)`.
Les collections utilisent `tuple[T, ...]` et non `list[T]` : `frozen=True` interdit la réassignation du champ mais pas la mutation d'une liste.

**Conséquences**
- Les modèles sont hashables et thread-safe.
- La validation Pydantic garantit les invariants à la construction.
- Les tests peuvent comparer des modèles par valeur (`==`).

---

## ADR-002 — Architecture Provider / Source par injection de dépendance

**Contexte**
Plusieurs sources de données F1 existent (OpenF1, Ergast, site officiel). Le provider ne doit pas être couplé à une source spécifique.

**Décision**
`Formula1Provider` reçoit une `Formula1Source` (ABC) au constructeur.
La source effectue tous les appels réseau et le parsing ; le provider ne fait que déléguer.

**Conséquences**
- On peut changer de source sans toucher au provider.
- Les sources sont testables indépendamment.
- L'ajout d'un `CachedFormula1Source` (décorateur) ne nécessite pas de modifier le provider.

---

## ADR-003 — `httpx` pour tous les appels HTTP asynchrones

**Contexte**
Les sources doivent appeler des API REST de manière asynchrone et être testables sans réseau.

**Décision**
Utiliser `httpx.AsyncClient` injecté optionnellement au constructeur de chaque Source.
En production, la Source crée son propre client avec les bons timeouts.
En test, un mock est injecté directement.

**Conséquences**
- Zéro appel réseau en CI.
- Timeout configuré à 10 secondes (constante `_TIMEOUT` dans chaque source).
- `httpx.HTTPStatusError` et `httpx.TimeoutException` sont les seules exceptions HTTP propagées.

---

## ADR-004 — `icalendar` pour la génération ICS (RFC 5545)

**Contexte**
Le format de sortie principal est `.ics` (iCalendar). Il faut respecter strictement RFC 5545 pour la compatibilité Google Calendar / Apple Calendar / Outlook.

**Décision**
Utiliser la bibliothèque `icalendar` (≥ 5.0). Un VEVENT est généré par Session (et non par Event/weekend).

**Conséquences**
- Compatibilité maximale avec les clients calendrier.
- `METHOD:PUBLISH` est ajouté pour indiquer un flux en lecture seule.
- Les datetimes timezone-aware sont sérialisés correctement par la lib.

---

## ADR-005 — `asyncio.run()` comme pont sync→async dans la CLI

**Contexte**
La CLI Typer est synchrone. Les providers sont async. Il faut un pont.

**Décision**
Chaque commande CLI crée une coroutine interne `_fetch()` et l'exécute avec `asyncio.run()`.
Pas de framework async au niveau CLI (pas de `anyio`, pas de `click-asyncio`).

**Conséquences**
- La CLI reste simple et sans dépendances supplémentaires.
- `asyncio.run()` crée un nouveau loop à chaque appel de commande — acceptable pour un outil CLI.
- Les tests CLI utilisent `CliRunner` (synchrone) sans conflit de loop.

---

## ADR-006 — `unittest.mock` uniquement pour les mocks HTTP

**Contexte**
Des bibliothèques comme `respx` ou `pytest-httpx` facilitent le mock HTTP mais ajoutent des dépendances.

**Décision**
Utiliser uniquement `unittest.mock.AsyncMock` + `MagicMock`. Le client httpx est soit injecté directement (tests OpenF1Source), soit patché via `patch.object` sur `_get_json` (tests CLI).

**Conséquences**
- Zéro dépendance de test supplémentaire.
- Les mocks sont explicites et lisibles.
- Le pattern est cohérent dans tout le projet.

---

## ADR-007 — Timezone via mapping `circuit_short_name` → IANA

**Contexte**
L'API OpenF1 retourne des datetimes en UTC + un champ `gmt_offset` (string, ex: "+03:00"). Elle ne fournit pas de nom de timezone IANA.

**Décision**
Maintenir un dictionnaire statique `_CIRCUIT_TZ_MAP` dans `openf1.py` : 25 circuits → timezone IANA. Fallback : `"UTC"`. Les sessions sont converties dans le fuseau local du circuit.

**Conséquences**
- Les VEVENTs ICS affichent les horaires locaux (meilleure UX).
- Le dict doit être maintenu manuellement quand un nouveau circuit apparaît.
- Fallback UTC évite un crash sur un circuit inconnu.

---

## ADR-008 — Cache HTTP centralisé indépendant de httpx

**Contexte**
Sans cache, chaque exécution de `motocal generate-f1` effectue 2 appels HTTP à OpenF1. Les futurs providers (Ergast, MotoGP…) auraient le même problème. Un cache ad hoc dans chaque provider violerait le principe DRY.

**Décision**
Créer `motorsport_calendar/cache/HttpCache` : cache disque JSON avec TTL.
L'API reçoit une coroutine `fetch` (pas d'httpx.AsyncClient) pour rester indépendant de la bibliothèque HTTP.
`OpenF1Source` active le cache uniquement si aucun client custom n'est injecté (heuristique "client injecté = mode test").
Option `--refresh` en CLI propage `refresh=True` jusqu'au cache.

**Conséquences**
- Tous les futurs providers utilisent `HttpCache` sans code supplémentaire.
- Les tests existants (`OpenF1Source(client=mock)`) ne nécessitent aucune modification.
- Le cache est dans `.cache/` (CWD) — simple mais pas idéal pour un outil installé globalement (dette technique documentée).
- `invalidate()` et `clear()` disponibles pour les cas avancés.

---

## ADR-009 — `ConfigService` + Pydantic pour la configuration centrale

**Contexte**
Plusieurs valeurs étaient codées en dur : chemin du cache (`.cache/`), TTL (86400s), alarm ICS, source F1. Avec l'ajout de WEC et des futures disciplines, la configuration doit être externalisée.

**Décision**
Créer `motorsport_calendar/config/` avec :
- Modèles Pydantic v2 `frozen=True` pour chaque section (`CacheConfig`, `IcsConfig`, `ProviderConfig`, `ProvidersConfig`, `AppConfig`)
- `ConfigService` qui lit `config.yaml` (CWD → `~/.config/…` → défauts)
- `config.yaml` dans `.gitignore`, `config.example.yaml` commité comme référence
- Dépendance : `pyyaml>=6.0`

**Conséquences**
- Plus aucun chemin ou TTL codé en dur dans les providers ou la CLI
- La sélection de source F1/WEC est pilotée par `providers.formula1.source` dans le YAML
- Pydantic valide la configuration au démarrage — erreur claire si malformée
- Le VALARM ICS est configurable via `ics.alarm_minutes` (0 = désactivé)
- Les tests passent un `config_path` explicite pour l'isolation

---

## ADR-012 — SourceRegistry : inversion de responsabilité source → registre

**Contexte**
Après le Sprint 9, la factory du provider connaissait ses sources (`if source == "openf1": ...`). Chaque nouvelle source (Ergast, Jolpica, Official) aurait ajouté un `elif`. Violation du principe ouvert/fermé.

**Décision**
Créer `motorsport_calendar/core/source_registry.py` avec un `SourceRegistry` singleton, symétrique au `ProviderRegistry`.
Chaque `providers/X/sources/__init__.py` enregistre ses sources :
```python
source_registry.register("formula1", "openf1", lambda cache, refresh: OpenF1Source(...))
```
La factory provider devient triviale : `_make_provider(source) → Formula1Provider(source)`.
La CLI orchestre : `source = source_registry.get("formula1", "openf1")(cache, refresh)`.

**Conséquences**
- Ajouter une source F1 (Ergast, Jolpica…) = une ligne dans `formula1/sources/__init__.py`. Zéro autre modification.
- La factory provider ne connaît aucune source concrète.
- `source_registry.discover()` importe `providers/X/sources/` de chaque championnat.
- 24 tests unitaires + d'intégration couvrent le registre.

**Note** : cette ADR marque la fin des refactorings structurels. L'architecture Provider/Source/Registry est désormais figée. Les prochains sprints ajoutent des fonctionnalités.

---

## ADR-011 — ProviderRegistry : auto-enregistrement par import

**Contexte**
Avec F1 et WEC coexistant, la CLI commençait à contenir `if source == "openf1": ...` et devrait grossir à chaque nouveau championnat. Il faut découpler la CLI de la connaissance des providers.

**Décision**
Créer `motorsport_calendar/core/registry.py` avec un `ProviderRegistry` singleton.
Chaque `providers/X/__init__.py` s'enregistre automatiquement à l'import :
```python
registry.register("formula1", _make_provider)
```
La CLI appelle `registry.discover()` (qui importe tous les sous-paquets via `pkgutil.iter_modules`), puis `registry.get("formula1")` pour obtenir une factory.
Pour ajouter un championnat : créer `providers/elms/` avec son `__init__.py` — zéro autre modification.

**Conséquences**
- La CLI ne connaît aucun provider individuellement.
- `registry.enabled(config.providers)` filtre selon `enabled: bool` dans le YAML (logique opt-out : absent = activé).
- `ProviderConfig` gagne `enabled: bool = True` et `source: str = ""` (optionnel).
- `ProvidersConfig` gagne `extra="allow"` + méthode `get(championship_id)` pour les providers hors champs nommés.
- 25 tests unitaires + d'intégration couvrent le registre à 100 %.

---

## ADR-013 — Data Acquisition Layer : interfaces abstraites dans `core/datasource/`

**Contexte**
Les sources de données (`OpenF1Source`, `JolpicaSource`, futurs scrapers WEC/ELMS) mélangent
deux responsabilités distinctes : acquisition réseau brute (HTTP, HTML, ICS) et mapping vers
les modèles métier. À mesure que le nombre de sources grandit, ce couplage ralentit les tests
et rend l'ajout de nouvelles sources moins prévisible.

**Décision**
Créer `motorsport_calendar/core/datasource/` avec quatre classes abstraites :
- `DataSource(ABC)` — marqueur commun
- `JsonDataSource(DataSource)` — `@abstractmethod fetch_json(url, params) → list | dict`
- `HtmlDataSource(DataSource)` — `@abstractmethod fetch_html(url) → str`
- `IcsDataSource(DataSource)` — `@abstractmethod fetch_ics(url) → str`

Chaque source implémente l'interface de sa catégorie **en plus** de l'interface domaine
existante (`Formula1Source`, `WecSource`…). Aucun provider ni modèle ne change.

`OpenF1Source` migre vers `JsonDataSource` comme validation du concept :
`fetch_json` est l'implémentation réelle (HTTP + cache) ; `_get_json` reste comme wrapper
pour la rétrocompatibilité avec les mocks CLI existants.

**Conséquences**
- Chaque nouvelle source sait quelle interface de transport implémenter avant même de coder.
- Le DAL est testable indépendamment des modèles et providers.
- Les mocks CLI (`patch.object(OpenF1Source, "_get_json", ...)`) restent valides sans modification.
- `JolpicaSource`, `OfficialWecSource` etc. migrent vers leur interface DAL au moment de leur implémentation.
- 374 tests, 0 régression, couverture 93 %.

---

## ADR-015 — Support Series Framework : extraction de la base commune avant les sprints F3/Academy/Supercup

**Contexte**
F2 est implémentée. F3, F1 Academy, et Porsche Supercup utilisent le même dataset f1calendar
avec la même structure JSON. Si chaque provider répète le code HTTP/cache/mapping, un fix ou
une amélioration devra être répliquée N fois.

**Décision**
Extraire `F1CalendarBaseSource` dans `providers/support_series/f1calendar_base.py` AVANT
d'implémenter F3/Academy/Supercup. `F1CalendarSource` (F2) est refactorisée pour en hériter.

Les 4 propriétés abstraites de la base : `_series_key`, `_session_map`, `_circuit_data`,
`_make_championship(year)`. Tout le reste est fourni par la base.

Les fonctions module-level de `f1calendar.py` (F2-spécifiques) sont conservées pour les tests
existants — elles ne sont plus utilisées en production mais restent comme unités testables
de la config F2.

**MRO** : `F1CalendarSource(F1CalendarBaseSource, Formula2Source)` — base class en premier pour
que `get_season` et `fetch_json` de la base priment sur les méthodes abstraites de `Formula2Source`.

**Conséquences**
- F3/Academy/Supercup : ~15 lignes de code chacun (4 overrides, rien d'autre).
- Zéro changement de comportement pour F2.
- 484 tests, 0 régression, couverture 94 %.

---

## ADR-014 — Formula 2 : source f1calendar.com JSON (MIT) plutôt que scraping HTML

**Contexte**
Plusieurs sources sont envisageables pour le calendrier F2 (voir `DATA_SOURCES.md`) :
scraping HTML de `fiaformula2.com`, scraping de `formula2.com`, ou le dataset JSON MIT
maintenu par `sportstimes` sur GitHub (`github.com/sportstimes/f1`).

**Décision**
Utiliser `https://raw.githubusercontent.com/sportstimes/f1/main/_db/f2/{year}.json`
(dataset MIT, mis à jour manuellement, stable) comme source primaire via `F1CalendarSource`,
qui implémente `JsonDataSource`.

Raisons du choix :
- Format JSON structuré → implémente directement `JsonDataSource`, pas de parsing HTML fragile
- Licence MIT → utilisation libre, sans restriction
- Un seul GET par saison → compatible avec `HttpCache` sans changement
- Aucun scraping JavaScript ou authentification requise
- Réutilise exactement le même pattern d'injection de dépendance que `OpenF1Source`

**Conséquences**
- La source dépend d'un dépôt tiers maintenu bénévolement ; si le dépôt disparaît, un fallback
  vers `fiaformula2.com` (HTML) devra être implémenté comme source alternative.
- Les timestamps sont en UTC, les end-times sont inférés (même approche que `JolpicaSource`).
- `F1CalendarSource` n'a pas de wrapper `_get_json` (pas de legacy mocks à maintenir).
- 448 tests, 0 régression, couverture 93 %.

---

## ADR-010 — VALARM dans IcsExporter via `alarm_minutes`

**Contexte**
Les utilisateurs souhaitent des rappels calendrier avant chaque session motorsport.

**Décision**
`IcsExporter(alarm_minutes=N)` — si N>0, chaque VEVENT contient un composant VALARM `ACTION:DISPLAY` avec `TRIGGER:-PTNm`. Valeur lue depuis `config.ics.alarm_minutes`.

**Conséquences**
- Compatible RFC 5545 — fonctionne dans Google Calendar, Apple Calendar, Outlook
- Rétrocompatible : `IcsExporter()` sans argument = `alarm_minutes=0` = aucun VALARM
- Les tests existants (`IcsExporter()`) ne nécessitent aucune modification
