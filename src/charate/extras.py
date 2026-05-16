"""Optional desktop-pet extras kept separate from the core character framework."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Reminder:
    """Local reminder configuration for future desktop-pet features."""

    text: str
    remind_at: datetime


@dataclass(frozen=True)
class Alarm:
    """Local alarm configuration for future desktop-pet features."""

    label: str
    ring_at: datetime
