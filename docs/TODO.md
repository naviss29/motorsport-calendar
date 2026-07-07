# TODO.md

> Légende priorité : 🔴 HAUTE — 🟡 MOYENNE — 🟢 BASSE
> Légende état : `[ ]` à faire — `[~]` en cours — `[x]` terminé

---

## Providers WEC

- [ ] 🔴 `OfficialWecSource` — implémenter `get_season()` via fiawec.com (API ou scraping)
  - Dépend de : investigation endpoint
  - Estimation : 4-6h (mapping + tests)

- [ ] 🔴 CLI `generate-wec YEAR OUTPUT.ics` — identique à `generate-f1`
  - Dépend de : OfficialWecSource implémentée (ou stub suffisant pour la CLI)
  - Estimation : 1h

- [x] 🔴 CLI `generate YEAR OUTPUT.ics` — merge F1 + WEC dans un seul ICS — terminé Sprint 12

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

- [x] 🔴 CLI `generate-wec YEAR OUTPUT.ics` — terminé, 16 tests (+ NotImplementedError géré gracieusement)

- [x] 🔴 CLI `generate YEAR OUTPUT.ics` — terminé Sprint 12, 17 tests, résilience partielle intégrée

- [ ] 🔴 Commande `export` — implémentation réelle (actuellement stub exit 1)
  - Dépend de : ErgastSource ou OpenF1Source
  - Estimation : 2h

- [x] 🟡 Commande `providers` — liste les providers enregistrés via registry.list_all()
  - Terminé Sprint 9

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

## Registre des identités visuelles de championnat — suites possibles (Sprint 33)

- [ ] 🔴 Livrer les logos officiels (F1, F2, F3, F1 Academy, WEC) dans
  `gui/assets/championships/` (voir README de ce dossier pour les noms de fichiers exacts)
  — aujourd'hui la fonctionnalité est architecturalement complète mais invisible faute de
  fichiers réels.
- [ ] 🔴 Décommenter `assets_dir=` dans `gui/app.py` une fois au moins un logo livré
  (partagé avec le logo de l'app elle-même — voir `gui/assets/logo/README.md`) — sans ça
  `ft.Image(src=...)` ne se résout pas visuellement même si le fichier est présent sur
  disque.
- [ ] 🟢 Étendre `ChampionshipAsset` avec un champ couleur/icône par championnat si un futur
  sprint en a besoin (Tableau de bord, Recherche) — un champ de plus, jamais un second
  point d'entrée à côté de `get_championship_asset()`.
- [ ] 🟢 Vérification visuelle réelle du logo aligné à gauche du titre (taille, alignement
  vertical) sur un poste avec affichage, une fois un vrai fichier livré.

---

## Normalisation des métadonnées — suites possibles (Sprint 32)

- [ ] 🟡 Corriger `f1calendar_base.py::_build_circuit` pour utiliser `event_data["location"]`
  comme `Circuit.name` (F2/F3/F1 Academy) au lieu de réutiliser `event_data["name"]` —
  réduirait le besoin de repli sur `circuit.city` dans `event_display.py`. Touche le
  provider, explicitement hors périmètre de ce sprint.
- [ ] 🟢 Compléter les tables `_CIRCUIT_DATA` (pays) de F2/F1 Academy pour réduire le
  nombre de lignes pays masquées dans "Ce week-end". Touche le provider, hors périmètre.
- [ ] 🟢 Envisager une table démonyme (pays → adjectif, "Canada"→"Canadian") si "Canada
  Grand Prix" au lieu de "Canadian Grand Prix" devient gênant visuellement.
- [ ] 🟢 Vérification visuelle réelle des cartes normalisées (F1/F2/F3, avec et sans pays)
  sur un poste avec affichage.

---

## Layout System — suites possibles (Sprint 31)

- [ ] 🟡 Utiliser `PageContainer`/`PageHeader`/`Section`/`CardList` dès la première future
  page (Favoris fonctionnel, Recherche, Tableau de bord, ...) — c'est exactement leur
  raison d'être, aucun code de mise en page à réécrire.
- [ ] 🟢 Premier consommateur réel de `SectionHeader` dès qu'une page affichera plusieurs
  groupes de cartes distincts (Tableau de bord probable en premier).
- [ ] 🟢 Vérification visuelle réelle du nouvel en-tête séparé (Ce week-end/Favoris/
  Préférences) et des bordures restaurées des lignes de Préférences, sur un poste avec
  affichage.
- [ ] 🟢 Envisager un séparateur optionnel dans `CardList` si une future liste en a
  vraiment besoin (point d'extension documenté, non codé).

---

## Bibliothèque de composants — suites possibles (Sprint 30)

- [ ] 🟡 Réutiliser `components.championship_card.build_championship_card` dès
  l'implémentation de "Mes favoris" — c'est exactement le cas d'usage visé.
- [ ] 🟢 Ajouter un bouton Favori ⭐ dans le `footer` de `ChampionshipCard` une fois la
  persistance des favoris disponible — le point d'extension existe déjà, aucun changement
  de signature nécessaire.
- [ ] 🟢 Documenter dans `gui/components/__init__.py` chaque nouveau composant au fur et à
  mesure de son ajout (index simple de la bibliothèque).

---

## Ce week-end — suites possibles (Sprint 29)

- [ ] 🔴 `OfficialWecSource` — tant qu'elle reste un stub `NotImplementedError`, "Ce week-end"
  n'affichera jamais de carte Endurance en conditions réelles (voir aussi la tâche WEC
  existante plus bas, partagée avec `generate-wec`).
- [ ] 🟢 Ancrer le découpage vendredi-dimanche sur le fuseau du circuit plutôt que UTC —
  cas limite pour les circuits très à l'est (Japon, Singapour, Chine, Australie).
- [ ] 🟢 Compléter `_COUNTRY_LABELS` (`gui/upcoming_weekend.py`) au fil des circuits
  effectivement rencontrés sans mapping (fallback actuel : nom brut, souvent anglais, sans
  drapeau).
- [ ] 🟢 Vérification visuelle réelle des 3 états (chargement/aucune course/trouvé) sur un
  poste avec affichage.

---

## Uniformisation finale de l'interface — suites possibles (Sprint 28)

- [ ] 🟢 Vérification visuelle réelle des cartes centrales (Ce week-end, Mes favoris,
  Préférences) et de la présentation compacte d'À propos sur un poste avec affichage.
- [ ] 🟢 Évaluer si les 6 lignes de Préférences ont besoin d'un séparateur visuel léger
  entre elles maintenant qu'elles n'ont plus leur propre bordure (actuellement juste de
  l'espacement) — purement cosmétique, à trancher après retour visuel.

---

## Uniformisation du layout — suites possibles (Sprint 27)

- [ ] 🟢 Vérification visuelle réelle du gabarit partagé (`theme.page_shell`) sur un poste
  avec affichage — comportement responsive attendu au redimensionnement (rétrécit sous
  1000px, plafonne au-delà), vérifié uniquement par structure/tests dans ce sandbox.

---

## Release Alpha Phase 2 — suites possibles (Sprint 26)

- [ ] 🔴 Intégrer les SVG définitifs du Brand Set v1.0 quand livrés dans le dépôt
  - Remplacer les appels `theme.logo_placeholder(...)` listés dans `gui/assets/logo/README.md`
  - Estimation : 30min (layout déjà prêt, pas de rework attendu)
- [ ] 🟡 Audit mypy `main_view.py` — signatures `on_click` Flet 0.80 vs 0.85.3 installé
  - 21 erreurs préexistantes avant Sprint 26 (26 après, proportionnel aux handlers du wizard)
  - Estimation : 2-3h (vérifier les stubs Flet actuels, éventuellement caster les handlers)
- [ ] 🟢 Écran/capture réels du wizard une fois un environnement graphique disponible
  - Ce sprint a été vérifié par tests unitaires (100 % theme/calendar/models) + simulation
    de parcours via une fausse `Page` (aucun display dans ce sandbox)

---

## Terminé ✅

- [x] Scaffold projet (pyproject.toml, CI, structure)
- [x] Modèles métier Pydantic v2 frozen
- [x] EventStatus + event_uid
- [x] IcsExporter (RFC 5545)
- [x] Architecture Provider/Source F1
- [x] OpenF1Source (httpx, mapping, 45 tests)
- [x] CLI `generate-f1 YEAR OUTPUT.ics` (11 tests intégration)
- [x] HttpCache — cache disque JSON centralisé, TTL, refresh, 24 tests
- [x] Migration OpenF1Source → HttpCache
- [x] CLI `--refresh` flag
- [x] WecProvider — architecture complète (provider + source ABC + OfficialWecSource stub), 24 tests
- [x] ConfigService — config.yaml, Pydantic, valeurs par défaut, 30 tests
- [x] IcsExporter — VALARM configurable (alarm_minutes), 7 tests
- [x] CLI generate-f1 — wiring ConfigService (cache path/TTL, source selection, alarm)
- [x] ProviderRegistry — register/get/list_all/enabled/discover, auto-enregistrement à l'import, 25 tests
- [x] SourceRegistry — register/get/list_for/list_all/discover, clé (championship, source), 24 tests
