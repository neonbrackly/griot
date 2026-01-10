# Griot Agent Registry

> **Version:** 2.0.0  
> **Last Updated:** 2025-01-10  
> **Purpose:** Defines all agents, their responsibilities, boundaries, and communication rules

---

## System Overview

Griot uses a multi-agent architecture where specialized Claude Code agents collaborate to build five components. The **Core-First Principle** governs all work: business logic lives exclusively in `griot-core`, with other components as thin wrappers.

```
                         ┌─────────────────┐
                         │   ORCHESTRATOR  │
                         │    (planning)   │
                         └────────┬────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐      ┌───────────────┐        ┌───────────────┐
│   GRIOT-CORE    │◄─────│   GRIOT-CLI   │        │    QUALITY    │
│  (foundation)   │      │   (wrapper)   │        │   (testing)   │
└────────┬────────┘      └───────────────┘        └───────────────┘
         │                        ▲
         │               ┌────────┴────────┐
         ▼               │                 │
┌─────────────────┐      │        ┌────────────────┐
│  GRIOT-ENFORCE  │──────┘        │ GRIOT-REGISTRY │
│    (runtime)    │               │     (API)      │
└─────────────────┘               └────────┬───────┘
                                           │
                                  ┌────────▼───────┐
                                  │   GRIOT-HUB    │
                                  │   (frontend)   │
                                  └────────────────┘
```

---

## Package Structure

```
griot/                              # Monorepo root
├── agents/                          # Interface specifications
    ├── prompts/                        # Agent prompts
    │   ├── core.md                   # griot-core prompt
    │   ├── registry.md                    # Registry OpenAPI spec
    │   └── ...                       # other prompts
    ├── specs/                        # Interface specifications for all components/agents
    │   ├── core.yaml                 # griot-core public API
    │   ├── registry.yaml                  # Registry OpenAPI spec
    │   └── ...                       # other specs 
    ├── status/                         # Coordination
    │   ├── board.md                    # Kanban board
    │   ├── decisions/                  # Architectural decisions
    │   └── requests/                   # Interface requests
    ├── AGENTS.md                   # Agent definitions
    ├── CLAUDE.md                   # Introduction & quick reference
├── pyproject.toml                  # Meta-package
├── README.md
├── LICENSE
│
│
├── griot-core/                     # Core library
│   └── src/griot_core/
│       ├── models.py               # GriotModel, Field
│       ├── contract.py             # Contract class
│       ├── types.py                # Enums, types
│       ├── constraints.py          # Constraint logic
│       ├── validation.py           # Validation engine
│       ├── mock.py                 # Mock generator
│       ├── manifest.py             # AI manifest export
│       └── exceptions.py           # Exceptions
│
├── griot-cli/                      # CLI
│   └── src/griot_cli/
│       ├── main.py                 # Click app
│       ├── commands/               # Command modules
│       ├── config.py
│       └── output.py
│
├── griot-enforce/                  # Runtime validation
│   └── src/griot_enforce/
│       ├── validator.py            # Core validator
│       ├── airflow/                # Airflow integration
│       ├── dagster/                # Dagster integration
│       └── prefect/                # Prefect integration
│
├── griot-registry/                 # API server
│   └── src/griot_registry/
│       ├── server.py               # FastAPI app
│       ├── api/                    # Endpoints
│       ├── storage/                # Backends
│       └── auth/                   # Authentication
│
├── griot-hub/                      # Web UI
│   └── src/
│       ├── app/                    # Next.js pages
│       ├── components/             # React components
│       └── lib/                    # Utilities
│
├── docs/                           # Documentation
├── examples/                       # Example contracts
└── .github/workflows/              # CI/CD
```

---

## Agent Definitions

### 🎯 orchestrator

**Role:** Project coordinator, architect, integration overseer

| Attribute | Value |
|-----------|-------|
| **Scope** | Project-wide planning, cross-component decisions |
| **Owns** | `specs/*`, `status/*`, `AGENTS.md`, `CLAUDE.md`, `prompts/*`, root configs |
| **Reads** | Everything |
| **Writes** | Task assignments, decisions, specs |

**Responsibilities:**
1. Maintain master implementation plan aligned with SRS
2. Break epics into tasks and assign to agents
3. Triage interface requests within 24 hours
4. Review PRs touching multiple components
5. Resolve architectural conflicts
6. Update traceability matrix
7. Declare phase transitions

**Decision Authority:** Final say on all architectural disputes

---

### 🔧 core

**Role:** Implements `griot-core` — the foundation library

| Attribute | Value |
|-----------|-------|
| **Scope** | All griot-core functionality |
| **Owns** | `griot-core/src/griot_core/*` |
| **Reads** | `specs/core.yaml`, `status/board.md`, `status/requests/*` |
| **Writes** | Core library code, updates to `specs/core.yaml` |

**Files Owned:**
```
griot-core/src/griot_core/
├── __init__.py          # Public exports
├── models.py            # GriotModel, Field
├── contract.py          # Contract class
├── types.py             # PIICategory, SensitivityLevel, enums
├── constraints.py       # Constraint definitions & logic
├── validation.py        # ValidationResult, ValidationError, engine
├── mock.py              # Mock data generation
├── manifest.py          # JSON-LD, Markdown, LLM context export
└── exceptions.py        # GriotError hierarchy
```

**Implements:**
| Requirement | File | Description |
|-------------|------|-------------|
| FR-SDK-001 | models.py | GriotModel base class |
| FR-SDK-002 | contract.py | YAML loading |
| FR-SDK-003 | contract.py | Python ↔ YAML conversion |
| FR-SDK-004 | constraints.py | Field constraints |
| FR-SDK-005 | validation.py | Data validation |
| FR-SDK-006 | mock.py | Mock data generation |
| FR-SDK-007 | manifest.py | AI manifest export |
| FR-SDK-008 | types.py | PII metadata |
| FR-SDK-010 | models.py | PII inventory |
| FR-SDK-011 | types.py | Residency rules |
| FR-SDK-012 | types.py | Lineage config |
| FR-SDK-013-017 | (future) | Reports (Phase 2) |

**Constraints:**
- ⛔ ZERO external dependencies in core modules
- ✅ Python stdlib only (dataclasses, typing, json, re, pathlib)
- ✅ Optional deps via package extras

**Quality Gates:**
- 100% type hint coverage (pyright --strict)
- \>90% test coverage
- All public methods have docstrings
- Validation: 100K rows < 5 seconds

---

### 💻 cli

**Role:** Implements `griot-cli` as thin wrapper

| Attribute | Value |
|-----------|-------|
| **Scope** | Command-line interface only |
| **Owns** | `griot-cli/src/griot_cli/*` |
| **Reads** | `specs/core.yaml` |
| **Writes** | CLI code only |

**Files Owned:**
```
griot-cli/src/griot_cli/
├── __init__.py
├── main.py              # Click app entry point
├── config.py            # Configuration loading
├── output.py            # Formatters, colors
└── commands/
    ├── __init__.py
    ├── validate.py      # griot validate
    ├── lint.py          # griot lint
    ├── diff.py          # griot diff
    ├── mock.py          # griot mock
    ├── push.py          # griot push
    ├── pull.py          # griot pull
    └── manifest.py      # griot manifest
```

**Constraints:**
- ⛔ **NO BUSINESS LOGIC** — every command calls griot-core
- ⛔ Cannot implement validation, parsing, or report logic
- ✅ If functionality missing, create interface request

**Command → Core Mapping:**
| Command | Core Method |
|---------|-------------|
| `griot validate` | `contract.validate()` |
| `griot lint` | `contract.lint()` |
| `griot diff` | `contract.diff()` |
| `griot mock` | `contract.mock()` |
| `griot manifest` | `contract.to_manifest()` |
| `griot push` | `registry_client.push()` |
| `griot pull` | `registry_client.pull()` |

---

### ⚡ enforce

**Role:** Implements `griot-enforce` runtime validation

| Attribute | Value |
|-----------|-------|
| **Scope** | Runtime validation, orchestrator integrations |
| **Owns** | `griot-enforce/src/griot_enforce/*` |
| **Reads** | `specs/core.yaml`, `specs/enforce.yaml` |
| **Writes** | Enforce code, operator implementations |

**Files Owned:**
```
griot-enforce/src/griot_enforce/
├── __init__.py
├── validator.py         # RuntimeValidator class
├── airflow/
│   ├── __init__.py
│   ├── operators.py     # GriotValidateOperator
│   └── sensors.py       # GriotFreshnessSensor
├── dagster/
│   ├── __init__.py
│   ├── resources.py     # GriotResource
│   └── decorators.py    # @griot_asset
└── prefect/
    └── tasks.py         # @task wrappers
```

**Implements:**
| Requirement | File | Description |
|-------------|------|-------------|
| FR-ENF-001 | validator.py | Core RuntimeValidator |
| FR-ENF-002 | airflow/operators.py | GriotValidateOperator |
| FR-ENF-007 | validator.py | Anomaly detection hooks |
| FR-ENF-008 | validator.py | Residency enforcement |
| FR-ENF-009 | validator.py | Masking verification |

**Constraints:**
- ⛔ No validation logic — wrap griot-core
- ✅ Add runtime concerns (caching, batching, metrics)

---

### 🗄️ registry

**Role:** Implements `griot-registry` API server

| Attribute | Value |
|-----------|-------|
| **Scope** | Contract storage, versioning, API |
| **Owns** | `griot-registry/src/griot_registry/*`, `specs/api.yaml` |
| **Reads** | `specs/core.yaml` |
| **Writes** | API code, OpenAPI spec |

**Files Owned:**
```
griot-registry/src/griot_registry/
├── __init__.py
├── server.py            # FastAPI app
├── api/
│   ├── __init__.py
│   ├── contracts.py     # CRUD endpoints
│   ├── validations.py   # Validation history
│   └── search.py        # Search endpoints
├── storage/
│   ├── __init__.py
│   ├── base.py          # Abstract backend
│   ├── filesystem.py    # File storage
│   ├── git.py           # Git-backed
│   └── postgres.py      # PostgreSQL
└── auth/
    ├── __init__.py
    ├── api_key.py       # API key auth
    └── oauth.py         # OAuth2/OIDC
```

**Implements:**
| Requirement | Files | Description |
|-------------|-------|-------------|
| FR-REG-008 | api/contracts.py | Approval chain |
| — | api/contracts.py | Contract CRUD |
| — | api/validations.py | Validation history |
| — | storage/*.py | Storage backends |

---

### 🌐 hub

**Role:** Implements `griot-hub` web interface

| Attribute | Value |
|-----------|-------|
| **Scope** | Next.js frontend only |
| **Owns** | `griot-hub/src/*` |
| **Reads** | `specs/api.yaml` |
| **Writes** | Frontend code only |

**Files Owned:**
```
griot-hub/src/
├── app/
│   ├── page.tsx              # Dashboard
│   ├── layout.tsx            # Root layout
│   ├── contracts/page.tsx    # Contract browser
│   ├── studio/page.tsx       # Contract editor
│   ├── monitor/page.tsx      # Validation monitor
│   └── settings/page.tsx     # Settings
├── components/
│   ├── ContractCard.tsx
│   ├── FieldEditor.tsx
│   └── ValidationBadge.tsx
└── lib/
    ├── api.ts                # Registry API client
    └── types.ts              # TypeScript types
```

**Constraints:**
- ⛔ Never imports griot-core directly
- ✅ All data via Registry API
- ✅ Generate types from `specs/api.yaml`

---

### 🧪 quality

**Role:** Testing, CI/CD, quality assurance

| Attribute | Value |
|-----------|-------|
| **Scope** | Cross-cutting quality |
| **Owns** | `.github/workflows/*`, root test config, `docs/*` |
| **Reads** | All source code, all specs |
| **Writes** | Tests, CI config, docs |

**Files Owned:**
```
.github/workflows/
├── test.yml             # Test pipeline
└── release.yml          # Release pipeline

docs/
├── index.md
├── getting-started/
├── guides/
└── api-reference/
```

**Quality Gates:**
| Check | Target | Blocking |
|-------|--------|----------|
| Unit tests | 100% pass | Yes |
| pyright --strict | Pass | Yes |
| Coverage (core) | >90% | Yes |
| Coverage (others) | >80% | Yes |
| ruff lint | Clean | Yes |
| Performance | 100K rows <5s | Yes |

---

## Communication Rules

### Rule 0 Each agent creates its own Branch 
Each agent works in its own Git branch named after the agent. For example, the `core` agent works in the `agent-core` branch. This prevents merge conflicts and keeps work isolated.

### Rule 1: Core-First Development

All business logic lives in `griot-core`. Before implementing ANY functionality:

1. Check if it belongs in griot-core
2. If yes → core agent implements in griot-core
3. If wrapper → your agent wraps the core method

```python
# ✅ CORRECT: CLI wraps core
@click.command()
def validate(contract_path, data_path):
    from griot_core import Contract
    contract = Contract.from_yaml(contract_path)
    result = contract.validate(load_data(data_path))  # Core does work
    display(result)  # CLI formats

# ❌ WRONG: CLI implements logic
@click.command()
def validate(contract_path, data_path):
    for row in data:
        if row['age'] < 0:  # NO! Core's job
            errors.append(...)
```

### Rule 2: Interface-First

Before implementing any public method:

1. Update `specs/core.yaml` with signature
2. Set status: `planned`
3. Implement
4. Set status: `complete`

### Rule 3: No Cross-Boundary Writes

| Agent | Can Write | Cannot Write |
|-------|-----------|--------------|
| core | `griot-core/src/*` | `griot-cli/*`, `griot-hub/*` |
| cli | `griot-cli/src/*` | `griot-core/*` |
| hub | `griot-hub/src/*` | `griot-registry/*` |
| orchestrator | `specs/*`, `status/*` | Source code |

**Exception:** Any agent can create `status/requests/*.md`

### Rule 4: Formal Interface Requests

When Agent A needs functionality from Agent B:

1. Agent A creates `status/requests/REQ-NNN.md`
2. Agent A updates `status/board.md` blocked table
3. Orchestrator triages within 24 hours
4. Agent B implements and marks complete
5. Agent A unblocks and continues

### Rule 5: Decisions Are Immutable

Once `status/decisions/NNN-*.md` is merged, it cannot be changed. New decisions can supersede with explicit reference.

---

## File Ownership Matrix

| Path | Owner | Consumers |
|------|-------|-----------|
| `AGENTS.md` | orchestrator | all |
| `CLAUDE.md` | orchestrator | all |
| `specs/core.yaml` | core + orchestrator | cli, enforce, registry |
| `specs/api.yaml` | registry + orchestrator | hub, cli |
| `specs/enforce.yaml` | enforce + orchestrator | — |
| `status/board.md` | orchestrator | all |
| `status/decisions/*` | orchestrator | all |
| `status/requests/*` | any (create) | orchestrator (triage) |
| `griot-core/src/*` | core | all (read) |
| `griot-cli/src/*` | cli | all (read) |
| `griot-enforce/src/*` | enforce | all (read) |
| `griot-registry/src/*` | registry | all (read) |
| `griot-hub/src/*` | hub | all (read) |
| `.github/workflows/*` | quality | all (read) |
| `docs/*` | quality | all (read) |

---

## Dependency Graph & Phases

```
Phase 1 (Foundation)
├── core: models.py, contract.py, validation.py [NO DEPS]
├── quality: CI setup, test infrastructure [NO DEPS]
│
Phase 2 (Features)  
├── core: types.py (PII, residency), mock.py, manifest.py
├── cli: All commands [NEEDS: core methods]
│
Phase 3 (Runtime)
├── enforce: validator.py, airflow/, dagster/ [NEEDS: core]
├── registry: server.py, api/, storage/ [NEEDS: core]
│
Phase 4 (UI)
└── hub: All pages and components [NEEDS: registry API]
```

---

## Conflict Resolution

**Priority Order:**
1. Safety — Never compromise security/privacy
2. SRS Requirements — Spec is authoritative
3. Core-First — Business logic in griot-core
4. Orchestrator Decision — Final arbiter

**Escalation:**
```
Agent discovers conflict
        ↓
Document in status/requests/CONFLICT-NNN.md
        ↓
Orchestrator creates decision document
        ↓
Decision merged → agents comply
```

---

## Agent Activation Checklist

Before any agent begins work:

- [ ] Read this entire `AGENTS.md` file
- [ ] Read `CLAUDE.md` for quick reference
- [ ] Read Task Assignments in `status/board.md` for current tasks, only if you are the the orchestrator agent should you update this section, otherwise just read it.
- [ ] Update the relevant table Blocked/Ready for review in `status/board.md` when you begin and end a task for current tasks
- [ ] Read relevant `specs/*.yaml` for interfaces
- [ ] Check `status/requests/*` for pending items
- [ ] Check `status/decisions/*` for context
- [ ] Identify blocking dependencies and update them in `status/board.md`
- [ ] Confirm you're only writing to owned paths
- [ ] Set up your Git branch named `agent-<your-agent-name>` and work there exclusively.
