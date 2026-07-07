# ROADMAP.md

> Vision : générer automatiquement des calendriers ICS pour n'importe quelle discipline motorsport, à partir de sources de données publiques, sans configuration manuelle.

---

## Vision produit

`motorsport-calendar` est un outil CLI open source qui :

- récupère les calendriers de saison depuis des API publiques ou des sources officielles
- exporte en format ICS (compatible Google Calendar, Apple Calendar, Outlook…)
- supporte plusieurs disciplines via un système de providers/sources extensible
- est configurable via un simple `config.yaml` (sources, cache, rappels, opt-out par championnat)

---

## v0.1.0 — MVP multi-provider ✅ (2026-07-05)

| Fonctionnalité | Statut |
|---|---|
| Modèles métier Pydantic v2 frozen (Championship, Circuit, Session, Event) | ✅ |
| IcsExporter RFC 5545 — 1 VEVENT par session + VALARM configurable | ✅ |
| Architecture provider/source F1 | ✅ |
| OpenF1Source — API openf1.org (2023+, 25 circuits IANA) | ✅ |
| HttpCache — cache disque JSON, TTL configurable, flag --refresh | ✅ |
| WecProvider + OfficialWecSource stub (architecture complète) | ✅ |
| ConfigService — lit config.yaml, valeurs par défaut Pydantic | ✅ |
| ProviderRegistry — auto-découverte, opt-out config | ✅ |
| SourceRegistry — clé (championnat, source), auto-enregistrement | ✅ |
| CLI `generate-f1 YEAR OUTPUT.ics` | ✅ |
| CLI `generate-wec YEAR OUTPUT.ics` (exit propre si source non implémentée) | ✅ |
| CLI `generate YEAR OUTPUT.ics` — agrégateur résilient multi-provider | ✅ |
| CLI `providers` — liste les providers enregistrés | ✅ |
| 306 tests — couverture 92 % | ✅ |
| CI GitHub Actions (Python 3.12 + 3.13) | ✅ |

---

## v0.2.0 — Sources enrichies + Formula 2 ✅ (2026-07-05)

| Fonctionnalité | Statut |
|---|---|
| `JolpicaSource` — données historiques F1 (1950+), `api.jolpi.ca` (successeur Ergast, Apache-2.0) | ✅ |
| Data Acquisition Layer (`core/datasource/`) — `JsonDataSource`, `HtmlDataSource`, `IcsDataSource` | ✅ |
| `Formula2Provider` + `F1CalendarSource` — calendrier FIA F2 complet (JSON MIT, f1calendar.com) | ✅ |
| CLI `generate-f2 YEAR OUTPUT.ics` | ✅ |
| `generate` inclut automatiquement F2 (opt-out via config) | ✅ |
| 448 tests — couverture 93 % | ✅ |

---

## v0.2.x — Nouvelles disciplines (Sprints 20-21-QA03) ✅ (2026-07-06)

| Fonctionnalité | Statut |
|---|---|
| `Formula3Provider` + `F1CalendarSource` — FIA F3 complet (2022+) | ✅ |
| `F1AcademyProvider` + `F1CalendarSource` — F1 Academy complète (2023+) | ✅ |
| Support Series Framework — `F1CalendarBaseSource` partagé F2/F3/Academy | ✅ |
| Rétrocompatibilité F2 clés sessions 2024 (`fp1`/`sprintRace`) et 2025+ (`practice`/`sprint`) | ✅ |
| Dataset Reality Check — correction bug `"events"` → `"races"`, fixtures réelles | ✅ |
| 627 tests — couverture 94 % | ✅ |

---

## v0.3.0 — Desktop Edition ✅ Sprint 22 (2026-07-06)

| Fonctionnalité | Statut |
|---|---|
| GUI Flet — fenêtre native desktop (`motocal-gui`) | ✅ |
| Sélecteur de saison (année courante ±5) | ✅ |
| Championnats auto-découverts depuis ProviderRegistry (cases à cocher) | ✅ |
| FilePicker natif — dialogue OS de sauvegarde | ✅ |
| Progression asynchrone — anneau pendant les requêtes réseau | ✅ |
| Résumé par championnat (✓ N événements / ✗ erreur) | ✅ |
| Dépendance optionnelle `flet>=0.80` (`pip install motorsport-calendar[gui]`) | ✅ |
| Zéro duplication du moteur — même pipeline que la CLI | ✅ |
| 32 tests GUI (models + controller, sans Flet) | ✅ |
| 659 tests total — couverture ~93 % | ✅ |

---

## v0.3.1 — Desktop Alpha 2 — UX Polish ✅ Sprint 23 (2026-07-06)

| Fonctionnalité | Statut |
|---|---|
| Noms de championnats lisibles (Formula 1, F1 Academy, FIA WEC…) | ✅ |
| Formula 1 cochée par défaut au premier lancement | ✅ |
| Mémorisation des sélections entre sessions | ✅ |
| Bouton "Créer mon calendrier" (texte orienté utilisateur) | ✅ |
| Nom de fichier intelligent `motorsport-calendar-{année}.ics` | ✅ |
| Dernier dossier de sortie mémorisé | ✅ |
| Dialogue succès : événements, sessions, chemin, "Ouvrir le dossier" | ✅ |
| Toutes les chaînes centralisées dans `strings.py` | ✅ |
| `display_names.py`, `preferences.py`, `assets/` (placeholder icône) | ✅ |
| `docs/PRODUCT_VISION.md` | ✅ |
| 36 nouveaux tests — 695 total | ✅ |

---

## v0.4.7 — Registre des identités visuelles de championnat ✅ Sprint 33 (2026-07-07)

| Fonctionnalité | Statut |
|---|---|
| `gui/championship_assets.py` — registre central `championship_id` → logo (extensible couleur/icône) | ✅ |
| Point d'entrée unique `get_championship_asset()` — aucune vue/composant ne connaît un chemin de fichier | ✅ |
| `ChampionshipCard` : logo affiché à gauche du titre, `IconSize.LG` (24px), aucun `if championnat == ...` | ✅ |
| Aucun fichier logo officiel livré — repli gracieux, layout actuel inchangé pixel pour pixel | ✅ |
| Aucune régression — Design System, navigation, providers, layout inchangés | ✅ |
| 16 nouveaux tests — 999 total, couverture 95 % | ✅ |

---

## v0.4.6 — Normalisation des métadonnées des événements ✅ Sprint 32 (2026-07-07)

| Fonctionnalité | Statut |
|---|---|
| `gui/event_display.py` — normalisation dédiée (jamais "Unknown", jamais de doublon) | ✅ |
| Règle documentée pour le nom de Grand Prix absent/court/déjà complet | ✅ |
| Investigation F1 vs F2/F3/F1 Academy documentée (cause API + cause mapping) | ✅ |
| `ChampionshipCardData` : circuit/pays optionnels, composant toujours sans logique métier | ✅ |
| Aucune régression — providers, Design System, navigation inchangés | ✅ |
| 26 nouveaux tests — 983 total, couverture 95 % | ✅ |

---

## v0.4.5 — Layout System ✅ Sprint 31 (2026-07-07)

| Fonctionnalité | Statut |
|---|---|
| `gui/components/layout/` — PageContainer, PageHeader, Section, SectionHeader, CardList, EmptyState, PageSpacing | ✅ |
| Les 5 vues migrées : plus aucune ne construit son propre conteneur/en-tête/carte | ✅ |
| Une nouvelle page se compose désormais sans code de mise en page manuel | ✅ |
| Aucune régression — Design System, couleurs, icônes, navigation, providers inchangés | ✅ |
| 51 nouveaux tests — 957 total, couverture 95 % | ✅ |

---

## v0.4.4 — Composant ChampionshipCard ✅ Sprint 30 (2026-07-07)

| Fonctionnalité | Statut |
|---|---|
| `gui/components/` — première bibliothèque de composants réutilisables | ✅ |
| `ChampionshipCard` — carte unique extraite de "Ce week-end", réutilisable partout | ✅ |
| En-tête (championnat, Grand Prix, circuit, pays), grille de sessions alignée | ✅ |
| Point d'extension `footer` prêt pour Favori/Notifications/Export ICS/Partage/Résultats | ✅ |
| "Ce week-end" migré : la vue construit une liste de `ChampionshipCard`, aucun layout propre | ✅ |
| Aucune régression — Design System, navigation, providers inchangés | ✅ |
| 23 nouveaux tests — 903 total, couverture 95 % | ✅ |

---

## v0.4.3 — Ce week-end : version fonctionnelle ✅ Sprint 29 (2026-07-07)

| Fonctionnalité | Statut |
|---|---|
| Recherche automatique du prochain week-end de course (F1, F2, F3, F1 Academy, WEC) | ✅ |
| Une carte par championnat — Grand Prix, circuit, pays (drapeau), sessions chronologiques | ✅ |
| Tri Formula puis Endurance, chronologique à l'intérieur de chaque catégorie | ✅ |
| 3 états : chargement / aucune course (avec prochaine date connue) / trouvé | ✅ |
| Fetch une seule fois par lancement, cache HTTP existant réutilisé (jamais de réseau à chaque ouverture) | ✅ |
| Aucun nouveau provider — réutilise `registry`/`source_registry`/`HttpCache` tels quels | ✅ |
| 34 nouveaux tests — 880 total, couverture 95 % | ✅ |

---

## v0.4.2 — Uniformisation du layout (UX) ✅ Sprint 27 (2026-07-07)

| Fonctionnalité | Statut |
|---|---|
| `theme.page_shell()` — grille de page unique (max-width 1000px, centrée, contenu toujours aligné à gauche) | ✅ |
| Ce week-end / Mes favoris / À propos alignés à gauche (fin du centrage mid-écran) | ✅ |
| En-tête uniforme (`section_title` + `Divider`) sur les 5 pages, y compris Mon calendrier | ✅ |
| Largeurs de cartes uniformisées (suppression des largeurs fixes ad hoc) | ✅ |
| `TestAllViewsShareTheSameGrid` — verrou anti-régression sur le gabarit partagé | ✅ |
| 18 nouveaux tests — 837 total, couverture 94 % | ✅ |

---

## v0.4.1 — Release Alpha Phase 2 — UX & Design System ✅ Sprint 26 (2026-07-07)

| Fonctionnalité | Statut |
|---|---|
| `gui/theme.py` — design system (couleurs BApps + Motorsport Calendar, spacing, radius, icônes, boutons, cartes) | ✅ |
| "Mon calendrier" transformé en assistant 4 étapes (saison / championnats / destination / créer) | ✅ |
| Navigation étapes gatée par validité, retour + puces d'étapes déjà visitées cliquables | ✅ |
| Récapitulatif étape finale avec liens "Modifier" vers chaque étape | ✅ |
| Uniformisation visuelle Ce week-end / Mes favoris / Préférences / À propos (theme uniquement, contenu inchangé) | ✅ |
| Emplacement logo préparé (`logo_placeholder()`, `gui/assets/logo/README.md`) — placeholder, pas d'asset définitif | ✅ |
| Correction warnings dépréciation `ft.Colors.WHITE12` → `WHITE_12` (Flet 0.85) | ✅ |
| 55 nouveaux tests — 819 total, couverture 94 % | ✅ |

---

## v0.4.0 — Release Alpha Phase 1 ✅ Sprint 25 (2026-07-06)

| Fonctionnalité | Statut |
|---|---|
| Navigation 5 pages : Ce week-end / Mon calendrier / Mes favoris / Préférences / À propos | ✅ |
| Architecture `views/` — une vue par module, indépendante et testable | ✅ |
| `views/weekend.py` — skeleton layout (Circuit, Pays, Championnat, Sessions) | ✅ |
| `views/favorites.py` — placeholder Mes favoris | ✅ |
| `views/preferences.py` — 6 rubriques préférences avec chip "prochainement" | ✅ |
| `PreferencesModel` — dataclass frozen avec 6 champs typés | ✅ |
| `main_view.py` refactorisé : shell de navigation uniquement | ✅ |
| 44 nouveaux tests — 764 total | ✅ |

---

## v0.3.2 — Desktop Alpha 3 — Product Polish ✅ Sprint 24 (2026-07-06)

| Fonctionnalité | Statut |
|---|---|
| Navigation multi-pages : Accueil / Calendrier / À propos | ✅ |
| `ft.NavigationRail` 3 destinations, responsive (étendu >900px) | ✅ |
| Championnats groupés visuellement : 🏎 Formula / 🏁 Endurance | ✅ |
| Architecture catégories extensible (`categories.py`) : FORMULA, ENDURANCE, MOTO, RALLY, AMERICA | ✅ |
| Écran Accueil : icône, description, CTA vers Calendrier | ✅ |
| Écran À propos : version, développeur BApps, GitHub, Licence MIT | ✅ |
| `strings.py` étendu (nav + about) | ✅ |
| 25 nouveaux tests (`test_gui_categories.py`) — 720 total | ✅ |

---

## v0.4.0 — Desktop Edition Phase 2 (Sprint 25)

| Fonctionnalité | Priorité |
|---|---|
| Packaging Windows `.exe` via `flet build windows` | 🔴 HAUTE |
| Mémorisation du dernier fichier de sortie | 🟡 MOYENNE |
| Option `--refresh` dans la GUI (case à cocher) | 🟡 MOYENNE |
| Aperçu du nombre de sessions avant export | 🟡 MOYENNE |
| Icône d'application personnalisée | 🟢 BASSE |
| Drag & drop du fichier `.ics` généré | 🟢 BASSE |

---

## v0.5.0 — Nouvelles sources

Sources documentées dans `docs/DATA_SOURCES.md`.

| Fonctionnalité | Source | Priorité |
|---|---|---|
| `OfficialWecSource` — calendrier FIA WEC | Scraping `fiawec.com` (voir DATA_SOURCES.md) | 🔴 HAUTE |
| `ELMSProvider` — European Le Mans Series | Scraping `europeanlemansseries.com` (XHR first) | 🔴 HAUTE |
| `PorscheSupercupProvider` | Scraping `racing.porsche.com` + venues F1 | 🟢 BASSE |
| Export JSON (machine-readable) | — | 🟢 BASSE |
| `DESCRIPTION` dans les VEVENTs (circuit, pays, type de session) | — | 🟡 MOYENNE |

---

## v1.0.0 — Version stable

| Fonctionnalité | Priorité |
|---|---|
| Publication PyPI (`pip install motorsport-calendar`) | 🔴 HAUTE |
| Documentation MkDocs complète (API + guides utilisateur) | 🔴 HAUTE |
| API Python publique documentée et stable | 🔴 HAUTE |
| Support Python 3.12 + 3.13 validé en CI | ✅ |
| Badge couverture dans README | 🟡 MOYENNE |
| GitHub Release avec assets ICS précalculés | 🟢 BASSE |
