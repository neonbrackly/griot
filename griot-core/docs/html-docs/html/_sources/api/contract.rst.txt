Contract API
============

The contract module provides classes for creating and managing data contracts.

Contract
--------

.. class:: griot_core.Contract

   Top-level entity representing a data contract with metadata and schemas.

   **Constructor Parameters**

   :param id: Unique contract identifier (required)
   :param name: Human-readable contract name
   :param version: Semantic version string (e.g., "1.0.0")
   :param status: Contract lifecycle status (:class:`ContractStatus`)
   :param api_version: ODCS API version (default: "v1.0.0")
   :param kind: Contract kind (default: "DataContract")
   :param description: :class:`ContractDescription` object
   :param team: :class:`ContractTeam` object
   :param support: List of :class:`ContractSupport` objects
   :param roles: List of :class:`ContractRole` objects
   :param sla_properties: List of :class:`SLAProperty` objects
   :param servers: List of :class:`Server` objects
   :param schemas: List of :class:`Schema` instances
   :param custom_properties: Extension properties (dict)

   **Basic Example**

   .. code-block:: python

      from griot_core import Contract, Schema, Field, ContractStatus

      class OrderSchema(Schema):
          order_id: str = Field("Order ID", primary_key=True)
          total: float = Field("Order total")

      contract = Contract(
          id="orders-v1",
          name="Orders Data Contract",
          version="1.0.0",
          status=ContractStatus.ACTIVE,
          schemas=[OrderSchema()]
      )

   **Full Example with Metadata**

   .. code-block:: python

      from griot_core import (
          Contract, ContractStatus, ContractDescription,
          ContractTeam, TeamMember, ContractSupport,
          SLAProperty, Server
      )

      contract = Contract(
          id="sales-data-v2",
          name="Sales Data Contract",
          version="2.0.0",
          status=ContractStatus.ACTIVE,

          description=ContractDescription(
              purpose="Provide sales data for analytics",
              usage="Daily batch processing",
              limitations="Contains PII"
          ),

          team=ContractTeam(
              id="data-team",
              name="Data Platform Team",
              members=[
                  TeamMember(username="alice", role="owner"),
                  TeamMember(username="bob", role="contributor"),
              ]
          ),

          support=[
              ContractSupport(
                  channel="slack",
                  tool="slack",
                  url="https://slack.example.com/data"
              )
          ],

          sla_properties=[
              SLAProperty(property="latency", value=15, unit="minutes"),
              SLAProperty(property="uptime", value=99.9, unit="percent"),
          ],

          servers=[
              Server(
                  server="prod-db",
                  type="postgresql",
                  environment="production"
              )
          ],

          schemas=[OrderSchema(), ProductSchema()]
      )

   **Properties**

   .. attribute:: id
      :type: str

      Unique contract identifier.

   .. attribute:: name
      :type: str | None

      Human-readable name.

   .. attribute:: version
      :type: str

      Semantic version.

   .. attribute:: status
      :type: ContractStatus

      Lifecycle status.

   .. attribute:: schemas
      :type: list[Schema]

      List of schemas in this contract.

   **Schema Management Methods**

   .. method:: add_schema(schema: Schema) -> None

      Add a schema to the contract.

      :param schema: Schema instance to add

   .. method:: remove_schema(schema: Schema) -> None

      Remove a schema from the contract.

      :param schema: Schema instance to remove

   .. method:: get_schema(index: int) -> Schema

      Get schema by index.

      :param index: Zero-based index
      :returns: Schema at the specified index

   .. method:: get_schema_by_id(schema_id: str) -> Schema | None

      Get schema by its ID.

      :param schema_id: Schema identifier
      :returns: Schema or None if not found

   .. method:: get_schema_by_name(name: str) -> Schema | None

      Get schema by its name.

      :param name: Schema name
      :returns: Schema or None if not found

   .. method:: list_schemas() -> list[Schema]

      Get all schemas.

      :returns: List of all schemas

   .. method:: list_schema_names() -> list[str]

      Get names of all schemas.

      :returns: List of schema names

   **Serialization Methods**

   .. method:: to_dict(camel_case: bool = True) -> dict

      Convert contract to ODCS dictionary format.

      :param camel_case: Use camelCase keys (default True)
      :returns: Dictionary representation

   .. method:: to_yaml() -> str

      Convert contract to YAML string.

      :returns: YAML formatted string

   **Iteration**

   Contracts support iteration over their schemas:

   .. code-block:: python

      for schema in contract:
          print(f"Schema: {schema.name}")

      # Length
      num_schemas = len(contract)

ContractDescription
-------------------

.. class:: griot_core.ContractDescription

   Contract description with purpose, usage, and limitations.

   :param purpose: Why this contract exists
   :param usage: How to use the data
   :param limitations: Any restrictions or caveats

   .. code-block:: python

      description = ContractDescription(
          purpose="Provide customer data for analytics",
          usage="Real-time dashboards and batch reports",
          limitations="PII requires data access approval"
      )

ContractTeam
------------

.. class:: griot_core.ContractTeam

   Team ownership information.

   :param id: Team identifier
   :param name: Team name
   :param members: List of :class:`TeamMember` objects

   .. code-block:: python

      team = ContractTeam(
          id="data-platform",
          name="Data Platform Team",
          members=[
              TeamMember(username="alice", role="owner"),
              TeamMember(username="bob", role="contributor"),
          ]
      )

TeamMember
----------

.. class:: griot_core.TeamMember

   Individual team member.

   :param username: User identifier
   :param role: Role in the team (e.g., "owner", "contributor")

ContractSupport
---------------

.. class:: griot_core.ContractSupport

   Support channel information.

   :param channel: Channel type (e.g., "slack", "email")
   :param tool: Tool used (e.g., "jira", "slack")
   :param url: Support URL

   .. code-block:: python

      support = ContractSupport(
          channel="slack",
          tool="slack",
          url="https://slack.example.com/data-support"
      )

ContractRole
------------

.. class:: griot_core.ContractRole

   Role definition for contract access.

   :param role: Role name
   :param access: Access level (e.g., "read", "write")

SLAProperty
-----------

.. class:: griot_core.SLAProperty

   Service Level Agreement property.

   :param property: SLA property name (e.g., "latency", "uptime")
   :param value: Numeric value
   :param unit: Unit of measurement (e.g., "minutes", "percent")
   :param element: Optional element reference

   .. code-block:: python

      sla = SLAProperty(
          property="latency",
          value=15,
          unit="minutes",
          element="delivery"
      )

Server
------

.. class:: griot_core.Server

   Server/data source information.

   :param server: Server name or identifier
   :param type: Server type (e.g., "postgresql", "bigquery")
   :param environment: Environment (e.g., "production", "staging")
   :param project: Project name (optional)
   :param dataset: Dataset name (optional)

   .. code-block:: python

      server = Server(
          server="sales-db",
          type="postgresql",
          environment="production",
          project="sales-analytics"
      )

Loading Functions
-----------------

.. function:: griot_core.load_contract(path: str) -> Contract

   Load a contract from a YAML file.

   :param path: Path to YAML file
   :returns: Contract instance
   :raises ContractNotFoundError: If file not found
   :raises ContractParseError: If parsing fails

   .. code-block:: python

      contract = load_contract("path/to/contract.yaml")

.. function:: griot_core.load_contract_from_string(yaml_content: str) -> Contract

   Load a contract from a YAML string.

   :param yaml_content: YAML formatted string
   :returns: Contract instance
   :raises ContractParseError: If parsing fails

   .. code-block:: python

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

.. function:: griot_core.load_contract_from_dict(data: dict) -> Contract

   Load a contract from a dictionary.

   :param data: ODCS-format dictionary
   :returns: Contract instance

   .. code-block:: python

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

Export Functions
----------------

.. function:: griot_core.contract_to_yaml(contract: Contract) -> str

   Export a contract to YAML format.

   :param contract: Contract instance
   :returns: YAML formatted string

   .. code-block:: python

      yaml_content = contract_to_yaml(contract)
      with open("contract.yaml", "w") as f:
          f.write(yaml_content)

.. function:: griot_core.contract_to_dict(contract: Contract, camel_case: bool = True) -> dict

   Export a contract to dictionary format.

   :param contract: Contract instance
   :param camel_case: Use camelCase keys (default True)
   :returns: Dictionary representation

   .. code-block:: python

      # camelCase (ODCS standard)
      data = contract_to_dict(contract)

      # snake_case
      data = contract_to_dict(contract, camel_case=False)

Linting Functions
-----------------

.. function:: griot_core.lint_contract(contract: Contract) -> list[LintIssue]

   Check a contract for issues.

   :param contract: Contract to lint
   :returns: List of :class:`LintIssue` objects

   .. code-block:: python

      from griot_core import lint_contract, Severity

      issues = lint_contract(contract)

      for issue in issues:
          print(f"[{issue.severity.value}] {issue.code}: {issue.message}")

      errors = [i for i in issues if i.severity == Severity.ERROR]

.. class:: griot_core.LintIssue

   Represents a linting issue.

   .. attribute:: code
      :type: str

      Issue code (e.g., "ODCS-001").

   .. attribute:: severity
      :type: Severity

      Issue severity (ERROR, WARNING, INFO).

   .. attribute:: message
      :type: str

      Human-readable message.

   .. attribute:: path
      :type: str | None

      Path to the problematic element.

   .. attribute:: suggestion
      :type: str | None

      Suggested fix.

Validation Functions
--------------------

.. function:: griot_core.validate_contract_structure(contract: Contract) -> ContractStructureResult

   Validate the structure of a contract.

   :param contract: Contract to validate
   :returns: :class:`ContractStructureResult` with validation results

   .. code-block:: python

      result = validate_contract_structure(contract)

      print(f"Valid: {result.is_valid}")
      print(f"Errors: {result.error_count}")
      print(f"Warnings: {result.warning_count}")
      print(result.summary())

      for issue in result.issues:
          print(f"[{issue.severity.value}] {issue.path}: {issue.message}")

.. class:: griot_core.ContractStructureResult

   Result of contract structure validation.

   .. attribute:: is_valid
      :type: bool

      Whether the contract is valid.

   .. attribute:: error_count
      :type: int

      Number of errors.

   .. attribute:: warning_count
      :type: int

      Number of warnings.

   .. attribute:: issues
      :type: list[ContractStructureIssue]

      List of issues found.

   .. method:: summary() -> str

      Get a summary string.

   .. method:: to_dict() -> dict

      Convert to dictionary.

Utility Functions
-----------------

.. function:: griot_core.normalize_keys(data: dict, to_case: str = "snake") -> dict

   Normalize dictionary keys to snake_case or camelCase.

   :param data: Dictionary to normalize
   :param to_case: Target case ("snake" or "camel")
   :returns: Dictionary with normalized keys

.. function:: griot_core.to_snake_case(s: str) -> str

   Convert string to snake_case.

   :param s: String to convert
   :returns: snake_case string

.. function:: griot_core.to_camel_case(s: str) -> str

   Convert string to camelCase.

   :param s: String to convert
   :returns: camelCase string

Constants
---------

.. data:: griot_core.CONTRACT_FIELD_TYPES

   Dictionary of contract field names to their expected types.

.. data:: griot_core.ODCS_MANDATORY_FIELDS

   List of mandatory fields for ODCS compliance.
