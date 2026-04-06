# TODO - Repository Scan

## Completed
- [x] Repository root identified: `/Users/huguoqing/zzzhu/code/exp/RAG/project1/context_system`
- [x] Directory structure analyzed
- [x] Top-level directories identified
- [x] Entry files identified
- [x] Configuration files identified
- [x] Core runtime files identified
- [x] Module groups identified
- [x] `repo_snapshot.json` created
- [x] `repo_overview.md` created
- [x] `file_manifest.json` created
- [x] `reading_order.md` created
- [x] `module_candidates.json` created
- [x] `manifest.json` created
- [x] `progress.md` created

## Files Created

### In `./code-reading-notes/00_repo_scan/`
- `repo_snapshot.json` - Repository snapshot with structure
- `repo_overview.md` - Human-readable overview
- `file_manifest.json` - Complete file listing with types
- `reading_order.md` - Recommended reading order
- `module_candidates.json` - Module structure for reading skills

### Root
- `manifest.json` - Manifest pointing to 00_repo_scan

## Next Steps

### Recommended: `/project-architecture`
Run `/project-architecture` to generate a comprehensive project architecture map. This will:
- Map package structure
- Identify module dependencies
- Show data flow between components
- Identify interfaces and interactions

### Alternative: `/module-note`
Run `/module-note` on `core/engine.py` or `agents/coordinator_agent.py` for a focused module summary.

### Direct Reading
Based on `reading_order.md`, start reading:
1. `config.py` - Understand configuration
2. `olmx_client.py` - LLM interface
3. `agents/__init__.py` - Agent registry
4. `core/session_memory.py` - Memory management

## Pending Skills

### After understanding the project:
1. **`/project-architecture`** - Full architecture map
2. **`/module-note`** - Module-by-module notes on reading order
3. **`/file-note`** - Individual file notes as needed

## Notes

- The project combines two implementations:
  - `core/` - Simplified agent system (context system)
  - `cc-mini/` - Full Claude Code harness
- Agent types: Plan, Explore, General, Guide, Verification, Statusline, Coordinator
- Key features: context compression, session persistence, sandbox, buddy system
- Configuration drives behavior through `config.py` and `cc-mini/pyproject.toml`
