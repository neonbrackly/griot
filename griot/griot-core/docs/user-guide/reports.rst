Report Generation
=================

griot-core provides four types of reports for analyzing your data contracts:
Analytics, AI Readiness, Audit, and Combined Readiness.

Analytics Report
----------------

Analyze the structure and characteristics of your contract:

.. code-block:: python

   from griot_core import GriotModel, Field, generate_analytics_report

   class Product(GriotModel):
       product_id: str = Field(description="Product ID", primary_key=True)
       name: str = Field(description="Product name", max_length=255)
       price: float = Field(description="Price", ge=0, unit="USD")
       category: str = Field(description="Category", enum=["electronics", "clothing", "food"])
       in_stock: bool = Field(description="Stock status")

   # Generate analytics report
   analytics = generate_analytics_report(Product)

   print(f"Contract: {analytics.contract_name}")
   print(f"Total fields: {analytics.total_fields}")
   print(f"Required fields: {analytics.required_field_count}")
   print(f"Nullable fields: {analytics.nullable_field_count}")
   print(f"PII fields: {analytics.pii_field_count}")

   # Field type breakdown
   print("\nField Types:")
   for type_name, count in analytics.field_types.items():
       print(f"  {type_name}: {count}")

   # Constraint coverage
   print(f"\nConstraint coverage: {analytics.constraint_coverage:.1%}")

Analytics Report Fields
^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Field
     - Description
   * - ``contract_name``
     - Name of the contract
   * - ``total_fields``
     - Total number of fields
   * - ``required_field_count``
     - Number of required fields
   * - ``nullable_field_count``
     - Number of nullable fields
   * - ``pii_field_count``
     - Number of PII fields
   * - ``primary_key_count``
     - Number of primary key fields
   * - ``field_types``
     - Dict of type -> count
   * - ``constraint_coverage``
     - Percentage of fields with constraints
   * - ``description_coverage``
     - Percentage of fields with descriptions
   * - ``example_coverage``
     - Percentage of fields with examples

AI Readiness Report
-------------------

Assess how ready your contract is for AI/LLM consumption:

.. code-block:: python

   from griot_core import generate_ai_readiness_report

   ai_report = generate_ai_readiness_report(Product)

   print(f"AI Readiness Score: {ai_report.overall_score:.1f}%")
   print(f"Grade: {ai_report.overall_grade}")

   # Component scores
   print("\nComponent Scores:")
   print(f"  Semantic coverage: {ai_report.semantic_score:.1f}%")
   print(f"  Description quality: {ai_report.description_score:.1f}%")
   print(f"  Example coverage: {ai_report.example_score:.1f}%")
   print(f"  Type clarity: {ai_report.type_score:.1f}%")

   # Recommendations
   print("\nRecommendations:")
   for rec in ai_report.recommendations:
       print(f"  - {rec}")

AI Readiness Criteria
^^^^^^^^^^^^^^^^^^^^^

The AI readiness score is based on:

1. **Semantic Coverage** (30%): Do fields have clear, descriptive names?
2. **Description Quality** (30%): Are descriptions complete and informative?
3. **Example Coverage** (20%): Do fields have example values?
4. **Type Clarity** (20%): Are types and constraints well-defined?

Grade scale:

- **A**: 90-100% (Excellent for AI consumption)
- **B**: 80-89% (Good, minor improvements possible)
- **C**: 70-79% (Acceptable, needs work)
- **D**: 60-69% (Poor AI readiness)
- **F**: Below 60% (Not suitable for AI)

Audit Report
------------

Generate a compliance and privacy audit:

.. code-block:: python

   from griot_core import (
       GriotModel, Field,
       PIICategory, SensitivityLevel, MaskingStrategy, LegalBasis,
       generate_audit_report
   )

   class CustomerRecord(GriotModel):
       customer_id: str = Field(description="Customer ID", primary_key=True)
       email: str = Field(
           description="Email",
           pii_category=PIICategory.EMAIL,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONTRACT
       )
       ssn: str = Field(
           description="SSN",
           pii_category=PIICategory.SSN,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.LEGAL_OBLIGATION,
           retention_days=2555
       )

   # Generate audit report
   audit = generate_audit_report(CustomerRecord)

   print(f"Compliance Score: {audit.compliance_score:.1f}%")
   print(f"Compliance Grade: {audit.compliance_grade}")
   print(f"Status: {audit.compliance_status}")

   # PII inventory
   print(f"\nPII Fields: {audit.pii_field_count}")
   for field in audit.pii_fields:
       print(f"  - {field['name']}: {field['category']}")

   # Regulatory readiness
   print("\nRegulatory Readiness:")
   print(f"  GDPR: {'Ready' if audit.gdpr_ready else 'Not Ready'}")
   print(f"  CCPA: {'Ready' if audit.ccpa_ready else 'Not Ready'}")
   print(f"  HIPAA: {'Ready' if audit.hipaa_ready else 'Not Ready'}")

   # Recommendations
   print("\nRecommendations:")
   for rec in audit.recommendations:
       print(f"  - {rec}")

Audit Report Fields
^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Field
     - Description
   * - ``compliance_score``
     - Overall compliance score (0-100)
   * - ``compliance_grade``
     - Letter grade (A-F)
   * - ``compliance_status``
     - Status: compliant, partial, non_compliant
   * - ``pii_field_count``
     - Number of PII fields
   * - ``pii_fields``
     - List of PII field details
   * - ``pii_categories``
     - Dict of category -> count
   * - ``sensitivity_breakdown``
     - Dict of sensitivity level -> count
   * - ``masking_coverage``
     - Percentage of PII with masking
   * - ``legal_basis_coverage``
     - Percentage of PII with legal basis
   * - ``retention_coverage``
     - Percentage with retention periods
   * - ``gdpr_ready``
     - GDPR compliance readiness
   * - ``ccpa_ready``
     - CCPA compliance readiness
   * - ``hipaa_ready``
     - HIPAA compliance readiness

Compliance Score Calculation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The compliance score weighs:

- **PII Documentation** (40%): Are all PII fields properly classified?
- **Lineage Documentation** (20%): Is data lineage tracked?
- **Regulatory Coverage** (40%): Legal basis, masking, retention

Combined Readiness Report
-------------------------

Get a comprehensive assessment combining all reports:

.. code-block:: python

   from griot_core import generate_readiness_report

   readiness = generate_readiness_report(CustomerRecord)

   print(f"Overall Score: {readiness.overall_score:.1f}%")
   print(f"Overall Grade: {readiness.overall_grade}")
   print(f"Status: {readiness.readiness_status}")

   # Component scores
   print("\nComponent Scores:")
   print(f"  Data Quality: {readiness.data_quality_score:.1f}%")
   print(f"  AI Readiness: {readiness.ai_readiness_score:.1f}%")
   print(f"  Compliance: {readiness.compliance_score:.1f}%")

   # Access individual reports
   if readiness.analytics_report:
       print(f"\nTotal fields: {readiness.analytics_report.total_fields}")

   if readiness.ai_report:
       print(f"AI grade: {readiness.ai_report.overall_grade}")

   if readiness.audit_report:
       print(f"GDPR ready: {readiness.audit_report.gdpr_ready}")

   # Consolidated recommendations
   print("\nAll Recommendations:")
   for rec in readiness.recommendations:
       print(f"  - {rec}")

Overall Score Calculation
^^^^^^^^^^^^^^^^^^^^^^^^^

The overall readiness score weighs:

- **Data Quality** (30%): From analytics report
- **AI Readiness** (35%): From AI readiness report
- **Compliance** (35%): From audit report

Export Formats
--------------

All reports support multiple export formats:

.. code-block:: python

   # As dictionary
   report_dict = audit.to_dict()

   # As JSON
   report_json = audit.to_json()

   # As Markdown
   report_md = audit.to_markdown()

   # Pretty print
   print(audit.to_markdown())

Markdown output example:

.. code-block:: markdown

   # Compliance Audit Report: CustomerRecord

   **Generated:** 2026-01-10T14:30:00Z
   **Score:** 85.0%
   **Grade:** B
   **Status:** Partial Compliance

   ## PII Inventory

   | Field | Category | Sensitivity | Masking | Legal Basis |
   |-------|----------|-------------|---------|-------------|
   | email | EMAIL | CONFIDENTIAL | PARTIAL_MASK | CONTRACT |
   | ssn | SSN | RESTRICTED | REDACT | LEGAL_OBLIGATION |

   ## Regulatory Readiness

   - GDPR: Ready
   - CCPA: Ready
   - HIPAA: Not Ready

   ## Recommendations

   - Add retention periods to all PII fields
   - Document data residency requirements

Batch Report Generation
-----------------------

Generate reports for multiple contracts:

.. code-block:: python

   from griot_core import (
       generate_analytics_report,
       generate_ai_readiness_report,
       generate_audit_report,
       generate_readiness_report
   )

   contracts = [CustomerRecord, Product, Order, Transaction]

   # Generate reports for all contracts
   for contract in contracts:
       readiness = generate_readiness_report(contract)
       print(f"{contract.__name__}: {readiness.overall_grade} ({readiness.overall_score:.0f}%)")

   # Find contracts needing attention
   needs_work = [
       c for c in contracts
       if generate_readiness_report(c).overall_score < 80
   ]
   print(f"\nContracts needing improvement: {[c.__name__ for c in needs_work]}")
