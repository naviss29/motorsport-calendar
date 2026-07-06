"""Centralized UI strings for Motorsport Calendar GUI.

All user-visible text lives here.

To add a language in the future:
  1. Create gui/i18n/fr.json (or en.json) with the same attribute names as keys
  2. Load it at startup: Strings.from_dict(json.loads(path.read_text()))
  3. Replace the module-level STRINGS singleton
"""
from __future__ import annotations


class Strings:
    """All user-visible text. Replace the STRINGS singleton to switch language."""

    # App chrome
    app_title: str = "Motorsport Calendar"
    app_subtitle: str = "Calendrier des courses automobiles"

    # Section labels
    season_label: str = "Saison"
    championships_label: str = "Championnats"
    output_label: str = "Fichier de sortie"

    # File picker
    output_hint: str = "Cliquer sur l'icône pour choisir l'emplacement…"
    browse_tooltip: str = "Choisir l'emplacement du fichier"
    save_dialog_title: str = "Enregistrer le calendrier"

    # Generate
    generate_btn: str = "Créer mon calendrier"
    generating_status: str = "Création du calendrier en cours…"

    # Success dialog
    success_title: str = "Calendrier créé avec succès"
    success_saved_at: str = "Enregistré dans :"
    open_folder_btn: str = "Ouvrir le dossier"
    close_btn: str = "Fermer"

    # Error messages
    error_no_events: str = "Aucun événement exporté"
    error_unexpected: str = "Erreur inattendue : {msg}"

    # Per-championship result lines (shown inside success dialog)
    summary_ok: str = "✓ {name} — {n} événement{s}"
    summary_error: str = "✗ {name} : {err}"

    # Navigation rail
    nav_home: str = "Accueil"
    nav_calendar: str = "Calendrier"
    nav_about: str = "À propos"

    # Home screen
    home_title: str = "Bienvenue"
    home_body: str = (
        "Créez votre calendrier de courses automobiles personnalisé "
        "et importez-le dans Google Calendar, Apple Calendar ou Outlook."
    )
    home_cta: str = "Créer mon calendrier"

    # About screen
    about_version: str = "Version Alpha"
    about_developer: str = "Développé par BApps"
    about_github_label: str = "Voir sur GitHub"
    about_license: str = "Licence MIT"
    about_description: str = (
        "Motorsport Calendar agrège les calendriers de saison de plusieurs "
        "championnats automobiles et les exporte au format ICS standard."
    )

    @classmethod
    def from_dict(cls, data: dict) -> "Strings":
        """Build a Strings instance from a dict (future i18n use).

        Unknown keys are ignored; existing attributes are overridden.
        """
        obj = cls()
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj


def plural(n: int) -> str:
    """Return 's' when n != 1, '' otherwise (French pluralisation)."""
    return "s" if n != 1 else ""


# Module-level singleton — replace to change language application-wide
STRINGS: Strings = Strings()
