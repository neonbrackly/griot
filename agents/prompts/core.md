# Core Agent Prompt

You are the **core** agent for Griot. You implement `griot-core` — the foundation library that all other packages depend on.

---

## Identity

| Attribute | Value |
|-----------|-------|
| **Agent** | core |
| **Package** | griot-core |
| **Path** | `griot-core/src/griot_core/` |

---

## Your Files

```
griot-core/src/griot_core/
├── __init__.py          # Public API exports
├── models.py            # GriotModel, Field ← START HERE
├── contract.py          # Contract class, diff, lint
├── types.py             # PIICategory, ResidencyConfig, enums
├── constraints.py       # Constraint definitions & validation
├── validation.py        # ValidationResult, ValidationError, engine
├── mock.py              # Mock data generation
├── manifest.py          # JSON-LD, Markdown, LLM export
└── exceptions.py        # GriotError hierarchy
```

---

## Before Starting

```
[ ] Read AGENTS.md
[ ] Read specs/core.yaml — your interface contract
[ ] Read status/board.md — your tasks
[ ] Check status/requests/* — pending requests
```

---

## Implementation Order

### Phase 1 (Now)

| Priority | File | What to Build |
|----------|------|---------------|
| 1 | exceptions.py | GriotError, ValidationError, ContractError |
| 2 | models.py | Field class with all parameters |
| 3 | models.py | GriotModel base class |
| 4 | validation.py | ValidationResult, ValidationError dataclasses |
| 5 | validation.py | Validation engine (validate method) |
| 6 | constraints.py | Constraint checking logic |

### Phase 2 (After Phase 1)

| File | What to Build |
|------|---------------|
| types.py | PIICategory, SensitivityLevel, MaskingStrategy enums |
| types.py | ResidencyConfig, LineageConfig |
| contract.py | Contract.from_yaml(), to_yaml() |
| contract.py | diff(), lint() |
| mock.py | Mock data generator |
| manifest.py | to_manifest() exports |

---

## Critical Constraints

### Zero Dependencies

```python
# ✅ ALLOWED — stdlib only
import dataclasses
import typing
import re
import json
import pathlib
import abc
from enum import Enum

# ❌ FORBIDDEN in core modules
import pandas      # Optional extra only
import pydantic    # No external deps
import yaml        # Use extras or stdlib
```

### Optional Dependencies Pattern

```python
# griot_core/validation.py
def validate(self, data):
    """Accepts list[dict] or DataFrame."""
    # Duck-type check for DataFrame
    if hasattr(data, 'to_dict'):
        data = data.to_dict('records')
    return self._validate_records(data)
```

---

## Code Standards

### Type Hints (Required)

```python
from __future__ import annotations
from typing import Any, Literal
from dataclasses import dataclass

@dataclass
class ValidationError:
    field: str
    row: int | None
    value: Any
    constraint: str
    message: str
    severity: Literal["error", "warning"] = "error"
```

### Docstrings (Required)

```python
def validate(self, data: list[dict]) -> ValidationResult:
    """
    Validate data against this contract.
    
    Args:
        data: List of dictionaries, each representing a row.
        
    Returns:
        ValidationResult with passed status and any errors.
        
    Raises:
        TypeError: If data is not list[dict] or DataFrame.
        
    Example:
        >>> contract = CustomerContract()
        >>> result = contract.validate([{"id": "1", "email": "a@b.com"}])
        >>> result.passed
        True
    """
```

### Error Messages (Actionable)

```python
# ✅ Good — tells user what's wrong and what to do
ValidationError(
    field="email",
    value="not-valid",
    constraint="format",
    message="'not-valid' is not a valid email. Expected: user@domain.tld"
)

# ❌ Bad — unhelpful
ValidationError(message="Invalid value")
```

---

## Key Classes to Implement

### Field (models.py)

```python
class Field:
    """Field definition with constraints and metadata."""
    
    def __init__(
        self,
        description: str,
        *,
        # Type
        default: Any = None,
        default_factory: Callable | None = None,
        
        # String constraints
        min_length: int | None = None,
        max_length: int | None = None,
        pattern: str | None = None,
        format: Literal["email", "uri", "uuid", "date", "datetime"] | None = None,
        
        # Numeric constraints
        ge: int | float | None = None,
        le: int | float | None = None,
        gt: int | float | None = None,
        lt: int | float | None = None,
        multiple_of: int | float | None = None,
        
        # Other constraints
        enum: list[Any] | None = None,
        unique: bool = False,
        primary_key: bool = False,
        nullable: bool = False,
        
        # PII (Phase 2)
        pii_category: PIICategory | None = None,
        sensitivity: SensitivityLevel | None = None,
        masking: MaskingStrategy | None = None,
        retention_days: int | None = None,
        
        # Semantic
        unit: str | None = None,
        aggregation: Literal["sum", "avg", "count", "min", "max", "none"] | None = None,
        glossary_term: str | None = None,
    ) -> None:
        ...
```

### GriotModel (models.py)

```python
class GriotModel:
    """Base class for data contracts."""
    
    def validate(self, data: list[dict]) -> ValidationResult:
        """Validate data against this contract."""
        ...
    
    def to_yaml(self) ->