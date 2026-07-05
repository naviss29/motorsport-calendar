# DATA_SOURCES.md

> Étude des sources de données disponibles pour chaque championnat motorsport.
> Dernière mise à jour : 2026-07-05

---

## Méthodologie

Pour chaque championnat, on évalue :

| Critère | Description |
|---|---|
| **API** | Endpoint HTTP documenté retournant des données structurées |
| **ICS** | Flux iCalendar prêt à l'emploi (abonnement ou téléchargement) |
| **JSON** | Données brutes disponibles en JSON (API ou réponse réseau) |
| **HTML** | Seule option : scraping de page web |
| **Auth** | Clé API, compte, ou autre authentification requise |
| **Stabilité** | Risque de rupture de la source (changement de structure, arrêt) |
| **Fréquence** | Rythme de mise à jour des données calendrier |
| **Licence** | Conditions d'utilisation des données |

---

## Vue d'ensemble rapide

| Championnat | Meilleure source | Format | Auth | Complexité |
|---|---|---|---|---|
| Formula 1 (2023+) | OpenF1 | JSON REST | Non | ✅ Implémentée |
| Formula 1 (historique) | Jolpica | JSON REST | Non | 🟢 Facile |
| Formula 2 | Scraping fiaformula2.com | HTML | Non | 🟡 Moyen |
| Formula 3 | Scraping fiaformula3.com | HTML | Non | 🟡 Moyen |
| F1 Academy | Scraping f1academy.com | HTML | Non | 🟡 Moyen |
| WEC | Scraping fiawec.com | HTML | Non | 🟡 Moyen |
| ELMS | Scraping europeanlemansseries.com | HTML | Non | 🟡 Moyen |
| Michelin Le Mans Cup | Scraping lemanscup.com | HTML (JS) | Non | 🔴 Complexe |
| Road to Le Mans | Scraping lemanscup.com | HTML (JS) | Non | 🔴 Complexe |
| Porsche Supercup | Scraping racing.porsche.com | HTML | Non | 🟡 Moyen |

---

## Observation architecturale clé

**F2, F3, F1 Academy et Porsche Supercup sont des « support series » de la F1.**

Ils courent sur un sous-ensemble des circuits F1, durant le même week-end.
Cela permet une optimisation importante :

> Les données de **circuit** (ville, pays, fuseau IANA) sont déjà disponibles via
> le provider Formula 1. Seuls les **horaires de sessions** propres à chaque série
> doivent être récupérés depuis une source tierce.

| Série | Rounds F1 couverts (2026) | Sessions propres à scraper |
|---|---|---|
| F2 | 14 des 24 | Essais, Qualif, Course sprint, Course |
| F3 | 10 des 24 | Essais, Qualif, Course sprint, Course |
| F1 Academy | 7 des 24 | Essais, Qualif, Course 1, Course 2 |
| Porsche Supercup | 8 (Europe uniquement) | Essais, Qualif, Course |

---

## Détails par championnat

---

### 🏎 Formula 1

**Site officiel :** https://formula1.com | https://calendar.formula1.com

#### OpenF1 — Recommandé pour 2023+

| Critère | Détail |
|---|---|
| URL API | `https://api.openf1.org/v1/` |
| Endpoints clés | `/meetings`, `/sessions`, `/laps`, `/position`, `/pit`, `/car_data`, `/weather` |
| Format | JSON (défaut), CSV |
| Authentification | **Aucune** |
| Couverture | **2023 → présent** |
| Temps réel | Oui — 3 s de délai pendant les sessions actives |
| Rate limit | 3 req/s (gratuit), 6 req/s (sponsor) |
| Stabilité | **Élevée** — projet open source actif, GitHub public |
| Fréquence | Temps réel pendant les sessions ; données permanentes après |
| Licence | **CC BY-NC-SA 4.0** — usage non commercial uniquement |
| GitHub | https://github.com/br-g/openf1 |

**Remarque licence :** CC BY-NC-SA 4.0 interdit l'usage commercial. Pour un projet open source ou personnel, c'est acceptable. Pour une offre commerciale, contacter les mainteneurs.

#### Jolpica — Recommandé pour données historiques (1950+)

| Critère | Détail |
|---|---|
| URL API | `http://api.jolpi.ca/ergast/f1/` |
| Compatibilité | **100 % compatible Ergast** (migration sans réécriture) |
| Format | JSON, XML |
| Authentification | **Aucune** |
| Couverture | **1950 → présent** |
| Stabilité | **Élevée** — successeur communautaire officiel d'Ergast (arrêté fin 2024) |
| Fréquence | Mise à jour le **lundi après chaque week-end de course** |
| Licence | **Apache-2.0** — usage commercial autorisé |
| GitHub | https://github.com/jolpica/jolpica-f1 |

> **Note :** L'API Ergast originale (ergast.com) a été définitivement arrêtée fin 2024.
> Jolpica est le successeur officiel, maintenu par la communauté.

#### ICS officiel Formula 1

| Critère | Détail |
|---|---|
| Source | https://www.formula1.com/en/latest/article/download-or-sync-the-f1-race-calendar-to-your-device.7mpETY062kafAl55qVnemu |
| Format | Fichier `.ics` statique ou abonnement |
| Contenu | Dates des Grand Prix uniquement (pas les sessions séparées) |
| Fréquence | Mis à jour en début de saison, pas en temps réel |
| Utilité | Faible pour ce projet (sessions individuelles non couvertes) |

#### f1calendar.com — Source ICS communautaire

| Critère | Détail |
|---|---|
| Site | https://f1calendar.com |
| GitHub | https://github.com/sportstimes/f1 (MIT) |
| Séries couvertes | F1, **F2, F3, F1 Academy**, Formula E, IndyCar, MotoGP |
| Format | ICS par abonnement (URLs générées dynamiquement) |
| Granularité | Par session (FP1/FP2/FP3, Qualif, Sprint, Course) |
| Stabilité | **Élevée** — projet actif, open source, 420+ stars |
| Utilité | Référence utile pour les horaires F2/F3/F1A ; à consommer en ICS ou via le code source |

**Recommandation F1 :** OpenF1 pour 2023+ (déjà implémenté). Jolpica pour les saisons historiques (1950-2022).

---

### 🔵 Formula 2

**Site officiel :** https://www.fiaformula2.com

| Critère | Détail |
|---|---|
| API publique | ❌ Aucune documentée. `api.fia.com` existe mais nécessite authentification |
| Flux ICS | ❌ Non trouvé sur le site officiel |
| JSON | ❌ Pas d'endpoint public |
| HTML | ✅ `https://www.fiaformula2.com/Calendar` — calendrier HTML |
| Authentification | N/A |
| Stabilité (scraping) | 🟡 Moyenne — site FIA, peu de restructurations fréquentes |
| Fréquence | Mise à jour en début de saison + annonces ponctuelles |
| Licence | Scraping : zone grise (ToS FIA) — données non commerciales |

**Caractéristiques séries :**
- 14 rounds en 2026, tous en support F1
- 4 sessions par round : Essais libres, Qualifications, Course Sprint, Course principale
- Mêmes circuits que F1 → venues dérivables du provider F1

**Sources alternatives :**
- `f1calendar.com` couvre F2 avec horaires complets (open source, MIT)
- Wikipedia pour le calendrier de saison (données statiques)

**Recommandation F2 :** Scraping de `fiaformula2.com/Calendar` + fallback `f1calendar.com` (ICS open source). Réutiliser les métadonnées circuit du provider F1.

---

### 🟢 Formula 3

**Site officiel :** https://www.fiaformula3.com

| Critère | Détail |
|---|---|
| API publique | ❌ Aucune documentée |
| Flux ICS | ❌ Non trouvé |
| JSON | ❌ Pas d'endpoint public |
| HTML | ✅ `https://www.fiaformula3.com/Calendar` |
| Stabilité (scraping) | 🟡 Moyenne |
| Fréquence | Début de saison + ajustements |

**Caractéristiques :**
- 10 rounds en 2026, tous en support F1
- Structure identique à F2 (architecture de site identique — même CMS FIA)
- 3 sessions : Qualifications, Course 1, Course 2

**Recommandation F3 :** Même approche que F2. Le code de scraping sera quasi-identique (même CMS FIA entre F2 et F3).

---

### 🩷 F1 Academy

**Site officiel :** https://www.f1academy.com

| Critère | Détail |
|---|---|
| API publique | ❌ Aucune documentée |
| Flux ICS | ❌ Non trouvé |
| JSON | ❌ Pas d'endpoint public |
| HTML | ✅ `https://www.f1academy.com/Racing-Series/Calendar` |
| Stabilité (scraping) | 🟡 Moyenne |
| Fréquence | Début de saison |

**Caractéristiques :**
- 7 rounds en 2026, support F1 (sous-ensemble des rounds européens + quelques autres)
- 4 sessions par round : Essais, Qualifications, Course 1, Course 2
- Série créée en 2023, site relativement récent

**Recommandation F1A :** Scraping de `f1academy.com/Racing-Series/Calendar`. Même logique de réutilisation des venues F1.

---

### 🟣 FIA World Endurance Championship (WEC)

**Site officiel :** https://www.fiawec.com

| Critère | Détail |
|---|---|
| API publique | ❌ Aucune documentée publiquement |
| Flux ICS | ❌ Non trouvé (fiawec.com ne publie pas d'ICS accessible) |
| JSON | ❌ Pas d'endpoint public |
| HTML | ✅ `https://www.fiawec.com/en/season` |
| Timing live | `https://fiawec.alkamelsystems.com/` (propriétaire, accès restreint) |
| Authentification | N/A (pour le calendrier HTML) |
| Stabilité (scraping) | 🟡 Moyenne — site WEC stable mais HTML peut changer |
| Fréquence | Mis à jour en septembre pour la saison suivante + ajustements |
| Licence | Scraping : zone grise (ToS fiawec.com) |

**Caractéristiques :**
- 8 rounds en 2025, dont Le Mans 24h (juin)
- Sessions spécifiques WEC : FP1, FP2, FP3, Hyperpole (= qualif WEC), Course (6h/8h/24h)
- `SessionType.HYPERPOLE` déjà présent dans le modèle

**Fournisseur de timing :** Al Kamel Systems (`fiawec.alkamelsystems.com`). Données de timing propriétaires, non accessibles publiquement sans accord commercial.

**Recommandation WEC :** Scraping HTML de `fiawec.com` pour le calendrier (rounds + dates). Structure de page à investiguer avant implémentation. `OfficialWecSource` est le nom prévu dans l'architecture.

---

### 🟠 European Le Mans Series (ELMS)

**Site officiel :** https://www.europeanlemansseries.com

| Critère | Détail |
|---|---|
| API publique | ❌ Aucune documentée |
| Flux ICS | ❌ Non trouvé (site mentionne un bouton "Subscribe" mais redirige vers compte) |
| JSON | ❌ Pas d'endpoint public |
| HTML | ✅ `https://www.europeanlemansseries.com/en/season` |
| Rendu JS | ⚠️ Probable — confirmer avant implémentation |
| Timing live | `https://elms.alkamelsystems.com/` (propriétaire) |
| Stabilité (scraping) | 🟡 Moyenne |
| Fréquence | Annonce calendrier en octobre pour l'année suivante |

**Caractéristiques :**
- 6 rounds en 2025 : Barcelone, Le Castellet, Imola, Spa, Silverstone, Portimão
- Sessions : EL1, EL2, Qualifications (4h de course)
- Organisé par l'ACO (Automobile Club de l'Ouest)
- Circuits européens uniquement — données de timezone stables

**Attention JS :** Si le calendrier est rendu côté client (JavaScript), un scraper HTTP classique (`httpx`) ne suffira pas. Il faudra Playwright ou une approche API réseau (inspecter les XHR dans les DevTools).

**Recommandation ELMS :** Inspecter les requêtes réseau de `europeanlemansseries.com/en/season` via DevTools avant d'implémenter. Un endpoint XHR JSON interne est probable — plus stable qu'un scraper HTML.

---

### 🔵 Michelin Le Mans Cup (MLMC)

**Site officiel :** https://www.lemanscup.com

| Critère | Détail |
|---|---|
| API publique | ❌ Aucune documentée |
| Flux ICS | ❌ Non trouvé |
| JSON | ❌ Pas d'endpoint public |
| HTML | ✅ `https://www.lemanscup.com/en/season` |
| Rendu JS | ⚠️ **Confirmé** — la page nécessite JavaScript |
| Timing live | `https://lemanscup.alkamelsystems.com/` (propriétaire) |
| Stabilité (scraping) | 🔴 Faible — JS rendering, structure fragile |
| Fréquence | Mise à jour annuelle |

**Caractéristiques :**
- 6 rounds en 2026 (co-localisés avec ELMS : Barcelone, Le Castellet, Imola, Spa, Silverstone, Portimão)
- Inclut **Road to Le Mans** lors de la semaine des 24h du Mans
- Organisé par l'ACO

**Recommandation MLMC :** Approche prioritaire = inspecter les XHR dans les DevTools du navigateur sur lemanscup.com. Si un endpoint JSON interne existe, l'utiliser directement (stable, pas de parsing HTML). Sinon, Playwright pour le rendu JS.

---

### 🟡 Road to Le Mans (RTLM)

**Site officiel :** https://www.lemanscup.com (intégré au MLMC)

| Critère | Détail |
|---|---|
| API publique | ❌ Aucune — intégré dans le site MLMC |
| Flux ICS | ❌ Non trouvé |
| JSON | ❌ Pas d'endpoint public |
| HTML | ✅ Via `lemanscup.com` |
| Rendu JS | ⚠️ Confirmé (même site que MLMC) |

**Caractéristiques :**
- Traditionnellement 2 sprint races de 55 min pendant la semaine du Mans
- **Format 2026 changé** : 1 course d'endurance de 3h (annonce juillet 2025)
- Co-organisé avec le MLMC — peut être traité dans le même provider

**Recommandation RTLM :** Fusionner dans le même provider que le MLMC. Une seule source, deux séries distinguées par le champ `championship_id`.

---

### 🟡 Porsche Mobil 1 Supercup (PMSC)

**Site officiel :** https://racing.porsche.com/mobil-1-supercup

| Critère | Détail |
|---|---|
| API publique | ❌ Aucune documentée |
| Flux ICS | ❌ Non trouvé |
| JSON | ❌ Pas d'endpoint public |
| HTML | ✅ `https://racing.porsche.com/mobil-1-supercup/race-calendar-{year}` |
| Rendu JS | ⚠️ Probable (site Porsche moderne) |
| Stabilité (scraping) | 🟡 Moyenne |
| Fréquence | Annonce calendrier en fin d'année précédente |

**Caractéristiques :**
- 8 rounds en 2026, tous en support **F1 Europe** (Monaco, Barcelone, Autriche, Belgique, Hongrie, Pays-Bas ×2, Monza)
- 3 sessions par round : Essais Libres, Qualifications, Course
- Nouveau modèle 2026 : Porsche 911 Cup (992.2)

**Approche recommandée :** Les venues (circuit, ville, pays, fuseau IANA) sont identiques aux rounds F1 correspondants. Seuls les horaires de sessions sont spécifiques.

**Plan d'implémentation :**
1. Scraper `racing.porsche.com/mobil-1-supercup/race-calendar-{year}` pour la liste des rounds F1 concernés
2. Réutiliser les métadonnées circuit du provider F1
3. Compléter avec les horaires propres au Supercup

---

## Sources tierces polyvalentes

### Rushsync (rushsync.com)

Service tiers qui agrège les calendriers motorsport et expose des abonnements ICS pour WEC, ELMS, Porsche Supercup et autres. Pratique pour valider les données scrapées. Non recommandé comme source primaire (service commercial, pas de garantie de pérennité).

### Motorsport.com / Autosport.com

Proposent des calendriers pour la plupart des championnats. HTML-only pour la plupart des séries. Utiles comme référence de vérification, pas comme source primaire.

### f1calendar.com (sportstimes/f1)

- **GitHub :** https://github.com/sportstimes/f1
- **Licence :** MIT
- **Couverture :** F1, F2, F3, F1 Academy, Formula E, IndyCar, MotoGP
- **Utilisation recommandée :** Source de référence pour valider les horaires F2/F3/F1A. Le code source expose les données en JSON dans le dossier `_db/` du dépôt — extractibles sans scraping.
- **Mise à jour :** Manuelle par les mainteneurs après chaque annonce officielle

---

## Recommandations d'implémentation

### Tableau de décision

| Championnat | Source | Endpoint | Complexité | Priorité |
|---|---|---|---|---|
| **Formula 1** (2023+) | OpenF1 | `https://api.openf1.org/v1/` | ✅ Fait | — |
| **Formula 1** (1950-2022) | Jolpica | `http://api.jolpi.ca/ergast/f1/` | 🟢 Facile | P1 |
| **WEC** | fiawec.com scraping HTML | `https://www.fiawec.com/en/season` | 🟡 Moyen | P1 |
| **ELMS** | europeanlemansseries.com — inspecter XHR d'abord | DevTools → XHR ou HTML | 🟡 Moyen | P2 |
| **Formula 2** | fiaformula2.com + venues F1 | `https://www.fiaformula2.com/Calendar` | 🟡 Moyen | P2 |
| **Formula 3** | fiaformula3.com + venues F1 | `https://www.fiaformula3.com/Calendar` | 🟡 Moyen | P2 |
| **Porsche Supercup** | racing.porsche.com + venues F1 | `https://racing.porsche.com/mobil-1-supercup/race-calendar-{year}` | 🟡 Moyen | P3 |
| **F1 Academy** | f1academy.com + venues F1 | `https://www.f1academy.com/Racing-Series/Calendar` | 🟡 Moyen | P3 |
| **MLMC + RTLM** | lemanscup.com — XHR prioritaire | `https://www.lemanscup.com/en/season` | 🔴 Complexe | P3 |

### Ordre d'implémentation recommandé

**P1 — Court terme (v0.2.0)**
1. `ErgastSource` (Jolpica) pour les saisons F1 historiques — API REST propre, Apache-2.0
2. `OfficialWecSource` — scraping HTML de fiawec.com + investigation XHR

**P2 — Moyen terme (v0.3.0)**
3. `ELMSSource` — investigation XHR europeanlemansseries.com en priorité
4. `Formula2Source` — scraping fiaformula2.com + venues réutilisées du provider F1
5. `Formula3Source` — même code que F2 (site identique)

**P3 — Long terme (v0.4.0 ou ultérieur)**
6. `PorscheSupercupSource` — scraping racing.porsche.com + dérivation venues F1
7. `F1AcademySource` — scraping f1academy.com
8. `MichelinLeMansSource` — fusionné MLMC + RTLM, approche Playwright si XHR indisponible

### Principe directeur

> Avant d'implémenter un scraper HTML, **ouvrir les DevTools du navigateur** et inspecter les requêtes réseau (onglet Network → XHR/Fetch) sur la page du calendrier.
> De nombreux sites modernes chargent leurs données via un endpoint JSON interne non documenté mais accessible.
> Un endpoint XHR est **10× plus stable** qu'un scraper HTML.

---

## Licences et usage des données

| Source | Licence | Usage commercial | Attribution |
|---|---|---|---|
| OpenF1 | CC BY-NC-SA 4.0 | ❌ Interdit | Requise |
| Jolpica | Apache-2.0 | ✅ Autorisé | Requise |
| f1calendar.com code | MIT | ✅ Autorisé | Requise |
| Sites HTML scrapés | ToS non commerciale | ⚠️ Zone grise | Bonne pratique |

**Recommandation :** Pour un usage open source / non commercial, toutes ces sources sont acceptables. Pour une offre commerciale, utiliser Jolpica (Apache-2.0) et s'assurer d'un accord ou d'une politique claire pour les données scrapées.
