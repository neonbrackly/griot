Contract Operations
===================

Functions for loading, diffing, and linting contracts.

load_contract
-------------

.. py:function:: griot_core.load_contract(path) -> type[GriotModel]

   Load a contract from a YAML file.

   :param path: Path to YAML contract file
   :type path: str | Path
   :returns: GriotModel subclass
   :rtype: type[GriotModel]
   :raises ContractNotFoundError: If file doesn't exist
   :raises ContractParseError: If YAML is invalid

   **Example:**

   .. code-block:: python

      from griot_core import load_contract

      Customer = load_contract("contracts/customer.yaml")
      result = Customer.validate(data)

ContractDiff
------------

.. py:class:: griot_core.ContractDiff

   Result of comparing two contracts.

   **Attributes:**

   .. py:attribute:: added_fields
      :type: list[str]

      Fields added in new contract.

   .. py:attribute:: removed_fields
      :type: list[str]

      Fields removed from old contract.

   .. py:attribute:: type_changes
      :type: list[TypeChange]

      Fields with changed types.

   .. py:attribute:: constraint_changes
      :type: list[ConstraintChange]

      Fields with changed constraints.

   .. py:attribute:: has_breaking_changes
      :type: bool

      True if any changes are breaking.

   **Methods:**

   .. py:method:: to_dict() -> dict

      Convert diff to dictionary.

   .. py:method:: to_markdown() -> str

      Format diff as markdown.

   **Example:**

   .. code-block:: python

      diff = NewCustomer.diff(OldCustomer)

      if diff.has_breaking_changes:
          print("Breaking changes detected!")
          for field in diff.removed_fields:
              print(f"  Removed: {field}")
          for change in diff.type_changes:
              print(f"  Type change: {change.field}")

TypeChange
----------

.. py:class:: griot_core.TypeChange

   Record of a field type change.

   **Attributes:**

   .. py:attribute:: field
      :type: str

      Field name.

   .. py:attribute:: old_type
      :type: str

      Previous type.

   .. py:attribute:: new_type
      :type: str

      New type.

   .. py:attribute:: breaking
      :type: bool

      Whether this is a breaking change.

ConstraintChange
----------------

.. py:class:: griot_core.ConstraintChange

   Record of a constraint change.

   **Attributes:**

   .. py:attribute:: field
      :type: str

      Field name.

   .. py:attribute:: constraint
      :type: str

      Constraint name (pattern, min_length, etc.).

   .. py:attribute:: old_value
      :type: Any

      Previous value.

   .. py:attribute:: new_value
      :type: Any

      New value.

   .. py:attribute:: breaking
      :type: bool

      Whether this is a breaking change.

LintIssue
---------

.. py:class:: griot_core.LintIssue

   Contract linting issue.

   **Attributes:**

   .. py:attribute:: field
      :type: str | None

      Field name (None for contract-level issues).

   .. py:attribute:: code
      :type: str

      Issue code (e.g., "W001").

   .. py:attribute:: message
      :type: str

      Human-readable message.

   .. py:attribute:: severity
      :type: Severity

      Issue severity.

   **Example:**

   .. code-block:: python

      issues = Customer.lint()

      for issue in issues:
          print(f"[{issue.code}] {issue.field or 'contract'}: {issue.message}")

Lint Codes
^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Code
     - Description
   * - W001
     - Field missing description
   * - W002
     - No examples provided
   * - W003
     - PII field without masking strategy
   * - W004
     - PII field without legal basis
   * - W005
     - No primary key defined
   * - W006
     - Contract missing version
   * - W007
     - Contract missing owner
   * - E001
     - Invalid pattern regex
   * - E002
     - Conflicting constraints
   * - E003
     - Invalid enum values
