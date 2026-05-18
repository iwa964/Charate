"""Local application settings and settings-page view models."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "zh": "Chinese",
}


@dataclass(frozen=True)
class AppSettings:
    """Local user settings for app text and character output."""

    interface_language: str = "en"
    character_output_language: str = "en"

    def __post_init__(self) -> None:
        _require_supported_language(self.interface_language, "interface_language")
        _require_supported_language(self.character_output_language, "character_output_language")

    @property
    def interface_language_name(self) -> str:
        return SUPPORTED_LANGUAGES[self.interface_language]

    @property
    def character_output_language_name(self) -> str:
        return SUPPORTED_LANGUAGES[self.character_output_language]

    def with_language_preferences(
        self,
        *,
        interface_language: str | None = None,
        character_output_language: str | None = None,
    ) -> "AppSettings":
        """Return settings updated from the language page."""
        return replace(
            self,
            interface_language=(
                self.interface_language if interface_language is None else normalize_language(interface_language)
            ),
            character_output_language=(
                self.character_output_language
                if character_output_language is None
                else normalize_language(character_output_language)
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "interface_language": self.interface_language,
            "character_output_language": self.character_output_language,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppSettings":
        return cls(
            interface_language=normalize_language(data.get("interface_language", "en")),
            character_output_language=normalize_language(data.get("character_output_language", "en")),
        )


@dataclass(frozen=True)
class SettingsPage:
    """View model for the top-level settings page."""

    settings: AppSettings = field(default_factory=AppSettings)

    @property
    def title(self) -> str:
        return _settings_label(self.settings.interface_language, "settings")

    @property
    def entries(self) -> tuple[str, ...]:
        language_label = _settings_label(self.settings.interface_language, "language")
        return (f"{language_label}: {self.settings.character_output_language_name}",)


@dataclass(frozen=True)
class LanguagePage:
    """View model for changing software and character-output languages."""

    settings: AppSettings = field(default_factory=AppSettings)

    @property
    def title(self) -> str:
        return _settings_label(self.settings.interface_language, "language")

    @property
    def options(self) -> tuple[dict[str, str], ...]:
        return tuple({"code": code, "name": name} for code, name in SUPPORTED_LANGUAGES.items())

    def apply(
        self,
        *,
        interface_language: str | None = None,
        character_output_language: str | None = None,
    ) -> AppSettings:
        return self.settings.with_language_preferences(
            interface_language=interface_language,
            character_output_language=character_output_language,
        )


_SETTINGS_LABELS: dict[str, dict[str, str]] = {
    "en": {"settings": "Settings", "language": "Language"},
    "es": {"settings": "Configuración", "language": "Idioma"},
    "fr": {"settings": "Paramètres", "language": "Langue"},
    "de": {"settings": "Einstellungen", "language": "Sprache"},
    "it": {"settings": "Impostazioni", "language": "Lingua"},
    "ja": {"settings": "設定", "language": "言語"},
    "ko": {"settings": "설정", "language": "언어"},
    "pt": {"settings": "Configurações", "language": "Idioma"},
    "zh": {"settings": "设置", "language": "语言"},
}


def normalize_language(language: str) -> str:
    """Normalize user-entered language codes or names to supported codes."""
    candidate = language.strip().lower().replace("_", "-")
    if not candidate:
        raise ValueError("language is required")
    primary = candidate.split("-", 1)[0]
    if primary in SUPPORTED_LANGUAGES:
        return primary
    for code, name in SUPPORTED_LANGUAGES.items():
        if candidate == name.lower():
            return code
    raise ValueError(f"unsupported language: {language}")


def language_instruction(language: str) -> str:
    """Return prompt instructions for character output language."""
    code = normalize_language(language)
    name = SUPPORTED_LANGUAGES[code]
    return f"Reply to the user in {name}."


def _require_supported_language(language: str, field_name: str) -> None:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"{field_name} must be one of: {', '.join(SUPPORTED_LANGUAGES)}")


def _settings_label(language: str, key: str) -> str:
    return _SETTINGS_LABELS.get(language, _SETTINGS_LABELS["en"])[key]
