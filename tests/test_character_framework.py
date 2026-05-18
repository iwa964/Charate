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


def test_cli_import_copies_photos_into_profile_store(tmp_path, monkeypatch, capsys) -> None:
    from charate.cli import main

    source_dir = tmp_path / "source"
    source_dir.mkdir()
    photo = source_dir / "rune.png"
    photo.write_bytes(b"fake image bytes")
    store_dir = tmp_path / "profiles"

    monkeypatch.chdir(source_dir)

    assert main(
        [
            "--store",
            str(store_dir),
            "import",
            "--name",
            "Rune",
            "--personality",
            "Quiet guardian.",
            "--photo",
            "./rune.png",
        ]
    ) == 0

    profile_id = capsys.readouterr().out.strip()
    profile, _ = LocalProfileStore(store_dir).load(profile_id)

    assert len(profile.assets) == 1
    copied_photo = store_dir / profile_id / "assets" / "rune.png"
    assert copied_photo.read_bytes() == b"fake image bytes"
    assert profile.assets[0].path == str(copied_photo)
    assert profile.assets[0].path != "./rune.png"


def test_language_page_updates_software_and_character_languages() -> None:
    from charate.settings import AppSettings, LanguagePage, SettingsPage

    settings = AppSettings()
    updated = LanguagePage(settings).apply(
        interface_language="Spanish",
        character_output_language="es",
    )

    assert updated.interface_language == "es"
    assert updated.character_output_language == "es"
    assert LanguagePage(updated).title == "Idioma"
    assert SettingsPage(updated).entries == ("Idioma: Spanish",)


def test_store_persists_language_settings(tmp_path) -> None:
    from charate.settings import AppSettings

    store = LocalProfileStore(tmp_path)
    path = store.save_settings(AppSettings(interface_language="fr", character_output_language="es"))

    assert path == tmp_path / "settings.json"
    assert store.load_settings().interface_language_name == "French"
    assert store.load_settings().character_output_language_name == "Spanish"


def test_agent_uses_character_output_language_in_prompt_and_response() -> None:
    profile = CharacterProfile.create("Luz", "Warm and bright.")
    agent = CharacterAgent(profile, output_language="es")

    assert "Reply to the user in Spanish." in agent.prompt_context()
    assert "Me alegra" in agent.respond("hello")


def test_cli_language_settings_affect_character_output(tmp_path, capsys) -> None:
    from charate.cli import main

    store_dir = tmp_path / "profiles"
    assert main(
        ["--store", str(store_dir), "settings", "language", "--software", "es", "--characters", "es"]
    ) == 0
    settings_output = capsys.readouterr().out
    assert "Idioma" in settings_output
    assert "Characters: Spanish (es)" in settings_output

    assert main(
        ["--store", str(store_dir), "create", "--name", "Luz", "--personality", "Warm and bright."]
    ) == 0
    profile_id = capsys.readouterr().out.strip()

    assert main(["--store", str(store_dir), "say", profile_id, "hello"]) == 0
    response = capsys.readouterr().out
    assert "Me alegra" in response
