"""Local JSON profile store."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from charate.memory import LocalMemory
from charate.profile import CharacterProfile, ImportedAsset


class LocalProfileStore:
    """Persist profiles, assets, and distilled memories on the user's machine."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser()
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, profile: CharacterProfile, memory: LocalMemory | None = None) -> Path:
        profile_dir = self._profile_dir(profile.id)
        profile_dir.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = profile.to_dict()
        payload["memory"] = (memory or LocalMemory()).to_list()
        path = profile_dir / "profile.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def load(self, profile_id: str) -> tuple[CharacterProfile, LocalMemory]:
        path = self._profile_dir(profile_id) / "profile.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        memory = LocalMemory.from_list(data.pop("memory", []))
        return CharacterProfile.from_dict(data), memory

    def list_profiles(self) -> tuple[CharacterProfile, ...]:
        profiles: list[CharacterProfile] = []
        for path in sorted(self.root.glob("*/profile.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            data.pop("memory", None)
            profiles.append(CharacterProfile.from_dict(data))
        return tuple(profiles)

    def import_assets(self, profile: CharacterProfile, photo_paths: tuple[str | Path, ...]) -> CharacterProfile:
        """Copy local photos into the profile folder and return an updated profile."""
        profile_dir = self._profile_dir(profile.id)
        asset_dir = profile_dir / "assets"
        asset_dir.mkdir(parents=True, exist_ok=True)
        imported = list(profile.assets)
        for photo_path in photo_paths:
            source = Path(photo_path).expanduser()
            if not source.exists():
                raise FileNotFoundError(source)
            destination = asset_dir / source.name
            if source.resolve() != destination.resolve():
                shutil.copy2(source, destination)
            imported.append(ImportedAsset(path=str(destination), kind="photo"))
        return CharacterProfile(
            id=profile.id,
            name=profile.name,
            personality=profile.personality,
            description=profile.description,
            source=profile.source,
            assets=tuple(imported),
            interaction_summaries=profile.interaction_summaries,
            created_at=profile.created_at,
        )

    def _profile_dir(self, profile_id: str) -> Path:
        if not profile_id.strip() or "/" in profile_id or ".." in profile_id:
            raise ValueError("invalid profile id")
        return self.root / profile_id
