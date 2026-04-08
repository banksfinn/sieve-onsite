"""
Dev MCP Server for fullstack-base development tools.

Provides MCP tools for common development tasks:
- Sync OpenAPI types to frontend
- Create/apply database migrations
- Git add and commit
- Python package management (uv)
- Code quality (ruff, pyright)
- Documentation vault tools (docs/ Obsidian vault)
"""

import shlex
import subprocess
from pathlib import Path

from fastmcp import FastMCP
from pydantic import BaseModel

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
# Documentation Vault Tools (docs/ Obsidian vault)
# =============================================================================

VAULT_ROOT = PROJECT_ROOT / "docs"

# Map short area names to the vault directories and notes most relevant to each
VAULT_AREA_MAP: dict[str, list[str]] = {
    "backend": [
        "Architecture/Backend Architecture.md",
        "Decisions/Async-First Backend.md",
        "Decisions/Editable Library Installs.md",
        "Decisions/Blueprint Pattern.md",
    ],
    "frontend": [
        "Architecture/Frontend Architecture.md",
        "Frontend/Provider Stack.md",
        "Frontend/State Management.md",
        "Frontend/Component Library.md",
        "Decisions/Redux Plus React Query.md",
    ],
    "auth": [
        "Decisions/Cookie-Based JWT Auth.md",
        "Frontend/Auth Flow.md",
        "API/Authentication Routes.md",
        "Clients/GoogleOAuthClient.md",
    ],
    "database": [
        "Clients/DatabaseClient.md",
        "Clients/BaseEntityStore.md",
        "Models/Data Model Overview.md",
        "Models/BaseEntity.md",
        "Decisions/Blueprint Pattern.md",
    ],
    "api": [
        "API/API Overview.md",
        "API/Authentication Routes.md",
        "API/User Routes.md",
        "Decisions/OpenAPI Type Generation.md",
    ],
    "infrastructure": [
        "Architecture/Infrastructure.md",
    ],
    "product": [
        "Product Notes.md",
        "Project Requirements.md",
    ],
}


class VaultNote(BaseModel):
    """A note from the documentation vault."""

    path: str
    title: str
    content: str


class VaultSearchResult(BaseModel):
    """A search match within a vault note."""

    path: str
    title: str
    matching_lines: list[str]


@mcp.tool()
def get_vault_index() -> str:
    """
    Get the documentation vault index (Map of Content).

    Returns the full Index.md which links to all vault notes.
    Read this first to understand what documentation is available.
    """
    index_path = VAULT_ROOT / "Index.md"
    if not index_path.exists():
        return "Vault index not found at docs/Index.md"
    return index_path.read_text()


@mcp.tool()
def get_vault_note(name: str) -> VaultNote | str:
    """
    Read a specific vault note by name.

    Searches for the note across all vault subdirectories.
    You can pass just the title (e.g., 'Cookie-Based JWT Auth')
    or the full relative path (e.g., 'Decisions/Cookie-Based JWT Auth.md').

    Args:
        name: Note title or relative path within docs/
    """
    # Try as direct path first
    if not name.endswith(".md"):
        name_with_ext = name + ".md"
    else:
        name_with_ext = name

    direct = VAULT_ROOT / name_with_ext
    if direct.exists():
        content = direct.read_text()
        title = content.split("\n", 1)[0].lstrip("# ").strip() if content else name
        return VaultNote(path=str(direct.relative_to(VAULT_ROOT)), title=title, content=content)

    # Search all subdirectories for the filename
    target_filename = Path(name_with_ext).name
    for md_file in VAULT_ROOT.rglob("*.md"):
        if md_file.name == target_filename:
            content = md_file.read_text()
            title = content.split("\n", 1)[0].lstrip("# ").strip() if content else name
            return VaultNote(path=str(md_file.relative_to(VAULT_ROOT)), title=title, content=content)

    return f"Note '{name}' not found in docs/"


@mcp.tool()
def search_vault(query: str) -> list[VaultSearchResult]:
    """
    Search the documentation vault for a term.

    Searches note titles and content across all vault notes.
    Returns matching notes with the lines that contain the query.

    Args:
        query: Text to search for (case-insensitive)
    """
    query_lower = query.lower()
    results: list[VaultSearchResult] = []

    for md_file in VAULT_ROOT.rglob("*.md"):
        content = md_file.read_text()
        title = content.split("\n", 1)[0].lstrip("# ").strip() if content else md_file.stem

        matching_lines: list[str] = []
        for line in content.splitlines():
            if query_lower in line.lower():
                matching_lines.append(line.strip())

        if matching_lines:
            results.append(
                VaultSearchResult(
                    path=str(md_file.relative_to(VAULT_ROOT)),
                    title=title,
                    matching_lines=matching_lines[:10],
                )
            )

    return results


@mcp.tool()
def get_product_notes() -> str:
    """
    Get the product notes with business rules and customer constraints.

    Returns docs/Product Notes.md which contains rules from product
    conversations that affect implementation decisions. Check this
    before making any product-facing changes.
    """
    notes_path = VAULT_ROOT / "Product Notes.md"
    if not notes_path.exists():
        return "Product Notes not found at docs/Product Notes.md"
    return notes_path.read_text()


@mcp.tool()
def get_vault_area(area: str) -> list[VaultNote] | str:
    """
    Get all vault notes relevant to a specific area of the codebase.

    Returns the full content of each note in the area. Available areas:
    backend, frontend, auth, database, api, infrastructure, product.

    Args:
        area: Area name (backend, frontend, auth, database, api, infrastructure, product)
    """
    area_lower = area.lower()
    if area_lower not in VAULT_AREA_MAP:
        available = ", ".join(sorted(VAULT_AREA_MAP.keys()))
        return f"Unknown area '{area}'. Available: {available}"

    notes: list[VaultNote] = []
    for rel_path in VAULT_AREA_MAP[area_lower]:
        full_path = VAULT_ROOT / rel_path
        if full_path.exists():
            content = full_path.read_text()
            title = content.split("\n", 1)[0].lstrip("# ").strip() if content else rel_path
            notes.append(VaultNote(path=rel_path, title=title, content=content))

    return notes


@mcp.tool()
def list_design_decisions() -> list[VaultNote]:
    """
    List all design decision notes with their summaries.

    Returns the title and first paragraph of each note in
    docs/Decisions/ to give a quick overview of all architectural
    decisions and their rationale.
    """
    decisions_dir = VAULT_ROOT / "Decisions"
    if not decisions_dir.exists():
        return []

    notes: list[VaultNote] = []
    for md_file in sorted(decisions_dir.glob("*.md")):
        content = md_file.read_text()
        lines = content.splitlines()
        title = lines[0].lstrip("# ").strip() if lines else md_file.stem

        # Extract the first paragraph after the title as summary
        summary_lines: list[str] = []
        in_summary = False
        for line in lines[1:]:
            stripped = line.strip()
            if not stripped and not in_summary:
                continue
            if stripped.startswith("#"):
                if in_summary:
                    break
                in_summary = True
                continue
            if in_summary:
                if not stripped:
                    break
                summary_lines.append(stripped)

        summary = " ".join(summary_lines) if summary_lines else ""
        notes.append(VaultNote(path=str(md_file.relative_to(VAULT_ROOT)), title=title, content=summary))

    return notes


if __name__ == "__main__":
    # Use stateless_http=True to avoid session issues when server reloads
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8100, stateless_http=True)
