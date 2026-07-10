# JOURNAL.md

---

## Session 2026-07-07 — Sprint 33 : Registre des identités visuelles de championnat

### Objectif
Utiliser les logos officiels des championnats pour renforcer l'identité visuelle des
`ChampionshipCard`, via un registre central (`championship_id` → ressources visuelles),
sans jamais coder de chemin de fichier dans une vue ni de `if championnat == ...` dans le
composant. Aucune modification de l'architecture existante (providers, Design System,
navigation), aucun commit.

### Constat préalable — aucun logo officiel présent dans le projet
Avant d'écrire le registre, recherche exhaustive dans `motorsport-calendar` et dans
`BApps-Studio` (où vit le Brand Set) : **aucun fichier logo de championnat (F1, F2, F3,
F1 Academy, WEC) n'existe nulle part** — seuls les assets de la marque *Motorsport
Calendar* elle-même sont présents dans `BApps-Studio/03-Products/Motorsport-Calendar/
Branding/` (`mc-icon`, `logo-horizontal/vertical`, favicons), pas encore copiés dans
`gui/assets/logo/` (toujours au stade placeholder depuis le Sprint 26). Le dossier
`BApps-Studio/02-Brand/Logos/` est vide. La prémisse du brief ("logos déjà présents")
ne correspondait donc à rien de concret — clarifié avec l'utilisateur avant de coder :
option retenue = construire le registre "prêt à recevoir" (même patron que
`gui/assets/logo/README.md` pour le logo de l'app), aucun fichier factice n'étant traité
comme un vrai logo officiel.

### Travail effectué

**`motorsport_calendar/gui/championship_assets.py`** — nouveau module, registre central
- `ChampionshipAsset(logo_src: str | None)` — frozen, extensible (couleur/icône futurs
  ajouteraient un champ, jamais un nouveau point d'entrée)
- `get_championship_asset(championship_id: str) -> ChampionshipAsset` — point d'entrée
  unique : résout un chemin Flet-relatif (`"championships/formula1.png"`) UNIQUEMENT si
  le fichier existe réellement sur disque ; sinon `logo_src=None`, que ce soit parce que
  l'id est inconnu ou parce que le fichier n'a simplement pas encore été livré — les deux
  cas ne sont jamais distingués par l'appelant, jamais d'exception.
- `_LOGO_FILENAMES` — mapping purement descriptif id → nom de fichier attendu ; ajouter un
  logo demain = déposer le fichier au bon nom, aucune ligne de code à changer ailleurs.

**`motorsport_calendar/gui/assets/championships/`** — nouveau dossier (`.gitkeep` +
`README.md` documentant les 5 fichiers attendus et la procédure d'intégration, même
patron que `gui/assets/logo/README.md`). Aucun fichier image livré.

**`motorsport_calendar/gui/components/championship_card.py`**
- `_header_title(data)` : construit le titre — `ft.Text` seul si `get_championship_asset`
  ne renvoie aucun logo (état réel de tous les championnats aujourd'hui, donc layout
  strictement identique à avant ce sprint), sinon `ft.Row([ft.Image(...), ft.Text(...)])`
  avec le logo en `theme.IconSize.LG` (24px, déjà un token existant) aligné verticalement
  au centre avec le titre.
- Aucun `if championship_id == ...` : la seule branche est "un logo a été résolu ou non",
  jamais un championnat en particulier.
- `ft.BoxFit.CONTAIN` (pas `ft.ImageFit` — n'existe plus dans Flet 0.85.3 installé,
  détecté immédiatement par les tests).

**Tests**
- `tests/test_gui_championship_assets.py` — 11 tests : dataclass frozen, les 5 ids connus
  sans fichier livré → `None` (état réel du dépôt), id inconnu et id vide → `None` sans
  exception, résolution correcte quand un fichier est simulé (`monkeypatch` sur
  `_ASSETS_DIR` + `tmp_path`), un seul id résolu parmi plusieurs, id inconnu toujours
  `None` même si le dossier contient des fichiers.
- `tests/test_gui_components_championship_card.py` — 5 tests ajoutés (`TestChampionshipLogo`) :
  aucun logo livré → titre `ft.Text` nu inchangé, id inconnu ne casse pas le rendu, logo
  simulé → `ft.Row([Image, Text])` dans le bon ordre, taille du logo = `IconSize.LG`, le
  reste de l'en-tête (circuit/pays/sessions) inchangé par l'ajout du logo.

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/gui/championship_assets.py` | Créé — registre central |
| `motorsport_calendar/gui/assets/championships/.gitkeep` | Créé |
| `motorsport_calendar/gui/assets/championships/README.md` | Créé |
| `motorsport_calendar/gui/components/championship_card.py` | Modifié — logo dans l'en-tête |
| `tests/test_gui_championship_assets.py` | Créé — 11 tests |
| `tests/test_gui_components_championship_card.py` | Modifié — 5 tests ajoutés |
| `docs/JOURNAL.md` | Mis à jour |
| `docs/AI_CONTEXT.md` | Mis à jour |
| `docs/TODO.md` | Mis à jour |
| `docs/ROADMAP.md` | Mis à jour |
| `docs/DECISIONS.md` | ADR-024 ajouté |

`providers/`, `models/`, `theme.py`, `components/layout/`, navigation, `main_view.py`,
Design System : **non modifiés**.

### Tests exécutés
```
999 passed — 0 failed — couverture 95 %
(983 → 999 : +16 tests — championship_assets.py et championship_card.py tous à 100 %)
```

Vérification manuelle additionnelle : script direct instanciant `build_championship_card`
pour tous les championship_id connus + un id inconnu (`nascar`) + une chaîne vide — aucune
exception, titre rendu en `ft.Text` nu dans tous les cas (aucun logo livré dans le vrai
dépôt), confirmant que ce sprint est visuellement invisible tant qu'aucun fichier n'est
déposé — exactement le comportement voulu.

### Limites
- Aucun logo officiel livré : la fonctionnalité est architecturalement complète mais
  invisible en pratique tant que les fichiers PNG/SVG (F1, F2, F3, F1 Academy, WEC) ne
  sont pas déposés dans `gui/assets/championships/`.
- `assets_dir=` reste commenté dans `gui/app.py` (partagé avec le logo de l'app, hors
  périmètre de ce sprint) — même une fois un fichier déposé, `ft.Image(src=...)` ne se
  résoudra visuellement qu'après ce décommentage.
- Toujours aucun environnement graphique dans ce sandbox — vérifié par 999 tests unitaires
  (100 % sur les 2 fichiers concernés) + script de smoke-test direct, pas par capture
  d'écran.

---

## Session 2026-07-07 — Sprint 32 : Normalisation des métadonnées des événements

### Objectif
Nettoyer les incohérences observées dans les cartes de championnat ("Belgian / Belgian /
🇧🇪 Belgique", "Unknown") en définissant une règle d'affichage unique, appliquée par une
logique dédiée (`EventDisplayData`), en amont du composant `ChampionshipCard` qui ne
contient toujours aucune logique métier. Comprendre et documenter pourquoi F2/F3
n'affichent pas les mêmes informations que F1. Aucun changement aux providers, au Design
System ni à la navigation.

### Investigation — pourquoi F2/F3/F1 Academy affichent moins bien que F1

Données réelles capturées en interrogeant `get_upcoming_weekend()` pour le même week-end
(Grand Prix de Belgique) :

```
formula1 | event.name='Belgian Grand Prix' | circuit.name='Spa-Francorchamps'
         | circuit.city='Spa-Francorchamps' | circuit.country='Belgium'
formula2 | event.name='Belgian'             | circuit.name='Belgian'
         | circuit.city='Spa-Francorchamps' | circuit.country='Unknown'
formula3 | event.name='Australian'          | circuit.name='Australian'
         | circuit.city='Melbourne'         | circuit.country='Australia'
```

**Conclusion : deux causes indépendantes, ni un bug du modèle `Event`/`Circuit`, ni une
perte au parsing au sens strict — une vraie différence d'API, plus un choix de mapping
propre au code partagé F2/F3/F1 Academy.**

1. **Différence réelle d'API (externe, non corrigible sans toucher aux providers)** — F1
   utilise Jolpica/Ergast, qui fournit un `raceName` complet ("Belgian Grand Prix"), un
   `circuitName` réel et distinct ("Spa-Francorchamps"), une vraie localité et un vrai
   pays. F2/F3/F1 Academy utilisent tous les trois le dataset ouvert `sportstimes/f1`
   (f1calendar.com), confirmé nettement plus pauvre : chaque entrée n'a qu'un descriptif
   de manche court (`name`: "Belgian", "Australian" — jamais "Grand Prix"), un `location`
   (qui se rapproche en réalité plus d'un nom de circuit que d'une ville — "Spa-
   Francorchamps", "Yas Marina") et un `slug`. **Il n'existe tout simplement aucun champ
   "nom de circuit" ni "pays" dédié dans ce dataset.**
2. **Un choix de mapping dans notre propre code** (`providers/support_series/
   f1calendar_base.py::_build_circuit`, code PARTAGÉ par F2/F3/F1 Academy) —
   `Circuit.name` y est rempli avec exactement le même descriptif court que `Event.name`,
   ce qui explique le doublon "Belgian / Belgian". Le champ `location` (mappé sur
   `Circuit.city`) est en réalité un bien meilleur candidat pour le nom de circuit, mais
   n'est pas utilisé à cette fin. Ceci est corrigible (côté provider — hors périmètre de
   ce sprint), ce n'est pas une limite du modèle `Event`/`Circuit` (les champs existent et
   sont suffisants ; c'est le CODE de mapping qui n'a rien de mieux à y mettre depuis ce
   dataset pauvre). Écart secondaire, indépendant : les tables statiques `_CIRCUIT_DATA`
   (pays) de F2/F3/F1 Academy sont incomplètes chacune à des degrés différents (F3 couvre
   "Australian", F2 ne couvre pas "Belgian") — un défaut de couverture/maintenance, pas
   une limite du dataset externe (le pays pourrait y être ajouté).

Conséquence pour ce sprint : la normalisation compense entièrement côté présentation
(sans toucher au provider), car les valeurs utiles (`circuit.city`) sont déjà présentes
sur le modèle — seul le CHOIX d'affichage était mauvais.

### Travail effectué

**`motorsport_calendar/gui/event_display.py`** — nouveau module, logique dédiée
- `EventDisplayData(grand_prix_name: str, circuit_name: str | None, country: str | None)`
- `normalize_event_display(championship_id, event) -> EventDisplayData` — applique les 4
  règles :
  1. **Grand Prix == Circuit → une seule ligne** : `circuit_name` devient `None` si sa
     valeur (une fois résolue) est identique (insensible à la casse) au nom de Grand Prix
     affiché.
  2. **Circuit inconnu → ligne masquée** : tente `circuit.name`, puis `circuit.city` en
     repli (c'est ce qui résout "Belgian"→"Spa-Francorchamps" pour F2/F3/F1 Academy) ;
     `None` si aucun des deux candidats n'est utilisable.
  3. **Pays inconnu → ligne masquée** : le littéral `"Unknown"` (insensible à la casse) ou
     une valeur vide donne `country=None` — jamais affiché tel quel.
  4. **Nom du Grand Prix absent → stratégie documentée** : ajoute " Grand Prix" au nom brut
     pour F1/F2/F3/F1 Academy s'il ne le contient pas déjà (jamais pour WEC, dont les noms
     — "24 Hours of Le Mans" — sont déjà complets) ; si le nom est totalement absent,
     utilise le nom de circuit disponible comme titre, sinon un repli générique
     ("Événement", `STRINGS.event_name_fallback`).
- Limite assumée et documentée : "Canada" → "Canada Grand Prix" plutôt que "Canadian
  Grand Prix" (pas de table démonyme complète — jugé hors de proportion pour ce sprint).

**`motorsport_calendar/gui/components/championship_card.py`**
- `ChampionshipCardData.circuit_name`/`.country` deviennent `str | None`
- `build_championship_card` : les lignes circuit/pays ne sont ajoutées que si non `None` —
  aucune décision, uniquement une omission conditionnelle (le composant reste sans la
  moindre logique métier, comme exigé)

**`motorsport_calendar/gui/upcoming_weekend.py`**
- `_COUNTRY_LABELS`/`country_label()` déplacés vers `event_display.py` (la décision
  "quel pays afficher" y vit désormais entièrement)
- `_build_card()` appelle `normalize_event_display(...)` puis construit
  `ChampionshipCardData` à partir du résultat — ne contient plus aucune logique de
  normalisation elle-même

**`motorsport_calendar/gui/strings.py`** — `event_name_fallback = "Événement"`

**Tests**
- `tests/test_gui_event_display.py` — 23 tests : fixtures réelles F1/F2/F3 capturées en
  direct, jamais "Unknown" (sentinelle + variantes de casse + valeur vide), jamais de
  doublon (circuit==nom brut, circuit==nom normalisé, city aussi dupliqué, casse
  différente), stratégie du nom de Grand Prix (suffixe ajouté/déjà présent/jamais
  doublé/championnat non-GP/nom absent avec et sans circuit de repli/nom blanc)
- `tests/test_gui_components_championship_card.py` — 4 tests ajoutés (`circuit_name=None`
  masqué, `country=None` masqué, les deux masqués, rendu toujours valide)
- `tests/test_gui_upcoming_weekend.py` — test existant corrigé (sa propre fixture
  reproduisait involontairement le bug F2/F3 par duplication délibérée circuit==event ;
  helper `_entry()` étendu avec `circuit_name`/`circuit_city` optionnels) + 1 test
  d'intégration bout-en-bout reproduisant exactement le cas réel F2 ; 2 tests
  `country_label` déplacés vers `test_gui_event_display.py`

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/gui/event_display.py` | Créé — normalisation dédiée |
| `motorsport_calendar/gui/components/championship_card.py` | Modifié — champs optionnels |
| `motorsport_calendar/gui/upcoming_weekend.py` | Modifié — délègue à `event_display.py` |
| `motorsport_calendar/gui/strings.py` | Modifié — `event_name_fallback` |
| `tests/test_gui_event_display.py` | Créé — 23 tests |
| `tests/test_gui_components_championship_card.py` | Modifié — 4 tests ajoutés |
| `tests/test_gui_upcoming_weekend.py` | Modifié — 1 test corrigé, 1 ajouté, 2 déplacés |
| `docs/JOURNAL.md` | Mis à jour |
| `docs/AI_CONTEXT.md` | Mis à jour |
| `docs/TODO.md` | Mis à jour |
| `docs/ROADMAP.md` | Mis à jour |
| `docs/DECISIONS.md` | ADR-023 ajouté |

`providers/`, `models/`, `theme.py`, `components/layout/`, navigation, `main_view.py` :
**non modifiés**.

### Tests exécutés
```
983 passed — 0 failed — couverture 95 %
(957 → 983 : +26 tests — event_display.py, upcoming_weekend.py et championship_card.py
 tous à 100 %)
```

Vérification manuelle additionnelle (vrais appels réseau) : `get_upcoming_weekend()` pour
le week-end réel du Grand Prix de Belgique — les 3 cartes (F3, F2, F1) affichent
désormais exactement "Belgian Grand Prix / Spa-Francorchamps / [pays ou masqué]", plus
aucun doublon ni "Unknown" ; `build_main_view()` piloté de bout en bout sans erreur.

### Limites
- "Canada Grand Prix" au lieu de "Canadian Grand Prix" (pas de table démonyme par pays —
  limitation cosmétique mineure, assumée).
- La couverture des tables de pays F2/F3/F1 Academy reste incomplète en amont (provider
  non modifié) — la ligne pays disparaît proprement pour les circuits non couverts plutôt
  que d'afficher "Unknown", mais elle n'apparaîtra pas non plus tant que ces tables ne
  seront pas complétées (hors périmètre de ce sprint).
- Toujours aucun environnement graphique dans ce sandbox — vérifié par 983 tests
  unitaires (100 % sur les 3 fichiers concernés) + appels réseau réels, pas par capture
  d'écran.

---

## Session 2026-07-07 — Sprint 31 : Mise en place du Layout System

### Objectif
Construire une base UI durable : un véritable Layout System utilisé par toute
l'application, pour que toute future page (Recherche, Tableau de bord, Favoris,
Notifications, Historique, Résultats, Paramètres, Synchronisation) se construise à partir
de composants réutilisables, sans jamais recréer marges, espacements, séparateurs,
largeurs ou cartes dans la vue elle-même. Aucune nouvelle fonctionnalité — uniquement
l'architecture de présentation. Design System, couleurs, icônes, `theme.py`, providers,
modèles, logique métier, navigation, fonctionnalités : non modifiés.

### Réflexion architecture (avant le code)

**Où vit le Layout System ?** `gui/components/layout/`, un sous-paquet de la bibliothèque
de composants créée au Sprint 30 (plutôt qu'un `gui/layout/` séparé) : un composant de
mise en page EST un composant, au même titre que `ChampionshipCard` — les deux partagent
la même philosophie ("connaître uniquement son modèle/ses props, jamais la logique
métier"). `championship_card.py` reste à sa place actuelle (aucun besoin de le déplacer
dans un sous-dossier pour "faire symétrique" — ç'aurait été du remaniement inutile).

**Une responsabilité par composant, strictement :**
- `PageContainer` — largeur max, padding, alignement. Rien d'autre. En interne, délègue
  entièrement à `theme.page_shell` (aucune réimplémentation, aucun nouveau token) ; expose
  juste une API `header=`/`body=` plus déclarative que l'ancienne liste `*sections` plate.
- `PageHeader` — icône, titre, sous-titre éventuel, séparateur. Un seul composant pour
  toutes les pages qui affichent un en-tête.
- `Section` — le seul job : l'espacement entre blocs liés. Ne connaît rien aux titres.
- `SectionHeader` — un intitulé plus discret *à l'intérieur* d'une Section (pas un
  substitut de `PageHeader`, qui reste le titre de la page). Aucun consommateur actuel,
  mais nécessaire dès qu'une page (Tableau de bord, Recherche) affichera plusieurs groupes
  de cartes distincts — construit maintenant plutôt que retardé, sans quoi il aurait fallu
  re-designer `Section` plus tard pour l'accueillir.
- `CardList` — empile une liste de cartes avec un espacement vertical uniforme. Les
  séparateurs entre cartes restent un point d'extension documenté, non construit (aucun
  appelant n'en a besoin aujourd'hui).
- `EmptyState` — le seul "rien ici pour l'instant", toujours encarté (règle héritée du
  Sprint 28, désormais centralisée).
- `PageSpacing` — un espace nommé et explicite pour le cas réellement ponctuel qu'aucun des
  composants ci-dessus ne couvre déjà (ex. avant la rangée d'actions du wizard).

**Changement architectural délibéré vis-à-vis du Sprint 28** : au Sprint 28, Favoris et
Ce week-end (vide) avaient leur titre de page absorbé À L'INTÉRIEUR de la carte, pour
éviter un doublon visuel (pas d'en-tête générique séparé à l'époque). Avec le Layout
System, CHAQUE page qui affiche un en-tête utilise désormais exactement le même
`PageHeader`, **séparé** du corps — cohérent avec Mon calendrier/Préférences, et surtout
généralisable : une future page "Recherche" aura un `PageHeader` + une barre de recherche
+ un `EmptyState` en cas d'absence de résultat, sans que ce dernier n'ait à porter le titre
de la page. Conséquence visible : le titre de "Ce week-end"/"Mes favoris" apparaît
désormais AU-DESSUS de la carte plutôt que dedans. Assumé et documenté ici — l'information
affichée est strictement identique, seule la structure change.
Autre conséquence, à Préférences : les lignes de réglages retrouvent leur bordure
individuelle (perdue au Sprint 28 pour éviter un double encadrement dans LA carte unique
englobante) — cette carte englobante n'existe plus (le `PageHeader` est séparé), donc
chaque ligne peut redevenir sa propre carte via `CardList`, sans double bordure.

**Nommage PascalCase** (`PageContainer`, `PageHeader`, ...) — délibérément aligné sur
l'exemple donné dans la demande plutôt que sur la convention `snake_case` du reste du
code (`build_championship_card`, `theme.card`) : signale clairement "ceci est un
composant/widget", à la manière Flet/Flutter. Ruff (`N802`, pep8-naming) aurait sinon
signalé chaque nom — ajout d'une exception `per-file-ignores` scoping strictement le
paquet `gui/components/layout/*.py` dans `ruff.toml`, avec commentaire explicite.

### Travail effectué

**`motorsport_calendar/gui/components/layout/`** — nouveau sous-paquet, 7 fichiers
- `page_container.py` → `PageContainer(*, header=None, body=())`
- `page_header.py` → `PageHeader(title, *, icon=None, subtitle=None)`
- `section.py` → `Section(*controls, spacing=Spacing.SM)` + `SectionHeader(title, *, icon=None)`
- `card_list.py` → `CardList(cards, *, spacing=Spacing.SM)`
- `empty_state.py` → `EmptyState(title, *, message=None, icon=None)`
- `spacing.py` → `PageSpacing(size=Spacing.MD)`
- `__init__.py` — ré-exporte les 7 composants

**Les 5 vues migrées** — chacune construite exclusivement à partir du Layout System :
- `weekend.py` : les 3 états (chargement/aucune course/trouvé) deviennent
  `PageContainer(header=PageHeader(...), body=[Section(...)])`, avec `EmptyState`/`CardList`
  pour le corps selon l'état
- `favorites.py` : réduite à un seul appel `PageContainer(header=..., body=[Section(EmptyState(...))])`
- `preferences.py` : `PageContainer(header=..., body=[Section(CardList(rows))])` — les
  lignes (`_pref_row`) redeviennent des `theme.card()` individuelles
- `about.py` : `PageContainer(body=[Section(...)])`, **sans** `header=` — conserve
  délibérément le bloc de marque compact du Sprint 28 (pas de `PageHeader` générique ici)
- `calendar.py` : `PageContainer(header=PageHeader(...), body=[...])` pour l'enveloppe ;
  le bandeau d'étapes, le corps d'étape et la rangée de navigation restent des contrôles
  bruts dans `body` (flux séquentiel du wizard, pas une "Section" générique) ; les deux
  espaceurs manuels de `_step_create` deviennent `PageSpacing(...)`

**`ruff.toml`** — exception `N802` scopée à `gui/components/layout/*.py`

**Tests**
- `tests/test_gui_components_layout.py` — 51 tests : chaque composant testé isolément
  (structure, valeurs par défaut, surcharge des paramètres, cas vides/limites) + 3 tests
  d'intégration prouvant la composition exacte de la demande + 1 test verrouillant qu'aucun
  spacing utilisé n'est étranger à l'échelle `theme.Spacing`
- `tests/test_gui_views.py` — 7 tests Sprint 28 adaptés à la nouvelle structure (en-tête
  désormais séparé de la carte) via un nouvel utilitaire `_bordered_cards()` qui parcourt
  récursivement l'arbre de contrôles plutôt que de supposer une profondeur d'imbrication
  fixe ; 3 nouveaux tests verrouillant la présence du `PageHeader` séparé (weekend,
  favorites, preferences) ; 1 test inversé (`test_pref_rows_now_carry_their_own_border`,
  documentant explicitement le changement Sprint 28 → 31)

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/gui/components/layout/__init__.py` | Créé |
| `motorsport_calendar/gui/components/layout/page_container.py` | Créé |
| `motorsport_calendar/gui/components/layout/page_header.py` | Créé |
| `motorsport_calendar/gui/components/layout/section.py` | Créé |
| `motorsport_calendar/gui/components/layout/card_list.py` | Créé |
| `motorsport_calendar/gui/components/layout/empty_state.py` | Créé |
| `motorsport_calendar/gui/components/layout/spacing.py` | Créé |
| `motorsport_calendar/gui/views/weekend.py` | Modifié — Layout System |
| `motorsport_calendar/gui/views/favorites.py` | Modifié — Layout System |
| `motorsport_calendar/gui/views/preferences.py` | Modifié — Layout System, bordures restaurées |
| `motorsport_calendar/gui/views/about.py` | Modifié — Layout System (sans PageHeader) |
| `motorsport_calendar/gui/views/calendar.py` | Modifié — Layout System + PageSpacing |
| `ruff.toml` | Modifié — exception N802 scopée |
| `tests/test_gui_components_layout.py` | Créé — 51 tests |
| `tests/test_gui_views.py` | Modifié — 7 tests adaptés, 4 nouveaux |
| `docs/JOURNAL.md` | Mis à jour |
| `docs/AI_CONTEXT.md` | Mis à jour |
| `docs/TODO.md` | Mis à jour |
| `docs/ROADMAP.md` | Mis à jour |
| `docs/DECISIONS.md` | ADR-022 ajouté |

`theme.py`, `main_view.py`, `controller.py`, `upcoming_weekend.py`,
`components/championship_card.py`, providers, modèles métier, navigation, couleurs,
icônes : **non modifiés**.

### Compromis / choix assumés
1. **En-tête séparé de la carte** (Favoris, Ce week-end vide) — changement visuel par
   rapport au Sprint 28, expliqué ci-dessus. Assumé pour une généralisation réelle.
2. **Préférences : bordures des lignes restaurées** — changement visuel par rapport au
   Sprint 28, pour la même raison (plus de carte englobante unique).
3. **Nommage PascalCase** — déroge à la convention `snake_case` du reste du code Python,
   accepté explicitement pour signaler "composant" et matcher l'exemple de la demande ;
   compensé par une exception `ruff.toml` scopée et documentée plutôt que des `noqa`
   dispersés.
4. **`SectionHeader` sans consommateur actuel** — construit par anticipation explicite
   (demandé nommément dans le brief), pas par déduction spéculative — seul composant du
   sprint dans ce cas.
5. **`Section`/`PageContainer` semblent redondants sur les pages à un seul bloc** —
   c'est voulu : la charge cognitive de `body=[Section(...)]` est nulle aujourd'hui, mais
   évite une deuxième passe de refactoring le jour où une page aura plusieurs sections.

### Tests exécutés
```
957 passed — 0 failed — couverture 95 %
(906 → 957 : +51 tests — les 7 fichiers du Layout System à 100 %, les 5 vues migrées à
 100 % (about.py 76 % — écart préexistant, confirmé inchangé en valeur absolue))
```

Vérification manuelle additionnelle : `get_upcoming_weekend()` + `build_weekend_view()`
exécutés avec de vraies données réseau ; `build_main_view()` piloté de bout en bout via une
fausse `Page` — les 5 destinations de navigation, le fetch de "Ce week-end" et les 4 étapes
du wizard fonctionnent identiquement à travers le nouveau Layout System.

### Limites
- Toujours aucun environnement graphique dans ce sandbox — vérifié par 957 tests unitaires
  (couverture 100 % sur tout le Layout System) + appels réseau réels + simulation complète
  du wiring, pas par capture d'écran.
- `CardList` n'implémente pas de séparateur entre cartes (option documentée, non codée —
  aucun appelant actuel n'en a besoin).
- `SectionHeader` n'a encore aucun consommateur réel dans le code — prêt pour Tableau de
  bord/Recherche, verrouillé par tests, mais non exercé par une vraie page avant leur
  arrivée.

---

## Session 2026-07-07 — Sprint 30 : Création du composant ChampionshipCard

### Objectif
Démarrer la bibliothèque de composants réutilisables de Motorsport Calendar. Premier
composant : `ChampionshipCard`, extrait de "Ce week-end" pour être réutilisable tel quel
dans toute future vue (Favoris, Recherche, Tableau de bord, Calendrier, Notifications,
Historique) sans qu'aucune vue n'ait plus jamais à reconstruire ce layout. Aucune
régression, aucune modification du Design System, de la navigation, des providers ou de la
logique métier — uniquement une extraction/réutilisation.

### Réflexion architecture (avant le code)
Le composant ne doit connaître que son propre modèle de données, jamais un objet du domaine
(`Event`/`Session`/`Championship`/`Circuit`) ni le concept de "week-end". Il fallait donc :
1. Un nouveau paquet dédié `gui/components/` (bibliothèque de composants), distinct de
   `gui/views/` (une page = un module) et de `gui/theme.py` (tokens/primitives bas niveau).
2. Un modèle de données propre au composant (`ChampionshipCardData` + `SessionRow`),
   promu depuis `upcoming_weekend.WeekendCard`/`SessionRow` qui remplissaient déjà
   exactement ce rôle mais vivaient au mauvais endroit (couplés à "Ce week-end").
3. Une zone de pied de carte (`footer: ft.Control | None`) — non implémentée (Favori,
   Notifications, Export ICS, Partage, Résultats restent hors scope), mais le point
   d'extension existe dès maintenant sans rien devoir changer à l'appel du composant le
   jour où une vue voudra l'utiliser.

### Travail effectué

**`motorsport_calendar/gui/components/__init__.py`** — nouveau paquet, docstring décrivant
la philosophie de la bibliothèque (données déjà formatées en entrée, jamais de logique
métier/provider à l'intérieur d'un composant).

**`motorsport_calendar/gui/components/championship_card.py`** — nouveau, le composant
- `SessionRow(label, day_time)` et `ChampionshipCardData(championship_id,
  championship_name, event_name, circuit_name, country, sessions)` — dataclasses frozen,
  déplacées depuis `upcoming_weekend.py` (renommage `WeekendCard` → `ChampionshipCardData`,
  car le nom n'a plus de sens hors du contexte "week-end")
- `build_championship_card(data, *, footer=None) -> ft.Control` — en-tête dans l'ordre
  exact demandé (championnat, Grand Prix, circuit, pays sur 4 lignes distinctes — plus de
  "·" combinant circuit et pays comme dans l'ancien `_championship_card` de `weekend.py`),
  puis `Divider`, puis la grille de sessions
- Alignement des sessions : chaque ligne est une `ft.Row(alignment=SPACE_BETWEEN)` — libellé
  et heure ancrés chacun à une extrémité de la ligne, un vrai alignement en colonnes qui ne
  dépend jamais de la longueur du texte du libellé (contrairement à un simple `expand=True`
  sur le libellé, qui fonctionne mais est moins explicite)
- Construit entièrement à partir des primitives existantes de `theme.py`
  (`theme.card`, `Spacing`/`FontSize`/`Colors`) — **aucun nouveau token, aucune nouvelle
  couleur, aucun changement au Design System**
- `footer` : quand `None` (partout aujourd'hui), rien n'est ajouté après la grille de
  sessions — zéro changement visuel. Quand fourni, un `Divider` puis le contrôle passé sont
  ajoutés — le composant ne sait pas ce qu'il contient (bouton favori, icônes, etc.), il ne
  fait que le positionner

**`motorsport_calendar/gui/upcoming_weekend.py`** — migré
- Suppression de `SessionRow`/`WeekendCard` (déplacées) ; importe désormais
  `ChampionshipCardData`/`SessionRow` depuis `components.championship_card`
- `WeekendResult.cards: tuple[ChampionshipCardData, ...]` (renommage de type uniquement,
  aucun changement de champ ni de comportement)
- `_build_card` construit désormais un `ChampionshipCardData`

**`motorsport_calendar/gui/views/weekend.py`** — migré
- Suppression de `_championship_card`/`_session_row` (le layout vit maintenant dans le
  composant partagé)
- `_found_state` construit une liste de `build_championship_card(card)` — la vue ne
  connaît plus aucun détail de layout de carte, exactement comme demandé
  ("La vue 'Ce week-end' devra simplement construire une liste de ChampionshipCard")

**`tests/test_gui_components_championship_card.py`** — nouveau, 23 tests
- Modèle : immutabilité (`frozen=True`), champs
- Construction : type de retour, carte bordée via `theme.card`, ordre exact de l'en-tête,
  hiérarchie visuelle (nom du championnat = texte le plus proéminent), séparateur présent
- Grille de sessions : une ligne par session, ordre préservé (le tri reste la responsabilité
  de l'appelant), alignement `SPACE_BETWEEN` vérifié quel que soit la longueur du libellé,
  0 session ne plante pas
- Footer : absent par défaut (aucune section ajoutée), présent → `Divider` + contrôle ajoutés,
  accepte n'importe quel contrôle sans l'interpréter
- Réutilisabilité : rendu paramétré sur les 5 championnats cités dans la demande (F1, F2,
  F3, WEC, F1 Academy) + un événement de forme très différente ("24 Hours of Le Mans")

**`tests/test_gui_views.py`** — mis à jour (import `ChampionshipCardData`/`SessionRow`
depuis leur nouvel emplacement) ; aucun test perdu

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/gui/components/__init__.py` | Créé |
| `motorsport_calendar/gui/components/championship_card.py` | Créé — le composant |
| `motorsport_calendar/gui/upcoming_weekend.py` | Modifié — utilise le modèle partagé |
| `motorsport_calendar/gui/views/weekend.py` | Modifié — construit une liste de cartes |
| `tests/test_gui_components_championship_card.py` | Créé — 23 tests |
| `tests/test_gui_views.py` | Modifié — import mis à jour |
| `docs/JOURNAL.md` | Mis à jour |
| `docs/AI_CONTEXT.md` | Mis à jour |
| `docs/TODO.md` | Mis à jour |
| `docs/ROADMAP.md` | Mis à jour |
| `docs/DECISIONS.md` | ADR-021 ajouté |

`theme.py`, `main_view.py`, `controller.py`, navigation, couleurs, espacements, providers,
modèles métier : **non modifiés**.

### Bugs rencontrés
Aucun — migration mécanique, verrouillée par les tests existants (aucun n'a dû changer de
comportement, seulement des imports).

### Tests exécutés
```
903 passed — 0 failed — couverture 95 %
(880 → 903 : +23 tests — championship_card.py, upcoming_weekend.py et views/weekend.py
 tous à 100 %)
```

Vérification manuelle additionnelle (vrais appels réseau) : `get_upcoming_weekend()` +
`build_weekend_view()` exécutés de bout en bout avec le nouveau composant — 3 cartes
(F3/F2/F1, week-end du Grand Prix de Belgique) rendues sans erreur.

### Limites
- Toujours aucun environnement graphique dans ce sandbox — vérifié par tests unitaires
  (100 % sur les 3 fichiers concernés) + appel réseau réel, pas par capture d'écran.
- Le footer reste un point d'extension vide : aucun bouton Favori/Notifications/Export/
  Partage/Résultats n'a été implémenté (explicitement hors scope de ce sprint).
- Le composant ne gère pas lui-même le tri/regroupement (Formula avant Endurance,
  chronologique) — c'est resté la responsabilité de `upcoming_weekend.py`, conforme à
  "aucune logique métier dans la vue/le composant".

---

## Session 2026-07-07 — Sprint 29 : Ce week-end (version fonctionnelle)

### Objectif
Transformer "Ce week-end" en première fonctionnalité réellement utile : trouver
automatiquement le prochain week-end de course (vendredi 00h00 → dimanche 23h59) à partir
des 5 championnats existants (F1, F2, F3, F1 Academy, WEC), afficher une carte par
championnat avec ses sessions, triées Formula puis Endurance puis chronologiquement.
Aucune nouvelle navigation, aucun changement graphique majeur, aucun nouveau provider —
uniquement le branchement de données réelles sur l'architecture existante (`registry` +
`source_registry` + `HttpCache`, exactement comme `generate_calendar`).

### Travail effectué

**`motorsport_calendar/gui/upcoming_weekend.py`** — nouveau module, logique pure (aucun
Flet, aucune I/O)
- `WEEKEND_CHAMPIONSHIP_IDS` — liste figée `(formula1, formula2, formula3, f1-academy, wec)`,
  indépendante de l'opt-out de `config.yaml` (cette page a son propre périmètre fixe)
- `WeekendEntry(championship_id, event)` — **découverte importante** : `Event.championship.id`
  tel que construit par chaque provider est suffixé par l'année (`"formula1-2026"`,
  `"f1-academy-2026"`), jamais l'id brut du registre (`"formula1"`). Le regroupement par
  catégorie (`categories.get_groups_for`) et les noms d'affichage (`display_names.
  get_display_name`) attendent l'id brut — `WeekendEntry` transporte donc explicitement
  l'id connu par l'appelant plutôt que de le déduire (fragile) de `event.championship.id`.
  Voir ADR-020.
- `find_next_weekend_entries(entries, now, max_weeks_ahead=104)` — avance semaine par
  semaine (vendredi→dimanche, dates UTC) jusqu'à trouver une fenêtre contenant au moins une
  session, conformément à l'énoncé ("le prochain week-end contenant au moins une
  compétition") ; retourne `None` si rien dans l'horizon (~2 ans, borné par les données
  réellement récupérées)
- `find_upcoming_weekend(entries, now)` — point d'entrée : recherche + regroupement
  (`_group_entries_for_display`, réutilise `categories.get_groups_for` tel quel — Formula
  puis Endurance, ordre chronologique préservé à l'intérieur) + mise en forme (`_build_card`)
  → `WeekendResult(found, friday, sunday, cards, next_hint_date)`
- Labels français présentation-only (même philosophie que `display_names.py`) :
  `_SESSION_LABELS` (SessionType → "Essais Libres 1"/"Qualifications"/"Course"/…),
  `_COUNTRY_LABELS` (~35 pays → emoji drapeau + nom FR, fallback sur le nom brut si absent),
  `_DAY_LABELS_FR`
- Heure affichée convertie dans le fuseau IANA du circuit (`Circuit.timezone`, déjà présent
  dans le modèle mais jusqu'ici jamais exploité) — fallback UTC si le fuseau est invalide

**`motorsport_calendar/gui/controller.py`** — `get_upcoming_weekend(now=None)`
- Mirroir exact du pipeline de `generate_calendar` : mêmes `registry`/`source_registry`,
  même `HttpCache`, **aucun nouveau provider**, `refresh=False` toujours — repose sur le TTL
  du cache existant pour ne jamais retaper le réseau à chaque ouverture de la page
- Boucle sur les 5 championnats fixes × 2 années (année courante + suivante, borne le
  scan sans appel réseau supplémentaire) ; échec d'un championnat/année → ignoré, les autres
  continuent (règle 8 de PROJECT_RULES.md)
- WEC : `OfficialWecSource.get_season()` lève `NotImplementedError` en conditions réelles —
  capturé comme n'importe quel autre échec, jamais un cas spécial

**`motorsport_calendar/gui/views/weekend.py`** — réécrit, 3 états exactement
- `build_weekend_view(result: WeekendResult | None = None)` :
  `None` → chargement ("Chargement..." dans une carte) ; `result.found is False` → carte
  unique "Aucune course ce week-end." + "Prochain week-end disponible le XX/XX." (si connu) ;
  `result.found is True` → en-tête de page + sous-titre (dates du week-end) + **une carte
  par championnat**, triées Formula puis Endurance puis chronologiquement (ordre déjà
  garanti par `find_upcoming_weekend`, la vue ne trie rien elle-même)
- Suppression du skeleton statique (`_race_preview_content`) et des chaînes qui n'allaient
  qu'avec lui (`weekend_coming_soon`, `weekend_section_*`, `weekend_layout_preview`)

**`motorsport_calendar/gui/main_view.py`**
- `weekend_container` (même pattern que `calendar_container`) : construit une fois avec
  l'état "chargement", puis `_load_weekend()` (tâche asyncio démarrée une seule fois au
  lancement de l'app, référencée sur `page.weekend_load_task` pour ne pas être ramassée par
  le GC en plein vol) appelle `get_upcoming_weekend()` et remplace `.content` une fois
  résolu — jamais retapé à chaque visite de l'onglet
- Docstring module mis à jour (2e exception à "vue construite une fois, swap sans rebuild")

**`motorsport_calendar/gui/strings.py`** — `weekend_loading`, `weekend_next_hint`
(gabarit `"Prochain week-end disponible le {date}."`) ; `weekend_empty_title` conservé
(désormais avec point final, conforme à l'énoncé) ; chaînes du skeleton statique retirées

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/gui/upcoming_weekend.py` | Créé — logique pure |
| `motorsport_calendar/gui/controller.py` | Modifié — `get_upcoming_weekend()` |
| `motorsport_calendar/gui/views/weekend.py` | Réécrit — 3 états réels |
| `motorsport_calendar/gui/main_view.py` | Modifié — fetch en arrière-plan, une fois |
| `motorsport_calendar/gui/strings.py` | Modifié — nouvelles chaînes, anciennes retirées |
| `tests/test_gui_upcoming_weekend.py` | Créé — 21 tests |
| `tests/test_gui_controller.py` | Modifié — 8 tests `TestGetUpcomingWeekend` |
| `tests/test_gui_views.py` | Modifié — 5 tests des 3 états de la vue |
| `docs/JOURNAL.md` | Mis à jour |
| `docs/AI_CONTEXT.md` | Mis à jour |
| `docs/TODO.md` | Mis à jour |
| `docs/ROADMAP.md` | Mis à jour |
| `docs/DECISIONS.md` | ADR-020 ajouté |

`theme.py`, `models.py` (calendrier/wizard), `categories.py`, `display_names.py`,
`preferences.py`, providers existants, navigation : **non modifiés**.

### Bugs rencontrés

1. **`Event.championship.id` suffixé par l'année** — découvert en testant le contrôleur
   avec de vraies données : le regroupement Formula/Endurance échouait silencieusement
   (tout tombait dans le groupe "Autres" de secours) parce que `get_groups_for` cherchait
   `"formula1"` mais recevait `"formula1-2026"`. Corrigé en introduisant `WeekendEntry` qui
   transporte l'id du registre explicitement au lieu de le déduire de l'événement. Voir
   ADR-020 — aucun modèle ni provider modifié, la correction reste entièrement côté GUI.
2. **Source par défaut de "formula1" = openf1, pas jolpica** — `ProvidersConfig.formula1`
   a un défaut explicite `source="openf1"` (voir `config/models.py`) alors que jolpica est
   la source enregistrée en premier. Mes premiers tests mockaient jolpica et voyaient
   fuiter de vraies données réseau parce que le contrôleur, fidèle à `generate_calendar`,
   respecte ce défaut. Corrigé en mockant `OpenF1Source.get_season` à la place.

### Tests exécutés

```
880 passed — 0 failed — couverture 95 %
(846 → 880 : +34 tests — upcoming_weekend.py 100 %, views/weekend.py 100 %)
```

Vérification manuelle additionnelle (vrais appels réseau, hors suite de tests) :
- `get_upcoming_weekend()` exécuté en conditions réelles → a trouvé le week-end du Grand
  Prix de Belgique avec 3 cartes (F3, F2, F1) correctement triées chronologiquement à
  l'intérieur du groupe Formula.
- `build_main_view()` piloté de bout en bout via une fausse `Page` : `page.weekend_load_task`
  se résout sans lever, `page.update()` est appelé exactement une fois après résolution,
  confirmant que le conteneur "Ce week-end" passe bien de l'état chargement à l'état réel.

### Limites

- Le découpage vendredi-dimanche est calculé en **UTC**, pas dans le fuseau du circuit. Un
  essai libre du vendredi matin en Asie (ex. Suzuka, UTC+9) peut techniquement tomber un
  "jeudi" UTC si l'heure locale est très matinale — cas limite documenté, non corrigé dans
  cette version (l'heure *affichée* sur chaque session est, elle, correctement convertie
  dans le fuseau du circuit ; seule la fenêtre de *recherche* reste ancrée UTC).
- Table pays → drapeau/nom FR non exhaustive (~35 pays couvrant les circuits F1/F2/F3/F1A/
  WEC courants) — un pays absent s'affiche sans drapeau, avec son nom brut (souvent
  anglais) plutôt que de faire échouer l'affichage.
- Toujours aucun environnement graphique dans ce sandbox — vérifié par tests unitaires
  (100 % sur les 2 nouveaux modules) + appels réseau réels manuels + simulation complète du
  wiring, pas par capture d'écran.
- La tâche de fond (`page.weekend_load_task`) démarre au lancement de l'app, pas à la
  première visite de l'onglet "Ce week-end" — choix délibéré pour respecter "jamais
  d'appel réseau à chaque ouverture" au sens le plus strict (une seule fois par lancement,
  pas une fois par visite), mais cela signifie qu'un utilisateur qui ne visite jamais cet
  onglet aura quand même déclenché le fetch (atténué par le cache existant : TTL 24h par
  défaut, donc sans coût réseau réel au-delà de la première fois par jour).

---

## Session 2026-07-07 — Sprint 28 : Uniformisation finale de l'interface

### Objectif
Finaliser la structure visuelle avant les futures vraies fonctionnalités. Trois retouches
ciblées, purement UX/UI, sans logique métier ni nouvelle fonctionnalité : simplifier le
wizard (le bandeau d'étapes suffit, le titre par étape est redondant), donner de la
présence visuelle aux pages "vides" (Ce week-end, Mes favoris, Préférences) via une carte
centrale, et rendre la page À propos plus compacte. Aucun changement à la navigation, aux
couleurs, au Design System, au mécanisme `theme.page_shell`, aux modèles, providers,
préférences (données) ou à l'architecture.

### Travail effectué

**1. Wizard simplifié (`motorsport_calendar/gui/views/calendar.py`)**
- Suppression de `_step_header()` et de ses appels dans les 4 fonctions `_step_*` — plus de
  titre "Étape N — ..." ni de texte d'aide sous le bandeau de pastilles.
- Chaque étape commence directement par son contenu : `_step_season` retourne juste le
  `year_dropdown`, `_step_destination` juste la `Row` fichier+bouton, etc.
- `_step_championships`/`_step_destination` simplifiées en un seul niveau (l'ancien
  wrapper `Column` qui ne contenait plus que le header + un enfant est devenu inutile).
- `motorsport_calendar/gui/strings.py` : suppression des 8 constantes orphelines
  (`wizard_title_season/championships/destination/create`, `wizard_help_*`) —
  `wizard_step_*` (labels des pastilles) conservées intactes.
- Aucun changement à `build_calendar_view` au-delà du contenu des étapes : en-tête de page
  ("Mon calendrier" + icône), bandeau de pastilles, navigation Précédent/Suivant — tous
  inchangés, comme demandé ("Wizard (hors suppression du titre)").

**2. Cartes centrales pour les pages vides (`weekend.py`, `favorites.py`, `preferences.py`)**
- Les 3 vues passent maintenant **une seule section** à `theme.page_shell(...)` : un
  `theme.card(...)` contenant tout le contenu existant (en-tête `section_title` + `Divider`
  + le contenu propre à la page), au lieu de sections multiples posées à plat sur le fond
  de la page.
- `weekend.py` : le skeleton de prévisualisation (`_race_preview_content`) perd son propre
  encadrement `theme.card(...)` — il vit maintenant à l'intérieur de la carte centrale de
  la page, un double encadrement aurait été redondant.
- `preferences.py` : `_pref_row()` perd son bordure individuelle (`border=None` désormais)
  pour la même raison — les 6 lignes sont nested dans la carte centrale unique de la page.
- Aucune fonctionnalité, aucun bouton actif, aucun texte modifié — uniquement le conteneur.

**3. À propos compactée (`about.py`)**
- Suppression du header générique `section_title(nav_about, icon=INFO)` + `Divider` — le
  bloc "Motorsport Calendar / Version Alpha" (avec le placeholder logo) sert désormais
  lui-même de titre de page, sans label "À propos" redondant au-dessus.
- Suppression des `ft.Container(height=...)` espaceurs manuels entre les blocs — l'espacement
  inter-sections uniforme de `page_shell` (`Spacing.SM`) s'en charge, présentation plus
  compacte comme demandé.
- Mêmes informations conservées : titre, version, description, développeur, lien GitHub,
  licence — rien retiré, rien de nouveau. Pas de carte (contrairement aux 3 pages du point 2
  — la demande ne le mentionnait pas pour À propos).

### Fichiers modifiés

| Fichier | Action |
|---|---|
| `motorsport_calendar/gui/views/calendar.py` | Modifié — suppression `_step_header`, simplification des 4 fonctions `_step_*` |
| `motorsport_calendar/gui/strings.py` | Modifié — 8 constantes wizard orphelines supprimées |
| `motorsport_calendar/gui/views/weekend.py` | Modifié — carte centrale unique |
| `motorsport_calendar/gui/views/favorites.py` | Modifié — carte centrale unique |
| `motorsport_calendar/gui/views/preferences.py` | Modifié — carte centrale unique, lignes sans bordure propre |
| `motorsport_calendar/gui/views/about.py` | Modifié — présentation compactée, header générique retiré |
| `tests/test_gui_views.py` | Modifié — 9 tests (carte centrale ×3, absence de carte À propos, titre unique, step body sans en-tête) |
| `tests/test_gui_strings.py` | Modifié — 2 tests (labels pastilles conservés, strings orphelines absentes) |
| `docs/JOURNAL.md` | Mis à jour |
| `docs/AI_CONTEXT.md` | Mis à jour |
| `docs/TODO.md` | Mis à jour |

`theme.py`, `main_view.py`, `models.py`, `controller.py`, `categories.py`,
`display_names.py`, `preferences.py` (persistance) **non modifiés**. `docs/ROADMAP.md`
**non modifié** (explicitement demandé).

### Bugs rencontrés
Aucun.

### Tests exécutés
```
846 passed — 0 failed — couverture 94 %
(837 → 846 : +9 tests)
```

Vérification manuelle additionnelle (toujours aucun environnement graphique disponible) :
- Script pilotant `build_main_view()` de bout en bout confirme que le wizard, après
  simplification, conserve exactement le même comportement de gating (Suivant désactivé/
  activé en direct selon la sélection, retour arrière fonctionnel).
- Script appelant directement les 4 `build_*_view()` restants confirme que Ce week-end,
  Mes favoris et Préférences n'exposent plus qu'**une seule section** (la carte centrale,
  bordure confirmée) tandis qu'À propos n'a **aucune** section bordée parmi ses 5 sections.

### Limites
- Toujours aucune capture d'écran réelle possible dans ce sandbox (pas de serveur
  d'affichage). Vérifié uniquement par tests unitaires + inspection structurelle du wiring
  réel — recommandé de confirmer visuellement sur un poste avec affichage.
- Nested cards (Préférences) : la carte centrale contient les 6 lignes de réglages ; ces
  lignes n'ont plus leur propre bordure (pour éviter un double encadrement), mais gardent
  leur espacement (`spacing=XS`) — pas de séparateur visuel entre elles. À ajuster si le
  rendu final paraît trop dense.
- Interprétation retenue pour "carte centrale" : une carte qui remplit la largeur du
  gabarit partagé (comme toutes les autres cartes de l'app depuis le Sprint 27), pas une
  carte volontairement plus étroite et centrée dans l'espace restant — cohérent avec la
  règle d'uniformisation des largeurs de cartes déjà en place, mais à confirmer si
  l'intention était une carte visuellement plus petite/isolée.

---

## Session 2026-07-07 — Sprint 27 : Uniformisation du layout (UX)

### Objectif
Corriger une incohérence visuelle identifiée après validation du Design System (Sprint 26) :
Ce week-end / Mes favoris / À propos rendaient leur contenu entièrement centré au milieu de
l'écran, tandis que Mon calendrier et Préférences étaient alignés à gauche — donnant
l'impression de plusieurs applications cohabitant dans la même fenêtre. Objectif unique :
une seule grille de page, partagée par les 5 vues, avec un conteneur principal centré
(largeur max 900–1100 px) et un contenu systématiquement aligné à gauche à l'intérieur.
Aucune fonctionnalité, logique métier, provider, modèle, préférence, navigation ou logique
de wizard modifiée — changement strictement visuel.

### Travail effectué

**`motorsport_calendar/gui/theme.py`**
- `MAX_CONTENT_WIDTH = 1000` — constante unique (dans la fourchette 900–1100 px demandée)
- `page_shell(*sections)` — nouvelle fonction, LE gabarit partagé : un `Container` externe
  `expand=True` avec `alignment=TOP_CENTER` (centre uniquement le conteneur, jamais son
  contenu) et le `padding` standard ; à l'intérieur, un `Container` à largeur fixe
  (`width=MAX_CONTENT_WIDTH`) qui se réduit naturellement sur une fenêtre plus étroite
  (comportement standard de contrainte Flutter — un enfant à largeur fixe est bridé par les
  contraintes du parent, jamais en dépassement) ; à l'intérieur, une `Column` unique
  `horizontal_alignment=STRETCH` qui fait remplir la largeur du conteneur à toute carte/
  formulaire sans jamais les centrer — la fonction ne fait que positionner le bloc principal,
  jamais son contenu.
- Toutes les vues appellent désormais `theme.page_shell(...)` en lieu et place de leur
  propre `Container(padding=..., alignment=...)` ad hoc.

**`motorsport_calendar/gui/views/weekend.py`, `favorites.py`, `preferences.py`, `about.py`,
`calendar.py`** — migrés vers `theme.page_shell(...)`
- Weekend/Favoris/À propos : suppression de tout `alignment=ft.Alignment.TOP_CENTER`,
  `horizontal_alignment=ft.CrossAxisAlignment.CENTER` et `text_align=ft.TextAlign.CENTER` —
  le contenu (icône, titres, description, carte placeholder) est désormais empilé et aligné
  à gauche, comme Mon calendrier/Préférences l'étaient déjà.
- Les 5 pages utilisent maintenant un **en-tête identique** : `theme.section_title(label,
  icon=...)` suivi d'un `ft.Divider(height=Spacing.MD)` — y compris Mon calendrier, dont
  l'en-tête custom (logo + "Motorsport Calendar") est remplacé par
  `section_title(STRINGS.nav_my_calendar, icon=CALENDAR_MONTH)`, cohérent avec les autres
  pages qui affichent leur propre nom de section (pas le nom de l'app). Le placeholder logo
  (Sprint 26) reste en place sur la page À propos, son unique emplacement désormais.
- Carte placeholder "Ce week-end" : suppression de la largeur fixe (`width=320`) — elle
  remplit maintenant la largeur du gabarit comme toutes les autres cartes (Préférences,
  récapitulatif du wizard), via le même mécanisme `STRETCH`.
- Espacement inter-sections unifié : `Spacing.SM` partout (porté par `page_shell`), plus
  besoin de le redéfinir par vue.

**`tests/test_gui_theme.py`**
- `TestPageShell` — 8 tests : type de retour, `expand`, centrage de l'unique conteneur,
  largeur plafonnée à `MAX_CONTENT_WIDTH`, valeur dans la fourchette 900–1100, alignement
  `STRETCH` (jamais centré), ordre des sections préservé, padding = `page_padding()`.

**`tests/test_gui_views.py`**
- Un test `test_uses_shared_page_shell` ajouté à chacune des 5 classes de vue.
- `TestAllViewsShareTheSameGrid` — 5 tests transversaux qui construisent les 5 vues et
  vérifient qu'elles partagent *exactement* la même largeur max, le même centrage externe,
  le même alignement de contenu (`STRETCH`) et le même padding — verrou anti-régression
  direct sur l'exigence "même gabarit partout".

### Fichiers modifiés

| Fichier | Action |
|---|---|
| `motorsport_calendar/gui/theme.py` | Modifié — `MAX_CONTENT_WIDTH`, `page_shell()` |
| `motorsport_calendar/gui/views/weekend.py` | Modifié — gabarit partagé, contenu aligné à gauche |
| `motorsport_calendar/gui/views/favorites.py` | Modifié — gabarit partagé, contenu aligné à gauche |
| `motorsport_calendar/gui/views/preferences.py` | Modifié — gabarit partagé |
| `motorsport_calendar/gui/views/about.py` | Modifié — gabarit partagé, contenu aligné à gauche, en-tête uniformisé |
| `motorsport_calendar/gui/views/calendar.py` | Modifié — gabarit partagé, en-tête uniformisé (section_title au lieu du logo custom) |
| `tests/test_gui_theme.py` | Modifié — 8 tests `TestPageShell` |
| `tests/test_gui_views.py` | Modifié — 5 tests unitaires + `TestAllViewsShareTheSameGrid` (5 tests) |
| `docs/JOURNAL.md` | Mis à jour |
| `docs/AI_CONTEXT.md` | Mis à jour |
| `docs/TODO.md` | Mis à jour |
| `docs/ROADMAP.md` | Mis à jour |
| `docs/DECISIONS.md` | ADR-019 ajouté |

`main_view.py` et `models.py` **non modifiés** — la logique du wizard (état, gating,
navigation entre étapes) est restée intacte ; seule la fonction de rendu `build_calendar_view`
change de conteneur racine.

### Bugs rencontrés
Aucun. Point de vigilance documenté en Limites : le mécanisme de largeur maximale responsive
repose sur le comportement standard des contraintes Flutter (`BoxConstraints.enforce`) plutôt
que sur un recalcul manuel au resize — vérifié structurellement (tests + simulation), pas
visuellement (voir Limites).

### Tests exécutés
```
837 passed — 0 failed — couverture 94 %
(819 → 837 : +18 tests — 100 % sur theme.py, calendar.py, weekend.py, favorites.py,
 preferences.py, about.py)
```

Vérification manuelle additionnelle (toujours aucun environnement graphique disponible) :
script pilotant `build_main_view()` de bout en bout — confirme que la page "Mon calendrier"
produite par le wiring réel (pas seulement `build_calendar_view()` isolé) utilise bien
`page_shell` avec `width=1000`, `alignment=TOP_CENTER`, `horizontal_alignment=STRETCH`,
identique aux 4 autres vues.

### Limites
- Toujours pas de capture d'écran réelle possible (pas de serveur d'affichage dans ce
  sandbox). Le mécanisme de largeur max responsive (`ft.Container(width=1000)` sous un
  parent `alignment=TOP_CENTER`) repose sur le comportement documenté des contraintes
  Flutter — pas de recalcul dynamique au resize (`page.on_resize`) : ce n'était pas
  nécessaire pour obtenir le comportement demandé (rétrécit sur fenêtre étroite, plafonne
  à 1000 px sur fenêtre large), mais une vérification visuelle réelle reste recommandée
  avant merge, en particulier en redimensionnant la fenêtre au-delà de 1000 px.
- Interprétation retenue : "aucun changement... aucun wizard" (contraintes du sprint) lu
  comme "ne pas changer la logique/l'état du wizard" et non "ne pas toucher au rendu visuel
  de la page Mon calendrier" — celle-ci était explicitement listée dans "Pages concernées".
  `GenerateState`, `CalendarViewControls` et tous les handlers de `main_view.py` sont
  inchangés ; seul l'habillage visuel de `build_calendar_view` a changé.
- L'en-tête de Mon calendrier a perdu le placeholder logo qu'il affichait depuis le
  Sprint 26, au profit du même `section_title` que les autres pages — jugé nécessaire pour
  une uniformité réelle des titres (l'un des points explicitement demandés). Le placeholder
  logo reste présent sur la page À propos.

---

## Session 2026-07-07 — Sprint 26 : Release Alpha Phase 2 — UX & Design System

### Objectif
Transformer l'app desktop en logiciel utilisable par un utilisateur non développeur,
sans ajouter de fonctionnalité métier : design system centralisé, assistant guidé pour
"Mon calendrier", homogénéisation visuelle, emplacement prêt pour le futur logo. Aucun
changement au moteur (providers, export ICS, modèles métier) ni aux pages Ce week-end /
Mes favoris / Préférences au-delà du reskin visuel commun.

### Travail effectué

**`motorsport_calendar/gui/theme.py`** — nouveau module, design system
- `BAppsColors` (palette écosystème, source `BApps-Studio/02-Brand/BrandGuide.md`) et
  `MotorsportColors` (palette produit v1.0, source `BApps-Studio/03-Products/
  Motorsport-Calendar/Branding/Branding.md`)
- `Colors` — rôles sémantiques (PRIMARY, SURFACE, BORDER, TEXT_*, CTA, SUCCESS, ERROR…)
  consommés par les vues ; seule couche autorisée à référencer les palettes brutes
- `Spacing` (échelle 4px), `Radius`, `IconSize`, `FontSize` — échelles centralisées
- `page_padding()`, `section_title()` — layout de page standard
- `button_style(variant)` — "primary" / "cta" / "ghost"
- `card()`, `chip()` — composants réutilisables (cartes bordées, badges "prochainement")
- `logo_placeholder(kind, size)` — emplacement réservé au futur logo (voir plus bas)
- 100 % de couverture, 34 tests (`tests/test_gui_theme.py`)

**`motorsport_calendar/gui/assets/logo/README.md`** — nouveau
- Emplacement prévu pour les assets définitifs du Brand Set v1.0 (non livrés ce sprint —
  contrainte explicite : le logo ne bloque pas le développement)
- Documente les fichiers attendus (`mc-icon.svg`, `logo-horizontal.svg`, favicons, `.ico`)
  et les 3 étapes d'intégration future (copier les fichiers, décommenter `assets_dir` dans
  `app.py`, remplacer `theme.logo_placeholder(...)` par `ft.Image(...)`)

**`motorsport_calendar/gui/views/calendar.py`** — refonte complète en assistant 4 étapes
- `CalendarViewControls` étendue : `current_step`, `on_step_click`, `back_btn`, `next_btn`,
  `recap_controls` (en plus des contrôles existants)
- Étape 1 Saison → Étape 2 Championnats → Étape 3 Destination → Étape 4 Créer
- `_step_indicator()` — 4 puces cliquables (retour uniquement vers une étape déjà visitée ;
  la progression en avant passe obligatoirement par "Suivant", qui valide l'étape courante)
- Un seul step est rendu à la fois ; `back_btn`/`next_btn` sont les mêmes instances
  d'une étape à l'autre — seule leur visibilité change (layout pur, aucune mutation d'état)
- Toujours strictement layout : aucune logique/état, conforme à la règle existante du module

**`motorsport_calendar/gui/models.py`** — `GenerateState`
- Ajout `current_step: int = 0`, `STEP_COUNT = 4`
- `step_valid(step)` — règle de validité par étape (saison toujours valide ; championnats
  ⇔ sélection non vide ; destination ⇔ chemin renseigné ; créer ⇔ `is_ready()`)
- `can_advance()` / `can_go_back()` — dérivés purs, testables sans Flet

**`motorsport_calendar/gui/main_view.py`**
- État/handlers du wizard : `on_wizard_next`, `on_wizard_back`, `on_step_click`,
  `_refresh_calendar_view()` (reconstruit `calendar_container.content` à chaque
  changement d'étape — seule exception à la règle "vue construite une fois, swap sans
  rebuild", nécessaire car chaque étape affiche des contrôles différents)
- `_build_recap_controls()` — récapitulatif étape 4 avec lien "Modifier" par ligne
  (saison / championnats / destination), renvoie directement à l'étape concernée
- Remplacement de toutes les couleurs codées en dur (`ft.Colors.GREEN_700`, `WHITE60`…)
  par les tokens `theme.*` — nav rail, dialogue de succès, bouton "Créer"
- Correction incidente : `ft.Colors.WHITE12/30/38/54/60/70` (dépréciés dans Flet 0.85)
  → `WHITE_12/30/38/54/60/70` — corrigé une seule fois dans `theme.py`, plus de warning

**`motorsport_calendar/gui/views/weekend.py`, `favorites.py`, `preferences.py`, `about.py`**
- Reskin visuel uniquement via les tokens `theme.*` (couleurs, spacing, radius, cartes,
  chip) — **aucun changement de contenu, de texte ou de comportement** sur ces 3 pages
  explicitement hors scope (Ce week-end, Mes favoris, Préférences)
- `about.py` : ajout de `theme.logo_placeholder("icon")` à la place de l'icône générique
  Flet en en-tête — c'est le seul autre emplacement de logo préparé ce sprint (avec le
  wizard "Mon calendrier")
- Padding de page harmonisé : `theme.page_padding()` partout (vertical 24 / horizontal 32)

**`motorsport_calendar/gui/strings.py`**
- 23 nouvelles chaînes `wizard_*` (titres d'étape, aides, boutons Suivant/Précédent/
  Modifier, libellés du récapitulatif) — toujours centralisées, comme le reste de l'UI

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/gui/theme.py` | Créé — design system |
| `motorsport_calendar/gui/assets/logo/README.md` | Créé — emplacement logo futur |
| `motorsport_calendar/gui/views/calendar.py` | Réécrit — assistant 4 étapes |
| `motorsport_calendar/gui/models.py` | Modifié — `current_step`, `step_valid`, `can_advance`, `can_go_back` |
| `motorsport_calendar/gui/main_view.py` | Modifié — wiring wizard + theme partout |
| `motorsport_calendar/gui/views/weekend.py` | Modifié — reskin theme uniquement |
| `motorsport_calendar/gui/views/favorites.py` | Modifié — reskin theme uniquement |
| `motorsport_calendar/gui/views/preferences.py` | Modifié — reskin theme uniquement |
| `motorsport_calendar/gui/views/about.py` | Modifié — reskin theme + logo placeholder |
| `motorsport_calendar/gui/strings.py` | Modifié — 23 chaînes wizard |
| `tests/test_gui_theme.py` | Créé — 34 tests |
| `tests/test_gui_models.py` | Modifié — 15 tests wizard state |
| `tests/test_gui_views.py` | Modifié — tests CalendarView adaptés au wizard (dataclass, gating nav, indicateur d'étapes) |
| `docs/JOURNAL.md` | Mis à jour |
| `docs/AI_CONTEXT.md` | Mis à jour |
| `docs/TODO.md` | Mis à jour |
| `docs/ROADMAP.md` | Mis à jour |
| `docs/DECISIONS.md` | ADR-018 ajouté |

### Bugs rencontrés

1. **Couleurs `ft.Colors.WHITE12/30/38/54/60/70` dépréciées** (Flet 0.85.3, code écrit
   contre `flet>=0.80`) — chaque usage émettait un `DeprecationWarning` à la construction.
   Corrigé une seule fois en dur dans `theme.Colors` (`WHITE_12` etc.) — bénéfice direct
   de la centralisation : plus aucun warning dans la suite de tests.
2. Aucun bug fonctionnel rencontré dans la logique du wizard — vérifié par simulation
   manuelle du parcours complet (voir Tests).

### Tests exécutés

```
819 passed — 0 failed — couverture 94 %
(764 → 819 : +55 tests — theme.py 100 %, calendar.py 100 %, models.py 100 %)
```

Vérification manuelle additionnelle (aucun environnement graphique disponible dans ce
sandbox pour lancer l'app desktop réelle) : script ad-hoc pilotant `build_main_view()`
avec une fausse `Page` pour simuler un parcours complet — sélection saison → coche/décoche
championnat (vérifie le blocage/déblocage en direct de "Suivant") → étape destination
(bloquée sans chemin) → retour arrière (l'état des étapes précédentes est préservé).
Tous les points de blocage se comportent comme attendu.

### Limites (voir aussi section dédiée du rapport)

- Pas de capture d'écran réelle possible : environnement sans serveur d'affichage
  (`flet build` / rendu Flutter nécessitent un display). Vérifié à la place par tests
  unitaires (100 % sur les 3 nouveaux modules) + simulation de parcours complet.
- Interprétation retenue pour "aucun changement" sur Ce week-end / Mes favoris /
  Préférences : appliquée au **contenu et au comportement**, pas au style visuel — sinon
  la tâche 3 (uniformisation) ne pourrait pas s'appliquer à ces pages. À confirmer avec
  le product owner si ce n'est pas l'intention.
- Dette mypy préexistante sur `main_view.py` (signatures `on_click` Flet 0.80 vs 0.85.3
  installé) : 21 erreurs sur `master` avant ce sprint, 26 après (+5 proportionnelles aux
  nouveaux handlers du wizard, même pattern que le code existant) — non corrigée, hors
  scope (nécessiterait un audit des stubs Flet sur tout le fichier).
- Logo définitif toujours non intégré (conforme à la contrainte) — emplacement prêt,
  voir `gui/assets/logo/README.md`.

---

## Session 2026-07-06 — Release Alpha : Branding v1.0

### Objectif
Produire les assets graphiques officiels du produit à partir du Brand Set validé (`BApps-Studio/03-Products/Motorsport-Calendar/Branding/Brand-Set-v1.0.png.png`) : logos, icône, favicons, `.ico`, visuels GitHub. Aucun redesign — déclinaison du Brand Set existant.

### Travail effectué

**Sources vectorielles** (recréation fidèle du Brand Set — palette, typographie et composition respectées ; pas un export direct du moodboard)
- `mc-icon.svg` — monogramme MC, dégradé BApps Blue → BApps Cyan, accent damier
- `logo-horizontal.svg` — monogramme + wordmark "Motorsport Calendar" (Variante A, texte blanc) + tagline "by BApps"
- `logo-vertical.svg` — monogramme centré au-dessus du wordmark, "Calendar" en dégradé

**Rendu** via un environnement de rendu isolé (Node + sharp/librsvg, polices Space Grotesk + Arial en substitut d'Inter — non commité, outillage local uniquement) :
- `mc-icon.png`, `logo-horizontal.png`, `logo-vertical.png` (fond transparent)
- `favicon-32.png`, `favicon-16.png`
- `icon.ico` — multi-résolution 16/24/32/48/64/128/256, tuile arrondie sur fond sombre
- `Cover-GitHub.png` (1200×630), `Banner.png` (1920×400)
- `Branding.md` — palette, typographie, principes d'usage, liste des livrables

**Diffusion**
- Livrables déposés dans `assets/branding/` (ce dépôt) et dans `BApps-Studio/03-Products/Motorsport-Calendar/Branding/` (référentiel central du studio)
- `motorsport_calendar/gui/assets/icon.png` peuplé (placeholder déjà prévu dans `app.py`, code non modifié — l'activation de `assets_dir`/`window.icon` reste à décider)
- `README.md` : ajout de la bannière en en-tête

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `assets/branding/*` | Créé — 12 fichiers (sources SVG + rendus + Branding.md) |
| `motorsport_calendar/gui/assets/icon.png` | Créé |
| `README.md` | Modifié — bannière en en-tête |
| `docs/JOURNAL.md` | Mis à jour |

### Tests exécutés
Non applicable — tâche de production d'assets graphiques, aucun code exécutable modifié.

### Bugs rencontrés
- La police variable Space Grotesk rendait en serif de repli avec `font-weight: 700` (Bold) via librsvg/Pango, mais correctement en sans-serif avec `font-weight: 600` — utilisé 600 (SemiBold), qui correspond de toute façon à la graisse spécifiée par la charte pour les titres.
- Les URLs `static/Inter-*.ttf` du dépôt `google/fonts` renvoyaient une page HTML 404 au lieu du fichier : substitution par Arial pour les textes secondaires en attendant une source Inter valide.

---

## Session 2026-07-05 — Sprint 12 : CLI generate (agrégateur multi-provider)

### Objectif
Ajouter la commande `motocal generate YEAR OUTPUT.ics` qui itère tous les providers activés, fusionne les événements en un seul ICS, et résiste à l'échec partiel.

### Travail effectué

**`docs/PROJECT_RULES.md`**
- Ajout règle 8 : résilience des commandes CLI agrégées — un provider qui échoue ne stoppe pas les autres.

**`motorsport_calendar/cli.py`** — nouvelle commande `generate`
- Lit `config.yaml` via `ConfigService`
- `registry.discover()` + `source_registry.discover()` — découverte automatique
- `registry.enabled(config.providers)` — liste des IDs activés (opt-out)
- Pour chaque provider : `source_registry.get(cid, source_name)(cache, refresh)` + `registry.get(cid)(source)`
- Fetch asynchrone groupé dans un seul `asyncio.run(_fetch_all())` — isolation d'erreur par provider
- Exceptions capturées individuellement : `NotImplementedError`, `httpx.HTTPStatusError`, `httpx.TimeoutException`, `Exception`
- Résumé `✓ provider : N événements` / `✗ provider : raison` affiché après fetch
- Tri chronologique par `min(s.start_datetime for s in e.sessions)` — events sans sessions triés en dernier
- Exit 0 si au moins un provider réussit, exit 1 si tous échouent
- Fallback source : `source_registry.list_for(cid)[0]` si `ProviderConfig.source == ""`

**`tests/test_cli_generate.py`** — 17 tests
- Happy path (9) : F1 seul exit 0, F1 seul crée fichier, F1 seul 3 VEVENTs, les deux exit 0, les deux 6 VEVENTs, VCALENDAR, ✓ dans output, ✗ dans output, saison vide exit 0
- Error path (5) : tous échouent exit 1, tous échouent pas de fichier, F1 HTTP 503 + WEC exit 0, F1 timeout + WEC exit 0, provider survivant exporté
- Refresh (2) : flag exit 0, flag crée fichier
- Tri (1) : WEC janvier avant F1 mars dans l'ICS

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `docs/PROJECT_RULES.md` | Modifié — règle 8 résilience |
| `motorsport_calendar/cli.py` | Modifié — ajout commande generate |
| `tests/test_cli_generate.py` | Créé — 17 tests |
| `docs/TODO.md` | Mis à jour |
| `docs/AI_CONTEXT.md` | Mis à jour |

### Tests exécutés
```
306 passed — 0 failed — couverture 92 %
```

---

## Session 2026-07-05 — Sprint 11 : CLI generate-wec

### Objectif
Ajouter la commande `motocal generate-wec YEAR OUTPUT.ics`, symétrique à `generate-f1`.

### Travail effectué

**`motorsport_calendar/cli.py`**
- Nouvelle commande `generate-wec` : même orchestration que `generate-f1`
- `source_registry.get("wec", source_name)` + `registry.get("wec")(source)`
- Gestion spécifique `NotImplementedError` : message clair "source non encore implémentée" → exit 1
- Flags : `YEAR`, `OUTPUT`, `--refresh`

**`tests/test_cli_generate_wec.py`** — 16 tests
- Happy path : exit 0, fichier créé, VCALENDAR, 3 VEVENTs (2 events, sessions mixtes), locations, saison vide
- Appel unique à `get_season` (vs 2 appels `_get_json` pour F1)
- Transmission du `year` correct au source
- Error path : `NotImplementedError` (stub réel — aucun mock), HTTP 503/404, timeout
- Flag `--refresh` : exit 0, fichier créé

### Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `motorsport_calendar/cli.py` | Modifié — ajout generate-wec |
| `tests/test_cli_generate_wec.py` | Créé — 16 tests |
| `docs/TODO.md` | Mis à jour |

### Bugs rencontrés
- `Circuit` a des champs requis supplémentaires (`id`, `city`, `timezone`) non documentés dans le résumé de session — corrigé dans les données de test.

### Tests exécutés
```
289 passed — 0 failed — couverture 92 %
```

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
