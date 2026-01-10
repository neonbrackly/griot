griot manifest
==============

Export contract as JSON-LD, Markdown, or LLM-optimized context.

Synopsis
--------

.. code-block:: bash

   griot manifest [OPTIONS] CONTRACT

Description
-----------

The ``manifest`` command exports a contract in various formats optimized
for different consumers: semantic web (JSON-LD), documentation (Markdown),
or AI/LLM systems (LLM context).

Arguments
---------

``CONTRACT``
   Path to a contract file (YAML) or Python module containing a GriotModel.

Options
-------

``--output``, ``-o``
   Output file path. If not specified, prints to stdout.

``--format``, ``-f``
   Export format. Choices: ``json_ld``, ``markdown``, ``llm_context``. Default: ``markdown``.

Examples
--------

Export Formats
~~~~~~~~~~~~~~

.. code-block:: bash

   # Markdown format (default) - for documentation
   griot manifest customer.yaml

   # JSON-LD format - for semantic web/linked data
   griot manifest customer.yaml -f json_ld

   # LLM context format - for AI systems
   griot manifest customer.yaml -f llm_context

   # Save to file
   griot manifest customer.yaml -f markdown -o customer_docs.md

Output Formats
--------------

JSON-LD Format
~~~~~~~~~~~~~~

JSON-LD (JavaScript Object Notation for Linked Data) provides a semantic
representation of the contract:

.. code-block:: json

   {
     "@context": {
       "@vocab": "https://schema.org/",
       "griot": "https://griot.io/vocab/"
     },
     "@type": "DataContract",
     "@id": "griot:Customer",
     "name": "Customer",
     "description": "Customer profile contract",
     "identifier": "customer_id",
     "properties": {
       "customer_id": {
         "@type": "Text",
         "description": "Unique customer identifier"
       },
       "email": {
         "@type": "Text",
         "format": "email"
       }
     }
   }

**Use cases:**

- Knowledge graphs
- Data catalogs
- Semantic search
- Linked data applications

Markdown Format
~~~~~~~~~~~~~~~

Human-readable documentation format:

.. code-block:: markdown

   # Customer

   Customer profile contract for AI systems.

   ## Fields

   | Field | Type | Description | Constraints |
   |-------|------|-------------|-------------|
   | `customer_id` | string | Unique customer identifier | PK, pattern |
   | `email` | string | Customer email address | format:email |
   | `age` | integer | Customer age in years | >= 0, <= 150 |

   ## Field Details

   ### customer_id

   **Type:** string
   **Description:** Unique customer identifier
   **Primary Key:** Yes
   **Pattern:** `^CUST-\d{6}$`

**Use cases:**

- API documentation
- Developer guides
- README files
- Wiki pages

LLM Context Format
~~~~~~~~~~~~~~~~~~

Optimized for AI/LLM system prompts:

.. code-block:: text

   DATA CONTRACT: Customer

   PURPOSE: Customer profile contract for AI systems.

   PRIMARY KEY: customer_id

   FIELDS:
   - customer_id (string) [PK]: Unique customer identifier
     Description: Unique customer identifier
     Constraints: pattern=^CUST-\d{6}$

   - email (string): Customer email address
     Description: Customer email address
     Constraints: format=email, max_length=255

   - age (integer): Customer age in years
     Description: Customer age in years
     Constraints: min=0, max=150, unit=years

   VALIDATION RULES:
   - All non-nullable fields are required
   - Type constraints must be satisfied
   - Enum fields must use listed values only

**Use cases:**

- LLM system prompts
- AI agent instructions
- Automated data processing
- Code generation context

Exit Codes
----------

.. list-table::
   :header-rows: 1

   * - Code
     - Meaning
   * - 0
     - Success
   * - 2
     - Error (invalid contract, file write error, etc.)

See Also
--------

- :doc:`report` - Generate analysis reports
- :doc:`lint` - Check contract quality
