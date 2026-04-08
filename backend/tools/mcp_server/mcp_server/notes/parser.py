"""Markdown parsing and serialization for notes."""

import re
from typing import Any

import yaml

from .models import (
    ItemEnforcement,
    ItemSource,
    ItemStatus,
    Note,
    NoteFrontmatter,
    NoteItem,
    NoteScope,
)

# Pattern to extract YAML frontmatter
FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)

# Pattern to find item markers and their content
# Matches: <!-- @item source:user status:active enforcement:strict -->
ITEM_MARKER_PATTERN = re.compile(
    r"<!--\s*@item\s+(.*?)\s*-->\s*\n(.*?)(?=<!--\s*@item|$)",
    re.DOTALL,
)

# Pattern to parse key:value pairs from item metadata
ITEM_ATTR_PATTERN = re.compile(r"(\w+):(\w+)")


def parse_item_metadata(attr_string: str) -> dict[str, str]:
    """Parse 'source:user status:active enforcement:strict' into dict."""
    return dict(ITEM_ATTR_PATTERN.findall(attr_string))


def _strip_structural_headers(content: str, title: str) -> str:
    """Remove title heading and ## Items from content since serialize regenerates them."""
    # Remove title headings (may be duplicated)
    title_pattern = re.compile(rf"^#\s+{re.escape(title)}\s*\n?", re.MULTILINE)
    content = title_pattern.sub("", content)

    # Remove ## Items headers (may be duplicated)
    items_pattern = re.compile(r"^##\s+Items\s*\n?", re.MULTILINE)
    content = items_pattern.sub("", content)

    return content.strip()


def parse_note(content: str) -> Note:
    """Parse a markdown note file into a Note object."""
    # Extract frontmatter
    frontmatter_match = FRONTMATTER_PATTERN.match(content)
    if not frontmatter_match:
        raise ValueError("Note must have YAML frontmatter")

    frontmatter_yaml = frontmatter_match.group(1)
    frontmatter_data = yaml.safe_load(frontmatter_yaml)

    # Build frontmatter object
    scope_data = frontmatter_data.get("scope", {})
    scope = NoteScope(
        paths=scope_data.get("paths", []),
        tags=scope_data.get("tags", []),
    )

    frontmatter = NoteFrontmatter(
        id=frontmatter_data["id"],
        title=frontmatter_data["title"],
        purpose=frontmatter_data.get("purpose", ""),
        scope=scope,
        related=frontmatter_data.get("related", []),
    )

    # Get content after frontmatter
    body = content[frontmatter_match.end() :]

    # Parse items from body
    items: list[NoteItem] = []
    raw_content_parts: list[str] = []

    # Split content by item markers
    last_end = 0
    for match in ITEM_MARKER_PATTERN.finditer(body):
        # Capture non-item content before this match
        if match.start() > last_end:
            raw_content_parts.append(body[last_end : match.start()])

        # Parse item metadata
        metadata_str = match.group(1)
        item_content = match.group(2).strip()
        metadata = parse_item_metadata(metadata_str)

        # Build item
        source = ItemSource(metadata.get("source", "llm"))
        status = ItemStatus(metadata.get("status", "proposed"))
        enforcement = None
        if "enforcement" in metadata:
            enforcement = ItemEnforcement(metadata["enforcement"])

        items.append(
            NoteItem(
                content=item_content,
                source=source,
                status=status,
                enforcement=enforcement,
            )
        )
        last_end = match.end()

    # Capture any remaining content after last item
    if last_end < len(body):
        remaining = body[last_end:].strip()
        if remaining and not ITEM_MARKER_PATTERN.search(remaining):
            raw_content_parts.append(remaining)

    # If no items found, the entire body is raw content
    if not items:
        raw_content = body.strip() if body.strip() else None
    else:
        raw_content = "\n".join(raw_content_parts).strip() or None

    # Strip structural headers from raw_content since serialize_note will regenerate them
    if raw_content:
        raw_content = _strip_structural_headers(raw_content, frontmatter.title)
        if not raw_content:
            raw_content = None

    return Note(
        frontmatter=frontmatter,
        items=items,
        raw_content=raw_content,
    )


def _remove_empty_values(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively remove empty lists and dicts from a dictionary."""
    result: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            cleaned = _remove_empty_values(value)  # type: ignore[reportUnknownArgumentType]
            if cleaned:  # Only include non-empty dicts
                result[key] = cleaned
        elif isinstance(value, list):
            if value:  # Only include non-empty lists
                result[key] = value
        else:
            result[key] = value
    return result  # type: ignore[reportUnknownVariableType]


def serialize_note(note: Note) -> str:
    """Serialize a Note object back to markdown format."""
    # Build frontmatter using Pydantic's model_dump
    frontmatter_data = note.frontmatter.model_dump(mode="json")

    # Remove empty fields for cleaner YAML output
    frontmatter_data = _remove_empty_values(frontmatter_data)

    frontmatter_yaml = yaml.dump(
        frontmatter_data,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )

    # Build markdown
    lines = ["---", frontmatter_yaml.rstrip(), "---", ""]

    # Add title as heading
    lines.append(f"# {note.frontmatter.title}")
    lines.append("")

    # Add raw content if present
    if note.raw_content:
        lines.append(note.raw_content)
        lines.append("")

    # Add items section
    if note.items:
        lines.append("## Items")
        lines.append("")

        for item in note.items:
            # Build metadata string
            metadata_parts = [
                f"source:{item.source.value}",
                f"status:{item.status.value}",
            ]
            if item.enforcement is not None:
                metadata_parts.append(f"enforcement:{item.enforcement.value}")

            metadata_str = " ".join(metadata_parts)
            lines.append(f"<!-- @item {metadata_str} -->")
            lines.append(item.content)
            lines.append("")

    return "\n".join(lines)
