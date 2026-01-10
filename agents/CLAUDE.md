# CLAUDE.md - Quick Reference for Claude Code Agents

> **Read this file when starting any session on Griot.**

---

## 🎯 Quick Start

1. **Ensure you're on master**: `git checkout master`
2. **Identify your agent role** (see table below)
3. **Read** `AGENTS.md` for full context
4. **Check** `status/board.md` for current tasks
5. **Read** your spec file in `specs/`
6. **Work only** in your owned directories
7. **Update YOUR status file** (not board.md!) when done
8. **Commit to master**: `git commit` then optionally push

> **Important**: All agents work on `master` branch. Do NOT create agent-specific branches.

---

## 🤖 Agent Identification

| Working on... | You are | Own | Read |
|---------------|---------|-----|------|
| `griot-core/src/griot_core/*` | **core** | griot-core | `specs/core.yaml` |
| `griot-cli/src/griot_cli/*` | **cli** | griot-cli | `specs/core.yaml`, `specs/cli.yaml` |
| `griot-enforce/src/griot_enforce/*` | **enforce** | griot-enforce | `specs/enforce.yaml` |
| `griot-registry/src/griot_registry/*` | **registry** | griot-registry | `specs/api.yaml` |
| `griot-hub/src/*` | **hub** | griot-hub | `specs/api.yaml`, `specs/hub.yaml` |
| `tests/*`, `.github/*` | **quality** | tests, CI | All specs |
| `specs/*`, `status/*`, `docs/*` | **orchestrator** | coordination | Everything |

---

## ⚖️ Core Rules

### Rule 1: core-First (griot-core)

**All business logic in `griot-core`.** Other packages are wrappers.

```python
# ✅ CLI calls core
result = contract.validate(df)
click.echo(format_result(result))

# ❌ CLI implements logic
for row in df:
    if not valid(row):  # NO!
        errors.append(...)
```

### Rule 2: Stay in Your Lane

Only modify files in your owned directories.

### Rule 3: Interface-First

Update `specs/*.yaml` BEFORE implementing:
```yaml
- name: new_method
  status: planned   # → implementing → complete
```

### Rule 4: Request When Blocked

Need something from another agent? Create `status/requests/REQ-NNN.md`

---

## 📁 Package Structure

```
griot/
├── griot-core/src/griot_core/    # core (owner: core)
│   ├── models.py                 # GriotModel, Field
│   ├── contract.py               # Loading, diffing
│   ├── validation.py             # Validation engine
│   ├── mock.py                   # Mock data
│   └── manifest.py               # AI export
│
├── griot-cli/src/griot_cli/      # CLI (owner: cli)
│   ├── main.py                   # Click app
│   └── commands/                 # Commands
│
├── griot-enforce/src/griot_enforce/  # Runtime (owner: enforce)
│   ├── validator.py
│   ├── airflow/
│   └── dagster/
│
├── griot-registry/src/griot_registry/  # API (owner: registry)
│   ├── server.py
│   ├── api/
│   └── storage/
│
├── griot-hub/src/                # Web UI (owner: hub)
│   ├── app/
│   └── components/
│
├── specs/                        # Interface specs (owner: orchestrator)
├── status/                       # Coordination (owner: orchestrator)
└── prompts/                      # Agent prompts
```

---

## 🔄 Common Workflows

### Starting a Session (IMPORTANT!)

```bash
# ALWAYS start with this
git checkout master   # Ensure you're on master (not a branch)
git status            # Verify clean working directory
```

> **No branches!** All agents work directly on master. The ownership model prevents conflicts.

### Working on a Task

```
1. Check status/board.md for your assigned tasks
2. Verify dependencies are complete
3. If blocked → create status/requests/REQ-NNN.md
4. Implement your task
5. Update spec status to 'complete'
```

### Ending a Session (CRITICAL!)

```bash
# 1. Update YOUR agent status file (NOT board.md!)
#    File: status/updates/<your-agent>.md

# 2. Commit everything together on master
git add <your-code-files>
git add agents/status/updates/<your-agent>.md
git commit -m "feat(<component>): <description>

Tasks completed: T-XXX, T-YYY"

# 3. (Optional) Push if remote exists
# git push origin master
```

> **Stay on master!** Do not create branches. Your owned directories ensure no conflicts with other agents.

### ⚠️ Status Board Rules

| Action | Who Can Do It |
|--------|---------------|
| Edit `board.md` | **orchestrator ONLY** |
| Edit `status/updates/<agent>.md` | That specific agent |
| Create `status/requests/REQ-NNN.md` | Any agent |

**Why?** Multiple agents editing board.md causes merge conflicts and lost updates.

> 📖 Full details: `status/COORDINATION.md`

### Creating Interface Request

```markdown
# status/requests/REQ-NNN.md

| From | To | Status |
|------|-----|--------|
| cli | core | pending |

## Request
Need `contract.foo()` method...

## Proposed Interface
```python
def foo(self) -> Result: ...
```
```

---

## 📋 Spec Files

| File | Owner | Contains |
|------|-------|----------|
| `specs/core.yaml` | core | GriotModel, Field, validation, all core methods |
| `specs/api.yaml` | registry | OpenAPI 3.0 spec for Registry |
| `specs/cli.yaml` | cli | Command definitions |
| `specs/enforce.yaml` | enforce | RuntimeValidator, operators |
| `specs/hub.yaml` | hub | Pages, components |

---

## 🚨 Red Flags - Stop and Ask

- Writing validation logic in CLI → Should be in core
- Importing griot-core in Hub → Should call API
- Modifying files outside your scope
- Implementing without updating spec first

---

## ✅ Success Criteria

- [ ] Working on `master` branch (no agent branches!)
- [ ] Code in your owned directories only
- [ ] Spec updated before/after implementing
- [ ] YOUR status file updated (`status/updates/<agent>.md`)
- [ ] Did NOT edit `board.md` directly (orchestrator only)
- [ ] Tests pass, coverage met
- [ ] Types check (pyright --strict for core)
- [ ] Changes committed to master
