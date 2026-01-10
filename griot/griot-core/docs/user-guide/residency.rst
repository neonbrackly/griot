Data Residency
==============

griot-core supports data residency configuration for geographic compliance requirements
like GDPR, data sovereignty laws, and organizational policies.

Basic Residency Configuration
-----------------------------

Add residency rules to your contract:

.. code-block:: python

   from griot_core import (
       GriotModel, Field,
       DataRegion, ResidencyConfig, ResidencyRule
   )

   class CustomerData(GriotModel):
       """Customer data with EU residency requirement."""

       class Meta:
           residency = ResidencyConfig(
               default_rule=ResidencyRule(
                   allowed_regions=[DataRegion.EU, DataRegion.US]
               )
           )

       customer_id: str = Field(description="Customer ID", primary_key=True)
       email: str = Field(description="Email")
       country: str = Field(description="Customer country")

Available Data Regions
----------------------

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Region
     - Code
     - Description
   * - ``US``
     - United States
     - US data centers
   * - ``EU``
     - European Union
     - EU/EEA data centers
   * - ``UK``
     - United Kingdom
     - UK data centers (post-Brexit)
   * - ``CA``
     - Canada
     - Canadian data centers
   * - ``AU``
     - Australia
     - Australian data centers
   * - ``JP``
     - Japan
     - Japanese data centers
   * - ``SG``
     - Singapore
     - Singapore data centers
   * - ``BR``
     - Brazil
     - Brazilian data centers
   * - ``IN``
     - India
     - Indian data centers
   * - ``CN``
     - China
     - China mainland data centers
   * - ``RU``
     - Russia
     - Russian data centers
   * - ``GLOBAL``
     - Global
     - Any region allowed

Default Rules
-------------

Set default residency rules that apply to all fields:

.. code-block:: python

   class GlobalData(GriotModel):
       class Meta:
           residency = ResidencyConfig(
               default_rule=ResidencyRule(
                   # Allow these regions
                   allowed_regions=[
                       DataRegion.US,
                       DataRegion.EU,
                       DataRegion.UK,
                       DataRegion.CA
                   ],
                   # Block these regions
                   prohibited_regions=[
                       DataRegion.CN,
                       DataRegion.RU
                   ]
               )
           )

       # All fields inherit the default rule
       data_field: str = Field(description="Some data")

Field-Specific Rules
--------------------

Override residency rules for specific fields:

.. code-block:: python

   class EUCustomer(GriotModel):
       """EU customer data with strict residency."""

       class Meta:
           residency = ResidencyConfig(
               # Default: US or EU
               default_rule=ResidencyRule(
                   allowed_regions=[DataRegion.US, DataRegion.EU]
               ),
               # Field-specific overrides
               field_rules={
                   # EU PII must stay in EU
                   "email": ResidencyRule(
                       allowed_regions=[DataRegion.EU],
                       required_encryption=True
                   ),
                   "address": ResidencyRule(
                       allowed_regions=[DataRegion.EU]
                   ),
                   # Non-PII can be anywhere
                   "customer_id": ResidencyRule(
                       allowed_regions=[DataRegion.GLOBAL]
                   )
               }
           )

       customer_id: str = Field(description="Customer ID")
       email: str = Field(description="Email", pii_category=PIICategory.EMAIL)
       address: str = Field(description="Address", pii_category=PIICategory.ADDRESS)
       order_count: int = Field(description="Total orders")

Encryption Requirements
-----------------------

Require encryption for data in transit or at rest:

.. code-block:: python

   class SensitiveData(GriotModel):
       class Meta:
           residency = ResidencyConfig(
               default_rule=ResidencyRule(
                   allowed_regions=[DataRegion.US],
                   required_encryption=True  # Require encryption
               )
           )

       # All fields require encryption
       secret_data: str = Field(description="Encrypted data")

Checking Residency Compliance
-----------------------------

Validate data storage locations:

.. code-block:: python

   # Check if a region is compliant
   is_valid = CustomerData.check_residency(DataRegion.EU)
   print(f"EU storage allowed: {is_valid}")  # True

   # Check specific field
   is_valid = CustomerData.check_residency(
       DataRegion.US,
       field="email"
   )

   # Check with storage URI
   is_valid = CustomerData.check_residency_uri(
       "s3://my-bucket-eu-west-1/data/"
   )

URI-Based Region Detection
--------------------------

griot-core can detect regions from cloud storage URIs:

.. code-block:: python

   from griot_core import detect_region_from_uri

   # AWS S3
   region = detect_region_from_uri("s3://bucket-eu-west-1/path/")
   # Returns: DataRegion.EU

   # Azure Blob
   region = detect_region_from_uri(
       "https://account.blob.core.windows.net/container/"
   )

   # GCP GCS
   region = detect_region_from_uri("gs://bucket-us/path/")

Supported URI patterns:

- **AWS S3**: ``s3://bucket-{region}/...``
- **Azure Blob**: ``https://{account}.blob.core.windows.net/...``
- **GCP GCS**: ``gs://bucket/...``

GDPR Compliance Pattern
-----------------------

Configure for GDPR compliance:

.. code-block:: python

   from griot_core import (
       GriotModel, Field,
       PIICategory, SensitivityLevel, MaskingStrategy, LegalBasis,
       DataRegion, ResidencyConfig, ResidencyRule
   )

   class GDPRCustomer(GriotModel):
       """GDPR-compliant customer data contract."""

       class Meta:
           description = "EU customer data with GDPR compliance"
           residency = ResidencyConfig(
               # Default: EU only
               default_rule=ResidencyRule(
                   allowed_regions=[DataRegion.EU],
                   required_encryption=True
               ),
               field_rules={
                   # Allow UK for adequacy decision
                   "customer_id": ResidencyRule(
                       allowed_regions=[DataRegion.EU, DataRegion.UK]
                   )
               }
           )

       customer_id: str = Field(
           description="Customer identifier",
           primary_key=True
       )

       email: str = Field(
           description="Email address",
           format="email",
           pii_category=PIICategory.EMAIL,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           legal_basis=LegalBasis.CONTRACT
       )

       name: str = Field(
           description="Full name",
           pii_category=PIICategory.NAME,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.CONTRACT
       )

   # Verify GDPR compliance
   audit = generate_audit_report(GDPRCustomer)
   print(f"GDPR ready: {audit.gdpr_ready}")

Multi-Region Strategy
---------------------

For organizations with global presence:

.. code-block:: python

   class GlobalCustomer(GriotModel):
       """Multi-region customer data."""

       class Meta:
           residency = ResidencyConfig(
               default_rule=ResidencyRule(
                   # Non-PII can go anywhere except restricted regions
                   allowed_regions=[
                       DataRegion.US, DataRegion.EU, DataRegion.UK,
                       DataRegion.CA, DataRegion.AU, DataRegion.JP, DataRegion.SG
                   ],
                   prohibited_regions=[DataRegion.CN, DataRegion.RU]
               ),
               field_rules={
                   # EU customer PII stays in EU
                   "eu_customer_email": ResidencyRule(
                       allowed_regions=[DataRegion.EU]
                   ),
                   # US customer PII stays in US
                   "us_customer_email": ResidencyRule(
                       allowed_regions=[DataRegion.US]
                   ),
                   # Financial data: US, EU, or UK only
                   "payment_info": ResidencyRule(
                       allowed_regions=[DataRegion.US, DataRegion.EU, DataRegion.UK],
                       required_encryption=True
                   )
               }
           )

       customer_id: str = Field(description="Global customer ID")
       customer_region: str = Field(description="Customer's region", enum=["US", "EU", "APAC"])
       eu_customer_email: str = Field(description="EU customer email", nullable=True)
       us_customer_email: str = Field(description="US customer email", nullable=True)
       payment_info: str = Field(description="Encrypted payment info")

Residency in Reports
--------------------

Residency compliance is included in audit reports:

.. code-block:: python

   from griot_core import generate_audit_report

   audit = generate_audit_report(GDPRCustomer)

   print("Residency Configuration:")
   print(f"  Default regions: {audit.residency_regions}")
   print(f"  Fields with overrides: {audit.residency_field_overrides}")
   print(f"  Encryption required: {audit.residency_encryption_required}")

   print("\nRegulatory Readiness:")
   print(f"  GDPR ready: {audit.gdpr_ready}")
   print(f"  CCPA ready: {audit.ccpa_ready}")
