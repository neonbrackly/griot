PII and Sensitivity Configuration
==================================

griot-core provides built-in support for tracking Personally Identifiable Information (PII)
and data sensitivity levels for compliance with GDPR, CCPA, HIPAA, and other regulations.

PII Categories
--------------

Mark fields with their PII category:

.. code-block:: python

   from griot_core import GriotModel, Field, PIICategory

   class Customer(GriotModel):
       customer_id: str = Field(description="Customer ID", primary_key=True)

       # Email PII
       email: str = Field(
           description="Customer email",
           pii_category=PIICategory.EMAIL
       )

       # Name PII
       full_name: str = Field(
           description="Full legal name",
           pii_category=PIICategory.NAME
       )

       # SSN (highly sensitive)
       ssn: str = Field(
           description="Social Security Number",
           pii_category=PIICategory.SSN
       )

       # Address
       address: str = Field(
           description="Mailing address",
           pii_category=PIICategory.ADDRESS
       )

Available PII Categories
^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Category
     - Description
   * - ``NAME``
     - Personal names (first, last, full)
   * - ``EMAIL``
     - Email addresses
   * - ``PHONE``
     - Phone numbers
   * - ``ADDRESS``
     - Physical addresses
   * - ``SSN``
     - Social Security Numbers
   * - ``PASSPORT``
     - Passport numbers
   * - ``DRIVERS_LICENSE``
     - Driver's license numbers
   * - ``CREDIT_CARD``
     - Credit/debit card numbers
   * - ``BANK_ACCOUNT``
     - Bank account numbers
   * - ``DATE_OF_BIRTH``
     - Birth dates
   * - ``IP_ADDRESS``
     - IP addresses
   * - ``DEVICE_ID``
     - Device identifiers
   * - ``BIOMETRIC``
     - Biometric data (fingerprints, face, etc.)
   * - ``HEALTH``
     - Health/medical information
   * - ``GENETIC``
     - Genetic data
   * - ``LOCATION``
     - Geolocation data
   * - ``FINANCIAL``
     - General financial information
   * - ``ETHNIC``
     - Racial/ethnic origin
   * - ``POLITICAL``
     - Political opinions
   * - ``RELIGIOUS``
     - Religious beliefs
   * - ``SEXUAL``
     - Sexual orientation
   * - ``UNION``
     - Trade union membership
   * - ``OTHER``
     - Other PII not categorized

Sensitivity Levels
------------------

Classify data sensitivity:

.. code-block:: python

   from griot_core import SensitivityLevel

   class Patient(GriotModel):
       # Public data
       patient_id: str = Field(
           description="Patient ID",
           sensitivity=SensitivityLevel.PUBLIC
       )

       # Internal use only
       admission_date: str = Field(
           description="Admission date",
           sensitivity=SensitivityLevel.INTERNAL
       )

       # Confidential
       diagnosis: str = Field(
           description="Primary diagnosis",
           pii_category=PIICategory.HEALTH,
           sensitivity=SensitivityLevel.CONFIDENTIAL
       )

       # Highly restricted
       ssn: str = Field(
           description="Social Security Number",
           pii_category=PIICategory.SSN,
           sensitivity=SensitivityLevel.RESTRICTED
       )

Sensitivity Level Hierarchy
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Level
     - Risk
     - Description
   * - ``PUBLIC``
     - Low
     - Can be freely shared
   * - ``INTERNAL``
     - Medium
     - Internal use only, not public
   * - ``CONFIDENTIAL``
     - High
     - Limited access, business sensitive
   * - ``RESTRICTED``
     - Critical
     - Highly restricted, regulatory requirements

Masking Strategies
------------------

Define how PII should be masked when displayed or exported:

.. code-block:: python

   from griot_core import MaskingStrategy

   class User(GriotModel):
       # Full redaction
       ssn: str = Field(
           description="SSN",
           pii_category=PIICategory.SSN,
           masking_strategy=MaskingStrategy.REDACT
       )
       # Result: "[REDACTED]"

       # Partial masking
       email: str = Field(
           description="Email",
           pii_category=PIICategory.EMAIL,
           masking_strategy=MaskingStrategy.PARTIAL_MASK
       )
       # Result: "j***@example.com"

       # Hash for linkage
       customer_id: str = Field(
           description="Customer ID for linking",
           masking_strategy=MaskingStrategy.HASH
       )
       # Result: "a1b2c3d4..." (consistent hash)

       # Tokenization
       credit_card: str = Field(
           description="Credit card",
           pii_category=PIICategory.CREDIT_CARD,
           masking_strategy=MaskingStrategy.TOKENIZE
       )
       # Result: "tok_abc123..."

       # Generalization
       age: int = Field(
           description="Age",
           masking_strategy=MaskingStrategy.GENERALIZE
       )
       # Result: "30-40" (age range)

Available Masking Strategies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Strategy
     - Description
   * - ``NONE``
     - No masking applied
   * - ``REDACT``
     - Complete removal, replaced with "[REDACTED]"
   * - ``PARTIAL_MASK``
     - Partial masking (e.g., "j***@example.com")
   * - ``HASH``
     - One-way hash for consistent linkage
   * - ``TOKENIZE``
     - Replace with reversible token
   * - ``GENERALIZE``
     - Replace with less specific value (ranges, categories)
   * - ``ENCRYPT``
     - Encrypt the value
   * - ``PSEUDONYMIZE``
     - Replace with pseudonym

Legal Basis
-----------

Document the legal basis for processing PII:

.. code-block:: python

   from griot_core import LegalBasis

   class CustomerData(GriotModel):
       # Necessary for contract
       email: str = Field(
           description="Email for order confirmation",
           pii_category=PIICategory.EMAIL,
           legal_basis=LegalBasis.CONTRACT
       )

       # User consented
       marketing_email: str = Field(
           description="Email for marketing",
           pii_category=PIICategory.EMAIL,
           legal_basis=LegalBasis.CONSENT,
           nullable=True
       )

       # Legal requirement
       tax_id: str = Field(
           description="Tax ID for reporting",
           legal_basis=LegalBasis.LEGAL_OBLIGATION
       )

       # Legitimate business interest
       ip_address: str = Field(
           description="IP for fraud detection",
           pii_category=PIICategory.IP_ADDRESS,
           legal_basis=LegalBasis.LEGITIMATE_INTEREST
       )

Legal Basis Options (GDPR Article 6)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Basis
     - Description
   * - ``CONSENT``
     - Data subject has given consent
   * - ``CONTRACT``
     - Necessary for contract performance
   * - ``LEGAL_OBLIGATION``
     - Required by law
   * - ``VITAL_INTEREST``
     - Protect vital interests
   * - ``PUBLIC_TASK``
     - Public interest or official authority
   * - ``LEGITIMATE_INTEREST``
     - Legitimate business interest

Retention Periods
-----------------

Specify how long PII should be retained:

.. code-block:: python

   class CustomerRecord(GriotModel):
       # Retain for 1 year
       email: str = Field(
           description="Email",
           pii_category=PIICategory.EMAIL,
           retention_days=365
       )

       # Retain for 7 years (tax requirement)
       tax_id: str = Field(
           description="Tax ID",
           retention_days=2555  # ~7 years
       )

       # No specific retention
       name: str = Field(
           description="Name",
           pii_category=PIICategory.NAME
           # retention_days not specified
       )

PII Inventory
-------------

Get a complete inventory of PII fields:

.. code-block:: python

   # Get all PII fields
   pii_fields = Customer.pii_inventory()

   for field in pii_fields:
       print(f"Field: {field.name}")
       print(f"  Category: {field.pii_category}")
       print(f"  Sensitivity: {field.sensitivity}")
       print(f"  Masking: {field.masking_strategy}")
       print(f"  Legal basis: {field.legal_basis}")
       print(f"  Retention: {field.retention_days} days")
       print("---")

Complete PII Example
--------------------

Here's a comprehensive example:

.. code-block:: python

   from griot_core import (
       GriotModel, Field,
       PIICategory, SensitivityLevel, MaskingStrategy, LegalBasis
   )

   class PatientRecord(GriotModel):
       """HIPAA-compliant patient record contract."""

       patient_id: str = Field(
           description="Patient identifier",
           primary_key=True,
           sensitivity=SensitivityLevel.INTERNAL
       )

       full_name: str = Field(
           description="Patient full name",
           pii_category=PIICategory.NAME,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.CONTRACT
       )

       date_of_birth: str = Field(
           description="Date of birth",
           format="date",
           pii_category=PIICategory.DATE_OF_BIRTH,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.GENERALIZE,
           legal_basis=LegalBasis.LEGAL_OBLIGATION
       )

       ssn: str = Field(
           description="Social Security Number",
           pattern=r"^\d{3}-\d{2}-\d{4}$",
           pii_category=PIICategory.SSN,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.REDACT,
           legal_basis=LegalBasis.LEGAL_OBLIGATION,
           retention_days=2555  # 7 years per HIPAA
       )

       diagnosis_code: str = Field(
           description="ICD-10 diagnosis code",
           pii_category=PIICategory.HEALTH,
           sensitivity=SensitivityLevel.RESTRICTED,
           masking_strategy=MaskingStrategy.ENCRYPT,
           legal_basis=LegalBasis.CONTRACT
       )

       email: str = Field(
           description="Contact email",
           format="email",
           pii_category=PIICategory.EMAIL,
           sensitivity=SensitivityLevel.CONFIDENTIAL,
           masking_strategy=MaskingStrategy.PARTIAL_MASK,
           legal_basis=LegalBasis.CONSENT,
           retention_days=365,
           nullable=True
       )

   # Generate PII inventory
   pii = PatientRecord.pii_inventory()
   print(f"Total PII fields: {len(pii)}")

   # Generate compliance audit
   from griot_core import generate_audit_report

   audit = generate_audit_report(PatientRecord)
   print(f"HIPAA ready: {audit.hipaa_ready}")
   print(f"Compliance score: {audit.compliance_score}%")
