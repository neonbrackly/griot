Contracts
=========

A :class:`~griot_core.Contract` is the top-level entity that wraps one or more schemas
with contract-level metadata.

Creating Contracts
------------------

Basic Contract
^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import Contract, Schema, Field, ContractStatus

   class ProductSchema(Schema):
       product_id: str = Field("Product ID", primary_key=True)
       name: str = Field("Product name")
       price: float = Field("Price")

   contract = Contract(
       id="product-data-v1",
       name="Product Data Contract",
       version="1.0.0",
       status=ContractStatus.ACTIVE,
       schemas=[ProductSchema()]
   )

Full Contract with Metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import (
       Contract, ContractStatus, ContractDescription,
       ContractTeam, TeamMember, ContractSupport,
       SLAProperty, Server
   )

   contract = Contract(
       # Required identification
       id="sales-data-v2",
       name="Sales Data Contract",
       version="2.0.0",
       status=ContractStatus.ACTIVE,

       # Description
       description=ContractDescription(
           purpose="Provide sales transaction data for analytics",
           usage="Daily batch processing, real-time dashboards",
           limitations="PII data requires approval"
       ),

       # Ownership
       team=ContractTeam(
           id="data-platform",
           name="Data Platform Team",
           members=[
               TeamMember(username="alice", role="owner"),
               TeamMember(username="bob", role="contributor"),
           ]
       ),

       # Support
       support=[
           ContractSupport(
               channel="email",
               tool="jira",
               url="https://jira.example.com/browse/DATA"
           )
       ],

       # SLAs
       sla_properties=[
           SLAProperty(
               property="latency",
               value=15,
               unit="minutes",
               element="delivery"
           ),
           SLAProperty(
               property="uptime",
               value=99.9,
               unit="percent"
           )
       ],

       # Data sources
       servers=[
           Server(
               server="production-db",
               type="postgresql",
               environment="production",
               project="sales-analytics"
           )
       ],

       # Schemas
       schemas=[OrderSchema(), ProductSchema()]
   )

Contract Lifecycle
------------------

Contracts have a lifecycle status:

.. code-block:: python

   from griot_core import ContractStatus

   # New contract in development
   contract = Contract(
       id="new-contract",
       status=ContractStatus.DRAFT,
       # ...
   )

   # Ready for production
   contract.status = ContractStatus.ACTIVE

   # Being phased out
   contract.status = ContractStatus.DEPRECATED

   # No longer available
   contract.status = ContractStatus.RETIRED

Status transitions:

.. code-block:: text

   DRAFT → ACTIVE → DEPRECATED → RETIRED
     ↑_________|

Managing Schemas
----------------

Add and remove schemas:

.. code-block:: python

   # Add a schema
   contract.add_schema(NewSchema())

   # Remove a schema
   contract.remove_schema(old_schema)

   # Get schema by index
   first_schema = contract.get_schema(0)

   # Get schema by ID
   schema = contract.get_schema_by_id("orders")

   # Get schema by name
   schema = contract.get_schema_by_name("Orders")

   # List all schemas
   schemas = contract.list_schemas()
   schema_names = contract.list_schema_names()

   # Iterate over schemas
   for schema in contract:
       print(f"Schema: {schema.name}")

   # Count schemas
   num_schemas = len(contract)

Serialization
-------------

Export to YAML
^^^^^^^^^^^^^^

.. code-block:: python

   # To YAML string
   yaml_content = contract.to_yaml()
   print(yaml_content)

   # Using helper function
   from griot_core import contract_to_yaml
   yaml_content = contract_to_yaml(contract)

   # Save to file
   with open("contract.yaml", "w") as f:
       f.write(yaml_content)

Export to Dictionary
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # To dict (camelCase keys for ODCS compliance)
   data = contract.to_dict()

   # Using helper function
   from griot_core import contract_to_dict

   # camelCase (default, ODCS standard)
   data = contract_to_dict(contract)

   # snake_case
   data = contract_to_dict(contract, camel_case=False)

Loading Contracts
-----------------

From YAML File
^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import load_contract

   contract = load_contract("path/to/contract.yaml")

From YAML String
^^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import load_contract_from_string

   yaml_content = '''
   apiVersion: v1.0.0
   kind: DataContract
   id: my-contract
   version: "1.0.0"
   status: active
   schema:
     - name: Users
       properties:
         - name: user_id
           logicalType: string
           primary_key: true
   '''

   contract = load_contract_from_string(yaml_content)

From Dictionary
^^^^^^^^^^^^^^^

.. code-block:: python

   from griot_core import load_contract_from_dict

   data = {
       "apiVersion": "v1.0.0",
       "kind": "DataContract",
       "id": "my-contract",
       "version": "1.0.0",
       "status": "active",
       "schema": [
           {
               "name": "Users",
               "properties": [
                   {"name": "user_id", "logicalType": "string", "primary_key": True}
               ]
           }
       ]
   }

   contract = load_contract_from_dict(data)

Contract Linting
----------------

Check contracts for issues:

.. code-block:: python

   from griot_core import lint_contract, Severity

   issues = lint_contract(contract)

   for issue in issues:
       print(f"[{issue.severity.value}] {issue.code}: {issue.message}")
       if issue.suggestion:
           print(f"  Suggestion: {issue.suggestion}")

   # Filter by severity
   errors = [i for i in issues if i.severity == Severity.ERROR]
   warnings = [i for i in issues if i.severity == Severity.WARNING]

Lint codes:

.. list-table::
   :header-rows: 1

   * - Code
     - Severity
     - Description
   * - ODCS-001
     - ERROR
     - Missing contract ID
   * - ODCS-002
     - ERROR
     - Invalid status
   * - ODCS-003
     - ERROR
     - No schemas defined
   * - ODCS-004
     - WARNING
     - Schema has no primary key
   * - ODCS-010
     - ERROR
     - Schema missing name
   * - ODCS-011
     - ERROR
     - Schema has no properties
   * - G001
     - WARNING
     - Field has no description

Structure Validation
--------------------

Validate contract structure:

.. code-block:: python

   from griot_core import validate_contract_structure

   result = validate_contract_structure(contract)

   print(f"Valid: {result.is_valid}")
   print(f"Errors: {result.error_count}")
   print(f"Warnings: {result.warning_count}")
   print(result.summary())

   for issue in result.issues:
       print(f"  [{issue.severity.value}] {issue.path}: {issue.message}")

   # Get as dictionary
   report = result.to_dict()

YAML Example
------------

Complete ODCS contract YAML:

.. code-block:: yaml

   apiVersion: v1.0.0
   kind: DataContract
   id: sales-orders-v1
   version: "1.0.0"
   status: active
   name: Sales Orders Contract

   description:
     purpose: Provide sales order data for analytics
     usage: Daily batch processing and real-time dashboards
     limitations: Contains PII - requires data access approval

   team:
     id: data-platform
     name: Data Platform Team
     members:
       - username: alice
         role: owner
       - username: bob
         role: contributor

   support:
     - channel: slack
       tool: slack
       url: https://slack.example.com/data-platform

   slaProperties:
     - property: latency
       value: 15
       unit: minutes
     - property: uptime
       value: 99.9
       unit: percent

   servers:
     - server: sales-db
       type: postgresql
       environment: production

   schema:
     - name: Orders
       physicalName: orders_tbl
       description: Sales order records
       properties:
         - name: order_id
           logicalType: string
           primary_key: true
           description: Unique order identifier
           quality:
             - metric: nullValues
               mustBe: 0
         - name: customer_id
           logicalType: string
           description: Customer reference
         - name: total
           logicalType: float
           description: Order total amount
       quality:
         - metric: rowCount
           mustBeGreaterThan: 0

Best Practices
--------------

1. **Version your contracts** - Use semantic versioning
2. **Document everything** - Add descriptions at all levels
3. **Define ownership** - Specify team and support channels
4. **Set SLAs** - Define latency and uptime expectations
5. **Lint before deployment** - Check for issues
6. **Store in version control** - Track contract changes

.. code-block:: python

   # Good practice: Complete contract
   contract = Contract(
       id="orders-v1",
       name="Orders Contract",
       version="1.0.0",
       status=ContractStatus.DRAFT,  # Start as draft
       description=ContractDescription(
           purpose="Clear purpose statement",
           usage="How to use this data"
       ),
       team=ContractTeam(
           id="team-id",
           name="Team Name"
       ),
       schemas=[OrderSchema()]
   )

   # Validate before publishing
   issues = lint_contract(contract)
   if any(i.severity == Severity.ERROR for i in issues):
       raise ValueError("Contract has errors")

   # Promote to active
   contract.status = ContractStatus.ACTIVE

Next Steps
----------

- Learn about :doc:`validation` for data validation
- Generate :doc:`mock_data` for testing
- See the :doc:`../api/contract` for full API reference
