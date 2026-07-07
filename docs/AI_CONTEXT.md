# AI_CONTEXT.md

> Fichier de reprise rapide pour une IA. Mis à jour après chaque session.
> Dernière mise à jour : 2026-07-07 (Sprint 32)

---

## État du projet

- **Nom** : motorsport-calendar
- **Version** : 0.2.0 (alpha)
- **Phase** : Sprint 32 — Normalisation des métadonnées des événements ✅
- **Tests** : 983 passants, 0 échouants — couverture ~95 %
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
24. **Release Alpha Phase 1 (Sprint 25)** — Architecture `gui/views/` : 5 modules indépendants (`weekend.py`, `calendar.py`, `favorites.py`, `preferences.py`, `about.py`), chacun exposant `build_*_view()`. `CalendarViewControls` dataclass pour injecter les contrôles dans `calendar.py`. `PreferencesModel` frozen dataclass (language, timezone, first_day_of_week, favorite_championships, preferred_calendar, bapps_sync_enabled). `main_view.py` refactorisé en shell de navigation pur. Navigation 5 destinations : Ce week-end / Mon calendrier / Mes favoris / Préférences / À propos. Flet fix bonus : `ft.Border.all()` (pas `ft.border.all()`). 44 nouveaux tests. **764 tests total**.
23. **GUI Desktop Alpha 3 — Product Polish (Sprint 24)** — `categories.py` (`Category` StrEnum 5 valeurs, `ChampionshipGroup` frozen dataclass, `GROUPS` registre, `get_groups_for()` helper avec fallback). Navigation `ft.NavigationRail` 3 destinations (Accueil/Calendrier/À propos). `page.on_resize` pour rail étendu >900px. Championnats groupés visuellement (`🏎 Formula`, `🏁 Endurance`). Écran Accueil + écran À propos (lien GitHub via `ft.UrlLauncher`). `strings.py` + 11 chaînes (nav + about). 25 nouveaux tests. **720 tests total**. Services Flet : `FilePicker` + `UrlLauncher` dans `page.services`.
25. **Release Alpha Phase 2 — UX & Design System (Sprint 26)** — `gui/theme.py` (nouveau) : `BAppsColors`/`MotorsportColors` (palettes brutes, sourcées depuis `BApps-Studio/02-Brand/BrandGuide.md` et `.../Motorsport-Calendar/Branding/Branding.md`), `Colors` (rôles sémantiques — seule couche que les vues doivent importer), `Spacing`/`Radius`/`IconSize`/`FontSize` (échelles), `page_padding()`/`section_title()`/`button_style()`/`card()`/`chip()`/`logo_placeholder()`. "Mon calendrier" (`gui/views/calendar.py`) réécrit en assistant 4 étapes (saison/championnats/destination/créer) : `CalendarViewControls` étendue (`current_step`, `on_step_click`, `back_btn`, `next_btn`, `recap_controls`), un seul step rendu à la fois, layout pur (aucun état). `GenerateState` (`models.py`) : `current_step`, `STEP_COUNT=4`, `step_valid(step)`, `can_advance()`, `can_go_back()` — logique de wizard testable sans Flet. `main_view.py` : handlers `on_wizard_next/back`, `on_step_click`, `_refresh_calendar_view()` (seule vue reconstruite à chaque changement — toutes les autres restent "construites une fois, swap sans rebuild"), `_build_recap_controls()` (récap étape 4 avec liens "Modifier"). `weekend.py`/`favorites.py`/`preferences.py`/`about.py` : reskin visuel via `theme.*` uniquement, contenu/comportement inchangés. `gui/assets/logo/README.md` : emplacement du futur logo (Brand Set v1.0 validé mais SVG non livrés ce sprint) — `theme.logo_placeholder()` en attendant, dans `about.py` et l'en-tête du wizard. Correction incidente : `ft.Colors.WHITE12/30/38/54/60/70` dépréciés en Flet 0.85 → `WHITE_12/30/38/54/60/70`, corrigé une seule fois dans `theme.py`. 55 nouveaux tests (34 `test_gui_theme.py` + 15 wizard state + 6 wizard views). **819 tests total**.
26. **Uniformisation du layout (Sprint 27)** — `theme.page_shell(*sections)` (nouveau) : LA grille unique de toutes les vues — `Container` externe `expand=True, alignment=TOP_CENTER` (centre uniquement le conteneur) + `Container` interne `width=MAX_CONTENT_WIDTH` (1000, se rétrécit naturellement sous 1000px via `BoxConstraints.enforce` de Flutter, aucun recalcul manuel au resize) + `Column` unique `horizontal_alignment=STRETCH` (remplit la largeur des cartes/formulaires, ne centre jamais le contenu). Les 5 vues (`weekend.py`, `calendar.py`, `favorites.py`, `preferences.py`, `about.py`) construisent leurs sections (`section_title` + `Divider` + contenu) et les passent à `page_shell(...)` au lieu de bâtir leur propre conteneur racine. Weekend/Favoris/À propos perdent leur centrage (`TOP_CENTER`/`CrossAxisAlignment.CENTER`/`text_align=CENTER`) au profit d'un contenu aligné à gauche, comme Mon calendrier/Préférences l'étaient déjà. Mon calendrier perd son en-tête custom (logo+nom app) au profit du même `section_title` que les autres pages (nom de section, pas nom de l'app) — le placeholder logo (Sprint 26) reste uniquement sur À propos. Carte placeholder Ce week-end : largeur fixe (320px) supprimée, remplit le gabarit comme les autres cartes. `GenerateState`, `CalendarViewControls` et les handlers de `main_view.py` **inchangés** — uniquement le conteneur racine retourné par chaque `build_*_view()`. `TestAllViewsShareTheSameGrid` verrouille que les 5 vues partagent strictement la même largeur/centrage/alignement/padding. 18 nouveaux tests. **837 tests total**.
27. **Uniformisation finale de l'interface (Sprint 28)** — Wizard : `_step_header()` supprimé de `gui/views/calendar.py`, plus de titre "Étape N — ..." ni de texte d'aide sous le bandeau de pastilles — chaque étape commence directement par son champ (`_step_season` = juste `year_dropdown`, etc.). 8 constantes `wizard_title_*`/`wizard_help_*` supprimées de `strings.py` (`wizard_step_*` conservées). Pages vides (`weekend.py`, `favorites.py`, `preferences.py`) : passent désormais **une seule section** à `page_shell(...)` — un `theme.card(...)` contenant tout leur contenu (en-tête `section_title` + `Divider` + corps). Sous-éléments qui avaient leur propre bordure (`_race_preview_content` dans weekend.py, `_pref_row` dans preferences.py) l'ont perdue pour éviter un double encadrement, maintenant nested dans la carte centrale unique de la page. À propos (`about.py`) : header générique `section_title("À propos")` retiré — le bloc "Motorsport Calendar / Version Alpha" (+ logo placeholder) sert lui-même de titre ; espaceurs `Container(height=...)` manuels remplacés par l'espacement uniforme de `page_shell`. Pas de carte pour À propos (contrairement aux 3 pages vides). `theme.py`, `main_view.py`, `models.py`, navigation, couleurs, Design Tokens **non modifiés**. 9 nouveaux tests. **846 tests total**.
28. **Ce week-end — version fonctionnelle (Sprint 29)** — `gui/upcoming_weekend.py` (nouveau, logique pure) : `WeekendEntry(championship_id, event)` (voir ADR-020 — `Event.championship.id` est suffixé par l'année, jamais l'id du registre), `find_next_weekend_entries()` (avance semaine par semaine, vendredi-dimanche UTC, jusqu'à trouver ≥1 session), `find_upcoming_weekend()` (recherche + regroupement via `categories.get_groups_for` réutilisé tel quel + mise en forme FR : `_SESSION_LABELS`, `_COUNTRY_LABELS` ~35 pays, heure convertie dans `Circuit.timezone`). `gui/controller.py` : `get_upcoming_weekend(now=None)` — mirroir exact de `generate_calendar` (mêmes registries/cache, `refresh=False` toujours, aucun nouveau provider), boucle sur les 5 championnats fixes (`WEEKEND_CHAMPIONSHIP_IDS`) × 2 années. `gui/views/weekend.py` réécrit : `build_weekend_view(result: WeekendResult | None)` — 3 états exacts (chargement/aucune course/trouvé, une carte par championnat). `main_view.py` : `weekend_container` + `_load_weekend()` tâche asyncio démarrée une fois au lancement (référencée sur `page.weekend_load_task`, jamais retapée par visite d'onglet), résolue via le cache HttpCache existant (TTL 24h). 34 nouveaux tests (21 logique pure + 8 contrôleur + 5 vue). **880 tests total**.
29. **Composant ChampionshipCard (Sprint 30)** — nouveau paquet `gui/components/` (bibliothèque de composants, distincte de `gui/views/` et de `gui/theme.py`). `components/championship_card.py` : `SessionRow`/`ChampionshipCardData` (modèle du composant, promu depuis `upcoming_weekend.WeekendCard`/`SessionRow` — renommage, mêmes champs) + `build_championship_card(data, *, footer=None)`. En-tête sur 4 lignes distinctes (championnat, Grand Prix, circuit, pays — plus de "·" combinant circuit/pays). Sessions alignées via `ft.Row(alignment=SPACE_BETWEEN)` (libellé à gauche, heure à droite, indépendant de la longueur du texte). `footer` : point d'extension pour Favori/Notifications/Export ICS/Partage/Résultats — `None` aujourd'hui partout, aucun changement visuel ; quand fourni, ajoute `Divider` + le contrôle sans l'interpréter. `upcoming_weekend.py` et `views/weekend.py` migrés pour consommer ce composant partagé (`_found_state` ne construit plus aucun layout de carte). 23 nouveaux tests. **903 tests total**.
30. **Layout System (Sprint 31)** — nouveau sous-paquet `gui/components/layout/` : `PageContainer(*, header=None, body=())` (délègue à `theme.page_shell`, largeur/padding/alignement), `PageHeader(title, *, icon=None, subtitle=None)` (icône+titre+sous-titre+séparateur, remplace `theme.section_title()+ft.Divider()` partout), `Section(*controls, spacing=Spacing.SM)` (espacement entre blocs, aucune connaissance des titres), `SectionHeader(title, *, icon=None)` (intitulé secondaire dans une Section, sans consommateur actuel — prêt pour Tableau de bord/Recherche), `CardList(cards, *, spacing=Spacing.SM)` (liste verticale uniforme), `EmptyState(title, *, message=None, icon=None)` (le "rien ici" encarté, centralisé), `PageSpacing(size=Spacing.MD)` (espace nommé ponctuel). Nommage PascalCase délibéré (widget-style) — exception `ruff.toml` `N802` scopée à ce seul paquet. Les 5 vues migrées : `weekend.py`/`favorites.py`/`preferences.py`/`calendar.py` utilisent `PageHeader` séparé du corps (changement assumé vis-à-vis du Sprint 28 — voir ADR-022) ; `about.py` garde son bloc de marque compact SANS `PageHeader` (choix Sprint 28 préservé). Préférences : les lignes retrouvent leur bordure individuelle (plus de carte englobante à éviter de doubler). 51 nouveaux tests (`test_gui_components_layout.py`) + 11 tests `test_gui_views.py` adaptés/ajoutés. **957 tests total**.
31. **Normalisation des métadonnées d'événement (Sprint 32)** — nouveau module `gui/event_display.py` : `EventDisplayData(grand_prix_name, circuit_name: str | None, country: str | None)` + `normalize_event_display(championship_id, event)`. Corrige le doublon "Belgian / Belgian" observé sur F2/F3/F1 Academy (voir investigation ci-dessus) et le "Unknown" affiché tel quel : (1) doublon Grand Prix/circuit → une seule ligne, (2) circuit inconnu → repli `circuit.name`→`circuit.city`→masqué, (3) pays `"Unknown"`/vide → masqué, jamais affiché, (4) nom absent → suffixe " Grand Prix" ajouté pour F1/F2/F3/F1 Academy (jamais WEC) puis repli circuit puis `STRINGS.event_name_fallback` ("Événement"). `country_label()` déménagé depuis `upcoming_weekend.py`. `ChampionshipCardData.circuit_name`/`.country` deviennent `str | None` ; `build_championship_card` omet simplement une ligne `None`, sans aucune décision (toujours zéro logique métier dans le composant). 26 nouveaux tests. **983 tests total**.
32. **Registre des identités visuelles de championnat (Sprint 33)** — nouveau module `gui/championship_assets.py` : `ChampionshipAsset(logo_src: str | None)` + `get_championship_asset(championship_id)`, point d'entrée unique. Recherche préalable dans `motorsport-calendar` ET `BApps-Studio` : aucun logo officiel de championnat n'existe nulle part dans le projet — clarifié avec l'utilisateur, option retenue = registre "prêt à recevoir" (même patron que `gui/assets/logo/README.md`). `logo_src` résolu seulement si le fichier existe réellement sur `_ASSETS_DIR / filename` ; id inconnu et id sans fichier livré → `None`, indistinguables côté appelant, jamais d'exception. `ChampionshipCard._header_title()` : `ft.Text` nu si `None` (état réel de tous les championnats aujourd'hui — layout strictement inchangé), sinon `ft.Row([ft.Image(logo_src, width=height=IconSize.LG, fit=BoxFit.CONTAIN), ft.Text(...)])` — aucun `if championship_id == ...` dans le composant. Nouveau dossier `gui/assets/championships/` (`.gitkeep` + README), aucun fichier logo livré. Piège Flet 0.85.3 : `ft.ImageFit` n'existe pas, c'est `ft.BoxFit`. 16 nouveaux tests. **999 tests total**.

---

## Fonctionnalités en cours / prochaines

**Prochaines tâches recommandées** (après Sprint 33) :

1. **Intégrer le logo définitif** — remplacer les appels `theme.logo_placeholder(...)` listés dans `gui/assets/logo/README.md` dès que les SVG du Brand Set v1.0 sont livrés dans le dépôt (un seul emplacement : À propos)
1bis. **Déposer les logos officiels de championnat** — copier `formula1.png`/`formula2.png`/`formula3.png`/`f1-academy.png`/`wec.png` dans `gui/assets/championships/` (voir README dans ce dossier) puis décommenter `assets_dir=` dans `gui/app.py` (partagé avec le point 1) : `get_championship_asset()` détecte les fichiers automatiquement, aucun autre changement de code nécessaire.
2. **Packaging Windows `.exe`** — `flet build windows` → distributable sans Python
3. **Fonctionnalités "Mes favoris"** — sauvegarder/charger une liste de championnats favoris ; composer sa vue avec `PageContainer(header=PageHeader(...), body=[Section(CardList([build_championship_card(...) for ...]))])` — le Layout System (Sprint 31) et ChampionshipCard (Sprint 30) couvrent déjà tout le nécessaire, plus aucun code de mise en page à écrire
4. **Activation Préférences** — brancher `PreferencesModel` sur l'UI (dropdowns actifs)
5. **Audit mypy `main_view.py`** — signatures `on_click` Flet 0.80 (code) vs 0.85.3 (installé) : 26 erreurs préexistantes, inchangé depuis Sprint 26 (non touché aux Sprints 27/28/29/30/31/32)
6. **Vérification visuelle réelle** — confirmer sur un poste avec affichage : le redimensionnement du gabarit, le rendu du nouvel en-tête séparé (Favoris/Ce week-end/Préférences), les bordures restaurées des lignes de Préférences, et les cartes ChampionshipCard réelles de Ce week-end (métadonnées normalisées, Sprint 32)
7. **`OfficialWecSource` réelle** — tant qu'elle reste `NotImplementedError`, "Ce week-end" ne montrera jamais de carte Endurance ; implémenter la source ferait automatiquement apparaître WEC dans les résultats sans toucher à `upcoming_weekend.py` ni au composant
8. **Ancrer le découpage vendredi-dimanche sur le fuseau du circuit** (actuellement UTC) — cas limite documenté pour les circuits très à l'est (Japon, Singapour, Chine, Australie) dont la séance du vendredi matin local peut tomber un "jeudi" UTC
9. **Prochains composants de la bibliothèque** — au fur et à mesure des besoins (Recherche, Tableau de bord, Notifications, Historique), ajouter à `gui/components/` en suivant le même principe : modèle propre au composant, aucune dépendance à un domaine métier, primitives `theme.py` uniquement. Pour une page de mise en page, partir de `gui/components/layout/` — c'est exactement pour ça qu'il existe.
10. **Premier consommateur réel de `SectionHeader`** — dès qu'une page affichera plusieurs groupes de cartes distincts (Tableau de bord probablement en premier), l'utiliser à l'intérieur d'une `Section` par groupe.
11. **Corriger `_build_circuit` côté provider** (F2/F3/F1 Academy) — utiliser `event_data["location"]` pour `Circuit.name` au lieu de réutiliser `event_data["name"]` ; réduirait le besoin de repli sur `circuit.city` dans `event_display.py`, mais nécessite de toucher au provider (explicitement hors périmètre du Sprint 32).
12. **Compléter les tables `_CIRCUIT_DATA`** (pays) de F2/F1 Academy — F3 couvre déjà mieux certains circuits ; réduirait le nombre de lignes pays masquées dans "Ce week-end" (côté provider, hors périmètre du Sprint 32).
13. **Table démonyme pays → adjectif** si la qualité "Canada Grand Prix" vs "Canadian Grand Prix" devient gênante — actuellement un compromis assumé (`event_display.py`).

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
- **`_build_circuit` met `Circuit.name = Event.name`** (Sprint 32 — investigation) : le dataset `sportstimes/f1` (F2/F3/F1 Academy) n'a pas de champ "nom de circuit" dédié, seulement un descriptif court de manche (`name`, ex. "Belgian") et un `location` (plus proche d'un nom de circuit que d'une ville, ex. "Spa-Francorchamps", mappé sur `Circuit.city`). Le code réutilise `name` pour `Circuit.name` aussi, d'où `Event.name == Circuit.name` pour ces 3 séries (jamais pour F1/Jolpica, qui a un vrai `circuitName`). Corrigible côté provider (utiliser `location` pour `Circuit.name`) mais non fait — compensé côté présentation par `gui/event_display.py` (ADR-023) sans toucher au provider.
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
- **Design system GUI (Sprint 26)** : toute couleur/spacing/radius/taille d'icône dans `gui/views/*` ou `gui/main_view.py` vient de `gui/theme.py` — jamais `ft.Colors.*` ni un entier brut. Palette écosystème = `theme.BAppsColors`, palette produit = `theme.MotorsportColors`, les vues n'importent que `theme.Colors` (rôles sémantiques).
- **Wizard "Mon calendrier"** : `GenerateState.current_step` (0-3) pilote quelle étape `views/calendar.py` rend. `state.can_advance()`/`can_go_back()` gèrent le gating — jamais de logique de validité dans `calendar.py` (layout pur, il ne fait que lire `c.current_step`).
- **Logo** : pas de SVG définitif dans le dépôt — `theme.logo_placeholder(kind, size)` partout où le logo apparaîtra. Voir `gui/assets/logo/README.md` pour la liste des emplacements et la procédure d'intégration future.
- **Flet 0.85 — couleurs `WHITE*` dépréciées** : utiliser `ft.Colors.WHITE_12/30/38/54/60/70` (underscore), pas `WHITE12` etc. — sinon `DeprecationWarning` à chaque construction du contrôle. Déjà corrigé dans `theme.py`.
- **`Event.championship.id` ≠ id du registre** (Sprint 29, ADR-020) : chaque provider suffixe par l'année (`"formula1-2026"`). Toute logique GUI qui doit regrouper/afficher par championnat (comme `categories.get_groups_for` ou `display_names.get_display_name`) doit recevoir l'id du registre séparément — jamais le déduire de `event.championship.id`. Pattern : `upcoming_weekend.WeekendEntry(championship_id, event)`.
- **Défaut de source par championnat** : `ConfigService().providers.get(cid)` peut avoir un défaut EXPLICITE différent du premier enregistré dans `source_registry` — ex. `formula1` défaut sur `"openf1"` (voir `config/models.py`), pas `"jolpica"` bien qu'enregistrée en premier. Toujours vérifier `ProvidersConfig` avant de mocker une source dans un test qui passe par `ConfigService` réel.
- **"Ce week-end" (Sprint 29)** : `gui/upcoming_weekend.py` (logique pure, testée sans HTTP) + `controller.get_upcoming_weekend()` (fetch, mirroir de `generate_calendar`). Périmètre figé à `upcoming_weekend.WEEKEND_CHAMPIONSHIP_IDS` (5 championnats), indépendant de l'opt-out `config.yaml`. Recherche vendredi-dimanche en **UTC** (limite documentée pour les circuits très à l'est) ; l'heure *affichée* par session est convertie dans `Circuit.timezone` (IANA, déjà présent dans le modèle). Fetch déclenché une fois au lancement de l'app (`main_view.py::_load_weekend`, référencé sur `page.weekend_load_task`), jamais à chaque visite d'onglet — repose sur le TTL de `HttpCache` (24h par défaut) pour l'aspect "jamais de réseau à chaque ouverture".
- **Bibliothèque de composants `gui/components/`** (Sprint 30, ADR-021) : distincte de `gui/views/` (une page = un module) et de `gui/theme.py` (tokens/primitives). Un composant définit son propre modèle de données (déjà mis en forme — jamais un `Event`/`Session`/`Championship`/`Circuit`), se construit uniquement à partir des primitives `theme.py`, et expose ses points d'extension explicitement (ex. `footer: ft.Control | None` sur `championship_card.build_championship_card` — le composant place le contrôle fourni sans jamais l'interpréter). Premier composant : `components/championship_card.py` (`ChampionshipCardData`, `SessionRow`, `build_championship_card`) — utilisé par `upcoming_weekend.py`/`views/weekend.py`, prévu pour Favoris/Recherche/Tableau de bord/Notifications/Historique. Prochain composant du même genre : suivre exactement ce patron (paquet `components/`, modèle dédié, primitives `theme.py` uniquement, point d'extension explicite plutôt qu'anticipé).
- **Layout System `gui/components/layout/`** (Sprint 31, ADR-022) : `PageContainer`/`PageHeader`/`Section`/`SectionHeader`/`CardList`/`EmptyState`/`PageSpacing`. Nommage PascalCase délibéré (widget-style — exception `ruff.toml` `N802` scopée à ce paquet). Toute nouvelle vue doit se composer ainsi : `PageContainer(header=PageHeader(titre, icon=...), body=[Section(...)])` — jamais de `theme.page_shell`/`theme.section_title`/`theme.card` appelés directement dans une vue pour ces besoins (le Layout System les enveloppe déjà). Règle : `PageHeader` est **toujours séparé** du corps, jamais absorbé dans une carte de contenu (changement Sprint 28→31, voir ADR-022) — seule exception assumée : `about.py`, qui garde son bloc de marque compact sans `PageHeader` du tout. `calendar.py` (wizard) n'utilise PAS `Section` pour son corps (flux séquentiel d'étapes, pas un regroupement générique) — seulement `PageContainer`/`PageHeader`/`PageSpacing`.
- **Normalisation des métadonnées d'événement `gui/event_display.py`** (Sprint 32, ADR-023) : toute vue qui construit une `ChampionshipCardData` à partir d'un `Event` domaine DOIT passer par `normalize_event_display(championship_id, event)` — ne jamais lire `event.name`/`circuit.name`/`circuit.city`/`circuit.country` directement pour peupler la carte (risque de doublon "X / X" ou de "Unknown" affiché tel quel, voir investigation Sprint 32). `circuit_name`/`country` valent `None` quand la ligne doit être masquée ; `build_championship_card` (composant) se contente d'omettre une ligne `None`, aucune décision n'est prise dans le composant.
- **Registre des identités visuelles `gui/championship_assets.py`** (Sprint 33, ADR-024) : point d'entrée unique `get_championship_asset(championship_id) -> ChampionshipAsset(logo_src: str | None)`. Jamais de chemin de fichier codé dans une vue/composant, jamais de `if championship_id == ...` — `ChampionshipCard` interroge ce registre et rend un `ft.Text` nu si `logo_src is None` (id inconnu OU logo pas encore livré, indistinguables côté appelant), sinon `ft.Row([ft.Image(logo_src, IconSize.LG), ft.Text(...)])`. Aucun logo officiel livré dans le dépôt à ce stade (voir `gui/assets/championships/README.md`, même patron que `gui/assets/logo/README.md`) — le rendu actuel de toutes les cartes est donc strictement identique à avant ce sprint. Ajouter un logo demain = déposer le fichier au nom attendu dans `gui/assets/championships/`, zéro ligne de code à changer. Attention Flet 0.85.3 : l'enum s'appelle `ft.BoxFit`, pas `ft.ImageFit` (n'existe pas dans cette version).

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
| mypy `main_view.py` : signatures `on_click`/`on_change` Flet 0.80 (code) vs 0.85.3 (installé) | 26 erreurs mypy (préexistant, non bloquant — tests runtime passent) | MOYENNE |
| Logo Motorsport Calendar toujours en placeholder (`theme.logo_placeholder()`) | Rendu visuel non définitif | BASSE — bloqué sur livraison des SVG Brand Set v1.0 |
| `OfficialWecSource` non implémentée | "Ce week-end" n'affichera jamais de carte Endurance en pratique | HAUTE — bloque aussi `generate`/`generate-wec` |
| Découpage vendredi-dimanche de "Ce week-end" ancré UTC, pas sur le fuseau du circuit | Un week-end très à l'est (Japon, Singapour…) peut être mal détecté à la marge | BASSE — cas limite documenté, heure affichée déjà correcte |
| `f1calendar_base.py::_build_circuit` réutilise `event.name` pour `Circuit.name` (F2/F3/F1 Academy) | Cause du doublon "Belgian/Belgian" — compensé côté présentation (`event_display.py`) mais pas corrigé à la source | MOYENNE — voir ADR-023, corrigible en utilisant `location` pour `Circuit.name` |
| Tables `_CIRCUIT_DATA` (pays) incomplètes pour F2/F1 Academy | Ligne pays masquée dans "Ce week-end" au lieu d'afficher un vrai pays | BASSE — comportement correct (jamais "Unknown"), juste incomplet |
| Aucun logo officiel de championnat livré (`gui/assets/championships/`) | `ChampionshipCard` ne montre jamais de logo en pratique — registre (Sprint 33, ADR-024) architecturalement prêt mais invisible | BASSE — bloqué sur livraison des fichiers + décommentage `assets_dir=` dans `gui/app.py` |

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
