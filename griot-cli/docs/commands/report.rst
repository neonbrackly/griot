griot report
============

Generate analysis reports for contracts.

Synopsis
--------

.. code-block:: bash

   griot report SUBCOMMAND [OPTIONS] CONTRACT

Description
-----------

The ``report`` command group generates various analysis reports for data contracts:

- **analytics**: Statistics about contract structure and quality
- **ai**: AI/ML readiness assessment
- **audit**: Compliance and privacy audit (PII, GDPR, CCPA, HIPAA)
- **all**: Comprehensive combined report

Subcommands
-----------

griot report analytics
~~~~~~~~~~~~~~~~~~~~~~

Generate analytics report with contract statistics.

.. code-block:: bash

   griot report analytics [OPTIONS] CONTRACT

**Options:**

``--output``, ``-o``
   Output file path. If not specified, prints to stdout.

``--format``, ``-f``
   Output format. Choices: ``json``, ``markdown``. Default: ``markdown``.

**Example:**

.. code-block:: bash

   griot report analytics customer.yaml
   griot report analytics customer.yaml -f json -o analytics.json

**Output includes:**

- Total field count
- Type distribution
- Constraint coverage
- Documentation coverage
- PII field summary
- Primary key info

griot report ai
~~~~~~~~~~~~~~~

Generate AI readiness assessment report.

.. code-block:: bash

   griot report ai [OPTIONS] CONTRACT

**Options:**

``--output``, ``-o``
   Output file path. If not specified, prints to stdout.

``--format``, ``-f``
   Output format. Choices: ``json``, ``markdown``. Default: ``markdown``.

``--min-score``
   Exit with code 1 if readiness score is below this threshold (0-100).

**Example:**

.. code-block:: bash

   # Generate AI readiness report
   griot report ai customer.yaml

   # Fail if score below 70
   griot report ai customer.yaml --min-score 70

   # Save as JSON
   griot report ai customer.yaml -f json -o ai_report.json

**Output includes:**

- Overall readiness score (0-100) and grade (A-F)
- Documentation score
- Type clarity score
- Constraint coverage score
- Semantic clarity score
- Recommendations for improvement

griot report audit
~~~~~~~~~~~~~~~~~~

Generate compliance audit report.

.. code-block:: bash

   griot report audit [OPTIONS] CONTRACT

**Options:**

``--output``, ``-o``
   Output file path. If not specified, prints to stdout.

``--format``, ``-f``
   Output format. Choices: ``json``, ``markdown``. Default: ``markdown``.

``--min-score``
   Exit with code 1 if compliance score is below this threshold (0-100).

**Example:**

.. code-block:: bash

   # Generate audit report
   griot report audit customer.yaml

   # Require minimum compliance score
   griot report audit customer.yaml --min-score 80

**Output includes:**

- Compliance score and grade
- PII inventory (fields, categories, sensitivity)
- Masking strategy coverage
- Legal basis coverage
- Residency configuration status
- GDPR readiness
- CCPA readiness
- HIPAA readiness
- Critical issues and recommendations

griot report all
~~~~~~~~~~~~~~~~

Generate comprehensive combined report.

.. code-block:: bash

   griot report all [OPTIONS] CONTRACT

**Options:**

``--output``, ``-o``
   Output file path. If not specified, prints to stdout.

``--format``, ``-f``
   Output format. Choices: ``json``, ``markdown``. Default: ``markdown``.

``--min-score``
   Exit with code 1 if overall readiness score is below this threshold (0-100).

**Example:**

.. code-block:: bash

   # Generate comprehensive report
   griot report all customer.yaml

   # Require minimum overall score
   griot report all customer.yaml --min-score 75 -o readiness.md

**Output includes:**

- Overall readiness score and grade
- Data quality score
- AI readiness score
- Compliance score
- Key indicators
- Top recommendations
- Critical issues

Examples
--------

CI/CD Quality Gates
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Require minimum AI readiness score
   griot report ai customer.yaml --min-score 70

   # Require minimum compliance score
   griot report audit customer.yaml --min-score 80

   # Require minimum overall readiness
   griot report all customer.yaml --min-score 75

Generate All Reports
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate all reports as JSON
   griot report analytics customer.yaml -f json -o analytics.json
   griot report ai customer.yaml -f json -o ai_readiness.json
   griot report audit customer.yaml -f json -o audit.json
   griot report all customer.yaml -f json -o readiness.json

Exit Codes
----------

.. list-table::
   :header-rows: 1

   * - Code
     - Meaning
   * - 0
     - Success (score above threshold if specified)
   * - 1
     - Score below ``--min-score`` threshold
   * - 2
     - Error (invalid contract, etc.)

See Also
--------

- :doc:`lint` - Quick contract quality check
- :doc:`manifest` - Export contract documentation
- :doc:`residency` - Residency compliance checking
