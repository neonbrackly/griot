Reports API
===========

The reports module provides functionality for generating contract documentation.

Functions
---------

generate_contract_report
^^^^^^^^^^^^^^^^^^^^^^^^

.. function:: griot_core.generate_contract_report(contract: Contract) -> ContractReport

   Generate a comprehensive report for a contract.

   :param contract: Contract instance
   :returns: :class:`ContractReport` with detailed information

   .. code-block:: python

      from griot_core import Contract, generate_contract_report

      contract = Contract(
          id="my-contract",
          name="My Data Contract",
          version="1.0.0",
          schemas=[OrderSchema(), ProductSchema()]
      )

      report = generate_contract_report(contract)

      print(f"Contract: {report.name}")
      print(f"Version: {report.version}")
      print(f"Schemas: {len(report.schemas)}")

      # Access schema details
      for schema_report in report.schemas:
          print(f"  Schema: {schema_report.name}")
          print(f"  Fields: {len(schema_report.fields)}")

export_manifest
^^^^^^^^^^^^^^^

.. function:: griot_core.export_manifest(contract: Contract, format: str = "json") -> str | dict

   Export a contract manifest in various formats.

   :param contract: Contract instance
   :param format: Output format ("json", "yaml", or "dict")
   :returns: Manifest as string or dictionary

   .. code-block:: python

      from griot_core import export_manifest

      # JSON format
      json_manifest = export_manifest(contract, format="json")

      # YAML format
      yaml_manifest = export_manifest(contract, format="yaml")

      # Dictionary
      dict_manifest = export_manifest(contract, format="dict")

Classes
-------

ContractReport
^^^^^^^^^^^^^^

.. class:: griot_core.ContractReport

   Comprehensive report for a data contract.

   **Attributes**

   .. attribute:: id
      :type: str

      Contract identifier.

   .. attribute:: name
      :type: str | None

      Contract name.

   .. attribute:: version
      :type: str

      Contract version.

   .. attribute:: status
      :type: str

      Contract status.

   .. attribute:: description
      :type: dict | None

      Contract description (purpose, usage, limitations).

   .. attribute:: team
      :type: dict | None

      Team information.

   .. attribute:: schemas
      :type: list[SchemaReport]

      List of schema reports.

   .. attribute:: sla_properties
      :type: list[dict] | None

      SLA properties.

   .. attribute:: servers
      :type: list[dict] | None

      Server information.

   **Methods**

   .. method:: to_dict() -> dict

      Convert to dictionary representation.

   .. method:: to_markdown() -> str

      Generate Markdown documentation.

   .. method:: summary() -> str

      Get a brief summary string.

   **Example**

   .. code-block:: python

      report = generate_contract_report(contract)

      # Access properties
      print(report.name)
      print(report.version)

      # Get markdown documentation
      markdown = report.to_markdown()
      with open("CONTRACT.md", "w") as f:
          f.write(markdown)

      # Get dictionary
      data = report.to_dict()

SchemaReport
^^^^^^^^^^^^

.. class:: SchemaReport

   Report for a single schema within a contract.

   **Attributes**

   .. attribute:: name
      :type: str

      Schema name.

   .. attribute:: description
      :type: str | None

      Schema description.

   .. attribute:: physical_name
      :type: str | None

      Physical storage name.

   .. attribute:: fields
      :type: list[FieldReport]

      List of field reports.

   .. attribute:: quality
      :type: list[dict]

      Schema-level quality rules.

   .. attribute:: primary_key
      :type: str | None

      Primary key field name.

   **Methods**

   .. method:: to_dict() -> dict

      Convert to dictionary.

   .. method:: to_markdown() -> str

      Generate Markdown for this schema.

FieldReport
^^^^^^^^^^^

.. class:: FieldReport

   Report for a single field within a schema.

   **Attributes**

   .. attribute:: name
      :type: str

      Field name.

   .. attribute:: description
      :type: str

      Field description.

   .. attribute:: logical_type
      :type: str

      ODCS logical type.

   .. attribute:: physical_type
      :type: str | None

      Storage-specific type.

   .. attribute:: primary_key
      :type: bool

      Whether this is the primary key.

   .. attribute:: nullable
      :type: bool

      Whether null values are allowed.

   .. attribute:: unique
      :type: bool

      Whether values must be unique.

   .. attribute:: quality
      :type: list[dict]

      Field-level quality rules.

   .. attribute:: tags
      :type: list[str]

      Classification tags.

   **Methods**

   .. method:: to_dict() -> dict

      Convert to dictionary.

   .. method:: to_markdown_row() -> str

      Generate Markdown table row.

Markdown Generation
-------------------

The report system generates clean Markdown documentation.

**Example Output**

.. code-block:: markdown

   # Orders Data Contract

   **Version:** 1.0.0
   **Status:** active

   ## Description

   **Purpose:** Provide order data for analytics

   **Usage:** Daily batch processing

   ## Schemas

   ### Orders

   Customer order records.

   **Physical Name:** `orders_tbl`

   | Field | Type | PK | Nullable | Description |
   |-------|------|:--:|:--------:|-------------|
   | order_id | string | ✓ | ✗ | Unique order identifier |
   | customer_id | string | | ✓ | Customer reference |
   | total | float | | ✗ | Order total amount |

   **Quality Rules:**
   - Row count must be greater than 0
   - No duplicate rows on [order_id]

Usage Examples
--------------

Generate Documentation
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import Contract, generate_contract_report

   contract = load_contract("contract.yaml")
   report = generate_contract_report(contract)

   # Write Markdown documentation
   with open("docs/CONTRACT.md", "w") as f:
       f.write(report.to_markdown())

   # Export as JSON
   import json
   with open("docs/contract.json", "w") as f:
       json.dump(report.to_dict(), f, indent=2)

Programmatic Access
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   report = generate_contract_report(contract)

   # Access contract info
   print(f"Contract: {report.name} v{report.version}")

   # List all fields across all schemas
   for schema in report.schemas:
       print(f"\nSchema: {schema.name}")
       for field in schema.fields:
           pk_marker = " (PK)" if field.primary_key else ""
           print(f"  - {field.name}: {field.logical_type}{pk_marker}")

   # Find all PII fields
   pii_fields = []
   for schema in report.schemas:
       for field in schema.fields:
           if "pii" in field.tags:
               pii_fields.append((schema.name, field.name))

   print(f"\nPII fields: {pii_fields}")

Integration with CI/CD
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import load_contract, generate_contract_report, lint_contract

   def generate_docs(contract_path: str, output_dir: str):
       """Generate documentation for a contract."""
       contract = load_contract(contract_path)

       # Lint first
       issues = lint_contract(contract)
       if any(i.severity.value == "error" for i in issues):
           raise ValueError("Contract has errors")

       # Generate report
       report = generate_contract_report(contract)

       # Write documentation
       with open(f"{output_dir}/CONTRACT.md", "w") as f:
           f.write(report.to_markdown())

       with open(f"{output_dir}/contract.json", "w") as f:
           import json
           json.dump(report.to_dict(), f, indent=2)

       return report
