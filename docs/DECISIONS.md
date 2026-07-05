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
