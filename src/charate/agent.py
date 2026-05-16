"""Character agent orchestration."""

from __future__ import annotations

from typing import Protocol

from charate.memory import LocalMemory, MemoryRecord
from charate.profile import CharacterProfile
from charate.response import RuleBasedCharacterModel


class ResponseModel(Protocol):
    """Protocol for local or user-configured LLM adapters."""

    def generate(self, profile: CharacterProfile, user_input: str, memory_context: str = "") -> str:
        """Generate a character response without persisting raw user input."""


class CharacterAgent:
    """Runs character responses and distilled local memory.

    The agent deliberately does not append raw messages to storage. Callers can
    decide whether a high-level memory should be saved by passing
    ``memory_summary`` to ``respond`` or by calling ``remember`` directly.
    """

    def __init__(
        self,
        profile: CharacterProfile,
        *,
        memory: LocalMemory | None = None,
        response_model: ResponseModel | None = None,
    ) -> None:
        self.profile = profile
        self.memory = memory or LocalMemory()
        self.response_model = response_model or RuleBasedCharacterModel()

    def respond(self, user_input: str, *, memory_summary: str | None = None) -> str:
        if not user_input.strip():
            raise ValueError("user input is required")
        if memory_summary and memory_summary.strip():
            self.remember(memory_summary, tags=("conversation-derived",))
        return self.response_model.generate(self.profile, user_input, self.memory.context())

    def remember(self, summary: str, *, importance: int = 1, tags: tuple[str, ...] = ()) -> MemoryRecord:
        return self.memory.remember(summary, importance=importance, tags=tags)

    def prompt_context(self) -> str:
        memory_context = self.memory.context()
        if not memory_context:
            return self.profile.system_prompt()
        return f"{self.profile.system_prompt()}\nLocal distilled memories:\n{memory_context}"
