# Defining Contracts

This guide covers all aspects of defining data contracts with Griot.

## Contract Structure

A Griot contract is a Python class that inherits from `GriotModel`:

```python
from griot_core import GriotModel, Field

class MyContract(GriotModel):
    """Description of the contract."""

    field_name: type = Field(
        description="Field description",
        # ... constraints
    )
```

## Field Types

Griot supports the following field types:

| Python Type | Data Type | Description |
|-------------|-----------|-------------|
| `str` | string | Text data |
| `int` | integer | Whole numbers |
| `float` | float | Decimal numbers |
| `bool` | boolean | True/False values |
| `list` | array | Lists/arrays |
| `dict` | object | Dictionaries/objects |

## Constraints

### String Constraints

```python
name: str = Field(
    description="Name field",
    min_length=1,
    max_length=100,
    pattern=r"^[A-Za-z]+$",
    format="email",  # email, uri, uuid, date, datetime, ipv4, ipv6, hostname
)
```

### Numeric Constraints

```python
age: int = Field(
    description="Age field",
    ge=0,        # Greater than or equal
    le=150,      # Less than or equal
    gt=0,        # Greater than (exclusive)
    lt=100,      # Less than (exclusive)
    multiple_of=5,  # Must be divisible by
)
```

### Enum Constraints

```python
status: str = Field(
    description="Status field",
    enum=["active", "inactive", "pending"],
)
```

## Special Fields

### Primary Key

```python
id: str = Field(
    description="Unique identifier",
    primary_key=True,
)
```

### Unique Fields

```python
email: str = Field(
    description="Email address",
    unique=True,
)
```

### Nullable Fields

```python
from typing import Optional

nickname: Optional[str] = Field(
    description="Optional nickname",
    nullable=True,
)
```

### Default Values

```python
status: str = Field(
    description="Account status",
    default="pending",
)
```

## Metadata

### Units

```python
weight: float = Field(
    description="Weight measurement",
    unit="kg",
)
```

### Aggregation

```python
revenue: float = Field(
    description="Revenue amount",
    aggregation="sum",  # sum, avg, min, max, count
)
```

### Glossary Terms

```python
ltv: float = Field(
    description="Lifetime value",
    glossary_term="customer_ltv",
)
```

## Contract Docstrings

Always include a docstring for your contract:

```python
class Customer(GriotModel):
    """
    Customer profile data contract.

    This contract defines the schema for customer data used in
    the CRM and analytics systems. It includes PII tracking and
    validation rules for data quality.

    Owner: Data Platform Team
    Version: 2.0.0
    """
```

## YAML Format

Contracts can also be defined in YAML:

```yaml
name: Customer
description: Customer profile data contract.
fields:
  customer_id:
    type: string
    description: Unique customer identifier
    primary_key: true
    pattern: ^CUST-\d{6}$
  email:
    type: string
    description: Email address
    format: email
    max_length: 255
  age:
    type: integer
    description: Age in years
    ge: 0
    le: 150
```

Load YAML contracts:

```python
from griot_core import GriotModel

Customer = GriotModel.from_yaml("customer.yaml")
```

## Best Practices

1. **Always include descriptions** - Every field should have a meaningful description
2. **Set primary keys** - Identify unique identifiers
3. **Use appropriate constraints** - Validate data at the schema level
4. **Track PII** - Mark sensitive fields with privacy metadata
5. **Document with docstrings** - Explain the contract's purpose and ownership
