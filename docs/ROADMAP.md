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

## v0.2.0 — Sources enrichies

| Fonctionnalité | Priorité |
|---|---|
| `ErgastSource` — données historiques F1 (1950+), API ergast.com | 🔴 HAUTE |
| `OfficialWecSource` — calendrier FIA WEC (investigation endpoint fiawec.com) | 🔴 HAUTE |
| `DESCRIPTION` dans les VEVENTs (circuit, pays, type de session) | 🟡 MOYENNE |
| `URL` dans les VEVENTs (lien source officielle) | 🟡 MOYENNE |
| Retry avec backoff exponentiel sur erreurs HTTP (max 3 tentatives) | 🟢 BASSE |
| Validation de l'année dans `generate-f1` (OpenF1 couvre 2023+) | 🟢 BASSE |

---

## v0.3.0 — Nouvelles disciplines

| Fonctionnalité | Priorité |
|---|---|
| `ELMSProvider` — European Le Mans Series | 🔴 HAUTE |
| `LeMansProvider` — Michelin Le Mans Cup + Road to Le Mans | 🔴 HAUTE |
| `Formula2Provider` | 🟡 MOYENNE |
| `Formula3Provider` | 🟡 MOYENNE |
| `F1AcademyProvider` | 🟡 MOYENNE |
| Export JSON (machine-readable) | 🟢 BASSE |
| Export CSV | 🟢 BASSE |

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
