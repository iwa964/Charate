"""Response model implementations for character agents."""

from __future__ import annotations

from dataclasses import dataclass

from charate.profile import CharacterProfile


@dataclass(frozen=True)
class RuleBasedCharacterModel:
    """Local fallback model for development and tests.

    Production apps can provide an on-device or user-configured LLM by
    implementing the ``ResponseModel`` protocol in ``charate.agent``.
    """

    def generate(self, profile: CharacterProfile, user_input: str, memory_context: str = "") -> str:
        tone_hint = profile.personality.split(".")[0].strip() or profile.personality
        memory_line = f" I remember: {memory_context.splitlines()[0].lstrip('- ')}" if memory_context else ""
        return f"{profile.name}: {tone_hint}. {self._respond_to(user_input)}{memory_line}"

    @staticmethod
    def _respond_to(user_input: str) -> str:
        lowered = user_input.lower()
        if any(word in lowered for word in ("hello", "hi", "hey")):
            return "I'm happy you came by."
        if "remind" in lowered:
            return "I can keep that as a local reminder once the reminder module is enabled."
        if "alarm" in lowered:
            return "Alarms should live in an optional local extension, separate from my core memory."
        return "Tell me more, and I'll answer in my own way."
