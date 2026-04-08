"""Pydantic models for the notes documentation system."""

from enum import Enum

from pydantic import BaseModel, Field, computed_field


class ItemSource(str, Enum):
    """Source of the item - user-created or LLM-suggested."""

    user = "user"
    llm = "llm"


class ItemStatus(str, Enum):
    """Current status of the item."""

    active = "active"
    proposed = "proposed"
    deprecated = "deprecated"


class ItemEnforcement(str, Enum):
    """How strictly the item should be enforced."""

    locked = "locked"  # Cannot be modified by LLM
    strict = "strict"  # Must be followed
    recommended = "recommended"  # Should be followed
    flexible = "flexible"  # Optional guidance


class NoteItem(BaseModel):
    """An individual rule/guideline within a note."""

    content: str
    source: ItemSource = ItemSource.llm
    status: ItemStatus = ItemStatus.proposed
    enforcement: ItemEnforcement | None = None  # None means use defaults

    @computed_field
    @property
    def effective_enforcement(self) -> ItemEnforcement:
        """Calculate effective enforcement based on source/status defaults."""
        if self.enforcement is not None:
            return self.enforcement

        # Default logic based on source and status
        if self.status == ItemStatus.proposed:
            return ItemEnforcement.flexible
        if self.source == ItemSource.user and self.status == ItemStatus.active:
            return ItemEnforcement.strict
        if self.source == ItemSource.llm and self.status == ItemStatus.active:
            return ItemEnforcement.recommended

        return ItemEnforcement.flexible


class NoteScope(BaseModel):
    """Defines which files/contexts a note applies to."""

    paths: list[str] = Field(default_factory=list)  # Glob patterns
    tags: list[str] = Field(default_factory=list)


class NoteFrontmatter(BaseModel):
    """YAML frontmatter for a note file."""

    id: str
    title: str
    purpose: str
    scope: NoteScope = Field(default_factory=NoteScope)
    related: list[str] = Field(default_factory=list)


class Note(BaseModel):
    """A complete note with frontmatter and items."""

    frontmatter: NoteFrontmatter
    items: list[NoteItem] = Field(default_factory=list[NoteItem])
    raw_content: str | None = None  # Original markdown content (non-item sections)


class IndexedItem(BaseModel):
    """Item summary for index."""

    index: int
    source: ItemSource
    status: ItemStatus
    enforcement: ItemEnforcement
    preview: str  # First ~100 chars of content


class IndexedNote(BaseModel):
    """Note summary for index."""

    id: str
    title: str
    purpose: str
    paths: list[str]
    tags: list[str]
    items: list[IndexedItem] = Field(default_factory=list[IndexedItem])


class NoteIndex(BaseModel):
    """Index for fast lookups across all notes."""

    notes: list[IndexedNote] = Field(default_factory=list[IndexedNote])
