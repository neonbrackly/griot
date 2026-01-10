# Validation Guide

Learn how to validate data effectively with Griot.

## Basic Validation

```python
from griot_core import GriotModel, Field

class Product(GriotModel):
    sku: str = Field(description="Product SKU", primary_key=True)
    price: float = Field(description="Price", ge=0)

# Validate a list of records
data = [
    {"sku": "PROD-001", "price": 29.99},
    {"sku": "PROD-002", "price": 49.99},
]

result = Product.validate(data)
```

## ValidationResult

The `validate()` method returns a `ValidationResult` object:

```python
result = Product.validate(data)

# Check if validation passed
if result.passed:
    print("All data is valid!")
else:
    print(f"Found {result.error_count} errors")

# Access detailed information
print(f"Rows validated: {result.row_count}")
print(f"Duration: {result.duration_ms}ms")
print(f"Error rate: {result.error_rate:.2%}")

# Get summary
print(result.summary())

# Convert to dict/JSON
result_dict = result.to_dict()
result_json = result.to_json()
```

## Error Handling

```python
result = Product.validate(data)

# Iterate over errors
for error in result.errors:
    print(f"Field: {error.field}")
    print(f"Row: {error.row}")
    print(f"Value: {error.value}")
    print(f"Constraint: {error.constraint}")
    print(f"Message: {error.message}")

# Raise exception on failure
try:
    result.raise_on_failure()
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## Field Statistics

Access per-field validation statistics:

```python
result = Product.validate(data)

for field_name, stats in result.field_stats.items():
    print(f"{field_name}:")
    print(f"  Total: {stats.total}")
    print(f"  Valid: {stats.valid}")
    print(f"  Invalid: {stats.invalid}")
    print(f"  Null count: {stats.null_count}")
    print(f"  Valid rate: {stats.valid_rate:.2%}")
```

## Single Row Validation

Validate a single row:

```python
from griot_core.validation import validate_single_row

row = {"sku": "PROD-001", "price": -10}
errors = validate_single_row(Product, row)

for error in errors:
    print(f"{error.field}: {error.message}")
```

## Performance

Griot is optimized for large datasets:

```python
# Validate 100,000 rows in under 5 seconds
large_data = Product.mock(rows=100000)
result = Product.validate(large_data)
print(f"Validated {result.row_count} rows in {result.duration_ms}ms")
```

## Validation with Uniqueness

```python
class User(GriotModel):
    id: str = Field(description="User ID", primary_key=True, unique=True)
    email: str = Field(description="Email", unique=True)

data = [
    {"id": "1", "email": "alice@example.com"},
    {"id": "2", "email": "bob@example.com"},
    {"id": "1", "email": "charlie@example.com"},  # Duplicate ID
]

result = User.validate(data)
# Will report uniqueness violation for id "1"
```

## CLI Validation

```bash
# Basic validation
griot validate contract.yaml data.csv

# JSON output
griot validate contract.yaml data.csv --format json

# GitHub Actions format
griot validate contract.yaml data.csv --format github

# Fail on warnings
griot validate contract.yaml data.csv --strict
```
