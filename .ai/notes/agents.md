---
id: agents
title: AI Agent Guidelines
purpose: |
  Core guidelines for AI agents working in this codebase.
  These rules apply to all AI interactions with the repository.
scope:
  paths:
    - "**/*"
  tags:
    - ai
    - agents
    - general
related: []
---

# AI Agent Guidelines

## Items

<!-- @item source:user status:active enforcement:strict -->
Before working on any file, call `get_notes_for_path("path/to/file")` to retrieve relevant guidelines. Each item includes an enforcement level (`locked`, `strict`, `recommended`, `flexible`) indicating how strictly to follow it.

<!-- @item source:user status:active enforcement:strict -->
When you discover important patterns, gotchas, or conventions during work, document them by calling `add_item(note_id, content)`. Use `search_notes()` to find the appropriate note, or `create_note()` if none exists.

<!-- @item source:user status:active enforcement:strict -->
Before editing user-created items (`source: user`), ask the user for approval. LLM-created items can be updated directly.

<!-- @item source:user status:active enforcement:strict -->
Always follow the patterns established in CLAUDE.md for this project.

<!-- @item source:user status:active enforcement:locked -->
Never commit secrets, API keys, or credentials to the repository.

<!-- @item source:user status:active enforcement:recommended -->
When creating new files, follow the existing directory structure and naming conventions.

<!-- @item source:user status:active enforcement:recommended -->
Run tests and linting before suggesting code is complete.
