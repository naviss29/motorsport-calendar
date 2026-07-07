# Emplacement du logo — à compléter

Ce dossier reçoit les assets définitifs du Brand Set Motorsport Calendar v1.0
(validé, voir `BApps-Studio/03-Products/Motorsport-Calendar/Branding/Branding.md`)
dès qu'ils seront livrés dans ce dépôt.

En attendant, l'app affiche un **placeholder** (`theme.logo_placeholder()` dans
`gui/theme.py`) partout où le vrai logo apparaîtra — aucun logo définitif n'a
été créé ni copié ici pour ce sprint.

## Fichiers attendus (non livrés)

| Fichier | Rôle | Consommateur prévu |
|---|---|---|
| `mc-icon.svg` / `.png` | Monogramme MC seul | Nav rail, en-tête "À propos", en-tête "Mon calendrier" |
| `logo-horizontal.svg` / `.png` | Monogramme + wordmark | En-tête large / bannière |
| `favicon-16.png`, `favicon-32.png` | Favicon | `app.py` (`page.window.icon`) |
| `icon.ico` | Icône Windows multi-résolution | Packaging `.exe` (hors scope de ce sprint) |

## Intégration future

1. Copier les fichiers définitifs dans ce dossier.
2. Décommenter `assets_dir=` dans `motorsport_calendar/gui/app.py`.
3. Remplacer les appels à `theme.logo_placeholder(...)` par `ft.Image(src="logo/mc-icon.svg", ...)`
   aux emplacements listés ci-dessus.

Aucune autre modification de layout n'est nécessaire : les emplacements ont
été dimensionnés pour accueillir le logo définitif tel quel.
