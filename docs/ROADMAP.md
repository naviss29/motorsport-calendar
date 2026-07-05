# ROADMAP.md

> Vision : générer automatiquement des calendriers ICS pour n'importe quelle discipline motorsport, à partir de sources de données publiques.

---

## Vision produit

`motorsport-calendar` est un outil CLI open source qui :
- récupère les calendriers de saison depuis des API publiques
- exporte en format ICS (compatible Google Calendar, Apple Calendar, Outlook)
- supporte plusieurs disciplines (F1, MotoGP, WEC, IMSA…)
- est extensible via un système de providers/sources

---

## v0.1.0 — MVP Formula 1 ✅ (en cours)

| Fonctionnalité | Statut |
|---|---|
| Modèles métier (Championship, Circuit, Session, Event) | ✅ |
| EventStatus enum + event_uid | ✅ |
| IcsExporter (RFC 5545) | ✅ |
| Architecture provider/source F1 | ✅ |
| OpenF1Source (API openf1.org, 2023+) | ✅ |
| CLI `generate-f1 YEAR OUTPUT.ics` | ✅ |
| Tests unitaires + intégration (130 tests) | ✅ |
| CI GitHub Actions | ✅ |

---

## v0.2.0 — Sources F1 enrichies

| Fonctionnalité | Priorité |
|---|---|
| `ErgastSource` — données historiques F1 (1950+) | HAUTE |
| `CachedFormula1Source` — cache fichier entre appels | HAUTE |
| DESCRIPTION dans les VEVENTs (détail session) | MOYENNE |
| Commande `export` générique (provider/exporter pluggables) | MOYENNE |
| Commande `providers` listant les providers disponibles | MOYENNE |
| Retry avec backoff exponentiel sur erreurs HTTP | BASSE |

---

## v0.3.0 — Nouvelles disciplines

| Fonctionnalité | Priorité |
|---|---|
| `MotoGPProvider` (API officielle MotoGP) | HAUTE |
| `WECProvider` (Championnat du monde Endurance) | MOYENNE |
| `IMSAProvider` | BASSE |
| Configuration YAML (sources, export paths, fuseaux) | MOYENNE |
| Plusieurs formats d'export (JSON, CSV) | BASSE |

---

## v1.0.0 — Version stable

| Fonctionnalité | Priorité |
|---|---|
| API Python publique documentée | HAUTE |
| Publication PyPI | HAUTE |
| Documentation complète (MkDocs ou Sphinx) | HAUTE |
| Support Python 3.12 + 3.13 validé en CI | HAUTE |
| Changelog structuré | MOYENNE |
