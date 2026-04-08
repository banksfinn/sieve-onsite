"""Path matching utilities for note scopes."""

import fnmatch
from pathlib import Path

from .models import NoteIndex


def normalize_path(path: str) -> str:
    """Normalize a path for matching."""
    # Remove leading ./ or /
    path = path.lstrip("./")
    # Convert backslashes to forward slashes
    path = path.replace("\\", "/")
    return path


def matches_path(file_path: str, pattern: str) -> bool:
    """
    Check if a file path matches a glob pattern.

    Supports:
    - * for single directory level
    - ** for recursive matching
    - ? for single character
    - ! prefix for negation (handled separately)
    """
    file_path = normalize_path(file_path)
    pattern = normalize_path(pattern)

    # Handle ** patterns by converting to fnmatch-compatible
    # fnmatch doesn't handle ** well, so we need special handling
    if "**" in pattern:
        # Split pattern on **
        parts = pattern.split("**")
        if len(parts) == 2:
            prefix, suffix = parts
            prefix = prefix.rstrip("/")
            suffix = suffix.lstrip("/")

            # Check if file starts with prefix
            if prefix and not file_path.startswith(prefix):
                return False

            # Get the rest of the path after prefix
            if prefix:
                remaining = file_path[len(prefix) :].lstrip("/")
            else:
                remaining = file_path

            # Check if suffix matches
            if suffix:
                # Suffix can match anywhere in the remaining path
                # But must match at a path boundary or the end
                if fnmatch.fnmatch(remaining, suffix):
                    return True
                if fnmatch.fnmatch(remaining, f"*/{suffix}"):
                    return True
                # Also try matching the filename directly
                filename = Path(file_path).name
                if fnmatch.fnmatch(filename, suffix):
                    return True
                return False
            else:
                # Pattern ends with **, matches everything under prefix
                return True

    # Simple fnmatch for non-** patterns
    return fnmatch.fnmatch(file_path, pattern)


def get_notes_for_path(file_path: str, index: NoteIndex) -> list[str]:
    """
    Return note IDs whose scope matches the given file path.

    Handles negation patterns (starting with !) to exclude files.
    """
    matching_note_ids: list[str] = []

    for indexed_note in index.notes:
        include_patterns: list[str] = []
        exclude_patterns: list[str] = []

        for pattern in indexed_note.paths:
            if pattern.startswith("!"):
                exclude_patterns.append(pattern[1:])
            else:
                include_patterns.append(pattern)

        # Check if file matches any include pattern
        matches_include = any(matches_path(file_path, p) for p in include_patterns)

        # Check if file matches any exclude pattern
        matches_exclude = any(matches_path(file_path, p) for p in exclude_patterns)

        if matches_include and not matches_exclude:
            matching_note_ids.append(indexed_note.id)

    return matching_note_ids


def get_notes_for_tags(tags: list[str], index: NoteIndex) -> list[str]:
    """Return note IDs that have any of the given tags."""
    matching_note_ids: list[str] = []
    tags_set = set(tags)

    for indexed_note in index.notes:
        if tags_set.intersection(indexed_note.tags):
            matching_note_ids.append(indexed_note.id)

    return matching_note_ids
