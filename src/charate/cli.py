"""Small CLI for initializing local character profiles."""

from __future__ import annotations

import argparse
from pathlib import Path

from charate.agent import CharacterAgent
from charate.profile import CharacterProfile
from charate.store import LocalProfileStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create or import local Charate profiles.")
    parser.add_argument("--store", default="~/.charate/profiles", help="Local profile store directory.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    create = subcommands.add_parser("create", help="Create a new OC profile.")
    create.add_argument("--name", required=True)
    create.add_argument("--personality", required=True)
    create.add_argument("--description", default="")

    import_cmd = subcommands.add_parser("import", help="Import an existing OC profile.")
    import_cmd.add_argument("--name", required=True)
    import_cmd.add_argument("--personality", required=True)
    import_cmd.add_argument("--description", default="")
    import_cmd.add_argument("--photo", action="append", default=[])
    import_cmd.add_argument("--interaction-summary", action="append", default=[])

    chat = subcommands.add_parser("say", help="Generate a local character response.")
    chat.add_argument("profile_id")
    chat.add_argument("message")
    chat.add_argument("--memory-summary", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = LocalProfileStore(Path(args.store))

    if args.command == "create":
        profile = CharacterProfile.create(args.name, args.personality, args.description)
        store.save(profile)
        print(profile.id)
        return 0

    if args.command == "import":
        profile = CharacterProfile.import_existing(
            args.name,
            args.personality,
            description=args.description,
            photo_paths=tuple(args.photo),
            interaction_summaries=tuple(args.interaction_summary),
        )
        store.save(profile)
        print(profile.id)
        return 0

    if args.command == "say":
        profile, memory = store.load(args.profile_id)
        agent = CharacterAgent(profile, memory=memory)
        print(agent.respond(args.message, memory_summary=args.memory_summary))
        store.save(profile, agent.memory)
        return 0

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
