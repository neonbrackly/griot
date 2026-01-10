# Privacy Compliance Guide

Implement privacy compliance with Griot's built-in PII tracking and data governance features.

## PII Categories

Mark fields with their PII category:

```python
from griot_core import GriotModel, Field

class Customer(GriotModel):
    id: str = Field(description="ID", primary_key=True)

    # PII fields
    email: str = Field(
        description="Email address",
        pii_category="email",
    )
    phone: str = Field(
        description="Phone number",
        pii_category="phone",
    )
    ssn: str = Field(
        description="Social Security Number",
        pii_category="ssn",
    )
```

Available PII categories:
- `none` - Not PII
- `name` - Personal name
- `email` - Email address
- `phone` - Phone number
- `ssn` - Social Security Number
- `address` - Physical address
- `dob` - Date of birth
- `financial` - Financial data
- `health` - Health information
- `biometric` - Biometric data
- `genetic` - Genetic data
- `location` - Location data
- `ip_address` - IP address
- `device_id` - Device identifier
- `other` - Other PII

## Sensitivity Levels

Classify data sensitivity:

```python
email: str = Field(
    description="Email",
    pii_category="email",
    sensitivity_level="confidential",
)
```

Levels (lowest to highest):
- `public` - Publicly available
- `internal` - Internal use only
- `confidential` - Confidential data
- `restricted` - Highly restricted

## Masking Strategies

Define how PII should be masked:

```python
ssn: str = Field(
    description="SSN",
    pii_category="ssn",
    masking_strategy="hash",
)
```

Strategies:
- `none` - No masking
- `redact` - Full redaction
- `partial` - Partial masking (e.g., `***@example.com`)
- `hash` - Cryptographic hash
- `encrypt` - Encryption
- `tokenize` - Tokenization
- `generalize` - Generalization
- `pseudonymize` - Pseudonymization

## Legal Basis

Document the legal basis for processing:

```python
email: str = Field(
    description="Email for marketing",
    pii_category="email",
    legal_basis="consent",
    consent_required=True,
)
```

Legal bases:
- `none` - Not specified
- `consent` - User consent
- `contract` - Contractual necessity
- `legal_obligation` - Legal requirement
- `vital_interest` - Vital interests
- `public_interest` - Public interest
- `legitimate_interest` - Legitimate interest

## Retention Periods

Set data retention:

```python
email: str = Field(
    description="Email",
    pii_category="email",
    retention_days=730,  # 2 years
)
```

## PII Inventory

Get a list of all PII fields:

```python
pii_fields = Customer.pii_inventory()

for field in pii_fields:
    print(f"Field: {field.name}")
    print(f"  Category: {field.pii_category}")
    print(f"  Sensitivity: {field.sensitivity_level}")
```

## Sensitive Fields

Get fields above a sensitivity threshold:

```python
sensitive = Customer.sensitive_fields()

for field in sensitive:
    print(f"{field.name}: {field.sensitivity_level}")
```

## PII Summary

Get a comprehensive PII summary:

```python
summary = Customer.pii_summary()

print(f"Total fields: {summary['total_fields']}")
print(f"PII fields: {summary['pii_field_count']}")
print(f"Categories: {summary['categories']}")
print(f"Sensitivity levels: {summary['sensitivity_levels']}")
print(f"Masking strategies: {summary['masking_strategies']}")
print(f"Consent required: {summary['consent_required']}")
print(f"Retention periods: {summary['retention_periods']}")
```

## Data Residency

Configure regional data storage requirements:

```python
from griot_core.types import DataRegion, ResidencyConfig, ResidencyRule

residency = ResidencyConfig(
    rules=[
        ResidencyRule(
            regions=[DataRegion.EU],
            field_patterns=["*"],  # All fields
            required=True,
        ),
    ],
    default_region=DataRegion.EU,
)

# Check if storage location is compliant
is_compliant = residency.check_residency(
    field="email",
    storage_location="s3://eu-west-1-bucket/data/",
)
```

## Compliance Reports

Generate compliance reports:

```python
from griot_core.reports import generate_analytics_report

report = generate_analytics_report(Customer)

# Check PII fields
print(f"PII fields: {report.pii_fields}")
print(f"Sensitivity breakdown: {report.sensitive_fields}")
```

## GDPR/CCPA Checklist

Use Griot for compliance:

| Requirement | Griot Feature |
|-------------|---------------|
| Data inventory | `pii_inventory()` |
| Lawful basis | `legal_basis` field |
| Consent tracking | `consent_required` field |
| Data minimization | Contract constraints |
| Retention limits | `retention_days` field |
| Access requests | Contract documentation |
| Masking/anonymization | `masking_strategy` field |
