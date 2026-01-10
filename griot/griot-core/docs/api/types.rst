Types
=====

Enumerations and type definitions.

ConstraintType
--------------

.. py:class:: griot_core.ConstraintType

   Types of validation constraints.

   .. py:attribute:: REQUIRED

      Field is required but missing.

   .. py:attribute:: TYPE

      Wrong data type.

   .. py:attribute:: PATTERN

      Regex pattern mismatch.

   .. py:attribute:: FORMAT

      Format validation failed.

   .. py:attribute:: ENUM

      Value not in allowed enum.

   .. py:attribute:: MIN_LENGTH

      String too short.

   .. py:attribute:: MAX_LENGTH

      String too long.

   .. py:attribute:: MINIMUM

      Number below minimum.

   .. py:attribute:: MAXIMUM

      Number above maximum.

   .. py:attribute:: MULTIPLE_OF

      Number not divisible.

   .. py:attribute:: MIN_ITEMS

      Array too short.

   .. py:attribute:: MAX_ITEMS

      Array too long.

   .. py:attribute:: UNIQUE_ITEMS

      Array has duplicates.

   .. py:attribute:: CUSTOM

      Custom validation failure.

Severity
--------

.. py:class:: griot_core.Severity

   Validation error severity levels.

   .. py:attribute:: ERROR

      Critical error, data is invalid.

   .. py:attribute:: WARNING

      Non-critical issue, data may be valid.

   .. py:attribute:: INFO

      Informational note.

FieldFormat
-----------

.. py:class:: griot_core.FieldFormat

   Built-in string format types.

   .. py:attribute:: EMAIL

      Email address format.

   .. py:attribute:: URI

      URI/URL format.

   .. py:attribute:: UUID

      UUID v4 format.

   .. py:attribute:: DATE

      ISO 8601 date (YYYY-MM-DD).

   .. py:attribute:: TIME

      ISO 8601 time (HH:MM:SS).

   .. py:attribute:: DATETIME

      ISO 8601 datetime.

   .. py:attribute:: IPV4

      IPv4 address.

   .. py:attribute:: IPV6

      IPv6 address.

   .. py:attribute:: HOSTNAME

      DNS hostname.

   .. py:attribute:: PHONE

      Phone number (E.164).

DataType
--------

.. py:class:: griot_core.DataType

   Supported data types.

   .. py:attribute:: STRING

      Text/string data.

   .. py:attribute:: INTEGER

      Integer numbers.

   .. py:attribute:: FLOAT

      Decimal numbers.

   .. py:attribute:: BOOLEAN

      Boolean values.

   .. py:attribute:: ARRAY

      List/array.

   .. py:attribute:: OBJECT

      Dictionary/object.

AggregationType
---------------

.. py:class:: griot_core.AggregationType

   Aggregation hints for analytics.

   .. py:attribute:: SUM

      Sum of values.

   .. py:attribute:: AVERAGE

      Mean of values.

   .. py:attribute:: COUNT

      Count of records.

   .. py:attribute:: COUNT_DISTINCT

      Count of unique values.

   .. py:attribute:: MIN

      Minimum value.

   .. py:attribute:: MAX

      Maximum value.

   .. py:attribute:: FIRST

      First value.

   .. py:attribute:: LAST

      Last value.

PIICategory
-----------

.. py:class:: griot_core.PIICategory

   PII classification categories.

   .. py:attribute:: NAME

      Personal names.

   .. py:attribute:: EMAIL

      Email addresses.

   .. py:attribute:: PHONE

      Phone numbers.

   .. py:attribute:: ADDRESS

      Physical addresses.

   .. py:attribute:: SSN

      Social Security Numbers.

   .. py:attribute:: PASSPORT

      Passport numbers.

   .. py:attribute:: DRIVERS_LICENSE

      Driver's license numbers.

   .. py:attribute:: CREDIT_CARD

      Credit/debit card numbers.

   .. py:attribute:: BANK_ACCOUNT

      Bank account numbers.

   .. py:attribute:: DATE_OF_BIRTH

      Birth dates.

   .. py:attribute:: IP_ADDRESS

      IP addresses.

   .. py:attribute:: DEVICE_ID

      Device identifiers.

   .. py:attribute:: BIOMETRIC

      Biometric data.

   .. py:attribute:: HEALTH

      Health/medical information.

   .. py:attribute:: GENETIC

      Genetic data.

   .. py:attribute:: LOCATION

      Geolocation data.

   .. py:attribute:: FINANCIAL

      Financial information.

   .. py:attribute:: ETHNIC

      Racial/ethnic origin.

   .. py:attribute:: POLITICAL

      Political opinions.

   .. py:attribute:: RELIGIOUS

      Religious beliefs.

   .. py:attribute:: SEXUAL

      Sexual orientation.

   .. py:attribute:: UNION

      Trade union membership.

   .. py:attribute:: OTHER

      Other PII.

SensitivityLevel
----------------

.. py:class:: griot_core.SensitivityLevel

   Data sensitivity levels.

   .. py:attribute:: PUBLIC

      Can be freely shared.

   .. py:attribute:: INTERNAL

      Internal use only.

   .. py:attribute:: CONFIDENTIAL

      Limited access, business sensitive.

   .. py:attribute:: RESTRICTED

      Highly restricted, regulatory requirements.

MaskingStrategy
---------------

.. py:class:: griot_core.MaskingStrategy

   PII masking strategies.

   .. py:attribute:: NONE

      No masking.

   .. py:attribute:: REDACT

      Complete removal ([REDACTED]).

   .. py:attribute:: PARTIAL_MASK

      Partial masking (j***@example.com).

   .. py:attribute:: HASH

      One-way hash.

   .. py:attribute:: TOKENIZE

      Reversible tokenization.

   .. py:attribute:: GENERALIZE

      Generalization (age ranges).

   .. py:attribute:: ENCRYPT

      Encryption.

   .. py:attribute:: PSEUDONYMIZE

      Pseudonymization.

LegalBasis
----------

.. py:class:: griot_core.LegalBasis

   Legal basis for processing (GDPR Article 6).

   .. py:attribute:: CONSENT

      Data subject consent.

   .. py:attribute:: CONTRACT

      Necessary for contract performance.

   .. py:attribute:: LEGAL_OBLIGATION

      Required by law.

   .. py:attribute:: VITAL_INTEREST

      Protect vital interests.

   .. py:attribute:: PUBLIC_TASK

      Public interest or official authority.

   .. py:attribute:: LEGITIMATE_INTEREST

      Legitimate business interest.

DataRegion
----------

.. py:class:: griot_core.DataRegion

   Geographic data regions.

   .. py:attribute:: US

      United States.

   .. py:attribute:: EU

      European Union.

   .. py:attribute:: UK

      United Kingdom.

   .. py:attribute:: CA

      Canada.

   .. py:attribute:: AU

      Australia.

   .. py:attribute:: JP

      Japan.

   .. py:attribute:: SG

      Singapore.

   .. py:attribute:: BR

      Brazil.

   .. py:attribute:: IN

      India.

   .. py:attribute:: CN

      China.

   .. py:attribute:: RU

      Russia.

   .. py:attribute:: GLOBAL

      Any region.

ResidencyConfig
---------------

.. py:class:: griot_core.ResidencyConfig

   Data residency configuration.

   **Attributes:**

   .. py:attribute:: default_rule
      :type: ResidencyRule

      Default residency rule for all fields.

   .. py:attribute:: field_rules
      :type: dict[str, ResidencyRule]

      Field-specific residency rules.

ResidencyRule
-------------

.. py:class:: griot_core.ResidencyRule

   Residency rule definition.

   **Attributes:**

   .. py:attribute:: allowed_regions
      :type: list[DataRegion]

      Regions where data can be stored.

   .. py:attribute:: prohibited_regions
      :type: list[DataRegion]

      Regions where data cannot be stored.

   .. py:attribute:: required_encryption
      :type: bool

      Whether encryption is required.

LineageConfig
-------------

.. py:class:: griot_core.LineageConfig

   Data lineage configuration.

   **Attributes:**

   .. py:attribute:: sources
      :type: list[Source]

      Data sources.

   .. py:attribute:: transformations
      :type: list[Transformation]

      Data transformations.

   .. py:attribute:: consumers
      :type: list[Consumer]

      Data consumers.

Source
------

.. py:class:: griot_core.Source

   Data source definition.

   **Attributes:**

   .. py:attribute:: name
      :type: str

      Source identifier.

   .. py:attribute:: type
      :type: str

      Source type (database, api, file, stream).

   .. py:attribute:: description
      :type: str

      Human-readable description.

   .. py:attribute:: connection
      :type: str

      Connection string or URL.

Transformation
--------------

.. py:class:: griot_core.Transformation

   Data transformation definition.

   **Attributes:**

   .. py:attribute:: name
      :type: str

      Transformation identifier.

   .. py:attribute:: description
      :type: str

      Human-readable description.

   .. py:attribute:: input_fields
      :type: list[str]

      Input field names.

   .. py:attribute:: output_fields
      :type: list[str]

      Output field names.

Consumer
--------

.. py:class:: griot_core.Consumer

   Data consumer definition.

   **Attributes:**

   .. py:attribute:: name
      :type: str

      Consumer identifier.

   .. py:attribute:: type
      :type: str

      Consumer type (warehouse, dashboard, api, ml).

   .. py:attribute:: description
      :type: str

      Human-readable description.

   .. py:attribute:: connection
      :type: str

      Connection string or URL.
