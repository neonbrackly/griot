# CLAUDE.md - Quick Reference for Claude Code Agents

> **Read this file when starting any session on Griot.**

---

## 🎯 Quick Start

1. **Identify your agent role** (see table below)
2. **Read** `AGENTS.md` for full context
3. **Check** `status/board.md` for current tasks
4. **Read** your spec file in `specs/`
5. **Work only** in your owned directories
6. **Update status** when done

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

### Starting a Task

```
1. Check status/board.md for your tasks
2. Verify dependencies are complete
3. If blocked → create status/requests/REQ-NNN.md
4. Move task to "In Progress"
5. Create branch: feat/{component}-{feature}
6. Implement
7. Update spec status to 'complete'
8. Move task to "Ready for Review"
```

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

- [ ] Code in your owned directories only
- [ ] Spec updated before/after implementing
- [ ] Status board updated
- [ ] Tests pass, coverage met
- [ ] Types check (pyright --strict for core)
