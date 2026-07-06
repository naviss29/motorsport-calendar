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
