# ADR-001: Breaking Change Detection and Enforcement

**Status:** Accepted
**Date:** 2026-01-11
**Author:** Orchestrator

## Context

As part of Phase 6 (Open Data Contract Standard Overhaul), we need to implement breaking change detection across all modules. Breaking changes in data contracts can cause downstream failures when:

1. Data producers change contract schemas
2. Data consumers (pipelines, dashboards, ML models) depend on specific schemas
3. Registry updates are pushed without proper review

Currently, the `griot push` command and registry API accept any contract update without validation. This poses a risk to data integrity and operational stability.

## Decision

### 1. Breaking Change Definition

The following changes are classified as **BREAKING**:

| Change Type | Breaking? | Rationale |
|-------------|-----------|-----------|
| Field removal | YES | Consumers depending on field will fail |
| Field type change (incompatible) | YES | Type coercion failures |
| Field rename | YES | Consumers referencing old name fail |
| Add required field without default | YES | Existing data won't have value |
| Remove enum values | YES | Existing data may have removed value |
| Tighten constraints (reduce max_length, etc.) | YES | Existing data may violate |
| nullable → non-nullable | YES | Existing nulls will fail |

The following changes are **NON-BREAKING**:

| Change Type | Breaking? | Rationale |
|-------------|-----------|-----------|
| Add optional field | NO | Existing data unaffected |
| Add enum values | NO | Expands valid options |
| Relax constraints (increase max_length, etc.) | NO | Existing data still valid |
| Update metadata (descriptions, semantic info) | NO | No schema impact |
| Add quality rules | NO | Validation only |
| Update SLAs | NO | Operational only |

### 2. Type Compatibility Matrix

| From Type | To Type | Breaking? |
|-----------|---------|-----------|
| integer | float | NO (widening) |
| float | integer | YES (lossy) |
| string | any numeric | YES |
| boolean | string | YES |
| any | specific | NO (valid narrowing) |
| specific | any | NO (widening) |

### 3. Enforcement Points

Breaking changes will be enforced at:

1. **griot-core** (`contract.py`):
   - `detect_breaking_changes(old, new) -> list[BreakingChange]`
   - `ContractDiff.has_breaking_changes -> bool`

2. **griot-cli** (`push.py`):
   - Default: Block push with breaking changes
   - Override: `--allow-breaking` flag

3. **griot-registry** (`api/contracts.py`):
   - Default: Return 409 Conflict with breaking change details
   - Override: `?allow_breaking=true` query parameter

4. **griot-hub** (`studio/page.tsx`):
   - Visual warning when editing creates breaking changes
   - Confirmation modal before saving

### 4. API Response Format

When breaking changes are detected, the API returns:

```json
{
  "error": "breaking_changes_detected",
  "code": "BC001",
  "message": "Contract update contains breaking changes",
  "breaking_changes": [
    {
      "type": "field_removed",
      "field": "customer_email",
      "severity": "breaking",
      "description": "Field 'customer_email' was removed"
    },
    {
      "type": "type_changed",
      "field": "age",
      "from": "string",
      "to": "integer",
      "severity": "breaking",
      "description": "Field 'age' type changed from string to integer (incompatible)"
    }
  ],
  "resolution": "Use --allow-breaking flag or ?allow_breaking=true to force update"
}
```

HTTP Status: `409 Conflict`

### 5. Breaking Change History

When breaking changes are allowed, they are recorded in the contract history:

```yaml
version_history:
  - version: "2.0.0"
    created_at: "2026-01-15T10:00:00Z"
    change_type: "major"
    breaking_changes:
      - type: field_removed
        field: customer_email
      - type: type_changed
        field: age
        from: string
        to: integer
    approved_by: "user@example.com"
    reason: "Schema redesign for v2"
```

## Consequences

### Positive

1. **Prevents accidental breaking changes** - Developers must explicitly acknowledge
2. **Audit trail** - Breaking changes are logged with approver
3. **Consumer protection** - Downstream systems have notice of changes
4. **Version discipline** - Major version bumps for breaking changes

### Negative

1. **Additional friction** - Developers must use override flag
2. **Implementation effort** - All modules need updates
3. **Edge cases** - Some constraint changes are ambiguous

### Neutral

1. **Learning curve** - Teams need to understand breaking change rules
2. **Documentation required** - Clear docs on what constitutes breaking

## Implementation

### Phase 1: Core Detection (Tasks T-300 to T-302)
- Implement `detect_breaking_changes()` in griot-core
- Add `BreakingChange` dataclass
- Update `ContractDiff` class

### Phase 2: CLI Enforcement (Tasks T-303, T-360-362)
- Add validation to `griot push`
- Add `--allow-breaking` flag
- Add `--dry-run` for breaking change preview

### Phase 3: Registry Enforcement (Tasks T-304, T-371-373)
- Add validation to PUT /contracts/{id}
- Add `?allow_breaking=true` parameter
- Add breaking change history tracking

### Phase 4: Hub Warnings (Tasks T-305, T-384-385)
- Add breaking change warnings in Contract Studio
- Add version comparison view with highlights
- Add confirmation modal

## References

- Open Data Contract Standard: `agents/example_contract.yaml`
- ODCS Spec: `agents/specs/odcs.yaml`
- Task Board: `agents/status/board.md` (Phase 6)
