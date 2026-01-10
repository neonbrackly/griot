Manifest Export
===============

Contract manifest export functions.

export_manifest
---------------

.. py:function:: griot_core.export_manifest(model, format="llm_context", **kwargs) -> str

   Export a contract as a manifest.

   :param model: Model class to export
   :type model: type[GriotModel]
   :param format: Export format
   :type format: str
   :param include_pii: Include PII metadata (default: False)
   :type include_pii: bool
   :param include_lineage: Include lineage info (default: False)
   :type include_lineage: bool
   :param include_examples: Include example values (default: True)
   :type include_examples: bool
   :returns: Manifest string
   :rtype: str

   **Formats:**

   - ``llm_context``: Optimized for AI/LLM consumption
   - ``json_ld``: Semantic web / linked data format
   - ``markdown``: Human-readable documentation

   **Example:**

   .. code-block:: python

      from griot_core import export_manifest

      # LLM context (default)
      manifest = export_manifest(Customer, format="llm_context")

      # JSON-LD with all metadata
      manifest = export_manifest(
          Customer,
          format="json_ld",
          include_pii=True,
          include_lineage=True
      )

      # Markdown documentation
      manifest = export_manifest(Customer, format="markdown")

LLM Context Format
------------------

Optimized for injection into AI/LLM prompts:

.. code-block:: text

   # Data Contract: Customer

   Customer master data contract.

   ## Fields

   ### customer_id (string) [PRIMARY KEY]
   Unique customer identifier
   - Pattern: ^CUST-\d{6}$
   - Examples: CUST-000001, CUST-123456

   ### email (string)
   Customer email address
   - Format: email
   - Max length: 255

   ### age (integer)
   Customer age in years
   - Minimum: 0
   - Maximum: 150

   ## Constraints
   - customer_id is the primary key
   - All fields are required unless marked nullable

JSON-LD Format
--------------

Semantic web format with schema.org vocabulary:

.. code-block:: json

   {
     "@context": {
       "@vocab": "https://schema.org/",
       "griot": "https://griot.dev/schema/"
     },
     "@type": "griot:DataContract",
     "@id": "griot:contract/Customer",
     "name": "Customer",
     "description": "Customer master data contract.",
     "griot:fields": [
       {
         "@type": "griot:Field",
         "name": "customer_id",
         "description": "Unique customer identifier",
         "griot:dataType": "string",
         "griot:primaryKey": true
       }
     ]
   }

Markdown Format
---------------

Human-readable documentation format:

.. code-block:: markdown

   # Customer

   Customer master data contract.

   ## Fields

   | Field | Type | Description | Constraints |
   |-------|------|-------------|-------------|
   | `customer_id` | string | Unique customer identifier | PK, pattern |
   | `email` | string | Customer email address | format: email |
   | `age` | integer | Customer age in years | 0-150 |

   ## Examples

   ### customer_id
   - `CUST-000001`
   - `CUST-123456`

Including PII Metadata
----------------------

When ``include_pii=True``, PII information is included:

.. code-block:: python

   manifest = export_manifest(Customer, format="llm_context", include_pii=True)

Output includes:

.. code-block:: text

   ### email (string) [PII: EMAIL, CONFIDENTIAL]
   Customer email address
   - Format: email
   - PII Category: EMAIL
   - Sensitivity: CONFIDENTIAL
   - Masking: PARTIAL_MASK
   - Legal Basis: CONTRACT

Including Lineage
-----------------

When ``include_lineage=True``, data lineage is included:

.. code-block:: python

   manifest = export_manifest(Customer, format="llm_context", include_lineage=True)

Output includes:

.. code-block:: text

   ## Data Lineage

   ### Sources
   - crm_database (database): Customer master from CRM

   ### Transformations
   - deduplicate: Merge duplicate customer records
   - enrich_address: Standardize and validate addresses

   ### Consumers
   - analytics_warehouse (warehouse): BigQuery analytics
   - marketing_platform (application): Braze marketing
