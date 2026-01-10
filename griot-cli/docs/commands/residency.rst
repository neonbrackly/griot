griot residency
===============

Check data residency compliance for regions.

Synopsis
--------

.. code-block:: bash

   griot residency SUBCOMMAND [OPTIONS]

Description
-----------

The ``residency`` command group helps verify data residency compliance,
ensuring data storage meets geographic and regulatory requirements.

Subcommands
-----------

griot residency check
~~~~~~~~~~~~~~~~~~~~~

Check residency compliance for a specific region.

.. code-block:: bash

   griot residency check [OPTIONS] CONTRACT REGION

**Arguments:**

``CONTRACT``
   Path to a contract file (YAML) or Python module.

``REGION``
   Target region code to check (e.g., ``us``, ``eu``, ``germany``).

**Options:**

``--format``, ``-f``
   Output format. Choices: ``table``, ``json``. Default: ``table``.

``--strict``
   Exit with code 1 if any field violates residency rules.

**Example:**

.. code-block:: bash

   # Check EU compliance
   griot residency check customer.yaml eu

   # Check with strict mode for CI
   griot residency check customer.yaml eu --strict

   # JSON output for automation
   griot residency check customer.yaml germany -f json

griot residency list-regions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List all available region codes.

.. code-block:: bash

   griot residency list-regions

**Output:**

.. code-block:: text

   Available Regions:
   ============================================================

   Americas:
     - us
     - us-east
     - us-west
     - canada
     - brazil
     - latam

   Europe:
     - eu
     - eu-west
     - eu-central
     - uk
     - germany
     - france
     - switzerland

   Asia Pacific:
     - apac
     - japan
     - australia
     - singapore
     - india
     - china
     - hong-kong
     - south-korea

   Middle East & Africa:
     - mea
     - uae
     - south-africa

   Global:
     - global
     - any

Output
------

Table Format
~~~~~~~~~~~~

.. code-block:: text

   Residency Check: Customer
   Target Region: eu
   ============================================================
   COMPLIANT - All fields can be stored in this region

   Summary:
   ----------------------------------------
     Total fields: 15
     Compliant: 15
     Non-compliant: 0

When violations exist:

.. code-block:: text

   Residency Check: Customer
   Target Region: us
   ============================================================
   NON-COMPLIANT - Some fields cannot be stored in this region

   Violations:
   ----------------------------------------
     ssn: Field must be stored in EU only
     national_id: Field forbidden in US region

   Configuration Summary:
   ----------------------------------------
     Default allowed regions: eu, eu-west, eu-central
     Compliance frameworks: GDPR

   Summary:
   ----------------------------------------
     Total fields: 15
     Compliant: 13
     Non-compliant: 2

JSON Format
~~~~~~~~~~~

.. code-block:: json

   {
     "compliant": false,
     "total_fields": 15,
     "violations": [
       {
         "field": "ssn",
         "message": "Field must be stored in EU only"
       },
       {
         "field": "national_id",
         "message": "Field forbidden in US region"
       }
     ],
     "warnings": [],
     "config": {
       "default_rule": {
         "allowed_regions": ["eu", "eu-west", "eu-central"]
       },
       "compliance_frameworks": ["GDPR"]
     }
   }

Configuring Residency
---------------------

Residency rules are configured in the contract:

.. code-block:: python

   from griot_core import GriotModel, Field, ResidencyConfig, ResidencyRule, DataRegion

   class Customer(GriotModel):
       customer_id: str = Field(description="Customer ID")
       ssn: str = Field(
           description="Social Security Number",
           pii_category="government_id"
       )

   # Set residency configuration
   Customer.set_residency_config(ResidencyConfig(
       default_rule=ResidencyRule(
           allowed_regions=[DataRegion.EU, DataRegion.EU_WEST]
       ),
       field_rules={
           "ssn": ResidencyRule(
               allowed_regions=[DataRegion.EU],
               forbidden_regions=[DataRegion.US]
           )
       },
       compliance_frameworks=["GDPR", "CCPA"]
   ))

Exit Codes
----------

.. list-table::
   :header-rows: 1

   * - Code
     - Meaning
   * - 0
     - Compliant (or non-strict mode)
   * - 1
     - Non-compliant (with ``--strict``)
   * - 2
     - Error (invalid contract, unknown region, etc.)

Use Cases
---------

GDPR Compliance
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Verify EU customer data can be stored in EU
   griot residency check eu_customer.yaml eu --strict

   # Check if data can be transferred to US
   griot residency check eu_customer.yaml us

Multi-Region Validation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check compliance for multiple regions
   for region in eu us apac; do
       griot residency check customer.yaml $region
   done

See Also
--------

- :doc:`report` - Generate compliance audit report
- :doc:`lint` - Check contract for PII issues
