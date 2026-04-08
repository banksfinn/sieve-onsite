"""Index generation and management for notes."""

from pathlib import Path

import yaml

from .models import IndexedItem, IndexedNote, NoteIndex
from .storage import get_notes_directory, list_note_ids, read_note

INDEX_FILENAME = "_index.yaml"


def get_index_path(notes_dir: Path | None = None) -> Path:
    """Get the path to the index file."""
    if notes_dir is None:
        notes_dir = get_notes_directory()
    return notes_dir / INDEX_FILENAME


def generate_index(notes_dir: Path | None = None) -> NoteIndex:
    """Scan all note files and generate index."""
    if notes_dir is None:
        notes_dir = get_notes_directory()

    indexed_notes: list[IndexedNote] = []

    for note_id in list_note_ids():
        note = read_note(note_id)
        if note is None:
            continue

        # Build indexed items
        indexed_items: list[IndexedItem] = []
        for i, item in enumerate(note.items):
            preview = item.content[:100]
            if len(item.content) > 100:
                preview += "..."

            indexed_items.append(
                IndexedItem(
                    index=i,
                    source=item.source,
                    status=item.status,
                    enforcement=item.effective_enforcement,
                    preview=preview,
                )
            )

        indexed_notes.append(
            IndexedNote(
                id=note.frontmatter.id,
                title=note.frontmatter.title,
                purpose=note.frontmatter.purpose,
                paths=note.frontmatter.scope.paths,
                tags=note.frontmatter.scope.tags,
                items=indexed_items,
            )
        )

    return NoteIndex(notes=indexed_notes)


def save_index(index: NoteIndex, notes_dir: Path | None = None) -> None:
    """Save index to _index.yaml."""
    index_path = get_index_path(notes_dir)

    # Use Pydantic's model_dump for proper serialization (converts enums to values)
    data = index.model_dump(mode="json")

    index_path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def load_index(notes_dir: Path | None = None) -> NoteIndex | None:
    """Load existing index from _index.yaml. Returns None if not found."""
    index_path = get_index_path(notes_dir)
    if not index_path.exists():
        return None

    data = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    if not data or "notes" not in data:
        return None

    indexed_notes: list[IndexedNote] = []
    for note_data in data["notes"]:
        items: list[IndexedItem] = []
        for item_data in note_data.get("items", []):
            items.append(
                IndexedItem(
                    index=item_data["index"],
                    source=item_data["source"],
                    status=item_data["status"],
                    enforcement=item_data["enforcement"],
                    preview=item_data["preview"],
                )
            )

        indexed_notes.append(
            IndexedNote(
                id=note_data["id"],
                title=note_data["title"],
                purpose=note_data.get("purpose", ""),
                paths=note_data.get("paths", []),
                tags=note_data.get("tags", []),
                items=items,
            )
        )

    return NoteIndex(notes=indexed_notes)


def rebuild_index(notes_dir: Path | None = None) -> NoteIndex:
    """Regenerate and save index."""
    index = generate_index(notes_dir)
    save_index(index, notes_dir)
    return index


def get_or_rebuild_index(notes_dir: Path | None = None) -> NoteIndex:
    """Load index if exists, otherwise rebuild it."""
    index = load_index(notes_dir)
    if index is None:
        index = rebuild_index(notes_dir)
    return index
