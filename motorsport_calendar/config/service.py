"""ConfigService — lecture et validation de config.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

from motorsport_calendar.config.models import (
    AppConfig,
    CacheConfig,
    IcsConfig,
    ProvidersConfig,
)


class ConfigService:
    """Charge et expose la configuration de l'application.

    Recherche ``config.yaml`` dans l'ordre suivant :
    1. Chemin explicite passé au constructeur
    2. ``config.yaml`` dans le répertoire courant
    3. ``~/.config/motorsport-calendar/config.yaml``

    Si aucun fichier n'est trouvé, les valeurs par défaut s'appliquent.
    La validation est assurée par Pydantic : un fichier invalide lève une erreur.

    Args:
        config_path: Chemin explicite vers un fichier ``config.yaml``.
                     Quand fourni, aucun autre chemin n'est cherché.
    """

    _DEFAULT_PATHS: list[Path] = [
        Path("config.yaml"),
        Path("~/.config/motorsport-calendar/config.yaml"),
    ]

    def __init__(self, config_path: Path | None = None) -> None:
        self._config = self._load(config_path)

    # ------------------------------------------------------------------
    # Accès direct aux sous-sections
    # ------------------------------------------------------------------

    @property
    def config(self) -> AppConfig:
        """Configuration complète."""
        return self._config

    @property
    def timezone(self) -> str:
        return self._config.timezone

    @property
    def cache(self) -> CacheConfig:
        return self._config.cache

    @property
    def ics(self) -> IcsConfig:
        return self._config.ics

    @property
    def providers(self) -> ProvidersConfig:
        return self._config.providers

    # ------------------------------------------------------------------
    # Chargement interne
    # ------------------------------------------------------------------

    def _load(self, explicit_path: Path | None) -> AppConfig:
        paths = [explicit_path] if explicit_path is not None else self._DEFAULT_PATHS
        for path in paths:
            resolved = path.expanduser()
            if resolved.exists():
                raw = yaml.safe_load(resolved.read_text(encoding="utf-8")) or {}
                return AppConfig.model_validate(raw)
        return AppConfig()
