"""Character profile models.

Profiles intentionally contain only creator-supplied character information and local
asset references. User conversations are handled by memory policies instead of being
stored verbatim by default.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class ImportedAsset:
    """A local file reference imported for an existing character."""

    path: str
    kind: str = "photo"
    caption: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "kind": self.kind, "caption": self.caption}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ImportedAsset":
        return cls(path=data["path"], kind=data.get("kind", "photo"), caption=data.get("caption"))


@dataclass(frozen=True)
class CharacterProfile:
    """Local character initialization data.

    A profile can be initialized in two ways:
    - ``create``: creator supplies a name and personality description.
    - ``import``: creator supplies existing OC information, local photos, and
      non-sensitive summaries of previous interactions.
    """

    id: str
    name: str
    personality: str
    description: str = ""
    source: str = "create"
    assets: tuple[ImportedAsset, ...] = field(default_factory=tuple)
    interaction_summaries: tuple[str, ...] = field(default_factory=tuple)
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    @classmethod
    def create(cls, name: str, personality: str, description: str = "") -> "CharacterProfile":
        """Create a new original character profile from minimal creator input."""
        return cls(
            id=str(uuid4()),
            name=_require_text(name, "name"),
            personality=_require_text(personality, "personality"),
            description=description.strip(),
            source="create",
        )

    @classmethod
    def import_existing(
        cls,
        name: str,
        personality: str,
        *,
        description: str = "",
        photo_paths: tuple[str | Path, ...] = (),
        interaction_summaries: tuple[str, ...] = (),
    ) -> "CharacterProfile":
        """Initialize a profile from creator-owned local OC information."""
        assets = tuple(ImportedAsset(path=str(Path(path).expanduser())) for path in photo_paths)
        summaries = tuple(summary.strip() for summary in interaction_summaries if summary.strip())
        return cls(
            id=str(uuid4()),
            name=_require_text(name, "name"),
            personality=_require_text(personality, "personality"),
            description=description.strip(),
            source="import",
            assets=assets,
            interaction_summaries=summaries,
        )

    def system_prompt(self) -> str:
        """Build instructions for an LLM to roleplay this character."""
        parts = [
            f"You are {self.name}, an original character owned by the local user.",
            "Stay in character while being kind, safe, and transparent about being software when needed.",
            f"Core personality: {self.personality}",
        ]
        if self.description:
            parts.append(f"Appearance/background: {self.description}")
        if self.interaction_summaries:
            parts.append("Prior relationship notes: " + " ".join(self.interaction_summaries))
        return "\n".join(parts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "personality": self.personality,
            "description": self.description,
            "source": self.source,
            "assets": [asset.to_dict() for asset in self.assets],
            "interaction_summaries": list(self.interaction_summaries),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CharacterProfile":
        return cls(
            id=data["id"],
            name=data["name"],
            personality=data["personality"],
            description=data.get("description", ""),
            source=data.get("source", "create"),
            assets=tuple(ImportedAsset.from_dict(asset) for asset in data.get("assets", [])),
            interaction_summaries=tuple(data.get("interaction_summaries", [])),
            created_at=data.get("created_at", _now_iso()),
            updated_at=data.get("updated_at", _now_iso()),
        )


def _require_text(value: str, field_name: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} is required")
    return value
