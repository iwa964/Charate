from __future__ import annotations

import json

from charate.agent import CharacterAgent
from charate.memory import LocalMemory
from charate.profile import CharacterProfile
from charate.store import LocalProfileStore


def test_create_profile_builds_character_prompt() -> None:
    profile = CharacterProfile.create("Mira", "Warm, curious, and gently mischievous.")

    prompt = profile.system_prompt()

    assert "You are Mira" in prompt
    assert "Warm, curious" in prompt
    assert profile.source == "create"


def test_import_profile_keeps_creator_supplied_context_local() -> None:
    profile = CharacterProfile.import_existing(
        "Rune",
        "Quiet guardian who speaks in short poetic lines.",
        description="Silver hair and a moon-shaped cloak.",
        photo_paths=("/tmp/rune.png",),
        interaction_summaries=("Trusts the user after a long journey.",),
    )

    assert profile.source == "import"
    assert profile.assets[0].path == "/tmp/rune.png"
    assert "Prior relationship notes" in profile.system_prompt()


def test_agent_responds_without_storing_raw_messages() -> None:
    profile = CharacterProfile.create("Pip", "Cheerful desk companion.")
    agent = CharacterAgent(profile)

    response = agent.respond("hello, can you help?", memory_summary="User likes morning greetings.")

    assert response.startswith("Pip:")
    assert "User likes morning greetings." in agent.memory.context()
    assert "hello, can you help?" not in agent.memory.context()


def test_store_round_trips_profile_and_distilled_memory(tmp_path) -> None:
    store = LocalProfileStore(tmp_path)
    profile = CharacterProfile.create("Nox", "Dry humor and loyal.")
    memory = LocalMemory()
    memory.remember("User prefers concise check-ins.", importance=4)

    profile_path = store.save(profile, memory)
    loaded_profile, loaded_memory = store.load(profile.id)

    assert profile_path.exists()
    assert loaded_profile == profile
    assert loaded_memory.context() == "- User prefers concise check-ins."
    raw = json.loads(profile_path.read_text(encoding="utf-8"))
    assert raw["memory"][0]["summary"] == "User prefers concise check-ins."
