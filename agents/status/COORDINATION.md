# Agent Coordination Protocol

> **Problem**: Multiple agents updating `board.md` simultaneously causes merge conflicts and lost updates.
>
> **Solution**: All agents work on master + agent-specific status files + orchestrator consolidation.

---

## The Golden Rules

1. **ALL agents work on `master` branch** (no agent-specific branches!)
2. **NEVER edit `board.md` directly** (except orchestrator)
3. **ALWAYS commit your work before ending a session**
4. **Write status updates to your agent file**

---

## Why No Branches?

All agents share the same working directory on one machine. When one agent switches branches, it affects all other agents. Since each agent owns different directories, conflicts are rare when working on master.

**Benefits of master-only workflow:**
- No branch confusion when multiple agents are active
- Immediate visibility of all work
- Simpler coordination
- Ownership model prevents file conflicts

---

## Directory Structure

```
agents/status/
├── board.md              # Master board (orchestrator-only edits)
├── COORDINATION.md       # This file
├── requests/             # Interface requests between agents
│   └── REQ-NNN.md
└── updates/              # Agent-specific status updates
    ├── core.md           # Core agent updates
    ├── cli.md            # CLI agent updates
    ├── enforce.md        # Enforce agent updates
    ├── registry.md       # Registry agent updates
    ├── hub.md            # Hub agent updates
    └── quality.md        # Quality agent updates
```

---

## Agent Workflow

### Starting a Session

```bash
# 1. Ensure you're on master (CRITICAL!)
git checkout master
git status   # Should show "On branch master"

# 2. Check board.md for your assigned tasks
# 3. Read your agent's update file for context
# 4. Start working on tasks in YOUR owned directories only
```

> **Do NOT create branches!** All agents work on master. The ownership model prevents conflicts.

### During Work

```bash
# Commit frequently with descriptive messages
git add <your-files>
git commit -m "feat(<component>): <description>"
```

### Ending a Session

```bash
# 1. Update YOUR agent status file (not board.md!)
# 2. Commit everything together on master
git add agents/status/updates/<your-agent>.md
git add <your-code-files>
git commit -m "feat(<component>): <task-description>

Tasks completed: T-XXX, T-YYY
Status update in agents/status/updates/<agent>.md"

# 3. (Optional) Push to remote if it exists
# git push origin master
```

---

## Agent Status File Format

Each agent maintains `agents/status/updates/<agent>.md`:

```markdown
# <Agent> Status Updates

## Session: YYYY-MM-DD HH:MM

### Tasks Completed
- T-XXX: Description of what was done
- T-YYY: Description of what was done

### Tasks Started (In Progress)
- T-ZZZ: Current status, what's remaining

### Blockers Encountered
- Blocked on T-AAA from <other-agent>: Need <description>

### Notes
- Any relevant context for orchestrator

### Files Changed
- path/to/file1.py
- path/to/file2.py
```

---

## Orchestrator Workflow

The orchestrator is the ONLY agent that edits `board.md`:

### Review Cycle

```bash
# 1. Ensure on master
git checkout master

# 2. Read all agent update files
cat agents/status/updates/*.md

# 3. Consolidate into board.md
# - Update task statuses
# - Move completed items
# - Update progress percentages
# - Update blocked/unblocked lists

# 4. Clear processed updates (optional, or archive)

# 5. Commit the consolidated board on master
git add agents/status/board.md
git commit -m "chore(orchestrator): Review cycle - consolidated agent updates"
```

---

## Handling Conflicts

### If you encounter a merge conflict:

1. **Don't force push** - you'll lose others' work
2. **Pull and merge** - resolve conflicts carefully
3. **For board.md conflicts** - defer to orchestrator
4. **For code conflicts** - resolve based on latest intent

### Conflict Resolution Priority

1. Code changes from the agent who owns that component
2. Board.md changes from orchestrator
3. Status update files - merge both versions

---

## Communication Between Agents

### Requesting Something from Another Agent

Create `agents/status/requests/REQ-NNN.md`:

```markdown
# REQ-NNN: <Title>

| From | To | Status | Created |
|------|-----|--------|---------|
| <your-agent> | <target-agent> | pending | YYYY-MM-DD |

## Request
<What you need>

## Proposed Interface
```python
def needed_method() -> ReturnType:
    ...
```

## Priority
high | medium | low

## Blocking
T-XXX, T-YYY (tasks blocked by this)
```

### Responding to Requests

Update the request file:

```markdown
## Response (YYYY-MM-DD)
**Decision**: accepted | rejected | needs-clarification
**Implemented in**: T-ZZZ
**Notes**: ...
```

---

## Quick Reference

| Action | Who | Where |
|--------|-----|-------|
| Edit board.md | orchestrator only | `agents/status/board.md` |
| Report task completion | any agent | `agents/status/updates/<agent>.md` |
| Request interface | any agent | `agents/status/requests/REQ-NNN.md` |
| Review/approve work | orchestrator | `agents/status/board.md` |

---

## Example Session (CLI Agent)

```bash
# Start - ensure on master
git checkout master
git status   # Verify "On branch master"

# Read board.md - see T-031 assigned to me

# Work on T-031...
# ... coding in griot-cli/ (my owned directory) ...

# Commit code on master
git add griot-cli/src/griot_cli/commands/validate.py
git commit -m "feat(cli): Implement griot validate command (T-031)"

# Update my status file
cat >> agents/status/updates/cli.md << 'EOF'

## Session: 2026-01-10 14:30

### Tasks Completed
- T-031: Implemented `griot validate` command with full SDK integration

### Files Changed
- griot-cli/src/griot_cli/commands/validate.py
EOF

# Commit status update
git add agents/status/updates/cli.md
git commit -m "chore(cli): Status update for T-031"

# Done! (push only if remote exists)
```

---

## Benefits

1. **No branch confusion** - All agents on master, no switching issues
2. **No overwrites** - Each agent owns different directories
3. **Clear audit trail** - Status updates are versioned in agent files
4. **Async coordination** - Agents don't need to wait for each other
5. **Single source of truth** - board.md is authoritative, managed by orchestrator
6. **Simple workflow** - Just commit to master, no merge/rebase complexity
