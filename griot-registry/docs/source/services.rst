Services Module
===============

The services module contains business logic for contract management and
validation. Services orchestrate operations between the API layer and storage.

ContractService
---------------

The ``ContractService`` handles contract lifecycle operations, including
validation, versioning, and status management.

Overview
^^^^^^^^

.. code-block:: python

   from griot_registry.services import ContractService

   class ContractService:
       def __init__(self, storage: StorageBackend, settings: Settings):
           self.storage = storage
           self.settings = settings
           self.validation_service = ValidationService(settings)

Key Methods
^^^^^^^^^^^

create
~~~~~~

Creates a new contract with validation:

.. code-block:: python

   async def create(
       self,
       contract: Contract,
       user: User,
       skip_validation: bool = False,
   ) -> Contract:
       """Create a new contract.

       Args:
           contract: The contract to create
           user: The authenticated user
           skip_validation: Skip validation (not recommended)

       Returns:
           Created contract with generated ID

       Raises:
           ValidationError: If contract fails validation
       """

**Workflow:**

1. Generate unique ID if not provided
2. Validate contract structure and lint (unless skipped)
3. Set created_by and timestamps
4. Store contract in repository
5. Update schema catalog

update
~~~~~~

Updates a contract with versioning and breaking change detection:

.. code-block:: python

   async def update(
       self,
       contract: Contract,
       user: User,
       change_type: str | None = None,
       change_notes: str | None = None,
       allow_breaking: bool = False,
   ) -> Contract:
       """Update an existing contract.

       Args:
           contract: Updated contract
           user: The authenticated user
           change_type: Version bump type (major, minor, patch)
           change_notes: Description of changes
           allow_breaking: Allow breaking changes without error

       Returns:
           Updated contract with new version

       Raises:
           ContractNotFoundError: If contract doesn't exist
           BreakingChangeError: If breaking change detected without allow_breaking
           ValidationError: If updated contract fails validation
       """

**Workflow:**

1. Fetch existing contract
2. Detect breaking changes by comparing schemas
3. If breaking change and not allowed, raise error
4. Determine version bump (auto-detect or use provided)
5. Store previous version in history
6. Validate and save updated contract
7. Update schema catalog

update_status
~~~~~~~~~~~~~

Manages contract status transitions:

.. code-block:: python

   async def update_status(
       self,
       contract_id: str,
       new_status: str,
       user: User,
   ) -> Contract:
       """Update contract status.

       Args:
           contract_id: Contract to update
           new_status: Target status
           user: Authenticated user

       Returns:
           Updated contract

       Raises:
           ValueError: If status transition is invalid
       """

**Valid Transitions:**

.. code-block:: text

   draft → active (activation)
   active → deprecated (deprecation)
   deprecated → retired (retirement)
   deprecated → active (reactivation)

search
~~~~~~

Full-text search across contracts:

.. code-block:: python

   async def search(
       self,
       query: str,
       limit: int = 50,
   ) -> list[dict[str, Any]]:
       """Search contracts.

       Returns list of search hits with:
       - contract_id
       - contract_name
       - version
       - status
       - score (relevance)
       - match_type
       - snippet
       """

ValidationService
-----------------

The ``ValidationService`` wraps griot-core validation functions and applies
registry-specific rules.

Overview
^^^^^^^^

.. code-block:: python

   from griot_registry.services import ValidationService

   class ValidationService:
       def __init__(self, settings: Settings):
           self.settings = settings

Key Methods
^^^^^^^^^^^

validate
~~~~~~~~

Validates a contract and returns results:

.. code-block:: python

   async def validate(
       self,
       contract: Contract,
   ) -> ValidationResult:
       """Validate a contract.

       Args:
           contract: Contract to validate

       Returns:
           ValidationResult with:
           - valid: bool
           - errors: list of error dicts
           - warnings: list of warning dicts
           - blocking: bool (should block operation)
       """

**Validation Steps:**

1. **Structure validation**: Uses ``griot_core.validate_contract_structure()``
2. **Linting**: Uses ``griot_core.lint_contract()`` for best practices
3. **Blocking determination**: Based on settings and severity

lint
~~~~

Runs linting rules without full validation:

.. code-block:: python

   async def lint(
       self,
       contract: Contract,
   ) -> list[LintIssue]:
       """Lint a contract for best practices.

       Returns list of issues with:
       - code: Issue code (e.g., "MISSING_DESCRIPTION")
       - message: Human-readable message
       - severity: "error" or "warning"
       - path: JSON path to problematic element
       """

Breaking Change Detection
-------------------------

The ``ContractService`` detects breaking changes when updating contracts:

.. code-block:: python

   def _detect_breaking_changes(
       self,
       old_contract: Contract,
       new_contract: Contract,
   ) -> list[str]:
       """Detect breaking changes between versions.

       Returns list of breaking change descriptions.
       """

**Breaking Changes Detected:**

- Removing a schema
- Removing a required field
- Changing a field's data type
- Making an optional field required
- Narrowing field constraints (e.g., removing enum values)

**Non-Breaking Changes:**

- Adding new schemas
- Adding new optional fields
- Making required fields optional
- Widening constraints

Version Increment Logic
-----------------------

The service automatically determines version bumps:

.. code-block:: python

   def _increment_version(
       self,
       current: str,
       change_type: str | None,
       is_breaking: bool,
   ) -> str:
       """Calculate new version.

       Args:
           current: Current version (e.g., "1.2.3")
           change_type: Explicit type or None for auto
           is_breaking: Whether changes are breaking

       Returns:
           New version string
       """

**Auto-Detection Rules:**

- Breaking changes → major bump (1.0.0 → 2.0.0)
- New schemas/fields → minor bump (1.0.0 → 1.1.0)
- Other changes → patch bump (1.0.0 → 1.0.1)

Using Services
--------------

Services are typically accessed through FastAPI dependencies:

.. code-block:: python

   from fastapi import Depends
   from griot_registry.api.dependencies import get_contract_service

   @router.post("/contracts")
   async def create_contract(
       request: ContractCreateRequest,
       service: ContractService = Depends(get_contract_service),
       user: User = Depends(get_current_user),
   ):
       contract = Contract(**request.model_dump())
       return await service.create(contract, user)

Or instantiate directly for scripts:

.. code-block:: python

   from griot_registry.services import ContractService, ValidationService
   from griot_registry.storage import create_storage
   from griot_registry.config import get_settings

   async def main():
       settings = get_settings()
       storage = await create_storage(settings)

       contract_service = ContractService(storage, settings)
       validation_service = ValidationService(settings)

       # Use services
       result = await validation_service.validate(my_contract)
       if result.valid:
           created = await contract_service.create(my_contract, user)

       await storage.close()
