# TODO.md

> Légende priorité : 🔴 HAUTE — 🟡 MOYENNE — 🟢 BASSE
> Légende état : `[ ]` à faire — `[~]` en cours — `[x]` terminé

---

## Providers F1

- [ ] 🔴 `ErgastSource` — implémenter `get_season()` via API Ergast (données historiques 1950+)
  - Dépend de : rien
  - Estimation : 3-4h (mapping + tests)
  - Note : API Ergast v1, endpoint `/api/f1/{year}/races.json`

- [ ] 🔴 `CachedFormula1Source` — implémenter le cache fichier (JSON local)
  - Dépend de : aucune source spécifique
  - Estimation : 2h
  - Note : invalider le cache après 24h, chemin configurable

- [ ] 🟡 `OfficialFormula1Source` — récupérer depuis l'API officielle formula1.com
  - Dépend de : investigation endpoint (non documenté)
  - Estimation : 4-6h

---

## CLI

- [ ] 🔴 Commande `export` — implémentation réelle (actuellement stub exit 1)
  - Dépend de : ErgastSource ou OpenF1Source
  - Estimation : 2h (wiring provider registry + exporter)

- [ ] 🟡 Commande `providers` — lister les providers disponibles avec leurs sources
  - Dépend de : provider registry
  - Estimation : 1h

- [ ] 🟡 Option `--year` avec validation (≥ 1950 pour Ergast, ≥ 2023 pour OpenF1)
  - Estimation : 30min

---

## Qualité des VEVENTs ICS

- [ ] 🟡 Ajouter `DESCRIPTION` dans chaque VEVENT (infos weekend, circuit, pays)
  - Dépend de : IcsExporter (ne pas modifier les modèles)
  - Estimation : 1h + tests

- [ ] 🟡 Ajouter `URL` dans chaque VEVENT (lien OpenF1 ou source officielle)
  - Estimation : 30min

- [ ] 🟢 Ajouter `CATEGORIES` (GP, Qualifying, Practice…)
  - Estimation : 30min

---

## Robustesse

- [ ] 🟡 Retry avec backoff exponentiel sur `httpx.TimeoutException`
  - Estimation : 1h
  - Note : max 3 tentatives, délais 1s / 2s / 4s

- [ ] 🟢 Validation de l'année dans `generate-f1` (ex: OpenF1 ne couvre que 2023+)
  - Estimation : 30min

---

## Infrastructure

- [ ] 🟡 Publier sur PyPI (configuration `hatchling` déjà en place)
  - Dépend de : v0.1.0 complète
  - Estimation : 1h

- [ ] 🟢 Documentation MkDocs
  - Estimation : 4h

- [ ] 🟢 Badge couverture dans README
  - Estimation : 30min

---

## Terminé ✅

- [x] Scaffold projet (pyproject.toml, CI, structure)
- [x] Modèles métier Pydantic v2 frozen
- [x] EventStatus + event_uid
- [x] IcsExporter (RFC 5545)
- [x] Architecture Provider/Source F1
- [x] OpenF1Source (httpx, mapping, 45 tests)
- [x] CLI `generate-f1 YEAR OUTPUT.ics` (11 tests intégration)
