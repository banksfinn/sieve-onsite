"""File I/O operations for notes."""

from pathlib import Path

from .models import Note
from .parser import parse_note, serialize_note

# Project root - storage.py is one level deeper than server.py (in notes/ subdir)
# Path: tools/mcp_server/mcp_server/notes/storage.py -> 6 levels up to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
NOTES_DIR = PROJECT_ROOT / ".ai" / "notes"


def get_notes_directory() -> Path:
    """Get the .ai/notes directory path."""
    return NOTES_DIR


def ensure_notes_directory() -> Path:
    """Ensure .ai/notes directory exists, creating if necessary."""
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    return NOTES_DIR


def get_note_path(note_id: str) -> Path:
    """Get the file path for a note by ID."""
    return NOTES_DIR / f"{note_id}.md"


def read_note(note_id: str) -> Note | None:
    """Read a note file by ID. Returns None if not found."""
    note_path = get_note_path(note_id)
    if not note_path.exists():
        return None

    content = note_path.read_text(encoding="utf-8")
    return parse_note(content)


def write_note(note: Note) -> None:
    """Write a note to its file."""
    ensure_notes_directory()
    note_path = get_note_path(note.frontmatter.id)
    content = serialize_note(note)
    note_path.write_text(content, encoding="utf-8")


def delete_note(note_id: str) -> bool:
    """Delete a note file. Returns True if deleted, False if not found."""
    note_path = get_note_path(note_id)
    if not note_path.exists():
        return False
    note_path.unlink()
    return True


def list_note_ids() -> list[str]:
    """List all note IDs in the notes directory."""
    if not NOTES_DIR.exists():
        return []

    note_ids: list[str] = []
    for path in NOTES_DIR.glob("*.md"):
        # Skip special files
        if path.name.startswith("_"):
            continue
        note_ids.append(path.stem)

    return sorted(note_ids)


def note_exists(note_id: str) -> bool:
    """Check if a note exists."""
    return get_note_path(note_id).exists()
