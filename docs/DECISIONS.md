# DECISIONS.md — Architecture Decision Records

---

## ADR-024 — `gui/championship_assets.py` : registre central des identités visuelles

**Contexte**
Sprint 33. Objectif : afficher le logo officiel de chaque championnat à gauche du titre
dans `ChampionshipCard`, sans coder de chemin de fichier dans une vue ni de branche
`if championship_id == "formula1"` dans le composant. Recherche préalable (dans
`motorsport-calendar` et `BApps-Studio`, où vit le Brand Set) : **aucun fichier logo de
championnat n'existe dans le projet** — seuls les assets de la marque *Motorsport
Calendar* elle-même sont présents (et toujours au stade placeholder, non copiés). Décision
prise avec l'utilisateur : construire le registre "prêt à recevoir" plutôt que d'inventer
des fichiers factices faisant office de faux logos officiels.

**Décision**
Un module dédié, `gui/championship_assets.py`, expose un unique point d'entrée
`get_championship_asset(championship_id: str) -> ChampionshipAsset(logo_src: str | None)`.
`logo_src` est un chemin Flet-relatif (`"championships/formula1.png"`), résolu UNIQUEMENT
si le fichier existe réellement sur disque (`_ASSETS_DIR / filename`) ; sinon `None` — id
inconnu et id connu dont le logo n'a pas encore été livré produisent exactement le même
résultat, jamais distingué par l'appelant. `ChampionshipCard._header_title()` interroge ce
registre et rend soit un `ft.Text` nu (aucun logo — comportement strictement identique à
avant ce sprint pour tous les championnats aujourd'hui), soit un `ft.Row([ft.Image(...),
ft.Text(...)])`, logo en `theme.IconSize.LG` (24px, token déjà existant, aucun nouveau
token créé). Aucune branche par championnat dans le composant — la seule décision qu'il
prend est "un logo a été résolu ou non".

**Conséquences**
- Suit exactement le patron déjà validé pour le logo de l'app (`gui/assets/logo/
  README.md`, Sprint 26) : dossier `gui/assets/championships/` livré vide (`.gitkeep` +
  README documentant les fichiers attendus), aucune autre modification nécessaire le jour
  où un vrai logo est déposé — `get_championship_asset()` le détecte à l'exécution.
- Extensible sans casser l'appelant : une future couleur/icône par championnat serait un
  champ de plus sur `ChampionshipAsset`, jamais un second point d'entrée.
- Zéro impact visuel dans l'état actuel du dépôt (aucun fichier livré) — vérifié par les
  999 tests et un script de smoke-test direct ; le layout de `ChampionshipCard` reste
  pixel pour pixel identique tant qu'aucun logo n'est déposé.
- `assets_dir=` reste commenté dans `gui/app.py` (partagé avec le logo de l'app) — même un
  logo déposé ne se résoudra visuellement qu'après ce décommentage, hors périmètre de ce
  sprint (documenté comme limite, pas comme un défaut de cet ADR).

---

## ADR-023 — `gui/event_display.py` : normalisation des métadonnées, en amont de la carte

**Contexte**
Sprint 32. Les cartes de championnat affichaient des incohérences ("Belgian / Belgian /
🇧🇪 Belgique", "Unknown") sur F2/F3/F1 Academy mais pas F1. Investigation (voir JOURNAL,
session Sprint 32) : F1 (Jolpica/Ergast) fournit un nom de Grand Prix complet, un nom de
circuit distinct et un pays réel ; F2/F3/F1 Academy partagent tous les trois
`providers/support_series/f1calendar_base.py`, qui mappe `Circuit.name` sur le même
descriptif court que `Event.name` (dataset `sportstimes/f1`, plus pauvre, sans champ nom
de circuit dédié) — d'où le doublon. Le pays "Unknown" vient de tables de couverture
`_CIRCUIT_DATA` incomplètes, propres à chaque module support-series. Corriger cela dans
les providers est hors périmètre de ce sprint.

**Décision**
Un module dédié, `gui/event_display.py`, décide de tout ce qu'il faut afficher ou masquer
à partir d'un `Event` brut : `normalize_event_display(championship_id, event) ->
EventDisplayData(grand_prix_name, circuit_name: str | None, country: str | None)`. Quatre
règles, toutes dans ce seul module : (1) doublon Grand Prix/Circuit → une ligne ; (2)
circuit inconnu → `circuit.name` puis repli sur `circuit.city` puis `None` ; (3) pays
inconnu (sentinelle `"Unknown"` ou vide) → `None`, jamais affiché ; (4) nom de Grand Prix
absent → suffixe " Grand Prix" ajouté pour les séries à ce format (F1/F2/F3/F1 Academy,
jamais WEC), repli sur le nom du circuit, puis un texte générique en dernier recours.

`ChampionshipCardData.circuit_name`/`.country` deviennent `str | None` ; `build_
championship_card` (le composant, Sprint 30) se contente d'omettre une ligne dont la
valeur est `None` — une simple omission conditionnelle, pas une décision. Le composant ne
contient toujours aucune logique métier ; toute la logique vit dans `event_display.py`.

**Conséquences**
- Corrige le défaut à la source des DONNÉES affichées sans toucher aux providers : la
  bonne valeur (`circuit.city`, souvent un meilleur nom de circuit pour F2/F3/F1 Academy)
  était déjà présente sur le modèle, seul le choix d'affichage était mauvais.
- `country_label()` (Sprint 29, formatage drapeau+nom FR) déménage de
  `upcoming_weekend.py` vers `event_display.py`, qui est désormais le seul endroit
  responsable de "quelle métadonnée d'événement afficher".
- Réutilisable par n'importe quelle future vue construisant des `ChampionshipCardData` à
  partir d'`Event` (Favoris, Recherche, Historique, ...) — la même normalisation
  s'applique automatiquement, sans dépendre de "Ce week-end".
- Limite assumée et documentée : pas de table démonyme complète ("Canada Grand Prix" au
  lieu de "Canadian Grand Prix") — jugée hors de proportion pour ce sprint.
- La couverture des tables `_CIRCUIT_DATA` par pays reste incomplète en amont — la ligne
  pays disparaît proprement plutôt que d'afficher "Unknown", mais un vrai pays
  n'apparaîtra pas tant que le provider (hors périmètre) n'est pas complété.

---

## ADR-022 — Layout System (`gui/components/layout/`) : en-tête toujours séparé du corps

**Contexte**
Sprint 31. Les 5 vues dupliquaient chacune la construction de leur conteneur de page, de
leur en-tête, de leurs espacements et de leur encartage — exactement le problème résolu
au niveau des cartes par ADR-021 (Sprint 30), mais au niveau de la page entière cette
fois. Objectif explicite : qu'une future page (Recherche, Tableau de bord, Notifications,
Historique, ...) se construise sans recréer ce code.

**Décision**
Sept composants à responsabilité unique dans `gui/components/layout/` : `PageContainer`
(largeur/padding/alignement, délègue à `theme.page_shell`), `PageHeader` (icône, titre,
sous-titre, séparateur), `Section` (espacement entre blocs), `SectionHeader` (intitulé
secondaire à l'intérieur d'une Section), `CardList` (liste verticale de cartes),
`EmptyState` (le "rien ici" encarté), `PageSpacing` (espace nommé ponctuel). Nommage
PascalCase délibéré (widget-style), avec exception `ruff.toml` scopée (`N802` sur ce seul
paquet) plutôt que des `noqa` dispersés.

Choix structurant : `PageHeader` est **toujours** un composant séparé, jamais absorbé
dans une carte de contenu — y compris pour Favoris et Ce week-end (vide), qui absorbaient
leur titre dans la carte depuis le Sprint 28 pour éviter un doublon visuel. Ce choix est
révisé ici : une future page avec un en-tête ET un contenu variable (ex. Recherche : titre
+ barre de recherche + résultats OU `EmptyState`) ne peut pas se permettre que son
`EmptyState` porte AUSSI le titre de la page — les deux responsabilités doivent rester
séparées dès maintenant, plutôt que de re-décorréler plus tard.

**Conséquences**
- Le titre de "Ce week-end" et "Mes favoris" apparaît désormais au-dessus de la carte
  plutôt qu'à l'intérieur — changement visuel mineur, assumé et documenté (voir JOURNAL,
  session Sprint 31).
- Les lignes de Préférences retrouvent leur bordure individuelle : la carte englobante
  unique du Sprint 28 (qui rendait cette bordure redondante) n'existe plus, chaque ligne
  redevient sa propre carte via `CardList` sans double encadrement.
- `championship_card.py` (Sprint 30) reste à sa place actuelle dans `gui/components/` —
  pas de réorganisation en sous-dossiers pour "faire symétrique" avec `layout/`, qui
  aurait été un remaniement sans bénéfice fonctionnel.
- `SectionHeader` est construit sans consommateur actuel — seul composant du sprint dans
  ce cas, justifié par une demande explicite du brief (nommé dans la liste des composants
  à créer), verrouillé par tests, prêt pour la première page à plusieurs groupes de cartes.
- Toute nouvelle page suit désormais le même moule :
  `PageContainer(header=PageHeader(...), body=[Section(...)])` — verrouillé par
  `TestLayoutSystemIntegration` (`tests/test_gui_components_layout.py`), qui construit une
  page hypothétique ("Historique", 2 sections avec `SectionHeader` + `CardList` chacune)
  sans aucun code de mise en page manuel, preuve directe de l'objectif du sprint.

---

## ADR-021 — `gui/components/` : bibliothèque de composants, séparée des vues et du thème

**Contexte**
Sprint 30. Jusqu'ici, chaque vue (`gui/views/*.py`) construisait entièrement son propre
layout à partir des primitives de `theme.py` (`card()`, `section_title()`, ...). "Ce
week-end" a le premier vrai besoin de layout réutilisable : une carte "événement d'un
championnat" qui devra réapparaître à l'identique dans Favoris, Recherche, Tableau de
bord, Calendrier, Notifications et Historique. Continuer à la reconstruire dans chaque
vue aurait garanti une dérive visuelle progressive (exactement le problème résolu au
Sprint 27 pour les pages, mais au niveau des cartes cette fois).

**Décision**
Nouveau paquet `motorsport_calendar/gui/components/`, distinct de `gui/views/` (une page =
un module, propriétaire de son état) et de `gui/theme.py` (tokens et primitives bas niveau
sans opinion sur le contenu). Un composant :
1. Définit son propre modèle de données minimal, déjà mis en forme (chaînes françaises,
   heures déjà converties) — jamais un objet du domaine (`Event`, `Session`, `Championship`,
   `Circuit`) ni un concept métier ("week-end", "favori", ...).
2. Se construit uniquement à partir des primitives de `theme.py` — aucun nouveau token.
3. Expose un point d'extension explicite (ici `footer: ft.Control | None`) plutôt que
   d'anticiper des fonctionnalités non demandées — le composant place le contrôle fourni
   sans jamais l'interpréter.

Premier composant : `championship_card.py` (`ChampionshipCardData`, `SessionRow`,
`build_championship_card`). Son modèle remplace `upcoming_weekend.WeekendCard`/`SessionRow`,
qui remplissaient déjà exactement ce rôle mais vivaient dans un module couplé au concept
"Ce week-end" — désormais promus à un emplacement neutre, `upcoming_weekend.py` les importe
au lieu de les définir.

**Conséquences**
- `views/weekend.py` ne construit plus aucun layout de carte : `_found_state` produit une
  liste de `build_championship_card(card)` — exactement l'attente exprimée ("la vue devra
  simplement construire une liste de ChampionshipCard").
- Une future vue Favoris/Recherche/Tableau de bord n'a qu'à produire des
  `ChampionshipCardData` depuis sa propre source de données (favoris sauvegardés, résultats
  de recherche, ...) et appeler `build_championship_card` — aucune modification au
  composant nécessaire.
- Ajouter un bouton Favori/Notifications/Export/Partage/Résultats plus tard se fait en
  construisant le contrôle du footer dans l'appelant et en le passant à
  `build_championship_card(data, footer=...)` — pas de changement de signature.
- 23 tests dédiés (`tests/test_gui_components_championship_card.py`) verrouillent l'ordre
  de l'en-tête, l'alignement de la grille de sessions (indépendant de la longueur du
  libellé), le comportement du footer (absent par défaut, extensible sans interprétation),
  et le rendu pour les 5 championnats actuels + un événement de forme différente (24h du
  Mans) — preuve directe de réutilisabilité, pas seulement de non-régression.

---

## ADR-020 — `WeekendEntry` : transporter l'id de championnat plutôt que le déduire

**Contexte**
Sprint 29 — "Ce week-end" doit regrouper les événements du week-end trouvé par catégorie
(Formula puis Endurance, via `categories.get_groups_for`) et afficher un nom lisible
(`display_names.get_display_name`). Ces deux fonctions attendent l'id brut du registre
(`"formula1"`, `"wec"`, …). En développant avec de vraies données (pas seulement des
fixtures), le regroupement échouait silencieusement : tout finissait dans le groupe
"Autres" de secours de `get_groups_for`.

**Cause racine**
Chaque provider construit ses `Event` avec un `Championship.id` suffixé par l'année —
`f"{cid}-{year}"` (`"formula1-2026"`, `"f1-academy-2026"`, …), visible dans
`jolpica.py::_make_championship`, `f1calendar.py::_make_championship` (F2/F3/F1 Academy).
Ce n'est pas un bug de ces providers : c'est un identifiant de *saison*, cohérent avec son
usage existant (`Formula1Provider.fetch_championship` produit le même format). Mais rien
dans le reste de la GUI n'avait encore eu besoin de comparer cet id à l'id du registre —
`generate_calendar`/`list_championships` ne le font jamais.

**Décision**
`upcoming_weekend.WeekendEntry(championship_id, event)` — le contrôleur, qui connaît déjà
l'id du registre au moment de l'appel (`for cid in WEEKEND_CHAMPIONSHIP_IDS: ...
await provider.fetch_events(cid, year)`), l'attache explicitement à chaque événement
récupéré. Toute la logique de recherche/regroupement/affichage de `upcoming_weekend.py`
lit `entry.championship_id`, jamais `entry.event.championship.id`.

**Conséquences**
- Aucune modification aux providers ni aux modèles métier — la correction reste
  entièrement côté GUI, conforme à la contrainte du sprint.
- `test_championship_id_comes_from_the_entry_not_the_event` (`test_gui_upcoming_weekend.py`)
  verrouille explicitement la régression : construit un événement dont l'id diffère
  volontairement de l'id de registre, vérifie que la carte utilise bien ce dernier.
- Règle pour les futures fonctionnalités GUI qui agrègent plusieurs championnats : ne
  jamais supposer que `Event.championship.id` égale l'id du registre — le transporter
  explicitement depuis l'appelant, comme `WeekendEntry`.
- Effet de bord découvert au passage : `ProvidersConfig.formula1` défaut sur la source
  `"openf1"` (pas `"jolpica"`, pourtant enregistrée en premier) — déjà le comportement de
  `generate_calendar`, simplement jamais remarqué faute de test F1 dans
  `test_gui_controller.py` avant ce sprint.

---

## ADR-019 — Grille de page unique (`theme.page_shell`) pour toutes les vues GUI

**Contexte**
Sprint 27. Après validation visuelle du Design System (Sprint 26), incohérence constatée :
Ce week-end / Mes favoris / À propos centraient tout leur contenu au milieu de l'écran,
tandis que Mon calendrier / Préférences étaient alignés à gauche. Chaque vue construisait
son propre `Container(padding=..., alignment=...)` — rien n'empêchait la dérive.

**Décision**
Une seule fonction, `theme.page_shell(*sections)`, rend toutes les vues. Elle centre
*uniquement* un conteneur à largeur plafonnée (`MAX_CONTENT_WIDTH = 1000`, dans la
fourchette 900–1100 px demandée) horizontalement dans la fenêtre ; à l'intérieur, une
`Column` unique en `horizontal_alignment=STRETCH` fait remplir la largeur du gabarit à
toute carte/formulaire sans jamais centrer le contenu lui-même. Les 5 vues (`weekend.py`,
`calendar.py`, `favorites.py`, `preferences.py`, `about.py`) appellent cette fonction avec
la liste de leurs sections (`section_title` + `Divider` + contenu propre à la page) au lieu
de construire leur propre conteneur racine.

**Conséquences**
- Un futur changement de largeur max, de padding ou d'alignement se fait à un seul endroit ;
  aucune vue ne peut plus dériver silencieusement vers un layout différent.
- `TestAllViewsShareTheSameGrid` (`tests/test_gui_views.py`) construit les 5 vues et vérifie
  qu'elles partagent strictement la même largeur, le même centrage externe, le même
  alignement interne et le même padding — verrou anti-régression direct sur l'exigence
  "même gabarit partout".
- Le rétrécissement responsive sur fenêtre étroite ne nécessite aucun recalcul manuel :
  `ft.Container(width=MAX_CONTENT_WIDTH)` sous un parent `alignment=TOP_CENTER` est
  automatiquement bridé par les contraintes du parent quand l'espace disponible est
  inférieur à 1000 px (comportement standard `BoxConstraints.enforce` de Flutter).
- Mon calendrier perd son en-tête custom (logo + nom de l'app) au profit du même
  `section_title` que les autres pages, pour une uniformité réelle des titres — le
  placeholder logo (ADR-018) reste sur la page À propos.
- Aucun changement à `GenerateState`, `CalendarViewControls` ou aux handlers de
  `main_view.py` : uniquement le conteneur racine retourné par chaque `build_*_view()`.

---

## ADR-018 — Design system `gui/theme.py` + assistant par étapes pour "Mon calendrier"

**Contexte**
Sprint 26 — Release Alpha Phase 2. Le brief produit interdit toute couleur codée en dur
dans les vues et demande de transformer "Mon calendrier" en parcours guidé, sans toucher
au moteur ni aux pages Ce week-end / Mes favoris / Préférences au-delà de leur habillage
visuel. Le Brand Set Motorsport Calendar v1.0 est validé (voir `BApps-Studio/03-Products/
Motorsport-Calendar/Branding/Branding.md`) mais ses SVG définitifs ne sont pas encore
livrés dans ce dépôt.

**Décision**
1. Un seul module, `motorsport_calendar/gui/theme.py`, porte toutes les couleurs
   (`BAppsColors`, `MotorsportColors`, puis `Colors` en rôles sémantiques), les échelles
   d'espacement/rayon/icône/typo, et les constructeurs de composants partagés
   (`card()`, `chip()`, `button_style()`, `page_padding()`, `section_title()`,
   `logo_placeholder()`). Toute vue qui a besoin d'une couleur ou d'une taille importe
   ces tokens — jamais `ft.Colors.*` ni un entier brut directement.
2. "Mon calendrier" (`gui/views/calendar.py`) devient un assistant à 4 étapes (saison →
   championnats → destination → créer) au lieu d'un formulaire long. La navigation avant
   est gatée par la validité de l'étape courante (`GenerateState.can_advance()`) ; le
   retour et le clic sur une puce d'étape déjà visitée sont toujours autorisés.
3. `logo_placeholder()` matérialise l'emplacement du futur logo (nav/À propos/en-tête du
   wizard) sans qu'aucun SVG définitif soit copié dans le dépôt — voir
   `gui/assets/logo/README.md`.

**Conséquences**
- Un changement de palette de marque ne touche plus qu'un seul fichier.
- `GenerateState` gagne `current_step`/`step_valid`/`can_advance`/`can_go_back` — logique
  de wizard 100 % testable sans Flet, comme le reste de `models.py`.
- `calendar.py` reste un module de layout pur : `main_view.py` continue de porter tout
  l'état et les handlers, conformément à la règle établie au Sprint 25.
- Effet de bord positif : centraliser les couleurs a fait apparaître (et corrigé en un
  seul endroit) l'usage de noms `ft.Colors.WHITE12/30/38/54/60/70` dépréciés depuis
  Flet 0.85 — remplacés par `WHITE_12/30/38/54/60/70`.
- Le remplacement du vrai logo, quand les SVG seront livrés, se limite à modifier
  `logo_placeholder()`'s call sites listés dans `gui/assets/logo/README.md` — aucun
  rework de layout attendu.

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

**Mise à jour 2026-07-06 (Sprint 21.2)** :
Audit Sprint 21.1 révèle un renommage de clés dans le dataset à partir de 2025 :
- `"fp1"` → `"practice"`
- `"sprintRace"` → `"sprint"`

F3 utilisait déjà `"practice"` et `"sprint"` depuis 2022 — le dataset a donc aligné F2 sur F3.
Conséquence : les calendriers F2 2025+ n'exportaient que 2 sessions sur 4 (qualifying + feature).

Correction : `_SESSION_MAP` inclut désormais les deux formes pour chaque clé renommée.
Les deux anciennes clés (`fp1`, `sprintRace`) sont conservées pour la rétrocompatibilité des
saisons 2024 et antérieures. Si un event contient à la fois `fp1` et `practice` (impossible
en pratique), les deux seraient exportés — un UID collision ICS en résulterait, mais cela
ne se produit pas dans le dataset réel.

---

## ADR-016 — F1 Academy : mapping SessionType contraint par l'absence de RACE2/RACE3

**Contexte**
F1 Academy court un format à trois courses par week-end (`race1`, `race2`, `race3`) depuis 2023.
Le format est le suivant :
- `fp1` / `fp2` : deux séances d'entraînement
- `qualifying1` (et `qualifying2` en 2023-2024) : qualifications
- `race1` / `race2` : courses sprint (~30 min chacune)
- `race3` : course principale (~30 min)

Le problème : `SessionType` ne possède pas de valeurs `RACE2` / `RACE3`. Si `race1`, `race2`
et `race3` sont tous mappés à `SessionType.RACE`, l'ICS généré contiendra trois VEVENTs
avec le même UID (`event_uid-RACE`) — ce qui viole RFC 5545 et provoque des collisions
dans les clients calendrier (un seul event visible sur trois).

**Décision**
Contrainte du sprint : "Aucun changement des modèles métier" → on ne peut pas ajouter
`RACE2`/`RACE3` à l'enum `SessionType`.

Mapping retenu pour garantir l'unicité des UIDs :
- `race1` → `SessionType.SPRINT`   "Race 1"  (sprint = course courte ✓)
- `race2` → `SessionType.FP3`      "Race 2"  (workaround — FP3 = type disponible non utilisé ailleurs)
- `race3` → `SessionType.RACE`     "Race 3"  (course principale ✓)

Le champ `title` affiché dans le calendrier est correct ("Race 1", "Race 2", "Race 3").
Le `type` FP3 n'est visible qu'en interne (logs, filtrage programmatique).

**Conséquences**
- Aucun UID en collision — calendrier RFC 5545 valide. ✓
- Les titres des sessions sont corrects pour l'utilisateur final. ✓
- Le type FP3 pour "Race 2" est sémantiquement incorrect — confusant pour les développeurs
  qui filtrent par `session.type == SessionType.FP3`.
- **Recommandation pour une prochaine version** : ajouter `RACE2 = "RACE2"` et
  `RACE3 = "RACE3"` à `SessionType` (changement purement additif, zéro régression),
  puis mettre à jour ce mapping.

---

## ADR-015 — Formula 3 : source f1calendar.com JSON, clés de sessions différentes de F2

**Contexte**
Le dataset `sportstimes/f1` couvre aussi F3 avec le même pattern d'URL
(`_db/f3/{year}.json`) et la même licence MIT. La question était de savoir si
les clés de sessions F3 sont identiques à celles de F2.

**Décision**
Utiliser `https://raw.githubusercontent.com/sportstimes/f1/main/_db/f3/{year}.json`
comme source primaire via `F1CalendarSource(F1CalendarBaseSource, Formula3Source)`.

Les clés de sessions F3 confirmées (2022-2025) différent de F2 sur deux points :
- `"practice"` (F3) au lieu de `"fp1"` (F2) → `SessionType.FP1`, 45 min
- `"sprint"` (F3) au lieu de `"sprintRace"` (F2) → `SessionType.SPRINT`, 30 min
- `"qualifying"` identique → `SessionType.QUALIFYING`, 30 min
- `"feature"` identique → `SessionType.RACE`, 40 min (vs 65 min pour F2)

Les saisons antérieures à 2022 utilisaient `"race1"/"race2"/"race3"` — ces sessions
ne sont pas mappées et sont silencieusement ignorées.

F3 ne couvre que les circuits F1 européens + Bahreïn + Melbourne (13 slugs connus).

**Conséquences**
- `F3CalendarSource` : uniquement `_series_key`, `_session_map`, `_circuit_data`,
  `_make_championship` — 4 overrides, ~50 lignes en tout (dont 13 entrées circuit).
- Aucune fonction module-level de backward-compat (F3 n'a pas de tests hérités qui
  importent directement ces helpers).
- Mutualisation : ~85 % de la logique héritée de `F1CalendarBaseSource`.

---

## ADR-017 — Dataset `sportstimes/f1` : clé `"races"`, pas `"events"`

**Contexte**
Sprint QA-03 — audit de l'environnement réel (`python -m motorsport_calendar generate 2026`).
F2, F3 et F1 Academy retournaient systématiquement 0 événements depuis l'introduction du
Support Series Framework (Sprint 14). La commande `generate 2026` produisait 26 événements
F1 mais 0 pour chaque série support.

**Cause racine**
`F1CalendarBaseSource._get_season()` lisait `raw.get("events", [])`. Mais le dataset
`sportstimes/f1` sur GitHub (source officielle, MIT) utilise `"races"` comme clé de premier
niveau — pas `"events"`. Le payload réel ressemble à :
```json
{ "races": [ { "name": "...", "sessions": {...} } ] }
```
Les tests unitaires et d'intégration utilisaient eux-mêmes la clé `"events"` dans leurs
fixtures (copié/collé du code incorrect), masquant le bug pendant tout le développement.

**Décision**
1. `f1calendar_base.py` ligne 111 : `raw.get("events", [])` → `raw.get("races", [])`.
2. Toutes les fixtures de test (`test_f1calendar_base.py`, `test_f1calendar_source.py`,
   `test_cli_generate_f2.py`, `test_cli_generate_f3.py`, `test_cli_generate_f1_academy.py`)
   corrigées (`"events"` → `"races"`).
3. Ajout de `tests/fixtures/real/` : extraits minimaux (2 événements) tirés directement
   du dataset réel GitHub (F2, F3, F1 Academy — saison 2025). Ces fixtures sont la
   référence de vérité : si le dataset change de structure, les tests `test_real_fixtures.py`
   le détectent immédiatement.
4. `TestRacesKeyRegression` dans `test_f1calendar_base.py` : 3 tests qui documentent et
   protègent ce comportement (`"races"` lu, `"events"` ignoré, les deux présents → seul
   `"races"` est lu).

**Règle pour les futurs tests**
Toute fixture mock renvoyée par `fetch_json` doit utiliser `{"races": [...]}`.
Ne jamais utiliser `{"events": [...]}` — c'est silencieusement ignoré.

**Conséquences**
- F2/F3/F1 Academy retournent maintenant les données réelles en production. ✓
- 627 tests passent (16 nouveaux).
- `tests/fixtures/real/` : référence vivante du format dataset — à mettre à jour si la
  structure du dataset `sportstimes/f1` change.
- **Comment éviter que cela se reproduise** : les nouveaux providers support series
  doivent ajouter une fixture dans `tests/fixtures/real/` et un test `test_real_fixtures.py`
  AVANT d'écrire la moindre fixture mock. Vérifier le dataset réel en premier.

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
