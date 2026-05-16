# Charate

Charate is a local-first character agent framework for creator-owned original
characters (OCs). The long-term product goal is a desktop pet that can respond,
remember lightweight preferences, and later support optional features such as
alarms and reminders.

## Core concepts

Charate starts every character profile in one of two ways:

1. **Create**: define a new OC with a name and basic personality description.
2. **Import**: initialize an existing OC with local photo paths, a description,
   and high-level summaries of previous interactions.

Every initialized character has:

- a `CharacterProfile` containing creator-supplied identity/personality data;
- `LocalMemory`, which stores distilled notes rather than raw chat transcripts;
- a `CharacterAgent`, which combines profile, memory, and a response model;
- a `ResponseModel` protocol so apps can plug in an on-device or user-configured
  LLM while keeping storage local.

## Privacy model

The framework is designed so the application creator does not need to know user
interactions. Profile files and memory are written to a user-selected local
folder. The default agent does not persist raw messages, dictation, or personal
content. Callers may save only explicit high-level memory summaries, such as
"user likes cozy greetings".

## Quick start

```bash
python -m pip install -e .
charate create --name Mira --personality "Warm, curious, and gently mischievous."
charate say <profile-id> "hello"
```

Importing an existing OC:

```bash
charate import \
  --name Rune \
  --personality "Quiet guardian who speaks in short poetic lines." \
  --description "Silver hair and a moon-shaped cloak." \
  --photo ./rune.png \
  --interaction-summary "Trusts the user after a long journey."
```

## Optional extensions

Desktop-pet extras are intentionally separate from the core framework. The
`charate.extras` module currently contains small local data models for future
alarms and reminders without coupling them to character memory or responses.
