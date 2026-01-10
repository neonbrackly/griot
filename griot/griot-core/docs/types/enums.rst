Enumerations
============

All enumeration types available in griot-core.

Validation Enums
----------------

ConstraintType
^^^^^^^^^^^^^^

Types of validation constraints that can fail.

.. code-block:: python

   from griot_core import ConstraintType

   # Check what type of constraint failed
   for error in result.errors:
       if error.constraint_type == ConstraintType.PATTERN:
           print(f"Pattern mismatch: {error.field}")
       elif error.constraint_type == ConstraintType.REQUIRED:
           print(f"Missing required: {error.field}")

**Values:**

- ``REQUIRED`` - Field is required but missing or null
- ``TYPE`` - Value has wrong data type
- ``PATTERN`` - String doesn't match regex pattern
- ``FORMAT`` - String doesn't match format (email, uuid, etc.)
- ``ENUM`` - Value not in allowed enumeration
- ``MIN_LENGTH`` - String shorter than minimum length
- ``MAX_LENGTH`` - String longer than maximum length
- ``MINIMUM`` - Number below minimum (ge/gt constraint)
- ``MAXIMUM`` - Number above maximum (le/lt constraint)
- ``MULTIPLE_OF`` - Number not divisible by specified value
- ``MIN_ITEMS`` - Array has fewer items than minimum
- ``MAX_ITEMS`` - Array has more items than maximum
- ``UNIQUE_ITEMS`` - Array contains duplicate items
- ``CUSTOM`` - Custom validation rule failed

Severity
^^^^^^^^

Severity levels for validation errors and lint issues.

.. code-block:: python

   from griot_core import Severity

   # Filter by severity
   errors = [e for e in result.errors if e.severity == Severity.ERROR]
   warnings = [e for e in result.errors if e.severity == Severity.WARNING]

**Values:**

- ``ERROR`` - Critical error, data is invalid
- ``WARNING`` - Non-critical issue, may need attention
- ``INFO`` - Informational note

FieldFormat
^^^^^^^^^^^

Built-in string format validators.

.. code-block:: python

   from griot_core import Field

   email: str = Field(format="email")
   uuid: str = Field(format="uuid")
   date: str = Field(format="date")

**Values:**

- ``EMAIL`` - Email address (RFC 5322)
- ``URI`` - URI/URL
- ``UUID`` - UUID v4 format
- ``DATE`` - ISO 8601 date (YYYY-MM-DD)
- ``TIME`` - ISO 8601 time (HH:MM:SS)
- ``DATETIME`` - ISO 8601 datetime
- ``IPV4`` - IPv4 address
- ``IPV6`` - IPv6 address
- ``HOSTNAME`` - DNS hostname
- ``PHONE`` - Phone number (E.164)

DataType
^^^^^^^^

Supported data types for fields.

**Values:**

- ``STRING`` - Text/string data
- ``INTEGER`` - Integer numbers
- ``FLOAT`` - Decimal/floating point numbers
- ``BOOLEAN`` - Boolean (true/false)
- ``ARRAY`` - List/array of values
- ``OBJECT`` - Dictionary/object

AggregationType
^^^^^^^^^^^^^^^

Hints for how fields should be aggregated in analytics.

.. code-block:: python

   from griot_core import Field, AggregationType

   revenue: float = Field(
       description="Revenue",
       aggregation=AggregationType.SUM
   )

**Values:**

- ``SUM`` - Sum of values
- ``AVERAGE`` - Mean/average of values
- ``COUNT`` - Count of records
- ``COUNT_DISTINCT`` - Count of unique values
- ``MIN`` - Minimum value
- ``MAX`` - Maximum value
- ``FIRST`` - First value in group
- ``LAST`` - Last value in group

PII/Privacy Enums
-----------------

PIICategory
^^^^^^^^^^^

Categories of Personally Identifiable Information.

.. code-block:: python

   from griot_core import Field, PIICategory

   email: str = Field(
       description="Email",
       pii_category=PIICategory.EMAIL
   )

**Values:**

- ``NAME`` - Personal names (first, last, full)
- ``EMAIL`` - Email addresses
- ``PHONE`` - Phone numbers
- ``ADDRESS`` - Physical/mailing addresses
- ``SSN`` - Social Security Numbers
- ``PASSPORT`` - Passport numbers
- ``DRIVERS_LICENSE`` - Driver's license numbers
- ``CREDIT_CARD`` - Credit/debit card numbers
- ``BANK_ACCOUNT`` - Bank account numbers
- ``DATE_OF_BIRTH`` - Birth dates
- ``IP_ADDRESS`` - IP addresses
- ``DEVICE_ID`` - Device identifiers
- ``BIOMETRIC`` - Biometric data (fingerprints, face)
- ``HEALTH`` - Health/medical information
- ``GENETIC`` - Genetic data
- ``LOCATION`` - Geolocation data
- ``FINANCIAL`` - General financial information
- ``ETHNIC`` - Racial/ethnic origin
- ``POLITICAL`` - Political opinions
- ``RELIGIOUS`` - Religious beliefs
- ``SEXUAL`` - Sexual orientation
- ``UNION`` - Trade union membership
- ``OTHER`` - Other PII

SensitivityLevel
^^^^^^^^^^^^^^^^

Data sensitivity classification levels.

.. code-block:: python

   from griot_core import Field, SensitivityLevel

   ssn: str = Field(
       description="SSN",
       sensitivity=SensitivityLevel.RESTRICTED
   )

**Values (increasing sensitivity):**

- ``PUBLIC`` - Can be freely shared, no restrictions
- ``INTERNAL`` - Internal use only, not for external sharing
- ``CONFIDENTIAL`` - Limited access, business sensitive
- ``RESTRICTED`` - Highly restricted, regulatory requirements

MaskingStrategy
^^^^^^^^^^^^^^^

Strategies for masking PII in outputs.

.. code-block:: python

   from griot_core import Field, MaskingStrategy

   email: str = Field(
       description="Email",
       masking_strategy=MaskingStrategy.PARTIAL_MASK
   )
   # Output: j***@example.com

**Values:**

- ``NONE`` - No masking applied
- ``REDACT`` - Complete removal, replaced with "[REDACTED]"
- ``PARTIAL_MASK`` - Partial masking (e.g., "j***@example.com")
- ``HASH`` - One-way hash for consistent linkage
- ``TOKENIZE`` - Replace with reversible token
- ``GENERALIZE`` - Replace with less specific value (age ranges)
- ``ENCRYPT`` - Encrypt the value
- ``PSEUDONYMIZE`` - Replace with pseudonym

LegalBasis
^^^^^^^^^^

Legal basis for processing personal data (GDPR Article 6).

.. code-block:: python

   from griot_core import Field, LegalBasis

   email: str = Field(
       description="Email for contract",
       legal_basis=LegalBasis.CONTRACT
   )

**Values:**

- ``CONSENT`` - Data subject has given explicit consent
- ``CONTRACT`` - Necessary for performance of a contract
- ``LEGAL_OBLIGATION`` - Required by law
- ``VITAL_INTEREST`` - Protect vital interests of data subject
- ``PUBLIC_TASK`` - Public interest or official authority
- ``LEGITIMATE_INTEREST`` - Legitimate business interest

Residency Enums
---------------

DataRegion
^^^^^^^^^^

Geographic data regions for residency rules.

.. code-block:: python

   from griot_core import DataRegion, ResidencyRule

   rule = ResidencyRule(
       allowed_regions=[DataRegion.US, DataRegion.EU]
   )

**Values:**

- ``US`` - United States
- ``EU`` - European Union / EEA
- ``UK`` - United Kingdom
- ``CA`` - Canada
- ``AU`` - Australia
- ``JP`` - Japan
- ``SG`` - Singapore
- ``BR`` - Brazil
- ``IN`` - India
- ``CN`` - China
- ``RU`` - Russia
- ``GLOBAL`` - Any region allowed
