# Reports Guide

Generate comprehensive reports for stakeholders with Griot.

## Report Types

Griot provides several report types:

| Report | Purpose |
|--------|---------|
| Analytics | Schema analysis, field distributions, constraints |
| AI Readiness | Score contracts for AI/ML consumption |
| Audit | Privacy compliance, PII inventory |
| Combined | All reports in one |

## Analytics Report

Analyze contract structure and quality:

```python
from griot_core.reports import generate_analytics_report

report = generate_analytics_report(Customer)

# Access report data
print(f"Total fields: {report.total_fields}")
print(f"Primary key: {report.primary_key}")
print(f"Field types: {report.field_types}")
print(f"Constraints: {report.constraint_types}")
print(f"Documentation: {report.documented_fields}/{report.total_fields}")

# Export
print(report.to_markdown())
print(report.to_json())
```

### Analytics Report Contents

- **Summary**: Total fields, types, nullable fields
- **Keys**: Primary key, unique fields
- **Constraints**: Min/max, patterns, enums
- **Documentation**: Coverage, descriptions
- **PII**: PII fields, categories, sensitivity
- **Recommendations**: Improvement suggestions

## AI Readiness Report

Evaluate contract quality for AI/ML systems:

```python
from griot_core.reports import generate_ai_readiness_report

report = generate_ai_readiness_report(Customer)

# Overall score
print(f"Score: {report.readiness_score}/100")
print(f"Grade: {report.readiness_grade}")

# Component scores
print(f"Documentation: {report.documentation_score}")
print(f"Type clarity: {report.type_clarity_score}")
print(f"Constraint coverage: {report.constraint_coverage_score}")
print(f"Semantic richness: {report.semantic_richness_score}")
print(f"Privacy clarity: {report.privacy_clarity_score}")

# Strengths and weaknesses
print(f"Strengths: {report.strengths}")
print(f"Weaknesses: {report.weaknesses}")

# Recommendations
for rec in report.recommendations:
    print(f"[{rec['priority']}] {rec['action']}")
```

### Scoring Components

| Component | Weight | Measures |
|-----------|--------|----------|
| Documentation | 25% | Description quality, docstrings |
| Type Clarity | 20% | Explicit types, format specifications |
| Constraint Coverage | 20% | Constraints per field |
| Semantic Richness | 20% | Units, glossary terms, aggregations |
| Privacy Clarity | 15% | PII tracking, sensitivity levels |

### Grade Scale

| Score | Grade |
|-------|-------|
| 90-100 | A |
| 80-89 | B |
| 70-79 | C |
| 60-69 | D |
| 0-59 | F |

## Export Formats

All reports support multiple formats:

```python
# Markdown (human-readable)
markdown = report.to_markdown()

# JSON (machine-readable)
json_str = report.to_json()

# Dictionary
data = report.to_dict()
```

## CLI Reports

Generate reports from the command line:

```bash
# Analytics report
griot report analytics customer.yaml

# AI readiness report
griot report ai customer.yaml

# Audit report
griot report audit customer.yaml

# All reports combined
griot report all customer.yaml

# Output to file
griot report all customer.yaml --output reports/

# JSON format
griot report analytics customer.yaml --format json
```

## Improving Scores

### Documentation Score

```python
# ❌ Low score
name: str = Field(description="Name")

# ✅ High score
name: str = Field(
    description="Customer's full legal name as registered in the system",
)
```

### Constraint Coverage

```python
# ❌ Low score
age: int = Field(description="Age")

# ✅ High score
age: int = Field(
    description="Age",
    ge=0,
    le=150,
)
```

### Semantic Richness

```python
# ❌ Low score
revenue: float = Field(description="Revenue")

# ✅ High score
revenue: float = Field(
    description="Monthly recurring revenue",
    unit="USD",
    aggregation="sum",
    glossary_term="mrr",
)
```

### Privacy Clarity

```python
# ❌ Low score (PII without metadata)
email: str = Field(description="Email")

# ✅ High score
email: str = Field(
    description="Email",
    pii_category="email",
    sensitivity_level="confidential",
    masking_strategy="partial",
    legal_basis="consent",
)
```

## Automated Quality Gates

Use reports in CI/CD:

```python
report = generate_ai_readiness_report(MyContract)

# Fail if score below threshold
if report.readiness_score < 70:
    raise ValueError(f"AI readiness score {report.readiness_score} below threshold 70")
```

```bash
# CLI with exit code
griot report ai contract.yaml --min-score 70
```
