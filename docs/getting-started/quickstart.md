# Quick Start

Get started with Griot in 5 minutes.

## Define a Contract

Create a Python class that inherits from `GriotModel`:

```python
from griot_core import GriotModel, Field

class Customer(GriotModel):
    """Customer data contract for the CRM system."""

    customer_id: str = Field(
        description="Unique customer identifier",
        primary_key=True,
        pattern=r"^CUST-\d{6}$",
    )
    email: str = Field(
        description="Customer email address",
        format="email",
        max_length=255,
    )
    age: int = Field(
        description="Customer age in years",
        ge=0,
        le=150,
    )
    status: str = Field(
        description="Account status",
        enum=["active", "inactive", "suspended"],
    )
```

## Validate Data

Validate your data against the contract:

```python
# Sample data
data = [
    {"customer_id": "CUST-000001", "email": "alice@example.com", "age": 30, "status": "active"},
    {"customer_id": "CUST-000002", "email": "bob@example.com", "age": 25, "status": "active"},
    {"customer_id": "INVALID", "email": "not-an-email", "age": -5, "status": "unknown"},
]

# Validate
result = Customer.validate(data)

# Check results
print(f"Passed: {result.passed}")
print(f"Errors: {result.error_count}")
print(result.summary())
```

Output:

```
Passed: False
Errors: 4
Validation FAILED
Rows: 3 | Errors: 4 | Duration: 1.23ms

Sample errors:
  - customer_id[row 2]: Value 'INVALID' does not match pattern '^CUST-\d{6}$'
  - email[row 2]: Invalid email format
  - age[row 2]: Value -5 must be >= 0
  - status[row 2]: Value 'unknown' not in enum ['active', 'inactive', 'suspended']
```

## Export as YAML

Save your contract as YAML:

```python
yaml_content = Customer.to_yaml()
print(yaml_content)
```

Output:

```yaml
name: Customer
description: Customer data contract for the CRM system.
fields:
  customer_id:
    type: string
    description: Unique customer identifier
    primary_key: true
    pattern: ^CUST-\d{6}$
  email:
    type: string
    description: Customer email address
    format: email
    max_length: 255
  age:
    type: integer
    description: Customer age in years
    ge: 0
    le: 150
  status:
    type: string
    description: Account status
    enum:
      - active
      - inactive
      - suspended
```

## Generate Mock Data

Generate test data that respects constraints:

```python
mock_data = Customer.mock(rows=5, seed=42)
for row in mock_data:
    print(row)
```

## CLI Usage

Use the command-line interface:

```bash
# Validate data against a contract
griot validate customer.yaml data.csv

# Lint a contract for quality issues
griot lint customer.yaml

# Generate mock data
griot mock customer.yaml --rows 100 --output mock_data.csv

# Export as AI manifest
griot manifest customer.yaml --format llm_context
```

## Next Steps

- [Create Your First Contract](first-contract.md) - Detailed tutorial
- [Validation Guide](../guides/validation.md) - Advanced validation patterns
- [API Reference](../api-reference/core.md) - Full API documentation
