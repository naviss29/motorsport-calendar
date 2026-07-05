"""Modèles Pydantic pour la configuration de l'application."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class CacheConfig(BaseModel):
    """Configuration du cache HTTP disque."""

    model_config = ConfigDict(frozen=True)

    enabled: bool = True
    path: Path = Field(default_factory=lambda: Path("~/.cache/motorsport-calendar"))
    ttl_hours: int = Field(default=24, ge=1)

    @property
    def resolved_path(self) -> Path:
        """Chemin absolu avec `~` résolu."""
        return self.path.expanduser()

    @property
    def ttl_seconds(self) -> int:
        """TTL converti en secondes."""
        return self.ttl_hours * 3600


class IcsConfig(BaseModel):
    """Configuration de l'exporteur ICS."""

    model_config = ConfigDict(frozen=True)

    alarm_minutes: int = Field(default=30, ge=0)


class ProviderConfig(BaseModel):
    """Configuration d'un provider (source sélectionnée)."""

    model_config = ConfigDict(frozen=True)

    source: str


class ProvidersConfig(BaseModel):
    """Configuration de tous les providers."""

    model_config = ConfigDict(frozen=True)

    formula1: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(source="openf1")
    )
    wec: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(source="official")
    )


class AppConfig(BaseModel):
    """Configuration globale de l'application.

    Correspond à la structure de ``config.yaml``.
    Toutes les valeurs ont des défauts — le fichier est entièrement optionnel.
    """

    model_config = ConfigDict(frozen=True)

    timezone: str = "Europe/Paris"
    cache: CacheConfig = Field(default_factory=CacheConfig)
    ics: IcsConfig = Field(default_factory=IcsConfig)
    providers: ProvidersConfig = Field(default_factory=ProvidersConfig)
