# Your First Contract

This tutorial walks through creating a complete data contract with all features.

## Scenario

You're building a customer analytics pipeline that needs to:
- Define a schema for customer data
- Validate incoming data
- Track PII fields for compliance
- Generate reports for stakeholders

## Step 1: Define the Contract

```python
from griot_core import GriotModel, Field

class CustomerAnalytics(GriotModel):
    """
    Customer analytics data contract.

    This contract defines the schema for customer data used in
    analytics pipelines, including PII tracking and validation rules.
    """

    # Primary identifier
    customer_id: str = Field(
        description="Unique customer identifier assigned at registration",
        primary_key=True,
        pattern=r"^CUST-\d{6}$",
        glossary_term="customer_identifier",
    )

    # PII fields with privacy metadata
    email: str = Field(
        description="Primary email address for customer communications",
        format="email",
        max_length=255,
        pii_category="email",
        sensitivity_level="confidential",
        masking_strategy="partial",
        legal_basis="consent",
        retention_days=730,  # 2 years
    )

    phone: str = Field(
        description="Primary phone number with country code",
        pattern=r"^\+\d{1,3}-\d{3,14}$",
        pii_category="phone",
        sensitivity_level="confidential",
        masking_strategy="partial",
        nullable=True,
    )

    # Demographic data
    age: int = Field(
        description="Customer age calculated from date of birth",
        ge=0,
        le=150,
        unit="years",
        aggregation="avg",
    )

    country: str = Field(
        description="Two-letter ISO country code of residence",
        pattern=r"^[A-Z]{2}$",
        glossary_term="country_code",
    )

    # Business data
    account_type: str = Field(
        description="Type of customer account",
        enum=["free", "basic", "premium", "enterprise"],
    )

    lifetime_value: float = Field(
        description="Total revenue attributed to this customer",
        ge=0.0,
        unit="USD",
        aggregation="sum",
        glossary_term="customer_ltv",
    )

    created_at: str = Field(
        description="Account creation timestamp in ISO 8601 format",
        format="datetime",
    )
```

## Step 2: Validate Data

```python
# Load your data (from CSV, database, API, etc.)
customer_data = [
    {
        "customer_id": "CUST-000001",
        "email": "alice@example.com",
        "phone": "+1-5551234567",
        "age": 32,
        "country": "US",
        "account_type": "premium",
        "lifetime_value": 1250.00,
        "created_at": "2024-01-15T10:30:00Z",
    },
    # ... more rows
]

# Validate
result = CustomerAnalytics.validate(customer_data)

if result.passed:
    print("Data validation passed!")
else:
    print(f"Validation failed with {result.error_count} errors")
    result.raise_on_failure()  # Raises ValidationError
```

## Step 3: Check PII Inventory

```python
# List all PII fields
pii_fields = CustomerAnalytics.pii_inventory()
for field in pii_fields:
    print(f"- {field.name}: {field.pii_category.value}")

# Output:
# - email: email
# - phone: phone

# Get full PII summary
summary = CustomerAnalytics.pii_summary()
print(f"Total PII fields: {summary['pii_field_count']}")
print(f"Categories: {summary['categories']}")
print(f"Sensitivity levels: {summary['sensitivity_levels']}")
```

## Step 4: Generate Reports

```python
from griot_core.reports import (
    generate_analytics_report,
    generate_ai_readiness_report,
)

# Analytics report
analytics = generate_analytics_report(CustomerAnalytics)
print(analytics.to_markdown())

# AI Readiness report
ai_report = generate_ai_readiness_report(CustomerAnalytics)
print(f"AI Readiness Score: {ai_report.readiness_score}/100")
print(f"Grade: {ai_report.readiness_grade}")
```

## Step 5: Export for Different Consumers

```python
# YAML for other teams
yaml_content = CustomerAnalytics.to_yaml()

# JSON-LD for semantic web / knowledge graphs
jsonld = CustomerAnalytics.to_manifest(format="json_ld")

# Markdown for documentation
markdown = CustomerAnalytics.to_manifest(format="markdown")

# LLM context for AI assistants
llm_context = CustomerAnalytics.to_manifest(format="llm_context")
```

## Step 6: Use with CLI

Save your contract as `customer_analytics.py`, then:

```bash
# Validate data
griot validate customer_analytics.py data.csv

# Lint for quality issues
griot lint customer_analytics.py

# Check contract differences
griot diff customer_analytics_v1.yaml customer_analytics_v2.yaml

# Generate mock data for testing
griot mock customer_analytics.py --rows 1000 --output test_data.csv

# Generate reports
griot report all customer_analytics.py --output reports/
```

## Best Practices

### 1. Write Good Descriptions

```python
# ❌ Bad
age: int = Field(description="Age")

# ✅ Good
age: int = Field(
    description="Customer age calculated from date of birth, used for eligibility checks",
)
```

### 2. Always Set Primary Key

```python
# ❌ Missing primary key - lint warning
class BadContract(GriotModel):
    name: str = Field(description="Name")

# ✅ Has primary key
class GoodContract(GriotModel):
    id: str = Field(description="Unique identifier", primary_key=True)
    name: str = Field(description="Name")
```

### 3. Track All PII Fields

```python
# ❌ PII without metadata
email: str = Field(description="Email")

# ✅ PII with full compliance metadata
email: str = Field(
    description="Email",
    pii_category="email",
    sensitivity_level="confidential",
    masking_strategy="partial",
    legal_basis="consent",
    retention_days=730,
)
```

### 4. Use Glossary Terms

```python
# Link to business glossary for consistent terminology
revenue: float = Field(
    description="Total revenue",
    glossary_term="gross_revenue",
)
```

## Next Steps

- [Validation Guide](../guides/validation.md) - Advanced validation patterns
- [Privacy Compliance Guide](../guides/privacy-compliance.md) - GDPR/CCPA compliance
- [Reports Guide](../guides/reports.md) - Generating all report types
