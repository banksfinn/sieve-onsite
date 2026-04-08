"""
Dev MCP Server for fullstack-base development tools.

Provides MCP tools for common development tasks:
- Sync OpenAPI types to frontend
- Create/apply database migrations
- Git add and commit
- Python package management (uv)
- Code quality (ruff, pyright)
- LLM notes documentation system
"""

import shlex
import subprocess
from pathlib import Path

from fastmcp import FastMCP
from mcp_server.notes.models import (
    ItemEnforcement,
    ItemSource,
    ItemStatus,
    Note,
    NoteFrontmatter,
    NoteItem,
    NoteScope,
)
from mcp_server.notes import index as notes_index
from mcp_server.notes import matcher as notes_matcher
from mcp_server.notes import storage as notes_storage
from pydantic import BaseModel, Field

# Project root (where Makefile lives)
# Path: tools/mcp_server/mcp_server/server.py -> 5 levels up to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
DOCKER_COMPOSE_FILE = PROJECT_ROOT / "infra" / "docker" / "local" / "docker-compose.yml"


# =============================================================================
# Response Models
# =============================================================================


class CommandResult(BaseModel):
    """Result from running a shell command."""

    success: bool
    output: str
    error: str | None = None


class EnforcementItem(BaseModel):
    """An item that may block or warn about a proposed change."""

    note_id: str
    note_title: str
    item_index: int
    content: str
    enforcement: str
    source: str


class EnforcementCheckResult(BaseModel):
    """Result from checking enforcement rules."""

    can_proceed: bool
    blocking_items: list[EnforcementItem] = Field(default_factory=list[EnforcementItem])
    warnings: list[EnforcementItem] = Field(default_factory=list[EnforcementItem])


# Create FastMCP server
mcp = FastMCP(name="Fullstack Dev Tools")


def run_command(cmd: list[str], cwd: Path | None = None) -> CommandResult:
    """Run a shell command and return the result.

    Uses a login shell (-l) to ensure the user's shell profile is sourced,
    which is necessary for tools like nvm/fnm/volta to set up the correct
    Node.js version.
    """
    try:
        # Join command and run through login shell to inherit user's environment
        cmd_str = " ".join(shlex.quote(c) for c in cmd)
        result = subprocess.run(
            ["bash", "-l", "-c", cmd_str],
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        return CommandResult(
            success=result.returncode == 0,
            output=result.stdout,
            error=result.stderr if result.returncode != 0 else None,
        )
    except subprocess.TimeoutExpired:
        return CommandResult(
            success=False,
            output="",
            error="Command timed out after 5 minutes",
        )
    except Exception as e:
        return CommandResult(
            success=False,
            output="",
            error=str(e),
        )


def run_make(target: str) -> CommandResult:
    """Run a Makefile target."""
    return run_command(["make", target])


# =============================================================================
# Development Tools
# =============================================================================


@mcp.tool()
def sync_openapi() -> CommandResult:
    """
    Sync OpenAPI spec from backend to frontend.

    Starts the gateway container, waits for it to be healthy,
    fetches the OpenAPI spec, and generates TypeScript types.
    """
    return run_make("sync_openapi")


@mcp.tool()
def create_migration(message: str) -> CommandResult:
    """
    Create a new Alembic database migration.

    Generates a new migration file based on model changes.
    The message should describe what the migration does.

    Args:
        message: Description of the migration (e.g., 'add user table')
    """
    cmd = [
        "docker",
        "compose",
        "-f",
        str(DOCKER_COMPOSE_FILE),
        "run",
        "migration",
        "alembic",
        "-c",
        "/app/alembic.ini",
        "revision",
        "--autogenerate",
        "-m",
        message,
    ]
    return run_command(cmd)


@mcp.tool()
def apply_migration() -> CommandResult:
    """
    Apply pending database migrations.

    Runs all pending Alembic migrations to bring the database
    schema up to date with the current models.
    """
    return run_make("db_apply_migration")


@mcp.tool()
def git_commit(message: str) -> CommandResult:
    """
    Stage all changes and create a git commit.

    Runs `git add -A` to stage all changes, then creates a commit
    with the provided message.

    Args:
        message: Commit message describing the changes
    """
    # First, stage all changes
    add_result = run_command(["git", "add", "-A"])
    if not add_result.success:
        return add_result

    # Then commit
    commit_result = run_command(["git", "commit", "-m", message])
    return CommandResult(
        success=commit_result.success,
        output=f"Staged files:\n{add_result.output}\n\nCommit:\n{commit_result.output}",
        error=commit_result.error,
    )


# =============================================================================
# Package Management Tools (UV)
# =============================================================================


@mcp.tool()
def uv_lock() -> CommandResult:
    """
    Update the uv.lock file.

    Resolves dependencies and updates the lock file without
    installing packages. Use this after modifying pyproject.toml.
    """
    return run_command(["uv", "lock"], cwd=BACKEND_ROOT)


@mcp.tool()
def uv_sync() -> CommandResult:
    """
    Sync installed packages with the lock file.

    Installs, updates, or removes packages to match the lock file.
    This is the standard way to ensure your environment matches
    the project's dependencies.
    """
    return run_command(["uv", "sync"], cwd=BACKEND_ROOT)


@mcp.tool()
def uv_add(package: str, dev: bool = False, group: str | None = None) -> CommandResult:
    """
    Add a new Python package dependency.

    Adds the package to pyproject.toml, updates the lock file,
    and installs it. Use --dev for development dependencies or
    specify a group like 'test' or 'lint'.

    Args:
        package: Package to add (e.g., 'requests', 'requests>=2.28.0')
        dev: Add as a dev dependency
        group: Dependency group to add to (e.g., 'test', 'lint')
    """
    cmd = ["uv", "add", package]

    if dev:
        cmd.append("--dev")
    elif group:
        cmd.extend(["--group", group])

    return run_command(cmd, cwd=BACKEND_ROOT)


# =============================================================================
# Code Quality Tools
# =============================================================================


class LintResult(BaseModel):
    """Result from running linters."""

    success: bool
    ruff_output: str | None = None
    ruff_error: str | None = None
    pyright_output: str | None = None
    pyright_error: str | None = None


@mcp.tool()
def run_linters(
    paths: list[str] | None = None,
    run_ruff: bool = True,
    run_pyright: bool = True,
) -> LintResult:
    """
    Run ruff and/or pyright linters on the backend code.

    By default, runs both linters on the entire backend. You can opt out
    of either linter or specify specific paths to check.

    Args:
        paths: Specific paths to lint (relative to backend/). Defaults to entire backend.
        run_ruff: Whether to run ruff (default: True)
        run_pyright: Whether to run pyright (default: True)
    """
    if not run_ruff and not run_pyright:
        return LintResult(
            success=False,
            ruff_error="At least one linter must be enabled",
        )

    # Default to checking everything
    target_paths = paths if paths else ["."]

    ruff_output = None
    ruff_error = None
    pyright_output = None
    pyright_error = None
    all_success = True

    if run_ruff:
        ruff_cmd = ["uv", "run", "ruff", "check", *target_paths]
        ruff_result = run_command(ruff_cmd, cwd=BACKEND_ROOT)
        ruff_output = ruff_result.output
        ruff_error = ruff_result.error
        if not ruff_result.success:
            all_success = False

    if run_pyright:
        pyright_cmd = ["uv", "run", "pyright", *target_paths]
        pyright_result = run_command(pyright_cmd, cwd=BACKEND_ROOT)
        pyright_output = pyright_result.output
        pyright_error = pyright_result.error
        if not pyright_result.success:
            all_success = False

    return LintResult(
        success=all_success,
        ruff_output=ruff_output,
        ruff_error=ruff_error,
        pyright_output=pyright_output,
        pyright_error=pyright_error,
    )


# =============================================================================
# Environment Setup Tools
# =============================================================================


@mcp.tool()
def generate_env() -> CommandResult:
    """
    Generate environment files from examples.

    Copies .env.example files to .env for both backend (Docker) and
    frontend (env.js). Run this after cloning the repo or when
    environment templates are updated.
    """
    return run_make("env")


# =============================================================================
# Notes Documentation Tools (Query)
# =============================================================================


@mcp.tool()
def get_notes_for_path(file_path: str) -> list[Note]:
    """
    Get notes whose scope matches the given file path.

    Returns full note content including all items for notes
    that have glob patterns matching the specified file.
    Use this before working on a file to see relevant guidelines.

    Args:
        file_path: File path to match against note scopes
    """
    notes_storage.ensure_notes_directory()
    index = notes_index.get_or_rebuild_index()
    matching_ids = notes_matcher.get_notes_for_path(file_path, index)

    notes: list[Note] = []
    for note_id in matching_ids:
        note = notes_storage.read_note(note_id)
        if note:
            notes.append(note)

    return notes


@mcp.tool()
def search_notes(
    query: str | None = None,
    tags: str | None = None,
    source: str | None = None,
    include_deprecated: bool = False,
) -> list[Note]:
    """
    Search notes by text, tags, or source.

    Returns matching notes with their items. Use this to find
    relevant documentation across the codebase.

    Args:
        query: Text to search for in note content
        tags: Comma-separated tags to filter by
        source: Filter by item source (user/llm)
        include_deprecated: Include deprecated items
    """
    notes_storage.ensure_notes_directory()
    index = notes_index.get_or_rebuild_index()

    # Start with all notes
    note_ids = [n.id for n in index.notes]

    # Filter by tags if specified
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        tag_matching = notes_matcher.get_notes_for_tags(tag_list, index)
        note_ids = [nid for nid in note_ids if nid in tag_matching]

    # Load and filter notes
    results: list[Note] = []
    for note_id in note_ids:
        note = notes_storage.read_note(note_id)
        if not note:
            continue

        # Filter items by source if specified
        if source:
            filtered_items = [item for item in note.items if item.source.value == source]
            note = Note(
                frontmatter=note.frontmatter,
                items=filtered_items,
                raw_content=note.raw_content,
            )

        # Filter out deprecated if not included
        if not include_deprecated:
            filtered_items = [item for item in note.items if item.status != ItemStatus.deprecated]
            note = Note(
                frontmatter=note.frontmatter,
                items=filtered_items,
                raw_content=note.raw_content,
            )

        # Text search if query specified
        if query:
            query_lower = query.lower()
            if query_lower not in note.frontmatter.title.lower() and query_lower not in note.frontmatter.purpose.lower():
                # Check if any items match
                matching_items = [item for item in note.items if query_lower in item.content.lower()]
                if not matching_items:
                    continue
                note = Note(
                    frontmatter=note.frontmatter,
                    items=matching_items,
                    raw_content=note.raw_content,
                )

        results.append(note)

    return results


@mcp.tool()
def get_note(note_id: str) -> Note | None:
    """
    Get the full content of a specific note.

    Returns the complete note including frontmatter and all items.

    Args:
        note_id: The ID of the note to retrieve
    """
    return notes_storage.read_note(note_id)


@mcp.tool()
def check_enforcement(file_path: str, proposed_change: str) -> EnforcementCheckResult:
    """
    Check if locked/strict items would block a proposed change.

    Analyzes applicable notes and returns any blocking rules
    or warnings that should be considered before making changes.

    Args:
        file_path: File path being modified
        proposed_change: Description of the proposed change
    """
    notes_storage.ensure_notes_directory()
    index = notes_index.get_or_rebuild_index()
    matching_ids = notes_matcher.get_notes_for_path(file_path, index)

    blocking_items: list[EnforcementItem] = []
    warnings: list[EnforcementItem] = []

    for note_id in matching_ids:
        note = notes_storage.read_note(note_id)
        if not note:
            continue

        for i, item in enumerate(note.items):
            if item.status == ItemStatus.deprecated:
                continue

            enforcement = item.effective_enforcement

            item_info = EnforcementItem(
                note_id=note_id,
                note_title=note.frontmatter.title,
                item_index=i,
                content=item.content,
                enforcement=enforcement.value,
                source=item.source.value,
            )

            if enforcement == ItemEnforcement.locked:
                blocking_items.append(item_info)
            elif enforcement == ItemEnforcement.strict:
                warnings.append(item_info)

    return EnforcementCheckResult(
        can_proceed=len(blocking_items) == 0,
        blocking_items=blocking_items,
        warnings=warnings,
    )


# =============================================================================
# Notes Documentation Tools (Mutation)
# =============================================================================


@mcp.tool()
def create_note(
    id: str,
    title: str,
    purpose: str,
    paths: str,
    tags: str | None = None,
) -> CommandResult:
    """
    Create a new note file.

    Creates a markdown file in .ai/notes/ with the specified
    frontmatter. Items can be added afterward with add_item.

    Args:
        id: Unique identifier for the note (e.g., 'pydantic-usage')
        title: Human-readable title
        purpose: Description of what this note covers
        paths: Comma-separated glob patterns for file paths this applies to
        tags: Optional comma-separated tags for categorization
    """
    notes_storage.ensure_notes_directory()

    # Check if note already exists
    if notes_storage.note_exists(id):
        return CommandResult(
            success=False,
            output="",
            error=f"Note '{id}' already exists",
        )

    # Parse paths and tags
    path_list = [p.strip() for p in paths.split(",") if p.strip()]
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    # Create note
    note = Note(
        frontmatter=NoteFrontmatter(
            id=id,
            title=title,
            purpose=purpose,
            scope=NoteScope(paths=path_list, tags=tag_list),
            related=[],
        ),
        items=[],
    )

    notes_storage.write_note(note)
    notes_index.rebuild_index()

    return CommandResult(
        success=True,
        output=f"Created note '{id}' at .ai/notes/{id}.md",
    )


@mcp.tool()
def add_item(
    note_id: str,
    content: str,
    source: str = "llm",
    status: str = "proposed",
    enforcement: str | None = None,
) -> CommandResult:
    """
    Add a new item to an existing note.

    Default source is 'llm' and default status is 'proposed'.
    Enforcement defaults based on source/status if not specified.

    Args:
        note_id: ID of the note to add to
        content: The item content/guideline
        source: Source: 'user' or 'llm'
        status: Status: 'active', 'proposed', or 'deprecated'
        enforcement: Enforcement level: 'locked', 'strict', 'recommended', or 'flexible'
    """
    note = notes_storage.read_note(note_id)
    if not note:
        return CommandResult(
            success=False,
            output="",
            error=f"Note '{note_id}' not found",
        )

    # Create item
    item = NoteItem(
        content=content,
        source=ItemSource(source),
        status=ItemStatus(status),
        enforcement=ItemEnforcement(enforcement) if enforcement else None,
    )

    note.items.append(item)
    notes_storage.write_note(note)
    notes_index.rebuild_index()

    item_index = len(note.items) - 1
    return CommandResult(
        success=True,
        output=f"Added item at index {item_index} to note '{note_id}'",
    )


@mcp.tool()
def update_item(
    note_id: str,
    item_index: int,
    content: str | None = None,
    status: str | None = None,
    enforcement: str | None = None,
) -> CommandResult:
    """
    Update an existing item in a note.

    Can update content, status, and/or enforcement.

    Args:
        note_id: ID of the note containing the item
        item_index: Index of the item to update
        content: Updated content
        status: New status: 'active', 'proposed', or 'deprecated'
        enforcement: New enforcement: 'locked', 'strict', 'recommended', or 'flexible'
    """
    note = notes_storage.read_note(note_id)
    if not note:
        return CommandResult(
            success=False,
            output="",
            error=f"Note '{note_id}' not found",
        )

    if item_index < 0 or item_index >= len(note.items):
        return CommandResult(
            success=False,
            output="",
            error=f"Item index {item_index} out of range (note has {len(note.items)} items)",
        )

    item = note.items[item_index]

    # Update fields
    if content is not None:
        item.content = content
    if status is not None:
        item.status = ItemStatus(status)
    if enforcement is not None:
        item.enforcement = ItemEnforcement(enforcement)

    notes_storage.write_note(note)
    notes_index.rebuild_index()

    return CommandResult(
        success=True,
        output=f"Updated item {item_index} in note '{note_id}'",
    )


@mcp.tool()
def rebuild_notes_index() -> CommandResult:
    """
    Rebuild the notes index.

    Scans all note files and regenerates _index.yaml for
    fast lookups. Run this after manually editing note files.
    """
    try:
        notes_storage.ensure_notes_directory()
        new_index = notes_index.rebuild_index()
        return CommandResult(
            success=True,
            output=f"Index rebuilt with {len(new_index.notes)} notes",
        )
    except Exception as e:
        return CommandResult(
            success=False,
            output="",
            error=str(e),
        )


if __name__ == "__main__":
    # Use stateless_http=True to avoid session issues when server reloads
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8100, stateless_http=True)
