# File Reading Order

## Phase 1: Core Structure (Essential for understanding the system)

### 1. Entry Points and Configuration
- `main.py` - Entry point, shows overall flow
- `config.py` - Global configuration (token thresholds, tool mappings)
- `olmx_client.py` - LLM client implementation

### 2. Agent System
- `agents/__init__.py` - Agent registry
- `agents/base.py` - Base agent class
- `agents/plan_agent.py` - Planning agent
- `agents/explore_agent.py` - Exploration agent
- `agents/general_agent.py` - General execution agent
- `agents/verification_agent.py` - Verification agent
- `agents/coordinator_agent.py` - Sub-agent coordinator

### 3. Core Runtime
- `core/session_memory.py` - Singleton memory (critical for cross-agent state)
- `core/executor.py` - Task execution logic
- `core/compact_system.py` - Context compression

### 4. Tools
- `tools/__init__.py` - Tool registration
- `tools/bash_tool.py` - Bash command execution
- `tools/file_tool.py` - File operations abstraction

## Phase 2: cc-mini Implementation (Full Claude Code Harness)

### 1. Entry Points
- `cc-mini/src/core/main.py` - REPL entry point
- `cc-mini/src/core/engine.py` - Core streaming loop
- `cc-mini/src/core/config.py` - Configuration loading
- `cc-mini/src/core/llm.py` - LLM client wrapper
- `cc-mini/src/core/context.py` - System prompt builder

### 2. Core Engine
- `cc-mini/src/core/commands.py` - Slash command system
- `cc-mini/src/core/session.py` - Session persistence
- `cc-mini/src/core/compact.py` - Compression logic
- `cc-mini/src/core/coordinator.py` - Coordinator mode
- `cc-mini/src/core/worker_manager.py` - Background workers

### 3. Supporting Modules
- `cc-mini/src/core/permissions.py` - Permission checker
- `cc-mini/src/core/cost_tracker.py` - Token tracking
- `cc-mini/src/core/_keylistener.py` - Keyboard handling
- `cc-mini/src/core/skills.py` - Skill registry

### 4. Buddy System
- `cc-mini/src/core/buddy/` - All buddy companion files in order

## Phase 3: Cross-Reference Files

### 1. Comparison/Migration
- `core/executor.py` vs `cc-mini/src/core/executor.py`
- `core/compact_system.py` vs `cc-mini/src/core/compact.py`
- `core/session_memory.py` vs `cc-mini/src/core/session.py`

## Priority Files (Read These First)

1. **`config.py`** - Understand token limits and tool mappings
2. **`main.py`** - See how agents interact with the executor
3. **`core/session_memory.py`** - Critical singleton for state
4. **`agents/coordinator_agent.py`** - How sub-agents are orchestrated
5. **`cc-mini/src/core/engine.py`** - Core streaming API
6. **`cc-mini/src/core/compact.py`** - How context compression works

## Reading Rules

- Always read parent directories before child files
- Read configuration files before implementation files
- Read base classes before subclasses
- Read files that import from other files first

---

*Generated on 2026-04-06*
