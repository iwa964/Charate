"""Privacy-preserving local memory for character agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class MemoryRecord:
    """A distilled local memory record.

    ``summary`` should be a high-level note such as "user likes cozy greetings".
    It should not contain raw chat transcripts, dictation, or private content.
    """

    summary: str
    importance: int = 1
    tags: tuple[str, ...] = field(default_factory=tuple)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=_now_iso)

    def __post_init__(self) -> None:
        if not self.summary.strip():
            raise ValueError("memory summary is required")
        if not 1 <= self.importance <= 5:
            raise ValueError("memory importance must be between 1 and 5")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "summary": self.summary.strip(),
            "importance": self.importance,
            "tags": list(self.tags),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryRecord":
        return cls(
            id=data["id"],
            summary=data["summary"],
            importance=int(data.get("importance", 1)),
            tags=tuple(data.get("tags", [])),
            created_at=data.get("created_at", _now_iso()),
        )


class LocalMemory:
    """In-memory helper that stores distilled facts only."""

    def __init__(self, records: tuple[MemoryRecord, ...] = ()) -> None:
        self._records = list(records)

    @property
    def records(self) -> tuple[MemoryRecord, ...]:
        return tuple(self._records)

    def remember(self, summary: str, *, importance: int = 1, tags: tuple[str, ...] = ()) -> MemoryRecord:
        record = MemoryRecord(summary=summary, importance=importance, tags=tags)
        self._records.append(record)
        return record

    def context(self, limit: int = 5) -> str:
        """Return the most relevant memory summaries for prompt context."""
        ordered = sorted(self._records, key=lambda record: (record.importance, record.created_at), reverse=True)
        return "\n".join(f"- {record.summary}" for record in ordered[:limit])

    def to_list(self) -> list[dict[str, Any]]:
        return [record.to_dict() for record in self._records]

    @classmethod
    def from_list(cls, data: list[dict[str, Any]]) -> "LocalMemory":
        return cls(tuple(MemoryRecord.from_dict(record) for record in data))
