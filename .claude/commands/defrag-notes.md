# Defrag and Reorganize AI Notes

Analyze and clean up the `.ai/notes/` documentation system.

## Instructions

1. **Read all notes**: Use `search_notes()` to get all notes, then read each one fully with `get_note(note_id)`.

2. **Identify issues**:
   - Duplicate or overlapping rules across different notes
   - Rules that would fit better in a different note
   - Notes with unclear or overly broad scope
   - Items with inconsistent enforcement levels for similar rules
   - Structural issues (missing `## Items` headers, malformed markers)

3. **Propose changes**: Before making any changes, present a summary:
   - List of duplicates found and how you'd consolidate them
   - Suggested note reorganization (if any)
   - Items to move between notes
   - Any notes to merge or split

4. **Ask for approval**: Wait for user confirmation before proceeding.

5. **Execute changes**:
   - Use `update_item()` to modify items
   - Rewrite note files directly if structural fixes are needed
   - Ensure all notes have clean formatting:
     - YAML frontmatter
     - `# Title` heading
     - `## Items` section header
     - Items with proper `<!-- @item ... -->` markers
   - Rebuild the index with `rebuild_notes_index()`

6. **Report results**: Summarize what was changed.

## Notes Location
All notes are in `.ai/notes/*.md`
